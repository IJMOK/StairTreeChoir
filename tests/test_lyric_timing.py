from types import SimpleNamespace as NS

from tools import lyric_timing as lt


def test_lyric_lines_strip_lrc_tags_and_blanks():
    text = "[ar: Someone]\n[00:12.34] First line\n\n[Chorus]\nSecond line  \n"
    assert lt.lyric_lines(text) == ["First line", "Second line"]


def test_word_key_matches_xlights_lookup():
    # xLights keeps apostrophes and drops other punctuation before uppercasing.
    assert lt.xlights_word_key("rockin',") == "ROCKIN'"
    assert lt.xlights_word_key("tree!") == "TREE"
    assert lt.xlights_word_key("(Hee-haw,") == "HEEHAW"  # brackets come off too


def test_to_xlights_shape():
    word = lambda w, s, e: NS(word=w, start=s, end=e)
    result = NS(segments=[
        NS(text=" Hello there ", start=1.0, end=2.0, words=[word(" Hello", 1.0, 1.4), word(" there", 1.5, 2.0)]),
        NS(text=" ", start=3.0, end=3.0, words=[word(" ", 3.0, 3.0)]),
    ])
    assert lt.to_xlights(result) == {"segments": [{
        "text": "Hello there", "start_time": 1.0, "end_time": 2.0,
        "words": [{"text": "Hello", "start_time": 1.0, "end_time": 1.4},
                  {"text": "there", "start_time": 1.5, "end_time": 2.0}]}]}


def test_lrc_fallback_replaces_only_bad_lines():
    seg = lambda a, b, n: {"text": "x", "start_time": a, "end_time": b,
                           "words": [{"text": "w", "start_time": a, "end_time": b} for _ in range(n)]}
    data = {"segments": [seg(1.0, 2.0, 2), seg(3.0, 3.01, 2), seg(9.0, 10.0, 2)]}
    starts = lt.lrc_starts("[00:01.10] a b\n[00:02.90] c d\n[00:05.00] e f\n")
    assert starts == [1.1, 2.9, 5.0]
    assert lt.apply_lrc_fallback(data, starts, 12.0) == [2, 3]
    s2 = data["segments"][1]
    assert s2["start_time"] == 2.9 and s2["end_time"] > 3.4
    assert s2["words"][0]["end_time"] == s2["words"][1]["start_time"]
    assert data["segments"][0]["start_time"] == 1.0  # good line untouched
