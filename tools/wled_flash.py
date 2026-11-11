"""Program a tree controller over USB: python -m tools.wled_flash <tree 1-14> [--port COMn] [--site]

Erases the ESP32, flashes WLED 16.0.1, joins it to Wi-Fi over Improv serial, POSTs the tree's
config, then reads it back. Bench mode (the default) leaves the board on DHCP on the Wi-Fi it
joined; --site also sets the tree's site network from data/sites.json (a fixed 192.168.8.x address
unless the site uses DHCP reservations), after which the PC may only reach
it through the site router.

    python -m tools.wled_flash --identify           # read-only: port, MAC, flash size, what's on it
    python -m tools.wled_flash 3 --port COM7        # flash tree 3, bench mode

USB only: never with 12V on the board (electronics/README.md). Wi-Fi comes from wled_apply.credentials(),
never git. The flash layout is the one install.wled.me uses for a 4MB ESP32, read from WLED-WebInstaller
at the commit below: bootloader at 0x1000 re-flagged for 4MB (esptool's --flash-size does this and redoes
its digest), partition table at 0x8000, firmware at 0x10000, with otadata left blank by the erase so it
boots app0.

Improv packets are as wled00/improv.cpp at tag v16.0.1: "IMPROV", version 1, type, length, data, then
the low byte of the sum of everything before it. Type 3 is an RPC: command, data length, data.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from tools.gen_site_config import WLED_DIR
from tools.gen_site_wiring import ip
from tools.tree_layout import ROOT
from tools.wled_apply import credentials

WLED_VERSION = "16.0.1"
INSTALLER = "https://raw.githubusercontent.com/wled/WLED-WebInstaller/35d7284fe64d4c22d2a32bd4ea9d7bee6f52a959/bin/boot"
# (offset, file name, url, sha256)
IMAGES = [
    (0x1000, "bootloader_esp32_8m.bin", f"{INSTALLER}/bootloaders/esp32/bootloader_esp32_8m.bin",
     "dd83e828882288c738d5f8916ba74d400491e6832abd65440b91f0a03fd2308e"),
    (0x8000, "partitions_c3_4m.bin", f"{INSTALLER}/partitions/partitions_c3_4m.bin",
     "ab7a19ebb0ea19e684687802f2d8f199225a270c6b7dd72d73e8a8876f382e73"),
    (0x10000, f"WLED_{WLED_VERSION}_ESP32.bin",
     f"https://github.com/wled/WLED/releases/download/v{WLED_VERSION}/WLED_{WLED_VERSION}_ESP32.bin",
     "628917b0753edcfc9a8408e6387c6d1ace6a360d315441e9563d60299fef8594"),
]
CACHE = Path.home() / ".cache" / "stairtree-wled" / WLED_VERSION
LOG_FILE = WLED_DIR / "provisioned.csv"

# Boards that are never tree controllers: the wreath, and the packed-away Star and SoundReactive.
PROTECTED = {"d48c49160a30": "the wreath", "a4cf12f11ff7": "the old wreath ESP8266",
             "98cdac30920f": "WLED_Star", "c4dee21939ec": "WLED-SoundReactive"}

RPC_WIFI, RPC_STATE, RPC_INFO = 1, 2, 3
TYPE_STATE, TYPE_ERROR, TYPE_RPC, TYPE_RESULT = 1, 2, 3, 4
PROVISIONED = 4
BOOT_S, WIFI_S, REBOOT_S, PORT_WAIT_S = 20, 45, 40, 60


def improv_packet(command: int, data: bytes = b"") -> bytes:
    body = bytes([command, len(data)]) + data
    packet = b"IMPROV" + bytes([1, TYPE_RPC, len(body)]) + body
    return packet + bytes([sum(packet) & 0xFF])


def wifi_payload(ssid: str, psk: str) -> bytes:
    s, p = ssid.encode(), psk.encode()
    if len(s) > 32 or len(p) > 64:
        raise ValueError("Wi-Fi name or password too long for WLED")
    return bytes([len(s)]) + s + bytes([len(p)]) + p


def improv_frames(buf: bytes) -> tuple[list[tuple[int, bytes]], bytes]:
    """Whole, valid frames in buf as (type, data), and what's left to wait for."""
    frames = []
    while True:
        start = buf.find(b"IMPROV")
        if start < 0:
            return frames, buf[-5:]
        buf = buf[start:]
        if len(buf) < 9 or len(buf) < 10 + buf[8]:
            return frames, buf
        end = 9 + buf[8]
        if sum(buf[:end]) & 0xFF == buf[end]:
            frames.append((buf[7], buf[9:end]))
        buf = buf[end + 1:]


