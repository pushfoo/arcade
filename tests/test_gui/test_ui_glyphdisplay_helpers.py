"""
Test if glyph display helpers work correctly
"""
from arcade import Texture
from arcade.gui.elements.glyph_display import (
    build_glyph_table_from_system_font,
    render_glyph_texture_from_system_font
)
import pytest


def test_render_glyph_texture_from_system_font():

    # type enforcement for glyphs
    with pytest.raises(TypeError):
        render_glyph_texture_from_system_font([])

    # single character enforcement
    for non_single_character_string in ["", "bad string"]:
        with pytest.raises(ValueError):
            render_glyph_texture_from_system_font(
                non_single_character_string)

    # nulls get properly escaped to be human readable and prevent
    # strange interpreter behavior when cstrings end early.
    null_character_texture = render_glyph_texture_from_system_font("\0")
    tex_name = null_character_texture.name
    assert "\0" not in tex_name
    assert tex_name.endswith("0x0")

    # type check
    assert isinstance(null_character_texture, Texture)


def test_build_glyph_table_from_system_font():


    # test type checking on range
    bad_code_range_types = [
        {},  # wrong type and wrong length
        "no",  # has length 2, but wrong type
        ("a", 1),  # non-integer values
        (0, "e"),
        (1, 2, 3)  # wrong length
    ]

    for bad_arg_type in bad_code_range_types:
        with pytest.raises(TypeError):
            build_glyph_table_from_system_font(code_range=bad_arg_type)

    # check codepoint range enforcement
    bad_code_range_values = [
        (-1, 256), # negative code point
        (12, 10)  # illegal ordering
    ]
    for bad_range_value in bad_code_range_values:
        with pytest.raises(ValueError):
            build_glyph_table_from_system_font(code_range=bad_range_value)

    # sniff check for result types
    table = build_glyph_table_from_system_font()
    assert len(table) == 256
    for glyph, texture in table.items():
        assert isinstance(glyph, str)
        assert isinstance(texture, Texture)
