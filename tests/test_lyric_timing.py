from types import SimpleNamespace as NS

from tools import lyric_timing as lt


def test_lyric_lines_strip_lrc_tags_and_blanks():
    text = "[ar: Someone]\n[00:12.34] First line\n\n[Chorus]\nSecond line  \n"
    assert lt.lyric_lines(text) == ["First line", "Second line"]


def test_word_key_matches_xlights_lookup():
    # xLights keeps apostrophes and drops other punctuation before uppercasing.
    assert lt.xlights_word_key("rockin',") == "ROCKIN'"
    assert lt.xlights_word_key("tree!") == "TREE"


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
