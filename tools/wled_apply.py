"""Apply a generated tree config to a WLED device: python -m tools.wled_apply <tree 1-14> <device ip>

Reads wled/stairtree-NN.json, puts the site's Wi-Fi name and password in from the environment
(never from git) and POSTs it to http://<device>/json/cfg, then the device reboots onto its
fixed IP. The device is usually still at its factory address (join its WLED-AP network and use
4.3.2.1) or on a DHCP address from the site router.

    STAIRTREE_WIFI_SSID=...  STAIRTREE_WIFI_PSK=...  python -m tools.wled_apply 3 4.3.2.1
    --dry-run prints the JSON that would be sent, with the password hidden.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

from tools.gen_site_config import WLED_DIR


def build(tree: int, ssid: str, psk: str) -> dict:
    cfg = json.loads((WLED_DIR / f"stairtree-{tree:02d}.json").read_text(encoding="utf-8"))
    wifi = cfg["nw"]["ins"][0]
    wifi["ssid"] = ssid
    wifi["psk"] = psk          # cfg.cpp deserializeConfig reads nw.ins[].psk when present
    return cfg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tree", type=int)
    ap.add_argument("device", help="the device's current IP address")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ssid, psk = os.environ.get("STAIRTREE_WIFI_SSID", ""), os.environ.get("STAIRTREE_WIFI_PSK", "")
    if not ssid or not psk:
        sys.exit("set STAIRTREE_WIFI_SSID and STAIRTREE_WIFI_PSK in the environment first")
    cfg = build(args.tree, ssid, psk)
    if args.dry_run:
        shown = json.loads(json.dumps(cfg))
        shown["nw"]["ins"][0]["psk"] = "********"
        print(json.dumps(shown, indent=2))
        return
    req = urllib.request.Request(f"http://{args.device}/json/cfg", data=json.dumps(cfg).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.status, r.read().decode())


if __name__ == "__main__":
    main()
