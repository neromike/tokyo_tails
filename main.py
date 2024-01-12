import pygame
import os
import sys
import math
import random
import time

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()



# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
MILLISECONDS_PER_DAY = 720000  # 12 minutes in milliseconds
MILLISECONDS_PER_HOUR = MILLISECONDS_PER_DAY / 24
START_HOUR = 8  # Start time (hour)
START_MINUTE = 0  # Start time (minute)
INITIAL_TIME_OFFSET = (START_HOUR * 60 + START_MINUTE) * (MILLISECONDS_PER_HOUR / 60)
START_TIME = pygame.time.get_ticks() + INITIAL_TIME_OFFSET
FONT_SIZE = 20
IMAGE_ASSET_PATH = 'asset_image'
SOUND_ASSET_PATH = 'asset_sound'



# Set up the screen
pygame.display.set_caption("Tokyo Tails")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, FONT_SIZE)



# Load and play background music
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(SOUND_ASSET_PATH, '1243769_Loneliness-Corrupts-Me-Lof.mp3'))
pygame.mixer.music.set_volume(1.0)  # Set the volume to full
pygame.mixer.music.play()  # The -1 makes the music loop indefinitely



# GRID
GRID_CELL_SIZE = 50  # Size of each grid cell in pixels
grid_width = grid_height = 0
def initialize_grid():
    global grid_width, grid_height
    # Get the dimensions of the background image
    background_width, background_height = background_layer.get_size()

    # Calculate the number of grid cells in each dimension
    grid_width = background_width // GRID_CELL_SIZE
    grid_height = background_height // GRID_CELL_SIZE

    # Create a 2D array with all cells set to passable (False)
    return [[False for _ in range(grid_width)] for _ in range(grid_height)]
