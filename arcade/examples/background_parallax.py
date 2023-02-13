"""
Parallax background layers move slower the "farther" away they are.

This is technique is common in side-scrolling games such as platformers.
Arcade has a special class for it. The bare minimum it requires is an
image path & depth value for each layer. When used with a camera object,
the parallax group will move each layer to create the impression of depth
for you.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_parallax
"""

import arcade
import arcade.background as background

SCREEN_WIDTH = 800

SCREEN_TITLE = "Background Group Example"

PLAYER_SPEED = 300

BASE_LAYER_HEIGHT = 240
PIXEL_SCALE = 3

# Prescale the size of the fill layers.
FINAL_LAYER_HEIGHT = BASE_LAYER_HEIGHT * PIXEL_SCALE


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, FINAL_LAYER_HEIGHT, SCREEN_TITLE, resizable=True)

        # Set the background color to equal to that of the first background.
        self.background_color = (162, 84, 162, 255)

        self.camera = arcade.SimpleCamera()

        # create a background group which will hold all the moving layers
        self.backgrounds = background.ParallaxGroup()

        # Calculate the current size of each background fill layer in pixels
        bg_layer_size_px = (SCREEN_WIDTH, FINAL_LAYER_HEIGHT)

        # Import the image data for each background layer from files.
        # Unlike sprites, the scale of background layers doesn't resize
        # the layer itself. Instead, it changes the zoom level, while
        # the depth controls how fast each layer scrolls. This means
        # that you have to precalculate the size of the background layer
        # as we have earlier in this file.
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/Layers/back.png",
            size=bg_layer_size_px,
            depth=10.0,  # The higher this value is, the slower the background will scroll.
            scale=PIXEL_SCALE
        )
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/Layers/buildings.png",
            size=bg_layer_size_px,
            depth=5.0,
            scale=PIXEL_SCALE
        )
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/Layers/palms.png",
            size=bg_layer_size_px,
            depth=3,
            scale=PIXEL_SCALE
        )
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/Layers/highway.png",
            size=bg_layer_size_px,
            depth=1.0,
            scale=PIXEL_SCALE
        )

        # Create & position the player sprite.
        self.player_sprite = arcade.Sprite(
            f":resources:/images/miami_synth_parallax/Car/car-idle.png",
            center_y=self.camera.viewport_height // 2, scale=3.0
        )
        self.player_sprite.bottom = 0

        # Track Player Motion
        self.x_direction = 0

    def pan_camera_to_player(self):
        # Move the camera toward the center of the player's sprite
        target_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        self.camera.move_to((target_x, 0.0), 0.1)

    def on_update(self, delta_time: float):
        self.player_sprite.center_x += self.x_direction * delta_time
        self.pan_camera_to_player()

    def on_draw(self):
        self.clear()

        self.camera.use()

        # Ensure the backgrounds aligns with the camera
        self.backgrounds.pos = self.camera.position

        # Offset the backgrounds texture.
        self.backgrounds.offset = self.camera.position

        self.backgrounds.draw()
        self.player_sprite.draw(pixelated=True)

    def update_car_direction(self):

        # Cheesy trick for inverting the direction. You should usually use
        # different textures instead, such as those created by Texture.flip_left_to_right().
        # This trick is used here because animation isn't the focus of this example.
        if self.x_direction < 0:
            self.player_sprite.scale_xy = (-PIXEL_SCALE, PIXEL_SCALE)
        elif self.x_direction > 0:
            self.player_sprite.scale_xy = (PIXEL_SCALE, PIXEL_SCALE)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_direction -= PLAYER_SPEED
            self.update_car_direction()
        elif symbol == arcade.key.RIGHT:
            self.x_direction += PLAYER_SPEED
            self.update_car_direction()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_direction += PLAYER_SPEED
            self.update_car_direction()
        elif symbol == arcade.key.RIGHT:
            self.x_direction -= PLAYER_SPEED
            self.update_car_direction()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.resize(width, height)
        full_width_size = (width, FINAL_LAYER_HEIGHT)

        # We can iterate through a background group,
        # but in the case of a parallax group the iter returns
        # both the Backgrounds and the depths. (tuple[Background, float])
        for layer, depth in self.backgrounds:
            layer.size = full_width_size


def main():
    app = MyGame()
    app.run()


if __name__ == "__main__":
    main()
