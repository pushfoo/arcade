"""
Playback Speed Example: Piano Synthesizer

We can change the pitch of a sound by changing its playback speed. 
Playing a sound faster raises its pitch, while playing slower lowers it.

If we have a sound sample we want to turn into music, we first need:
    - the pitch in the original sample
    - the pitches of the notes we want to play

From those, we can figure out how fast to play the sample for each note.

Combining that with user input makes a playable instrument!

For more information on how piano tuning works, see the following link:
https://en.wikipedia.org/wiki/Piano_key_frequencies

"""
import math
from typing import List, Tuple
from collections import namedtuple

import arcade
from arcade import Color
import pyglet.media as media


# the repeating key pattern for an octave on a piano
OCTAVE_PATTERN = [
    # First 3 white keys with 2 black keys in between them
    False, True, False, True, False,
    # Next 4 white keys with 3 black keys in between
    False, True, False, True, False, True, False
]


def key_is_black(n: int, scale: List[bool] = OCTAVE_PATTERN) -> bool:
    """
    Calculate the color of the nth key on a standard piano keyboard

    :param int n: 1-indexed location on a piano keyboard
    :return bool: whether the nth key is black or not
    """

    # compensate for n being 1 indexed, 3 white keys + 1 index boost 
    return scale[(n - 4) % len(scale)]


def key_frequency(n: int, a_above_middle_c_hz: float = 440.0) -> float:
    """
    Calculate the frequency in hertz (hz) for the nth key on a piano
    
    This defaults to an equal temparament scale & A440 "concert" tuning.

    It's ok if you don't know what any of that means! For this example,
    all you need to know is that we use a specific note's frequency as
    reference to tune the entire scale.

    You can safely skip to the playback speed math, but you can check
    the wikipedia link at the start of this file if you're curious.

    :param int n: 1-indexed location on a piano keyboard 
    :param float a_above_middle_c_hz: reference frequency to use
    :return float: the note frequency for the nth key in hertz
    """
    return a_above_middle_c_hz * math.pow(2, (n - 49) / 12)


class SynthKey(arcade.SpriteSolidColor):
    """
    A single key that can be pressed down to play a note

    By default, it uses a built-in looping sample and keeps playing when
    the button is pressed, but that behavior can be overridden.

    Use the SynthKeyboard class further down to conveniently build a
    playable array of these that all use the same sample.
    """
    def __init__(
        self,
        width: float,
        height: float,
        sample: str,
        speed: float,
        up_color: Color = (255, 255, 255),
        down_color: Color = (210, 210, 210),
        loop: bool = True
    ):
        super().__init__(math.ceil(width), math.ceil(height), arcade.color.WHITE)
        
        self._sound = arcade.Sound(sample)
        self._loop = loop
        self._player: media.Player = None

        self._up_color = up_color
        self._down_color = down_color

        self._speed: float = speed
        self._pressed: bool = False
        self.color: Color = up_color

    @property
    def pressed(self) -> bool:
        return self._pressed

    @pressed.setter
    def pressed(self, new_state: bool):

        if new_state:
            # play sample with speed adjusment to hit this key's note
            self._player = arcade.play_sound(
                self._sound,
                looping=self._loop,
                pitch=self._speed
            )
            self.color = self._down_color

        else:
            # stop playing the clip
            if self._player is not None:
                if self._sound.is_playing(self._player):
                    arcade.stop_sound(self._player)

            self.color = self._up_color

        self._pressed = new_state

 
