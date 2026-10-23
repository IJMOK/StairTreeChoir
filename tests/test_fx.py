import pytest

from tools import fx


def test_settings_use_the_source_keys():
    s = fx.build_settings("On", {"Eff_On_Start": 100, "Eff_On_End": 20})
    assert s == "E_TEXTCTRL_Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=20"
    assert fx.build_settings("Marquee", {"Marquee_Band_Size": 3}) == "E_SLIDER_Marquee_Band_Size=3"


def test_decimals_go_in_the_text_box():
    assert fx.build_settings("ColorWash", {"ColorWash_Cycles": 2.5}) == "E_TEXTCTRL_ColorWash_Cycles=2.5"
    assert fx.build_settings("SingleStrand", {"Chase_Rotations": 3.0}) == "E_TEXTCTRL_Chase_Rotations=3.0"


def test_shared_panels_and_raw_keys():
    s = fx.build_settings("Fire", {"buffer": "Per Preview", "brightness": 35, "E_NOTEBOOK_SSEFFECT_TYPE": "Skips"})
    assert s == "B_CHOICE_BufferStyle=Per Preview,C_SLIDER_Brightness=35,E_NOTEBOOK_SSEFFECT_TYPE=Skips"


def test_bad_settings_fail_early():
    with pytest.raises(KeyError):
        fx.build_settings("Marquee", {"Marquee_Bandsize": 3})
    with pytest.raises(ValueError):
        fx.build_settings("Marquee", {"Marquee_Speed": 500})
    with pytest.raises(ValueError):
        fx.build_settings("Meteors", {"Meteors_Effect": "Sideways"})


def test_rainbow_turns_one_step_per_tree():
    assert fx.colours_for("rainbow", 1) == fx.RAINBOW
    assert fx.colours_for("rainbow", 2)[0] == fx.RAINBOW[1]
    assert fx.colours_for(["#123456"], 3) == ["#123456"]


def test_palette_string():
    assert fx.palette(["#FF0000", "#00FF00"]) == ("C_BUTTON_Palette1=#FF0000,C_CHECKBOX_Palette1=1,"
                                                 "C_BUTTON_Palette2=#00FF00,C_CHECKBOX_Palette2=1")


def test_eye_gaze_positions_land_on_the_right_pixels():
    # ring order: top, upper-right, lower-right, bottom, lower-left, upper-left (1-based start)
    (e,) = fx.eyes("follow", 2, 0, 1000, [], [], [(0, 1000, "left")])
    assert e.target == "StairTree2/Eyes"
    assert e.settings["Skips_StartPos"] == 5 and e.settings["Skips_BandSize"] == 2
    assert e.settings["Skips_BandSize"] + e.settings["Skips_SkipSize"] == 6   # same spot in both 6-pixel eyes
