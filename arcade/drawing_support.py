"""
Functions used to support drawing. No Pyglet/OpenGL here.
"""

import math
from typing import Tuple, Union, cast

from arcade.types import Color, RGBA


def get_points_for_thick_line(start_x: float, start_y: float,
                              end_x: float, end_y: float,
                              line_width: float):
    """
    Function used internally for Arcade. OpenGL draws triangles only, so a thick
    line must be two triangles that make up a rectangle. This calculates and returns
    those points.
    """
    vector_x = start_x - end_x
    vector_y = start_y - end_y
    perpendicular_x = vector_y
    perpendicular_y = -vector_x
    length = math.sqrt(vector_x * vector_x + vector_y * vector_y)
    if length == 0:
        normal_x = 1.0
        normal_y = 1.0
    else:
        normal_x = perpendicular_x / length
        normal_y = perpendicular_y / length
    r1_x = start_x + normal_x * line_width / 2
    r1_y = start_y + normal_y * line_width / 2
    r2_x = start_x - normal_x * line_width / 2
    r2_y = start_y - normal_y * line_width / 2
    r3_x = end_x + normal_x * line_width / 2
    r3_y = end_y + normal_y * line_width / 2
    r4_x = end_x - normal_x * line_width / 2
    r4_y = end_y - normal_y * line_width / 2
    return (r1_x, r1_y), (r2_x, r2_y), (r4_x, r4_y), (r3_x, r3_y)


def get_four_byte_color(color: Color) -> RGBA:
    """
    Converts a color to RGBA. If the color is already
    RGBA the original color value will be returned.
    If the alpha channel is not present a 255 value will be added.

    This function is useful when a mix of RGB and RGBA
    values are used and you need to enforce RGBA.

    Examples::

        >>> arcade.get_four_byte_color((255, 255, 255))
        (255, 255, 255, 255)

    :param Color color: Three or four byte tuple

    :returns:  return: Four byte RGBA tuple
    """

    if len(color) == 4:
        return cast(RGBA, color)
    elif len(color) == 3:
        return color[0], color[1], color[2], 255
    else:
        raise ValueError(f"This isn't a 3 or 4 byte color: {color}")


def get_three_float_color(color: Color) -> Tuple[float, float, float]:
    """
    Converts an RGB or RGBA byte color to a floating point RGB color.
    Basically we divide each component by 255.
    Float based colors are often used with OpenGL.

    Examples:

        >>> arcade.get_three_float_color(arcade.color.RED)
        (1.0, 0.0, 0.0)
        >>> arcade.get_three_float_color((255, 255, 255, 255)) 
        (1.0, 1.0, 1.0)

    :param Color color: Three or four byte tuple
    :return: Three floats as a RGB tuple
    """
    if len(color) in (3, 4):
        return color[0] / 255, color[1] / 255, color[2] / 255  # type: ignore
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def color_from_hex_string(code: str) -> RGBA:
    """
    Make a color from a hex code (3, 4, 6 or 8 characters of hex, normally with a hashtag).
    Supports most formats used in CSS. Returns an RGBA color.

    Examples::

        >>> arcade.color_from_hex_string("#ff00ff")
        (255, 0, 255, 255)
        >>> arcade.color_from_hex_string("#ff00ff00")
        (255, 0, 255, 0)
        >>> arcade.color_from_hex_string("#fff")
        (255, 255, 255, 255)

    """
    code = code.lstrip("#")
    if len(code) <= 4:
        code = "".join(i * 2 for i in code)

    if len(code) == 6:
        # full opacity if no alpha specified
        return int(code[:2], 16), int(code[2:4], 16), int(code[4:6], 16), 255
    elif len(code) == 8:
        return int(code[:2], 16), int(code[2:4], 16), int(code[4:6], 16), int(code[6:8], 16)

    raise ValueError(f"Improperly formatted color: '{code}'")
