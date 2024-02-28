import os

import pygame

from Constants import *


# ENTITY class
class Entity:
    entities = []

    def __init__(self, position, collision_rect_offset=(), collision_rect_size=(), file_name='', sprite_size=None, holdable=False, held_y_offset=0, icon_file_name='', draggable=False):
        self.position = position
        self.collision_rect_offset = collision_rect_offset
        self.collision_rect_size = collision_rect_size
        self.file_name = file_name
        self.sprite_sheet = {}
        self.sprite_size = sprite_size
        self.sprite = None
        self.collide_rect = None
        self.update_collide_rect()
        if not self.file_name == '':
            self.sprite = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, self.file_name)).convert_alpha()
            self.sprite_size = self.sprite.get_width()
        self.holdable = holdable
        self.held = False
        self.held_y_offset = held_y_offset
        self.icon = None
        self.icon_file_name = icon_file_name
        self.draggable = draggable
        self.being_dragged = False
        if not self.icon_file_name == '':
            self.icon = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, self.icon_file_name)).convert_alpha()
        self.entities.append(self)
        self.energy = 100
        self.loc = "house"

    def update_collide_rect(self):
        self.collide_rect = pygame.Rect(self.position[0] + self.collision_rect_offset[0], self.position[1] + self.collision_rect_offset[1], self.collision_rect_size[0], self.collision_rect_size[1])
    def check_collision(self, object2, proximity=20, update_first=True):
        # first update the collide_rects
        if update_first:
            self.update_collide_rect()
            object2.update_collide_rect()
        # checks if this entity's collide_rect intersects with the second object's collide_rect
        return self.collide_rect.colliderect(object2.collide_rect.inflate(proximity, proximity))
    def get_z_order(self):
        # Assuming y-coordinate determines depth
        return self.position[1] + self.collision_rect_offset[1] + (self.collision_rect_size[1] / 2)
    def collision_center(self):
        return [self.position[0] + self.collision_rect_offset[0] + (self.collision_rect_size[0] / 2), self.position[1] + self.collision_rect_offset[1] + (self.collision_rect_size[1] / 2)]
    def get_sprite(self, sprite_sheet, x, y):
        # Extracts and returns a single sprite from the sprite sheet.
        image = pygame.Surface((self.sprite_size, self.sprite_size))
        image.blit(sprite_sheet, (0, 0), (x * self.sprite_size, y * self.sprite_size, self.sprite_size, self.sprite_size))
        image.set_colorkey(image.get_at((0,0)))  # Assumes top-left pixel is the transparent color
        return image
    def blit(self, camera_offset, screen, override = False):
        if not self.held or override:
            screen.blit(self.sprite, (self.position[0]-camera_offset[0], self.position[1]-camera_offset[1]))
    def interact(self):
        if self.holdable:
            return True

    def pick_up(self):
        self.held = True