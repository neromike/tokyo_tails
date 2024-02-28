import Map
from Entity import Entity
import math
import pygame

# ACTOR class
class Actor(Entity):
    def __init__(self, position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size=None):
        super().__init__(position, collision_rect_offset, collision_rect_size, file_name, sprite_size=sprite_size,
                         holdable=False)
        self.speed = speed
        self.current_direction = 'down'
        self.pose_index = 0
        self.is_moving = False
        self.bubble_surface = None
        self.bubble_text = None
        self.bubble_image = None
        self.bubble_visible = False
        self.bubble_display_time = 2000  # in milliseconds
        self.bubble_start_time = None
        self.held_entity = None

    def move(self, angle, distance):
        # Set the actor to moving
        self.is_moving = True

        # Select the correct direction for the sprite
        if angle >= 325 or angle <= 45:
            self.current_direction = 'right'
        elif 45 < angle <= 135:
            self.current_direction = 'up'
        elif 135 < angle < 225:
            self.current_direction = 'left'
        else:
            self.current_direction = 'down'

        # Convert angle from degrees to radians
        radians = math.radians(angle)

        # Calculate x and y components
        dx = distance * math.cos(radians)
        dy = -distance * math.sin(radians)  # Invert y-axis for Pygame

        colliders = Map.loc_to_colliders[self.loc]

        # Check for X-axis collision
        x_collision = self.check_collision_with_obstacles(colliders,self.real_rect(self.position[0] + dx, self.position[1]))
        if not x_collision[0]:
            self.position[0] = self.position[0] + dx
            self.update_collide_rect()

        # Check for Y-axis collision
        y_collision = self.check_collision_with_obstacles(colliders,self.real_rect(self.position[0], self.position[1] + dy))
        if not y_collision[0]:
            self.position[1] = self.position[1] + dy
            self.update_collide_rect()

        # Actor doesn't move if collision on both x and y
        if x_collision[0] and y_collision[0]:
            self.is_moving = False
        elif x_collision[0] or y_collision[0]:
            # but nudge the actor is they hit x OR y and are near a corner
            if x_collision[0]:
                self.nudge_towards_corner(x_collision[1], 'y')
            elif y_collision[0]:
                self.nudge_towards_corner(y_collision[1], 'x')

        # Exit the room
        if x_collision[0] == 'exit' or y_collision[0] == 'exit':
            pass
            """
            global background_layer
            global room_obstacles, room_exits
            global BACKGROUND_WIDTH, BACKGROUND_HEIGHT
            background_layer = background_layer_farm
            room_obstacles = []
            room_exits = []
            BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 2500, 2500
            """

    def check_collision_with_obstacles(self, colliders, new_rect):
        # Check for collision with each obstacle
        for item in colliders[0]:
            if item is not self and item.collide_rect is not None:
                if new_rect.colliderect(item.collide_rect):
                    return 'item', item
        for item in colliders[1]:
            if new_rect.colliderect(item.collide_rect):
                return 'room', item
        for item in colliders[2]:
            if new_rect.colliderect(item.collide_rect):
                return 'exit', item
        return False, None

    def nudge_towards_corner(self, item, axis):
        # Nudges the actor towards the nearest corner of the item.
        corners = [
            (item.collide_rect.left, item.collide_rect.top),  # Top-left
            (item.collide_rect.right, item.collide_rect.top),  # Top-right
            (item.collide_rect.left, item.collide_rect.bottom),  # Bottom-left
            (item.collide_rect.right, item.collide_rect.bottom)  # Bottom-right
        ]
        nearest_corner = min(corners, key=lambda corner: self.distance_to_corner(corner))
        nudge_amount = 3  # Adjust this value as needed
        if axis == 'x':
            if corners.index(nearest_corner) % 2 == 0:
                self.position[0] -= nudge_amount
            else:
                self.position[0] += nudge_amount
        elif axis == 'y':
            if corners.index(nearest_corner) < 2:
                self.position[1] -= nudge_amount
            else:
                self.position[1] += nudge_amount

        self.update_collide_rect()

    def distance_to_corner(self, corner):
        # Calculates the distance from the actor's center to a corner.
        actor_center = self.collision_center()
        return ((actor_center[0] - corner[0]) ** 2 + (actor_center[1] - corner[1]) ** 2) ** 0.5

    def real_rect(self, x, y):
        # Return the actual rect size for the sprite
        return pygame.Rect(
            x + self.collision_rect_offset[0],
            y + self.collision_rect_offset[1],
            self.collision_rect_size[0],
            self.collision_rect_size[1]
        )

    def show_bubble(self, text=None, image=None):
        # Shows a speech bubble above the actor with either text or an image.
        self.bubble_text = text
        self.bubble_image = image
        self.bubble_visible = True

        # Create the bubble surface
        bubble_width, bubble_height = 80, 30  # adjust size as needed
        self.bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)

        # Set bubble surface alpha for semi-transparency
        bubble_alpha = 128  # Set this to desired transparency (0-255)
        self.bubble_surface.set_alpha(bubble_alpha)

        # Draw a rounded rectangle for the bubble
        rect = pygame.Rect(0, 0, bubble_width, bubble_height)
        roundness = 15  # adjust for desired curvature
        pygame.draw.rect(self.bubble_surface, (255, 255, 255), rect, border_radius=roundness)

        # Optionally, add a tail to the bubble
        tail_height = 10
        tail_width = 20
        tail_points = [(bubble_width // 2, bubble_height),
                       (bubble_width // 2 - tail_width // 2, bubble_height - tail_height),
                       (bubble_width // 2 + tail_width // 2, bubble_height - tail_height)]
        pygame.draw.polygon(self.bubble_surface, (255, 255, 255), tail_points)

        # Draw text or image onto the bubble surface
        if self.bubble_text:
            font = pygame.font.Font(None, 20)  # adjust font size as needed
            text_surface = font.render(self.bubble_text, True, (0, 0, 0))  # black text
            # Center the text inside the bubble
            text_rect = text_surface.get_rect(center=(bubble_width // 2, bubble_height // 2))
            self.bubble_surface.blit(text_surface, text_rect)
        elif self.bubble_image:
            # Scale or transform the image if necessary
            image_rect = self.bubble_image.get_rect(center=(bubble_width // 2, bubble_height // 2))
            self.bubble_surface.blit(self.bubble_image, image_rect)

        # Record the time when the bubble is shown
        self.bubble_start_time = pygame.time.get_ticks()

    def update_bubble(self):
        # Updates the speech bubble. Hides it if the display time has passed.
        if self.bubble_visible and self.bubble_start_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.bubble_start_time > self.bubble_display_time:
                self.hide_bubble()

    def hide_bubble(self):
        # Hides the speech bubble.
        self.bubble_visible = False

    def hold_entity(self, entity):
        if entity.holdable:
            self.held_entity = entity
            entity.held = True
            # print(entity.file_name.replace('.png',''))

    def update_held_position(self, object):
        object.position[0] = self.position[0] + (self.sprite_size // 2) - (object.sprite.get_width() // 2)
        object.position[1] = self.position[1] - object.collision_rect_size[1] - object.held_y_offset
        object.collide_rect = None

    def drop_entity(self, object):
        object.position[0] = self.position[0] + self.collision_rect_offset[0] - object.collision_rect_size[0] - 5
        object.position[1] = self.position[1] + self.collision_rect_offset[1] + self.collision_rect_size[1] - \
                             object.collision_rect_size[1] - object.collision_rect_offset[1]
        object.update_collide_rect()
        object.held = False
        self.held_entity = None