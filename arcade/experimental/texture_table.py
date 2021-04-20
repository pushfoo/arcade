"""
Experimental Dict[str, Texture] tools for helping UI label prototyping.

Much of this will either be moved or replaced shortly. Do not rely on
these functions if you are an end user rather than a developer.

"""
from pathlib import Path
from typing import Union, List, Tuple, Dict
from arcade import Texture, load_spritesheet, Color
from arcade.color import WHITE
from arcade.gui import text_utils

TextureTable = Dict[str, Texture]

# Glyph selections are intentionally limited to these types.
# Other iterables like iterators will end up being consumed
# during type checking.
GlyphSelection = Union[str, List[str], Tuple[str]]


ASCII_WITH_LATIN_1 = ''.join([chr(c) for c in range(0, 256)])


def flatten_glyph_selection(selection: GlyphSelection) -> str:
    """
    Validate the argument and flatten it into a string.

    Note that you have to use raw string literals to cover certain
    characters when passing a glyph selection or you will get a
    misalignment in the number of characters.

    Ideally, this would be implemented as a Protocol if we could
    support 3.8 and up, but this allows 3.7 to work without adding
    any backport dependencies.

    :param selection: object to validate and flatten into a string
    :return: a string
    """
    if not isinstance(selection, (str, list, tuple)):
        raise TypeError(
            f"A glyph selection can only a string, list of "
            f"strings, or tuple of strings. Got {selection!r}"
            f" instead."
        )

    if len(selection) < 1 or len(selection[0]) < 1:
        raise ValueError(
            "Glyph selection is empty despite being the right type")

    # strings are already both valid and flat
    if isinstance(selection, str):
        return selection

    # make sure all elements are strings
    for index, element in enumerate(selection):
        if not isinstance(element, str):
            raise TypeError(
                f"Not all elements are strings: {element!r},"
                f" element at index {index}, is a {type(element)},"
                f"not a valid string."
            )

    # flatten it
    return ''.join(selection)


def remap_font_glyph_table_lowercase_to_upper(
        glyph_table: TextureTable) -> None:
    """
    Make lowercase glyphs duplicates of uppercase glyphs.

    Some fonts don't have lower case characters. Visually remappping
    lowercase characters to their uppercase equivalents will make those
    font spritesheets usable for general purposes.

    Modifies the texture table rather than returning a new one.

    :param glyph_table: A font texture table to modify in place
    :return:
    """

    for character, upper_texture in glyph_table.items():
        if character.isupper():
            glyph_table[character.lower()] = upper_texture


def load_monospace_spritesheet_font(
    file_name: Union[str, Path],
    sprite_width: int,
    sprite_height: int,
    columns: int,
    count: int,
    margin: int = 0,
    glyph_selection: GlyphSelection = ASCII_WITH_LATIN_1,
    check_lengths: bool = True,
    map_lower_to_upper: bool = False
) -> TextureTable:
    """
    Load a font from disk to a TextureTable (Dict[str, Texture]).

    Arguments are similar to those of load_spritesheet aside from the
    last two.

    glyph_selection is a string, list of strings, or tuple of strings.
    It specifies how the tiles in a sprite sheet map to characters.

    check_lengths guards against the user forgetting to use raw mode
    strings. If users don't use raw strings with triple-quotes, they
    may accidentally terminate a line with a comment or escape a
    character when declaring the character to glyph mapping for the
    sheet. If this happens, the length of the flat selection won't
    match  the the declared count.

    :param file_name: what file to load the font from.
    :param sprite_width: how wide each sprite is.
    :param sprite_height: how tall each sprite is.
    :param columns: how many columns there are in the sprite sheet.
    :param count: how many sprites to read from the sheet.
    :param margin: marging between sprites.
    :param glyph_selection: which glyphs are in the spritesheet.
    :param check_lengths: sniff for malformed glyph selections.
    :param map_lower_to_upper: make lowercase characters draw as upper.
    :return:
    """
    flat_selection = flatten_glyph_selection(glyph_selection)
    flat_length = len(flat_selection)


    if check_lengths and flat_length != count:
        raise ValueError(
            f"The glyph selection is valid but its length {flat_length}"
            f"does not match the number of sprites requested from the "
            f"sheet ({count}"
         )

    raw_sheet = load_spritesheet(
        file_name,
        sprite_width,
        sprite_height,
        columns,
        count,
        margin=margin
    )

    texture_table: TextureTable = {}

    # assign each sprite to a value.
    for index, character in enumerate(flat_selection):
        texture_table[character] = raw_sheet[index]

        # make fonts with no lower case able to display lowercase
        if map_lower_to_upper and character.isupper():
            texture_table[character.lower()] = raw_sheet[index]

    if map_lower_to_upper:
        remap_font_glyph_table_lowercase_to_upper(texture_table)

    return texture_table


def render_glyph_texture_from_system_font(
        glyph: str,
        font_name: str = "arial",
        font_size: int = 16,
        font_color: Color = WHITE,
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
        glyph_selection: GlyphSelection = ASCII_WITH_LATIN_1,
        map_lower_to_upper: bool = False
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
    :param glyph_selection: what glyphs to rasterize to the table
    :return: A glyph table matching this font and size.
    """

    flattened_selection = flatten_glyph_selection(glyph_selection)

    # build the glyph table for all included_glyphs in the passed range
    glyph_table = {}

    for char in flattened_selection:
        glyph_table[char] = render_glyph_texture_from_system_font(
            char,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color
        )
    return glyph_table

DEFAULT_GLYPH_FONT = build_glyph_table_from_system_font()