class SynthKeyboard:
    """
    Manager and generator for a playable keyboard. 

    It builds a range of keys on a standard piano keyboard. By default,
    the keys generated go from middle C to C5, including black keys.

    It's ok if you don't know what that means! Pay attention to the
    parts where frequency and speed are mentioned.
    """

    def __init__(
        self,
        width_px: float, 
        height_px: float,
        center_x: float = 0,
        center_y: float = 0,
        start_key_n: int = 40,
        end_key_n: int = 52,
        key_spacing_px: float = 2,
        sample: str = ":resources:/sounds/440hz_tuning_C4_sinewave.wav",
        loop_sample: bool = True,
        sample_pitch_hz: float = 440.0,
        a_above_middle_c_hz: float = 440.0,
        black_key_scale_x: float = 0.5,
        black_key_scale_y: float = 0.6
    ):

        self._center_x, self._center_y = center_x, center_y
        self._width_px, self._height_px = width_px, height_px

        self._start_key_n = start_key_n
        self._end_key_n = end_key_n
        self._sample = sample
        self._sample_pitch_hz = sample_pitch_hz
        self._key_spacing_px = key_spacing_px

        # figure out metadata needed to determine sizes 
        self._num_white_keys = 0
        self._num_black_keys = 0
        key_metadata = {} 

        for n in range(self._start_key_n, self._end_key_n + 1):
            is_black = key_is_black(n)
            
            if is_black:
                self._num_black_keys += 1
            else:
                self._num_white_keys += 1
                
            key_metadata[n] = is_black
        
        # determine key sizes and spacing
        self._white_key_width_px = self._width_px
        self._white_key_width_px -= key_spacing_px * (self._num_white_keys - 1)
        self._white_key_width_px /= self._num_white_keys

        self._white_key_height_px = height_px - 2 * self._key_spacing_px
        half_white_width = self._white_key_width_px / 2

        self._black_key_width_px, self._black_key_height_px = (
            self._white_key_width_px * black_key_scale_x,
            self._white_key_height_px * black_key_scale_y
        )

        white_key_step = self._white_key_width_px + self._key_spacing_px

        # how much to shift black keys left and up
        black_key_offset_x_px, black_key_offset_y_px = (
            half_white_width - white_key_step,
            self._white_key_height_px * ( 1 - black_key_scale_y) / 2
        )

        # calculate the leftmost center x for white keys
        white_key_start_x = self._center_x
        white_key_start_x -= (self._width_px / 2) - half_white_width

        # set up a place to store the keys
        self.keys_piano_order = arcade.SpriteList()
        self.black_keys = arcade.SpriteList()
        self.white_keys = arcade.SpriteList()
        self.keys_draw_order = arcade.SpriteList()

        # build and place the keyboard elements
        current_white_key_index = 0
        for n, is_black in key_metadata.items():

            # calculate how fast we need to play the sample
            current_frequency = key_frequency(n)
            speed = current_frequency / self._sample_pitch_hz
          
            # set the new key's initial centerpoint, bottom row default
            current_key_x = white_key_start_x
            current_key_x += white_key_step * current_white_key_index
            current_key_y = self._center_y

            if is_black:
                target_list = self.black_keys
                key_width, key_height, up_color, down_color = (
                    self._black_key_width_px,
                    self._black_key_height_px,
                    (45, 45, 45),
                    (0, 0, 0)
                )

                # shift the key to the correct position if it's black
                current_key_x += black_key_offset_x_px
                current_key_y += black_key_offset_y_px

            else:
                target_list = self.white_keys

                key_width, key_height, up_color, down_color = (
                    self._white_key_width_px,
                    self._white_key_height_px,
                    (205, 205, 205),
                    (255, 255, 255)
                )

                current_white_key_index += 1

            key = SynthKey(
                key_width,
                key_height,
                self._sample,
                speed,
                up_color,
                down_color
            )
            key.position = current_key_x, current_key_y

            target_list.append(key)
            self.keys_piano_order.append(key)

        # place white keys below black keys in draw order 
        self.keys_draw_order.extend(self.white_keys)
        self.keys_draw_order.extend(self.black_keys)

    def draw(self):
        self.keys_draw_order.draw()

    @property
    def position(self) -> Tuple:
        return self._center_x, self._center_y

class PianoExample(arcade.Window):

    def __init__(
        self,
        width_fraction: float = 0.9,
    ):
        super().__init__(800, 600, "Playback Speed Example: Piano")
        arcade.set_background_color((128,128,128))

        self.keyboard = SynthKeyboard(
            self.width * width_fraction, self.height * 0.5,
            self.width / 2, self.height / 2
        )

    def on_draw(self):
        self.clear()
        self.keyboard.draw()

    def on_key_press(self, key, modifiers):
        pass

    def on_key_release(self, key, modifiers):
        pass
            
if __name__ == "__main__":
    p = PianoExample()
    arcade.run()