def rpc_strings(data: bytes) -> list[str]:
    """The strings in an RPC result: command, total length, then length-prefixed strings."""
    out, pos = [], 2
    while pos < len(data):
        n = data[pos]
        out.append(data[pos + 1:pos + 1 + n].decode(errors="replace"))
        pos += 1 + n
    return out


def esptool(port: str, *args: str) -> str:
    done = subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32", "--port", port, "--baud", "460800",
                           *args], capture_output=True, text=True, errors="replace")
    if done.returncode:
        sys.exit(f"FAIL esptool {args[0]}:\n" + (done.stdout + done.stderr)[-800:])
    return done.stdout


def ports() -> list[str]:
    from serial.tools import list_ports
    return [p.device for p in list_ports.comports() if p.vid is not None]


def identify(port: str) -> dict:
    """Read-only. Resets the board, which is why this can't run while it's streaming."""
    out = esptool(port, "flash-id")
    mac = re.search(r"MAC:\s+([0-9a-f:]{17})", out)
    size = re.search(r"Detected flash size:\s+(\S+)", out)
    chip = re.search(r"Chip type:\s+(.+)", out)
    return {"port": port, "mac": mac.group(1).replace(":", "") if mac else "?",
            "flash": size.group(1) if size else "?", "chip": chip.group(1).strip() if chip else "?"}


