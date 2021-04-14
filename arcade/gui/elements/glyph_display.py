"""

UI elements for displaying rapidly changing values of specific types.

Integer scores, timers, etc.

The implementation details can be changed later once graphics and
text rendering are refactored.

"""

from typing import Tuple, Dict, List, Union
from arcade import SpriteList, Texture, Color
from arcade.color import WHITE
from arcade.gui import UIBoxLayout, text_utils


# Intentionally includes 0 and 256 because:
# 1. This will be passed to the range function
# 2. Some fonts include support for normally unprintable characters
ASCII_WITH_LATIN_1 = (0, 256)


def render_glyph_texture_from_system_font(
        glyph: str,
        font_name: str = "arial",
        font_size: int = 16,
        font_color: Color = WHITE
) -> Texture:
    """
    Create a texture for a single character from a system font.

    :param glyph: A 1-length string of any unicode codepoint.
    :param font_name: what font to use.
    :param font_size:
    :param font_color:
    :return:
    """

    if not isinstance(glyph, str):
        raise TypeError(f"glyph must be a string, not {type(glyph)!r}")

    if len(glyph) != 1:
        raise ValueError("glyph string must be of length 1")

    glyph_raw_image = text_utils.create_raw_text_image(
        text=glyph,
        font_name=font_name,
        font_size=font_size,
        font_color=font_color
    )

    # Ensure strange byte values are readable to humans. An early null
    # byte in the texture name seems to cause issues in the interpreter
    # and cause a blank stack trace to print on exit. Regardless, null
    # is technically a valid unicode code point that can have map to
    # glyphs, so we will try to sanitize all unprintable characters to
    # readable names.
    tex_name = f"{font_name}-{font_size}-{hex(ord(glyph))}"

    glyph_texture = Texture(
        tex_name,
        glyph_raw_image,
        # Ensure the dimensions of the image are used for packing to
        # preserve kerning instead of making characters touch.
        hit_box_algorithm='None'
    )
    return glyph_texture


def build_glyph_table_from_system_font(
        font_name: str = "arial",
        font_size: int = 16,
        font_color: Color = WHITE,
        code_range: Union[Tuple[int, int], List] = ASCII_WITH_LATIN_1
) -> Dict[str, Texture]:
    """
    Use a system font to build a table of glyph images to display data.

    By default, attempt to rasterize glyphs for ASCII + latin1. This
    includes null and other normally unprintable characters because
    fonts can choose to provide glyphs for these character values even
    if most do not.

    Common use cases for these unusual fonts include shipping custom
    glyphs for games and interfaces, so it makes sense to support this
    feature here.

    :param font_name: a string matching an installed system font
    :param font_color: a color to set the font to
    :param font_size: unclear what unit this is, may be points
    :param code_range: start and stop characters to cache in unicode
    :return: A glyph table matching this font and size.
    """

    # enforce typing on code range
    if not isinstance(code_range, (tuple, list)) or \
            len(code_range) != 2 or \
            not isinstance(code_range[0], int) or \
            not isinstance(code_range[1], int):
        raise TypeError(
            f"code_range must be a list or tuple of two integers,"
            f" not {code_range!r}")

    range_start, range_stop = code_range

    # Unicode codepoints can't be negative
    if range_start < 0:
        raise ValueError(
            f"code_range must start at 0 or higher, not {range_start!r}"
        )

    # Restrict values so that range_start < range_stop
    elif range_stop <= range_start:
        raise ValueError(
            f"code_range's first value must be higher than its second,"
            f"but got {code_range!r}"
        )

    # build the glyph table for all glyphs in the passed range
    glyph_table = {}
    for char in (chr(code) for code in range(range_start, range_stop)):
        glyph_table[char] = render_glyph_texture_from_system_font(
            char,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color
        )
    return glyph_table











