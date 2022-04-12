"""
A reasonably efficient healthbar example.

Artwork from https://kenney.nl

If Python and Arcade are intalled, this example can be run from the command line with:
python -m arcade.examples.healthbar_for_units
"""

import arcade
from arcade import Color
from arcade.color import WHITE, BLACK, GREEN, RED


def _make_tinted_rect(color: Color = None, size_px: int = 8) -> arcade.Sprite:
    """
    Make a tintable sprite with a cached texture.

    These sprites are intended to be stretched to fill rectangular
    areas with a flat color.

    The default size_px is set to 8 to avoid edge artifacts and
    other issues when setting the texture. You may be able to
    go as small as n = 2. Pixel sizes of 1 may cause issues.

    :param color: what color to tint it to, if any
    :param size_px: how big the texture square should be
    """
    generated = arcade.SpriteSolidColor(size_px, size_px, WHITE)
    if color:
        generated.color = color

    return generated


class IndicatorBar:
    """
    Minimal indicator bar for displaying information about units

    For example, health bars are often used to show enemy health levels
    in top-down or isometric games. Although health bars are drawn over
    the background and units, the player's UI will cover up
    any enemy unit health bars drawn.

    In arcade terms, this means that the health bar should be drawn
    after units, but before the UI manager is told to draw.
    """

    def __init__(
        self,
        fill_width_px: int = 100,
        position: arcade.Point = (0, 0),
        height_px: int = 4,
        fullness: float = 1.0,
        full_color: Color = GREEN,
        empty_color: Color = RED,
        border_color: Color = BLACK,
        border_thickness_px: int = 2,
    ):
        self._fullness = 0.0
        self._fill_width_px = fill_width_px

        self._fill_height_px = height_px
        self._half_fill_width_px = self._fill_width_px // 2
        self._double_thickness = 2 * border_thickness_px

        self._height_px = height_px

        self._center_x: float = 0.0
        self._center_y: float = 0.0

        self.sprite_list = arcade.SpriteList()

        self.background_box = _make_tinted_rect(border_color)
        self.background_box.width = self._fill_width_px + self._double_thickness
        self.background_box.height = self._fill_height_px + self._double_thickness
        self.sprite_list.append(self.background_box)

        self.empty_part = _make_tinted_rect(empty_color)
        self.sprite_list.append(self.empty_part)
        self.empty_part.width = self._fill_width_px 
        self.empty_part.height = self._fill_height_px

        # the width of this sprite will be set directly to change how
        # full the bar appears.
        self.full_part = _make_tinted_rect(full_color)
        self.sprite_list.append(self.full_part)
        self.full_part.width = self._fill_width_px
        self.full_part.height = self._fill_height_px

        # apply appearance using the properties defined below
        self.fullness = fullness
        self.position = position

    def draw(self):
        self.sprite_list.draw()

    @property
    def fullness(self) -> float:
        return self._fullness

    @fullness.setter
    def fullness(self, new_fullness: float):
        if new_fullness > 1.0 or new_fullness < 0.0:
            raise ValueError(
                f"Got {new_fullness}, but fullness must be between 0.0 and 1.0"
            )
        else:
            fpart = self.full_part
            fpart.width = self._fill_width_px * new_fullness
            fpart.left = self._center_x - self._half_fill_width_px

            self._fullness = new_fullness

    @property
    def position(self):
        return self._center_x, self._center_y

    @position.setter
    def position(self, new_position):

        # only bother calling move if the position actually changed
        if new_position != self.position:
            self.sprite_list.move(
                new_position[0] - self._center_x, new_position[1] - self._center_y
            )
            self._center_x, self._center_y = new_position


class Game(arcade.Window):
    def __init__(self):
        super().__init__(640, 480, "Test")
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.hp_bar = IndicatorBar(position=(640 // 2, 480 // 2))

    def on_update(self, dt: float):

        new_fullness = max(self.hp_bar.fullness - (dt / 1), 0.0)
        if new_fullness <= 0:
            new_fullness = 1.0
        self.hp_bar.fullness = new_fullness

    def on_draw(self):
        self.clear()
        self.hp_bar.draw()


if __name__ == "__main__":
    game = Game()
    arcade.run()
