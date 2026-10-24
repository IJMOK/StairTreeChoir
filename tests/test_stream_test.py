import av

from tools import stream_test


def test_build_interleaves_two_songs(tmp_path):
    out = stream_test.build(["rockin-around", "auld-lang-syne"], tmp_path / "t.mp4", seconds=2)
    with av.open(str(out)) as c:
        v, a = c.streams.video[0], c.streams.audio[0]
        assert (v.width, v.height) == (stream_test.W, stream_test.H)
        assert abs(float(v.duration * v.time_base) - 4) < 0.2
        assert abs(float(a.duration * a.time_base) - 4) < 0.2
        # packets in file order never let one stream run ahead: the stream step sends them as read
        last = {"video": 0.0, "audio": 0.0}
        for p in c.demux():
            if p.dts is not None:
                last[p.stream.type] = float(p.dts * p.time_base)
                assert abs(last["video"] - last["audio"]) < 0.5


def test_stream_key_absent_is_none(monkeypatch):
    monkeypatch.delenv("YT_STREAM_KEY", raising=False)
    monkeypatch.setattr(stream_test.os, "name", "posix")    # skip the Windows registry
    assert stream_test._stream_key() is None
