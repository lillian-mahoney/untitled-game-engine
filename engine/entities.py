# engine/entities.py
# Lillian Mahoney <lillian.lynn.mahoney@gmail.com>
#
# This module is part of Untitled Game Engine and is released under the
# Attribution Assurance License: http://opensource.org/licenses/AAL

"""Entities: interactive/dynamic map objects.

Interactive/stateful map stuff.

"""

import os
import glob
import render
import pyganim
import pygame
from collections import OrderedDict

__author__ = "Lillian Mahoney"
__copyright__ = "Copyright 2014, Lillian Mahoney"
__credits__ = ["Lillian Mahoney"]
__license__ = "Attribution Assurance License"
__maintainer__ = "Lillian Mahoney"
__email__ = "lillian.lynn.mahoney@gmail.com"
__status__ = "Development"


class Player(object):
    """Scaffolding."""

    def __init__(self, walkabout=None):
        """NPC or human player; depends on which controller
        is assigned.

        Args:
          walkabout (Walkabout): walkabout settings/sprites

        """

        self.walkabout = Walkabout(walkabout or 'debug')


class Walkabout(object):

    def __init__(self, walkabout_directory, start_position=None):
        """Interactive entity which uses a walkabout sprite.

        An entity capable of walking about the map. Sprites for
        "walking about" are defined as action__direction.gif therein
        the specified walkabout_directory.

        ASSUMPTION: walkabout_directory contains sprites for
        walk, run actions.

        Args:
          walkabout_directory (str): directory containing (animated)
            walkabout GIFs. Assumed parent is data/walkabouts/
          start_position (tuple): (x, y) coordinates (integers)
            referring to absolute pixel coordinate.

        Unfinished:
          * Anchors: head, hands, feet, torso

        """

        walkabout_directory = os.path.join('data', 'walkabouts',
                                           walkabout_directory)
        sprite_name_pattern = os.path.join(walkabout_directory, '*.gif')
        self.sprites = {}
        self.size = None

        for sprite_path in glob.iglob(sprite_name_pattern):
            file_name, file_ext = os.path.splitext(sprite_path)
            file_name = os.path.split(file_name)[1]
            action, direction = file_name.split('_', 1)
            animation = render.gif_to_pyganim(sprite_path)
            animation.convert()
            self.size = animation.getMaxSize()

            try:
                self.sprites[action][direction] = animation
            except KeyError:
                self.sprites[action] = {direction: animation}

        self.action = 'stand'
        self.direction = 'up'
        self.speed = 1

        position = start_position or (0, 0)  # px values
        self.rect = pygame.Rect(position, self.size)

    def move(self, direction, tilemap):
        """Modify positional data to reflect a legitimate player
        movement operation.

        Will round down to nearest probable step if full step is impassable.

        Args:
          direction (str): may be one of: up, right, down, left
          tilemap (tiles.TileMap): tilemap for reference, so we can
            avoid walking into water and such.

        """

        self.direction = direction
        planned_movement_in_pixels = self.speed

        for pixels in xrange(planned_movement_in_pixels, 0, -1):
            new_topleft_x, new_topleft_y = self.rect.topleft

            if direction == 'up':
                new_topleft_y -= pixels
            elif direction == 'right':
                new_topleft_x += pixels
            elif direction == 'down':
                new_topleft_y += pixels
            elif direction == 'left':
                new_topleft_x -= pixels

            new_bottomright_x = new_topleft_x + self.size[0]
            new_bottomright_y = new_topleft_y + self.size[1]

            movement_size_x = abs(new_bottomright_x - self.rect.topleft[0])
            movement_size_y = abs(new_bottomright_y - self.rect.topleft[1])
            movement_area_size = (movement_size_x, movement_size_y)

            if direction == 'up':
                new_topleft = (new_topleft_x, new_topleft_y)
            elif direction == 'right':
                new_topleft = self.rect.topleft
            elif direction == 'down':
                new_topleft = self.rect.topleft
            elif direction == 'left':
                new_topleft = (new_topleft_x, new_topleft_y)

            movement_rectangle = pygame.Rect(new_topleft,
                                             movement_area_size)
            movement_rectangle_collides = False

            for impassable_area in tilemap.impassability:

                if impassable_area and (impassable_area
                                        .colliderect(movement_rectangle)):
                    movement_rectangle_collides = True
                    break

            if movement_rectangle_collides:
                # done; can't move!

                return False

            else:
                # we're done, we can move!
                new_topleft = (new_topleft_x, new_topleft_y)
                new_sprite_rect = pygame.Rect(new_topleft, self.size)

                self.rect = new_sprite_rect
                self.action = 'walk'


                return True

    def blit(self, screen, offset):
        """Draw the appropriate/active animation to screen.

        Args:
          screen (pygame.Surface): the primary display/screen.
          offset (x, y tuple): the x, y coords of the absolute
            starting top left corner for the current screen/viewport
            position.

        Returns:
          None

        """

        x, y = self.rect.topleft
        x -= offset[0]
        y -= offset[1]
        position_on_screen = (x, y)
        self.sprites[self.action][self.direction].blit(
                                                       screen,
                                                       position_on_screen
                                                      )

        return None


def walkabout_generator():
    """Create the walkabout sprites for a character
    based off of some info.

    Gender, obvs.

    Why not make this a meta class?

    """

    pass