def fetch_images() -> list[tuple[int, Path]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    out = []
    for offset, name, url, sha in IMAGES:
        path = CACHE / name
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            print("downloading", name, flush=True)
            with urllib.request.urlopen(url, timeout=60) as r:
                path.write_bytes(r.read())
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            path.unlink()
            sys.exit(f"FAIL {name} does not match its pinned SHA-256")
        out.append((offset, path))
    return out


def flash(port: str) -> None:
    images = fetch_images()
    print("erasing", flush=True)
    esptool(port, "erase-flash")
    print("writing WLED", WLED_VERSION, flush=True)
    args = ["write-flash", "--flash-size", "4MB", "--flash-mode", "dio"]
    for offset, path in images:
        args += [hex(offset), str(path)]
    esptool(port, *args)


class Improv:
    """Improv over the board's serial port, with DTR and RTS held so that opening it doesn't reset it."""

    def __init__(self, port: str):
        import serial
        self.s = serial.Serial()
        self.s.port, self.s.baudrate, self.s.timeout = port, 115200, 0.2
        self.s.dtr, self.s.rts = False, False
        self.s.open()
        self.buf = b""

    def close(self) -> None:
        self.s.close()

    def poll(self) -> list[tuple[int, bytes]]:
        self.buf += self.s.read(512)
        frames, self.buf = improv_frames(self.buf)
        return frames

    def info(self, wait_s: float) -> list[str]:
        """Device, version, chip and name, retrying while the board boots."""
        end = time.monotonic() + wait_s
        while time.monotonic() < end:
            self.s.write(improv_packet(RPC_INFO))
            until = time.monotonic() + 1
            while time.monotonic() < until:
                for kind, data in self.poll():
                    if kind == TYPE_RESULT and data[0] == RPC_INFO:
                        return rpc_strings(data)
        return []

    def join(self, ssid: str, psk: str, wait_s: float) -> str:
        """Send the Wi-Fi details; returns the device's http address once it's on the network."""
        self.s.write(improv_packet(RPC_WIFI, wifi_payload(ssid, psk)))
        end = time.monotonic() + wait_s
        while time.monotonic() < end:
            self.s.write(improv_packet(RPC_STATE))
            until = time.monotonic() + 2
            while time.monotonic() < until:
                for kind, data in self.poll():
                    if kind == TYPE_ERROR and data and data[0]:
                        sys.exit(f"FAIL Improv error {data[0]}")
                    if kind == TYPE_RESULT and data[0] in (RPC_WIFI, RPC_STATE):
                        found = [s for s in rpc_strings(data) if s.startswith("http")]
                        if found:
                            return found[0]
        sys.exit("FAIL no Wi-Fi join: check ~/.stairtree_wifi.json and that the network is in range")


def tree_config(tree: int, site: bool, ssid: str, psk: str) -> dict:
    cfg = json.loads((WLED_DIR / f"stairtree-{tree:02d}.json").read_text(encoding="utf-8"))
    if site:
        wifi = cfg["nw"]["ins"][0]
        wifi["ssid"], wifi["psk"] = ssid, psk
    else:
        del cfg["nw"]          # keep the join Improv made, on DHCP
    return cfg


def get(base: str, path: str) -> dict:
    with urllib.request.urlopen(base + path, timeout=5) as r:
        return json.load(r)


def apply_config(base: str, cfg: dict) -> None:
    req = urllib.request.Request(base + "/json/cfg", data=json.dumps(cfg).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        if r.status != 200:
            sys.exit(f"FAIL config POST returned {r.status}")


def check(tree: int, cfg: dict, base: str, mac: str) -> list[str]:
    """What's wrong on the device, read back after its reboot; empty is a pass."""
    end = time.monotonic() + REBOOT_S
    time.sleep(5)
    while True:
        try:
            info, live = get(base, "/json/info"), get(base, "/json/cfg")
            break
        except OSError:
            if time.monotonic() > end:
                return [f"no answer from {base} after the reboot"]
            time.sleep(2)
    want, bus = cfg["hw"]["led"]["ins"][0], live["hw"]["led"]["ins"][0]
    wrong = []
    if info.get("ver") != WLED_VERSION:
        wrong.append(f"version {info.get('ver')}")
    if info.get("mac") != mac:
        wrong.append(f"answered as {info.get('mac')}, expected {mac}")
    if live["id"]["mdns"] != f"stairtree-{tree:02d}":
        wrong.append(f"name {live['id']['mdns']}")
    if live["hw"]["led"]["maxpwr"] != cfg["hw"]["led"]["maxpwr"]:
        wrong.append(f"limit {live['hw']['led']['maxpwr']}")
    for key in ("len", "pin", "order", "type", "ledma"):
        if bus.get(key) != want[key]:
            wrong.append(f"{key} {bus.get(key)}, expected {want[key]}")
    if live["if"]["live"]["en"] is not True:
        wrong.append("receive realtime off")
    return wrong


def log(tree: int, mac: str, mode: str, address: str, path: Path = LOG_FILE) -> None:
    """One row per tree and per board: a renumbered board or a replaced tree loses its old row."""
    rows = []
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["mac"] != mac and r["tree"] != str(tree)]
    rows.append({"date": datetime.date.today().isoformat(), "tree": str(tree), "mac": mac,
                 "wled": WLED_VERSION, "mode": mode, "address": address})
    rows.sort(key=lambda r: int(r["tree"]))
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["date", "tree", "mac", "wled", "mode", "address"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def pick_port(given: str | None) -> str:
    if given:
        return given
    end = time.monotonic() + PORT_WAIT_S
    found = ports()
    if not found:
        print(f"waiting up to {PORT_WAIT_S}s for a board on USB", flush=True)
    while not found and time.monotonic() < end:
        time.sleep(1)
        found = ports()
    if len(found) != 1:
        sys.exit(f"FAIL expected one USB serial port, found {found or 'none'}: use --port")
    return found[0]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tree", type=int, nargs="?")
    ap.add_argument("--port")
    ap.add_argument("--site", action="store_true", help="also set the site Wi-Fi and the site's addressing (data/sites.json)")
    ap.add_argument("--identify", action="store_true", help="report what's on the port, change nothing")
    args = ap.parse_args()
    port = pick_port(args.port)
    board = identify(port)
    mac = board["mac"]
    if args.identify:
        print(board)
        if mac in PROTECTED:
            print("PROTECTED:", PROTECTED[mac])
        link = Improv(port)
        try:
            print("on it:", link.info(BOOT_S) or "no WLED answer")
        finally:
            link.close()
        return
    if args.tree is None or not 1 <= args.tree <= 14:
        sys.exit("give a tree number, 1 to 14")
    if mac in PROTECTED:
        sys.exit(f"FAIL refusing: {mac} is {PROTECTED[mac]}")
    if board["flash"] != "4MB":
        sys.exit(f"FAIL expected 4MB flash, found {board['flash']}")
    ssid, psk = credentials()
    print(f"tree {args.tree}, {board['chip']}, MAC {mac}, {port}", flush=True)
    flash(port)
    link = Improv(port)
    try:
        info = link.info(BOOT_S)
        if WLED_VERSION not in " ".join(info):
            sys.exit(f"FAIL WLED didn't answer after flashing: {info}")
        print("joining Wi-Fi", flush=True)
        base = link.join(ssid, psk, WIFI_S)
    finally:
        link.close()
    print("on the network at", base, flush=True)
    cfg = tree_config(args.tree, args.site, ssid, psk)
    apply_config(base, cfg)
    if args.site:
        log(args.tree, mac, "site", f"stairtree-{args.tree:02d}")
        print(f"PASS flashed; site config sent. Not read back: it reboots onto {ip(args.tree)}")
        return
    wrong = check(args.tree, cfg, base, mac)
    if wrong:
        sys.exit("FAIL read back: " + "; ".join(wrong))
    log(args.tree, mac, "bench", base)
    print(f"PASS tree {args.tree} = stairtree-{args.tree:02d}, MAC {mac}, WLED {WLED_VERSION}, {base}")


if __name__ == "__main__":
    main()