def mark_obstacles_on_grid():
    # Reset the grid
    grid = initialize_grid()

    # Now mark the impassable cells
    for obstacle in room_obstacles + items:

        if obstacle is not None and obstacle.collide_rect is not None:
            top_left_cell = (obstacle.collide_rect.left // GRID_CELL_SIZE, obstacle.collide_rect.top // GRID_CELL_SIZE)
            bottom_right_cell = (obstacle.collide_rect.right // GRID_CELL_SIZE, obstacle.collide_rect.bottom // GRID_CELL_SIZE)

            for x in range(top_left_cell[0], bottom_right_cell[0] + 1):
                for y in range(top_left_cell[1], bottom_right_cell[1] + 1):
                    if 0 <= x < grid_width and 0 <= y < grid_height:
                        grid[y][x] = True  # Mark cell as impassable
    return grid
def draw_grid(passable_color=(0, 255, 0), impassable_color=(255, 0, 0)):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            color = impassable_color if cell else passable_color
            rect = pygame.Rect((x * GRID_CELL_SIZE + 1) - camera_offset[0], 
                               (y * GRID_CELL_SIZE + 1) - camera_offset[1], 
                               GRID_CELL_SIZE - 2, 
                               GRID_CELL_SIZE - 2)
            pygame.draw.rect(screen, color, rect, 1)  # Change '1' to '0' if you want filled rectangles
def grid_to_pixel(cell_x, cell_y):
    # Converts grid cell coordinates to pixel coordinates.
    return cell_x * GRID_CELL_SIZE, cell_y * GRID_CELL_SIZE
def pixel_to_grid(position):
    # Converts pixel coordinates to grid cell coordinates.
    return int(position[0] // GRID_CELL_SIZE), int(position[1] // GRID_CELL_SIZE)
def print_grid(start=None, end=None, marked_positions=None):
    # Print column labels
    print(' ', end=' ')
    for x in range(len(grid[0])):
        print(f'{x:2d}', end=' ')
    print()

    for y, row in enumerate(grid):
        # Print row label
        print(f'{y:2d}', end=' ')

        row_string = ''
        for x, cell in enumerate(row):
            if start and (x, y) == start:
                row_string += 'S  '  # Start
            elif end and (x, y) == end:
                row_string += 'E  '  # End
            elif marked_positions and (x, y) in [node.position for node in marked_positions]:
                row_string += 'o  ' # Marked
            else:
                row_string += 'X  ' if cell else '.  '  # Obstacle or Empty
        print(row_string)
def initialize_connectivity_grid():
    connectivity_grid = [[[] for _ in range(grid_width)] for _ in range(grid_height)]
    return connectivity_grid
def populate_connectivity_grid():
    # Redo the original grid first
    mark_obstacles_on_grid()
    # Reset the connectivity grid
    connectivity_grid = initialize_connectivity_grid()
    for y in range(grid_height):
        for x in range(grid_width):
            if not grid[y][x]:  # If the current cell is passable
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Adjacent cells
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid_width and 0 <= ny < grid_height and not grid[ny][nx]:
                        connectivity_grid[y][x].append((nx, ny))
    return connectivity_grid
def is_path_possible(start, end, update_first=True):
    if update_first:
        connectivity_grid = populate_connectivity_grid()
    # If either the start or end cells have no connections, a path is not possible
    return bool(connectivity_grid[start[1]][start[0]]) and bool(connectivity_grid[end[1]][end[0]])



class Node():
    # A node class for A* Pathfinding
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0
    def __eq__(self, other):
        return self.position == other.position
astar_times = []
def astar(start, end):
    global astar_times
    timer_start = time.time()
    # Returns a list of tuples as a path from the given start to the given end in the given maze

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current index off of the open list, and add it to the closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            timer_end = time.time()
            astar_times.append(timer_end - timer_start)
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares
            
            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[1] > (len(grid)-1) or node_position[1] < 0 or node_position[0] > (len(grid[len(grid)-1])-1) or node_position[0] < 0:
                continue

            # Make sure walkable terrain, ignore any obstacles at our current position and the end position
            if grid[node_position[1]][node_position[0]] and node_position != end and node_position != current_node.position:
                continue
            
            # Make sure we don't cut corners
            if new_position == (-1, -1) or new_position == (-1, 1) or new_position == (1, -1) or new_position == (1, 1):
                if grid[current_node.position[1] + new_position[1]][current_node.position[0]] or grid[current_node.position[1]][current_node.position[0] + new_position[0]]:
                    continue

            # Create new node
            new_node = Node(current_node, node_position)
            
            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            if child in closed_list:
                continue
            
            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            if child in open_list:
                index = open_list.index(child)
                if child.h > open_list[index].g:
                    continue
            
            # Add the child to the open list
            open_list.append(child)
    


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
    def get_sprite(self, x, y):
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
            if add_to_inventory(self):
                self.held = True



# ACTOR class
class Actor(Entity):
    def __init__(self, position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size=None):
        super().__init__(position, collision_rect_offset, collision_rect_size, file_name, sprite_size=sprite_size, holdable=False)
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
        elif angle > 45 and angle <= 135:
            self.current_direction = 'up'
        elif angle > 135 and angle < 225:
            self.current_direction = 'left'
        else:
            self.current_direction = 'down'

        # Convert angle from degrees to radians
        radians = math.radians(angle)

        # Calculate x and y components
        dx = distance * math.cos(radians)
        dy = -distance * math.sin(radians)  # Invert y-axis for Pygame

        # Check for X-axis collision
        x_collision = self.check_collision_with_obstacles(self.real_rect(self.position[0] + dx, self.position[1]))
        if not x_collision[0]:
            self.position[0] = self.position[0] + dx
            self.update_collide_rect()

        # Check for Y-axis collision
        y_collision = self.check_collision_with_obstacles(self.real_rect(self.position[0], self.position[1] + dy))
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

    def check_collision_with_obstacles(self, new_rect):
        # Check for collision with each obstacle
        for item in items:
            if item is not self and item.collide_rect is not None:
                if new_rect.colliderect(item.collide_rect):
                    return 'item', item
        for item in room_obstacles:
            if new_rect.colliderect(item.collide_rect):
                return 'room', item
        for item in room_exits:
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
            if nearest_corner[0] > self.position[0]:
                self.position[0] -= nudge_amount
            else:
                self.position[0] += nudge_amount
        elif axis == 'y':
            if nearest_corner[1] > self.position[1]:
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
        tail_points = [(bubble_width // 2, bubble_height), (bubble_width // 2 - tail_width // 2, bubble_height - tail_height), (bubble_width // 2 + tail_width // 2, bubble_height - tail_height)]
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
            #print(entity.file_name.replace('.png',''))

    def update_held_position(self, object):
        object.position[0] = self.position[0] + (self.sprite_size // 2) - (object.sprite.get_width() // 2)
        object.position[1] = self.position[1] - object.collision_rect_size[1] - object.held_y_offset
        object.collide_rect = None

    def drop_entity(self, object):
        object.position[0] = self.position[0] + self.collision_rect_offset[0] - object.collision_rect_size[0] - 5
        object.position[1] = self.position[1] + self.collision_rect_offset[1] + self.collision_rect_size[1] - object.collision_rect_size[1] - object.collision_rect_offset[1]
        object.update_collide_rect()
        object.held = False
        self.held_entity = None



# NPC class
class NPC(Actor):
    def __init__(self, position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size=None):
        super().__init__(position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size)
        self.happiness = random.randint(30,90)
        self.fullness = random.randint(50,90)
        self.thirsty = random.randint(10,30)
        self.digest_speed = random.randint(20,80) / (1 * 1000)  # 80% per 5 minutes = 80 /(5 * 60 * 1000)
        self.poop = random.randint(10,30)
        self.poop_generation_rate = random.random()
        self.pee = random.randint(10,30)
        self.pee_generation_rate = random.random()
        self.thirsty_gain_speed = random.randint(20,80) / (1 * 1000)
        self.energy_drain_speed = random.randint(20,80) / (1 * 1000)
        self.happiness_drain_speed = random.randint(20,80) / (1 * 1000)
        self.direction = 0
        self.task = ''
        self.path = None
        self.destination = ()
        self.currently_exploring = False
        self.time_since_last_activity_change = 0
        self.new_activity_every_x_seconds = random.randint(10,20)
    def update(self):
        # DEBUG
        #print(f'doing self.task:{self.task}')
        if self.task != '':
            #self.show_bubble(text=self.task)
            pass
        #self.task = 'explore'
        
        # Update the activity change timer
        self.time_since_last_activity_change += 1

        # Digest food
        self.fullness -= self.digest_speed

        # Find food if hungry
        if self.fullness <= 20 and self.task in ['', 'explore']:
            self.task = 'find-food'
            #self.show_bubble(image=bubble['hunger'])

        # Lower the cat energy
        self.energy -= self.energy_drain_speed

        # Find bed if low on energy
        if self.energy <= 20 and self.task in ['', 'explore']:
            self.task = 'find-sleep'
            #self.show_bubble(image=bubble['tired']

        # Lower happiness
        self.happiness -= self.happiness_drain_speed

        # Find toy if not happy
        if self.happiness <= 20 and self.task in ['', 'explore']:
            self.task = 'find-toy'
            #self.show_bubble(image=bubble['sad'])

        # Get thirsty
        self.thirsty += self.thirsty_gain_speed

        # Find water bowl if thirsty
        if self.thirsty >= 80 and self.task in ['', 'explore']:
            self.task = 'find-water'
            #self.show_bubble(image=bubble['thirsty'])

        # Find litter box if need to pee or poop
        if (self.poop >= 80 or self.pee >= 80) and self.task in ['', 'explore']:
            self.task = 'find-litter-box'
            #self.show_bubble(image=bubble['bathroom'])
        
        # --- EAT ---
        if self.task == 'eat':
            self.is_moving = False
            # Check if there is a food bowl nearby
            if self.check_collision(item_cat_food_bowl, proximity=40):
                # Can only eat if the bowl has food
                if item_cat_food_bowl.energy > 0:

                    # Eat the food
                    self.fullness += 1

                    # Make poop
                    self.poop += self.poop_generation_rate

                    # Stop eating when full
                    if self.fullness >= 100:
                        self.task = ''

                    # The bowl gets less full
                    #item_cat_food_bowl.energy -= 1
                    if item_cat_food_bowl.energy > 70:
                        item_cat_food_bowl.sprite = item_cat_food_bowl.sprite_sheet['full']
                    elif item_cat_food_bowl.energy > 30:
                        item_cat_food_bowl.sprite = item_cat_food_bowl.sprite_sheet['mid']
                    else:
                        item_cat_food_bowl.sprite = item_cat_food_bowl.sprite_sheet['empty']
            else:
                self.task = ''
        
        # --- DRINK ---
        if self.task == 'drink':
            self.is_moving = False
            # Check if there is a water bowl nearby
            if self.check_collision(item_cat_water_bowl, proximity=40):
                # Drink
                self.thirsty -= 1

                # Make pee
                self.pee += self.pee_generation_rate
                
                # Stop drinking when not thirsty
                if self.thirsty <= 0:
                    self.task = ''
            else:
                self.task = ''

        # --- BATHROOM ---
        if self.task == 'bathroom':
            self.is_moving = False
            # Check if there is a litter box nearby
            if self.check_collision(item_cat_litter_box, proximity=40):
                #Pee
                self.pee -= 1
                if self.pee < 0:
                    self.pee = 0

                #Poop
                self.poop -= 1
                if self.poop < 0:
                    self.poop = 0
                
                #Stop using the litter box when done
                if self.pee <= 0 and self.poop <= 0:
                    self.task = ''
            else:
                self.task = ''

        # --- PLAY ---
        if self.task == 'play':
            self.is_moving = False
            # Check if there is a toy nearby
            if self.check_collision(item_cat_scratcher, proximity=40):
                #Play
                self.happiness += 1
                
                #Stop playing when happy
                if self.happiness >= 100:
                    self.task = ''
            else:
                self.task = ''
        
        # --- SLEEP ---
        if self.task == 'sleep':
            self.is_moving = False
            # Check if there is a bed nearby
            if self.check_collision(item_cat_bed, proximity=40):
                #Sleep
                self.energy += 0.5
                
                #Stop sleeping when full of energy
                if self.energy >= 100:
                    self.task = ''
            else:
                self.task = ''

        # --- FIND-LITTER-BOX ---
        if self.task == 'find-litter-box':
            new_task = 'bathroom'
            if self.check_collision(item_cat_litter_box, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = pixel_to_grid(self.collision_center())
                
                # Get the end position
                litter_box_position = pixel_to_grid(item_cat_litter_box.collision_center())

                # Find a path to the cat litter box
                self.path = astar(cat_position, litter_box_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)
        
        # --- FIND-TOY ---
        if self.task == 'find-toy':
            new_task = 'play'
            if self.check_collision(item_cat_scratcher, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = pixel_to_grid(self.collision_center())
                
                # Get the end position
                toy_position = pixel_to_grid(item_cat_scratcher.collision_center())

                # Find a path to the cat toy
                self.path = astar(cat_position, toy_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-SLEEP ---
        if self.task == 'find-sleep':
            new_task = 'sleep'
            if self.check_collision(item_cat_bed, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = pixel_to_grid(self.collision_center())
                
                # Get the end position
                bed_position = pixel_to_grid(item_cat_bed.collision_center())

                # Find a path to the cat toy
                self.path = astar(cat_position, bed_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-FOOD ---
        if self.task == 'find-food':
            new_task = 'eat'
            if self.check_collision(item_cat_food_bowl, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = pixel_to_grid(self.collision_center())
                
                # Get the end position
                if item_cat_food_bowl.held:
                    food_position = pixel_to_grid(player.collision_center())
                else:
                    food_position = pixel_to_grid(item_cat_food_bowl.collision_center())

                # Find a path to the cat food bowl
                self.path = astar(cat_position, food_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-WATER ---
        if self.task == 'find-water':
            new_task = 'drink'
            if self.check_collision(item_cat_water_bowl, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = pixel_to_grid(self.collision_center())
                
                # Get the end position
                if item_cat_water_bowl.held:
                    water_position = pixel_to_grid(player.collision_center())
                else:
                    water_position = pixel_to_grid(item_cat_water_bowl.collision_center())

                # Find a path to the cat food bowl
                self.path = astar(cat_position, water_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- EXPLORE ---
        if self.task == 'explore':
            # Get start and end positions
            cat_position = pixel_to_grid(self.collision_center())
            
            # Find a new path if not currently exploring
            if not self.currently_exploring:
                self.path = None
                while self.path is None:

                    # Get the end position
                    end_position = random.randint(0, grid_width-1), random.randint(0, grid_height-1)

                    # Find a path to the end_position if it's possible to this end position
                    if is_path_possible(cat_position, end_position):
                        self.path = astar(cat_position, end_position)
                
                # The NPC is now exploring
                self.currently_exploring = True
                self.destination = end_position
            else:
                # Update the path to the end_position
                self.path = astar(cat_position, self.destination)

            # Move towards the next step
            if not self.move_along_path(cat_position, new_task=''):
                self.currently_exploring = False
        
        # explore if nothing else is a priority
        if self.task == '' and (self.time_since_last_activity_change * clock.get_fps()) >= self.new_activity_every_x_seconds:
            self.time_since_last_activity_change = 0
            self.task = 'explore'
        
    
    def move_along_path(self, curr_pos, new_task=''):
        if self.path is not None:
            if len(self.path) > 1:
                next_step = self.path[1]

                # DEBUG
                #print(f'curr_pos:{curr_pos} next_step:{next_step} self.path:{self.path}')

                # Move the NPC if it's not next to the correct position
                if next_step[0] < curr_pos[0]:
                    if next_step[1] < curr_pos[1]:
                        self.move(135, self.speed)
                    elif next_step[1] == curr_pos[1]:
                        self.move(180, self.speed)
                    else:
                        self.move(225, self.speed)
                elif next_step[0] == curr_pos[0]:
                    if next_step[1] < curr_pos[1]:
                        self.move(90, self.speed)
                    elif next_step[1] > curr_pos[1]:
                        self.move(270, self.speed)
                else:
                    if next_step[1] < curr_pos[1]:
                        self.move(45, self.speed)
                    elif next_step[1] == curr_pos[1]:
                        self.move(0, self.speed)
                    else:
                        self.move(315, self.speed)
            else:
                next_step = curr_pos
                self.task = new_task
                self.path = None
                self.is_moving = False
                return False
        return True

    def interact(self):
        player.show_bubble(image=bubble['heart'])


# PLAYER class
class Player(Actor):
    def __init__(self, position, speed, collision_rect_offset=(), collision_rect_size=(), file_name='', sprite_size=None):
        super().__init__(position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size)
        self.hp = 100


# Player setup
player = Player(position=[SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], speed=5, collision_rect_offset=(50,100), collision_rect_size=(40,20), file_name='', sprite_size=128)
sprite_sheet = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'sprite_player2_128.png'))
player.sprite_sheet = {
    'idle_down': player.get_sprite(0, 0),
    'idle_up': player.get_sprite(0, 1),
    'idle_right': player.get_sprite(0, 2),
    'idle_left': player.get_sprite(0, 3),
    'down': [player.get_sprite(1, 0), player.get_sprite(2, 0), player.get_sprite(3, 0), player.get_sprite(4, 0), player.get_sprite(5, 0), player.get_sprite(6, 0)],
    'up': [player.get_sprite(1, 1), player.get_sprite(2, 1), player.get_sprite(3, 1), player.get_sprite(4, 1), player.get_sprite(5, 1), player.get_sprite(6, 1)],
    'right': [player.get_sprite(1, 2), player.get_sprite(2, 2), player.get_sprite(3, 2), player.get_sprite(4, 2), player.get_sprite(5, 2), player.get_sprite(6, 2)],
    'left': [player.get_sprite(1, 3), player.get_sprite(2, 3), player.get_sprite(3, 3), player.get_sprite(4, 3), player.get_sprite(5, 3), player.get_sprite(6, 3)],
}

# cat setup
cat = NPC(position=[550, 470], speed=7, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
sprite_sheet = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'sprite_cat2_64.png'))
cat.sprite_sheet = {
    'down': [cat.get_sprite(0, 0), cat.get_sprite(1, 0), cat.get_sprite(2, 0)],
    'left': [cat.get_sprite(0, 1), cat.get_sprite(1, 1), cat.get_sprite(2, 1)],
    'right': [cat.get_sprite(0, 2), cat.get_sprite(1, 2), cat.get_sprite(2, 2)],
    'up': [cat.get_sprite(0, 3), cat.get_sprite(1, 3), cat.get_sprite(2, 3)],
    'idle_down': cat.get_sprite(0, 0),
    'idle_left': cat.get_sprite(0, 1),
    'idle_right': cat.get_sprite(0, 2),
    'idle_up': cat.get_sprite(0, 3)
}

# cat2 setup
cat2 = NPC(position=[1550, 670], speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat2.sprite_sheet = {
    'down': [cat2.get_sprite(3, 0), cat2.get_sprite(4, 0), cat2.get_sprite(5, 0)],
    'left': [cat2.get_sprite(3, 1), cat2.get_sprite(4, 1), cat2.get_sprite(5, 1)],
    'right': [cat2.get_sprite(3, 2), cat2.get_sprite(4, 2), cat2.get_sprite(5, 2)],
    'up': [cat2.get_sprite(3, 3), cat2.get_sprite(4, 3), cat2.get_sprite(5, 3)],
    'idle_down': cat2.get_sprite(3, 0),
    'idle_left': cat2.get_sprite(3, 1),
    'idle_right': cat2.get_sprite(3, 2),
    'idle_up': cat2.get_sprite(3, 3)
}

# cat3 setup
cat3 = NPC(position=[1550, 730], speed=3, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat3.sprite_sheet = {
    'down': [cat3.get_sprite(6, 0), cat3.get_sprite(7, 0), cat3.get_sprite(8, 0)],
    'left': [cat3.get_sprite(6, 1), cat3.get_sprite(7, 1), cat3.get_sprite(8, 1)],
    'right': [cat3.get_sprite(6, 2), cat3.get_sprite(7, 2), cat3.get_sprite(8, 2)],
    'up': [cat3.get_sprite(6, 3), cat3.get_sprite(7, 3), cat3.get_sprite(8, 3)],
    'idle_down': cat3.get_sprite(6, 0),
    'idle_left': cat3.get_sprite(6, 1),
    'idle_right': cat3.get_sprite(6, 2),
    'idle_up': cat3.get_sprite(6, 3)
}

# cat4 setup
cat4 = NPC(position=[1550, 700], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat4.sprite_sheet = {
    'down': [cat4.get_sprite(9, 0), cat4.get_sprite(10, 0), cat4.get_sprite(11, 0)],
    'left': [cat4.get_sprite(9, 1), cat4.get_sprite(10, 1), cat4.get_sprite(11, 1)],
    'right': [cat4.get_sprite(9, 2), cat4.get_sprite(10, 2), cat4.get_sprite(11, 2)],
    'up': [cat4.get_sprite(9, 3), cat4.get_sprite(10, 3), cat4.get_sprite(11, 3)],
    'idle_down': cat4.get_sprite(9, 0),
    'idle_left': cat4.get_sprite(9, 1),
    'idle_right': cat4.get_sprite(9, 2),
    'idle_up': cat4.get_sprite(9, 3)
}

# cat5 setup
cat5 = NPC(position=[1200, 500], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
sprite_sheet = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'sprite_cat_fluffy.png'))
cat5.sprite_sheet = {
    'down': [cat5.get_sprite(0, 0), cat5.get_sprite(1, 0), cat5.get_sprite(2, 0)],
    'left': [cat5.get_sprite(0, 1), cat5.get_sprite(1, 1), cat5.get_sprite(2, 1)],
    'right': [cat5.get_sprite(0, 2), cat5.get_sprite(1, 2), cat5.get_sprite(2, 2)],
    'up': [cat5.get_sprite(0, 3), cat5.get_sprite(1, 3), cat5.get_sprite(2, 3)],
    'idle_down': cat5.get_sprite(0, 0),
    'idle_left': cat5.get_sprite(0, 1),
    'idle_right': cat5.get_sprite(0, 2),
    'idle_up': cat5.get_sprite(0, 3)
}

# cat6 setup
cat6 = NPC(position=[1200, 550], speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat6.sprite_sheet = {
    'down': [cat6.get_sprite(3, 0), cat6.get_sprite(4, 0), cat6.get_sprite(5, 0)],
    'left': [cat6.get_sprite(3, 1), cat6.get_sprite(4, 1), cat6.get_sprite(5, 1)],
    'right': [cat6.get_sprite(3, 2), cat6.get_sprite(4, 2), cat6.get_sprite(5, 2)],
    'up': [cat6.get_sprite(3, 3), cat6.get_sprite(4, 3), cat6.get_sprite(5, 3)],
    'idle_down': cat6.get_sprite(3, 0),
    'idle_left': cat6.get_sprite(3, 1),
    'idle_right': cat6.get_sprite(3, 2),
    'idle_up': cat6.get_sprite(3, 3)
}

# cat7 setup
cat7 = NPC(position=[1200, 500], speed=3, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat7.sprite_sheet = {
    'down': [cat7.get_sprite(6, 0), cat7.get_sprite(7, 0), cat7.get_sprite(8, 0)],
    'left': [cat7.get_sprite(6, 1), cat7.get_sprite(7, 1), cat7.get_sprite(8, 1)],
    'right': [cat7.get_sprite(6, 2), cat7.get_sprite(7, 2), cat7.get_sprite(8, 2)],
    'up': [cat7.get_sprite(6, 3), cat7.get_sprite(7, 3), cat7.get_sprite(8, 3)],
    'idle_down': cat7.get_sprite(6, 0),
    'idle_left': cat7.get_sprite(6, 1),
    'idle_right': cat7.get_sprite(6, 2),
    'idle_up': cat7.get_sprite(6, 3)
}

# cat8 setup
cat8 = NPC(position=[1200, 450], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat8.sprite_sheet = {
    'down': [cat8.get_sprite(9, 0), cat8.get_sprite(10, 0), cat8.get_sprite(11, 0)],
    'left': [cat8.get_sprite(9, 1), cat8.get_sprite(10, 1), cat8.get_sprite(11, 1)],
    'right': [cat8.get_sprite(9, 2), cat8.get_sprite(10, 2), cat8.get_sprite(11, 2)],
    'up': [cat8.get_sprite(9, 3), cat8.get_sprite(10, 3), cat8.get_sprite(11, 3)],
    'idle_down': cat8.get_sprite(9, 0),
    'idle_left': cat8.get_sprite(9, 1),
    'idle_right': cat8.get_sprite(9, 2),
    'idle_up': cat8.get_sprite(9, 3)
}

# cat9 setup
cat9 = NPC(position=[1200, 400], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat9.sprite_sheet = {
    'down': [cat9.get_sprite(9, 0), cat9.get_sprite(10, 0), cat9.get_sprite(11, 0)],
    'left': [cat9.get_sprite(9, 1), cat9.get_sprite(10, 1), cat9.get_sprite(11, 1)],
    'right': [cat9.get_sprite(9, 2), cat9.get_sprite(10, 2), cat9.get_sprite(11, 2)],
    'up': [cat9.get_sprite(9, 3), cat9.get_sprite(10, 3), cat9.get_sprite(11, 3)],
    'idle_down': cat9.get_sprite(9, 0),
    'idle_left': cat9.get_sprite(9, 1),
    'idle_right': cat9.get_sprite(9, 2),
    'idle_up': cat9.get_sprite(9, 3)
}

# cat10 setup
cat10 = NPC(position=[1200, 350], speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat10.sprite_sheet = {
    'down': [cat10.get_sprite(3, 0), cat10.get_sprite(4, 0), cat10.get_sprite(5, 0)],
    'left': [cat10.get_sprite(3, 1), cat10.get_sprite(4, 1), cat10.get_sprite(5, 1)],
    'right': [cat10.get_sprite(3, 2), cat10.get_sprite(4, 2), cat10.get_sprite(5, 2)],
    'up': [cat10.get_sprite(3, 3), cat10.get_sprite(4, 3), cat10.get_sprite(5, 3)],
    'idle_down': cat10.get_sprite(3, 0),
    'idle_left': cat10.get_sprite(3, 1),
    'idle_right': cat10.get_sprite(3, 2),
    'idle_up': cat10.get_sprite(3, 3)
}

npcs = []
npcs.append(cat)
npcs.append(cat2)
npcs.append(cat3)
npcs.append(cat4)
npcs.append(cat5)
npcs.append(cat6)
npcs.append(cat7)
npcs.append(cat8)
npcs.append(cat9)
npcs.append(cat10)



# Item setup
item_table = Entity([570,715], [7,50], [157,120], 'item_table.png')
item_shelf = Entity([65,760], [7,110], [157,40], 'item_shelf.png')
item_computer_desk = Entity([1300,250], [15,60], [120,55], 'item_computer_desk.png')
item_cat_food_bowl = Entity([1300,450], [8,8], [40,20], 'item_cat_food_bowl_full.png', holdable=True, held_y_offset=10, icon_file_name='icon_cat_food_bowl.png')
item_cat_food_bowl.sprite_sheet = {
    'full': pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'item_cat_food_bowl_full.png')),
    'mid': pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'item_cat_food_bowl_mid.png')),
    'empty': pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'item_cat_food_bowl_empty.png')),
}
item_cat_water_bowl = Entity([1300,650], [8,8], [40,20], 'item_cat_water_bowl.png', holdable=True, held_y_offset=10, icon_file_name='icon_cat_water_bowl.png')
item_cat_food_bag = Entity([1200,700], [5,50], [44,14], 'item_cat_food_bag.png', holdable=True, held_y_offset=40, icon_file_name='icon_cat_food_bag.png')
item_cat_litter_box = Entity([1000,700], [13,37], [67,54], 'item_cat_litter_box.png', draggable=True)
item_cat_scratcher = Entity([1000,500], [12,39], [58,39], 'item_cat_scratcher.png')
item_cat_bed = Entity([900,400], [17,14], [67,43], 'item_cat_bed.png')
item_bed = Entity([75,657], [13,19], [100,10], 'item_bed.png')

# Master list of all items
items = []
items.append(item_table)
items.append(item_shelf)
items.append(item_computer_desk)
items.append(item_cat_food_bowl)
items.append(item_cat_water_bowl)
items.append(item_cat_food_bag)
items.append(item_cat_litter_box)
items.append(item_cat_scratcher)
items.append(item_cat_bed)
items.append(item_bed)



# Inventory setup
INV_DISPLAY_SIZE = 60    # Size of inventory items in pixels
INV_NUM = 12             # Number of inventory slots shown
INV_PADDING = 10
INV_BASE_X = (SCREEN_WIDTH / 2) - (((INV_DISPLAY_SIZE + INV_PADDING) * INV_NUM) / 2)
INV_BASE_Y = 10
active_slot_index = 0
inventory = [None] * INV_NUM
dragging_item = None
dragging_item_index = None
def add_to_inventory(item):
    # Find the next empty inventory slot
    for i in range(INV_NUM):
        if inventory[i] is None:
            inventory[i] = item
            return True
    return False
def remove_from_inventory(item):
    # Removes an item from the inventory.
    if item in inventory:
        i = inventory.index(item)
        inventory[i] = None
        return True
    return False
def draw_inventory_gui():
    border_width = 5
    inactive_color = (128, 128, 128)
    active_color = (0, 0, 0)
    bar_color = (255, 255, 255)
    empty_slot_color = (200, 200, 200)

    bar_width = (INV_DISPLAY_SIZE * INV_NUM) + (INV_PADDING * (INV_NUM - 1))
    bar_height = INV_DISPLAY_SIZE + 20
    pygame.draw.rect(screen, bar_color, (INV_BASE_X - 10, INV_BASE_Y - 10, bar_width + 20, bar_height))

    for i in range(INV_NUM):
        item_x = INV_BASE_X + (i * (INV_DISPLAY_SIZE + INV_PADDING))
        item_y = INV_BASE_Y

        # Determine border color (black for active slot, grey for others)
        border_color = active_color if i == active_slot_index else inactive_color

        # Draw border for the slot
        pygame.draw.rect(screen, border_color, (item_x - border_width, item_y - border_width, INV_DISPLAY_SIZE + (border_width * 2), INV_DISPLAY_SIZE + (border_width * 2)))

        if inventory[i] is not None:
            # Draw item image
            screen.blit(inventory[i].icon, (item_x, item_y))
        else:
            # Draw empty slot
            pygame.draw.rect(screen, empty_slot_color, (item_x, item_y, INV_DISPLAY_SIZE, INV_DISPLAY_SIZE))
def check_inventory_click(mouse_x, mouse_y):
    for i in range(INV_NUM):
        item_x = INV_BASE_X + (i * (INV_DISPLAY_SIZE + INV_PADDING))
        item_y = INV_BASE_Y

        item_rect = pygame.Rect(item_x, item_y, INV_DISPLAY_SIZE, INV_DISPLAY_SIZE)

        if item_rect.collidepoint(mouse_x, mouse_y):
            return i  # Return the index of the clicked inventory slot
    return None



def check_interaction(object1, object2, inflation=20):
    if object1.check_collision(object2):
        if object1.collide_rect.inflate(inflation,inflation).collidepoint(adjusted_mouse_pos) or object2.collide_rect.inflate(inflation,inflation).collidepoint(adjusted_mouse_pos):
            return True
    return False




# Set up the room
background_layer = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'background_cafe3.png')).convert_alpha()
background_layer_farm = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'background_farm.png')).convert_alpha()
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 3000, 1080
bubble = {
    "heart": pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'emoji_heart.png')).convert_alpha(),
    "hunger": pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'emoji_hunger.png')).convert_alpha(),
}
room_obstacles = []
room_obstacles.append( Entity((0, 0), collision_rect_offset=(0,0), collision_rect_size=(370,330)) )      # top-left
room_obstacles.append( Entity((450, 0), collision_rect_offset=(0,0), collision_rect_size=(3000,330)) )   # top-right
room_obstacles.append( Entity((0, 0), collision_rect_offset=(0,0), collision_rect_size=(80,1080)) )      # left
room_obstacles.append( Entity((0, 1000), collision_rect_offset=(0,0), collision_rect_size=(3000,1080)) ) # bottom
room_obstacles.append( Entity((2940, 0), collision_rect_offset=(0,0), collision_rect_size=(3000,1080)) ) # right
room_exits = []
room_exits.append( Entity((330, 0), collision_rect_offset=(0,0), collision_rect_size=(450,310)) )




# GAME LOOP
running = True
current_day = None
current_time = None
camera_offset = [max(0, min(player.position[0] - SCREEN_WIDTH // 2, BACKGROUND_WIDTH - SCREEN_WIDTH)), max(0, min(player.position[1] - SCREEN_HEIGHT // 2, BACKGROUND_HEIGHT - SCREEN_HEIGHT))]
grid = mark_obstacles_on_grid()
connectivity_grid = populate_connectivity_grid()
while running:
    #print(astar_times)
    # Calculate elapsed time
    elapsed_time = pygame.time.get_ticks() - START_TIME
    current_day = (elapsed_time // MILLISECONDS_PER_DAY) + 1
    current_time = elapsed_time % MILLISECONDS_PER_DAY

    # Convert current time to hours and minutes for display
    in_game_hour = int(current_time // MILLISECONDS_PER_HOUR)
    in_game_minute = int((current_time % MILLISECONDS_PER_HOUR) / (MILLISECONDS_PER_HOUR / 60))

    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position
            mouse_pos = pygame.mouse.get_pos()

            # Check if an inventory item was clicked
            clicked_slot = check_inventory_click(mouse_pos[0], mouse_pos[1])
            if clicked_slot is not None:
                dragging_item = inventory[clicked_slot]
                dragging_item_index = clicked_slot

            # Adjust mouse position based on camera offset
            adjusted_mouse_pos = (mouse_pos[0] + camera_offset[0], mouse_pos[1] + camera_offset[1])

            # Check if the player is near the cat
            for entity in Entity.entities:
                if check_interaction(player, entity):
                    entity.interact()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button not in (4,5):   # button 4 or 5 gets a BUTTONUP event when the MOUSEWHEEL is moved
                clicked_slot = check_inventory_click(mouse_pos[0], mouse_pos[1])
                if clicked_slot is not None:
                    active_slot_index = clicked_slot
                    #print(f'active_slot_index:{active_slot_index}')
                release_slot = check_inventory_click(event.pos[0], event.pos[1])
                if release_slot is not None and dragging_item is not None:
                    # Swap the items
                    #print(f'dragging_item_index:{dragging_item_index} release_slot:{release_slot}')
                    inventory[dragging_item_index], inventory[release_slot] = inventory[release_slot], inventory[dragging_item_index]
                elif dragging_item is not None:
                    player.drop_entity(dragging_item)
                    remove_from_inventory(dragging_item)
                dragging_item = None
                dragging_item_index = None

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                active_slot_index -= 1
                if active_slot_index < 0:
                    active_slot_index = INV_NUM - 1
            elif event.y < 0:
                active_slot_index += 1
                if active_slot_index >= INV_NUM:
                    active_slot_index = 0

    # Handle movement through event handling
    keys = pygame.key.get_pressed()
    player.is_moving = False
    dx, dy = 0, 0   # Initialize movement changes
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and (keys[pygame.K_UP] or keys[pygame.K_w]):
        player.move(135, player.speed)
    elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
        player.move(225, player.speed)
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and (keys[pygame.K_UP] or keys[pygame.K_w]):
        player.move(45, player.speed)
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
        player.move(315, player.speed)
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move(180, player.speed)
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move(0, player.speed)
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        player.move(90, player.speed)
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.move(270, player.speed)
    elif keys[pygame.K_ESCAPE]:
        running = False
    elif keys[pygame.K_p]:
        print(f'mean:{sum(astar_times) / len(astar_times)} total:{sum(astar_times)}')

    # Update player game object sprite and position
    if player.is_moving:
        player.pose_index = (player.pose_index + 1) % 17
        sprite_to_draw = player.sprite_sheet[player.current_direction][round(player.pose_index / 3)]
    else:
        sprite_to_draw = player.sprite_sheet[f'idle_{player.current_direction}']
    player.sprite = sprite_to_draw

    # Update the player and NPC bubbles
    player.update_bubble()
    for npc in npcs:
        npc.update_bubble()

    # Update NPC states
    #print(f'cat1.fullness{cat.fullness} cat2.fullness{cat2.fullness} cat3.fullness{cat3.fullness} cat4.fullness{cat4.fullness}')
    for npc in npcs:
        npc.update()

    # Update NPC sprites
    for npc in npcs:
        if npc.is_moving:
            npc.pose_index = (npc.pose_index + 1) % 8
            sprite_to_draw = npc.sprite_sheet[npc.current_direction][round(npc.pose_index / 3)]
        else:
            sprite_to_draw = npc.sprite_sheet[f'idle_{npc.current_direction}']
        npc.sprite = sprite_to_draw

    # Calculate camera offset based on player position
    camera_offset = [max(0, min(player.position[0] - SCREEN_WIDTH // 2, BACKGROUND_WIDTH - SCREEN_WIDTH)), max(0, min(player.position[1] - SCREEN_HEIGHT // 2, BACKGROUND_HEIGHT - SCREEN_HEIGHT))]

    # Update the collision grid
    grid = mark_obstacles_on_grid()

    # Draw the background
    screen.blit(background_layer, (0 - camera_offset[0], 0 - camera_offset[1]))

    # Draw the rest of the items
    all_entities = items + npcs + [player]
    all_entities.sort(key=lambda obj: obj.get_z_order())
    for obj in all_entities:
        obj.blit(camera_offset, screen)

    # Draw held items
    if inventory[active_slot_index] is not None:
        player.update_held_position(inventory[active_slot_index])
        inventory[active_slot_index].blit(camera_offset, screen, True)

    # Draw the player bubble
    if player.bubble_visible and player.bubble_surface:
        # Adjust bubble_position as needed to position it above the actor
        bubble_position = (player.position[0] - camera_offset[0], player.position[1] - 60 - camera_offset[1])
        screen.blit(player.bubble_surface, bubble_position)
    
    # Draw NPC bubbles
    for npc in npcs:
        if npc.bubble_visible and npc.bubble_surface:
            # Adjust bubble_position as needed to position it above the actor
            bubble_position = (npc.position[0] - camera_offset[0], npc.position[1] - 20 - camera_offset[1])
            screen.blit(npc.bubble_surface, bubble_position)

    # DEBUG: Draw the grid
    #draw_grid()

    # Draw the player coordinates
    text = font.render(f"({player.position[0]}, {player.position[1]})", True, (255,255,255))
    screen.blit(text, (10, SCREEN_HEIGHT - 30))

    # Draw the in-game time
    am_pm = "AM" if in_game_hour < 12 else "PM"
    in_game_hour = in_game_hour % 12
    if in_game_hour == 0:
        in_game_hour = 12  # Adjust for midnight and noon
    time_string = f"Day {current_day}, {in_game_hour:02}:{in_game_minute:02} {am_pm}"
    time_surface = font.render(time_string, True, (255, 255, 255))
    screen.blit(time_surface, (10, 10))

    # Draw the FPS
    fps = str(int(clock.get_fps()))  # clock is your pygame.time.Clock() instance
    fps_text = font.render(f'FPS: {fps}', True, (255, 255, 255))  # White color
    screen.blit(fps_text, (10, 50))  # Position the FPS display; adjust as needed

    # Draw the inventory GUI
    draw_inventory_gui()

    # Draw dragging inventory items
    if dragging_item:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(dragging_item.icon, (mouse_x - INV_DISPLAY_SIZE // 2, mouse_y - INV_DISPLAY_SIZE // 2))

    # Flip
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
