import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
FONT_SIZE = 20

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tokyo Tails")
font = pygame.font.Font(None, FONT_SIZE)

# Load image assets
background_layer = pygame.image.load('background_cafe3.png').convert_alpha()
item_images = {
    "schmuppy": pygame.image.load('asset_item_schmuppy.png').convert_alpha(),
    "queso": pygame.image.load('asset_item_queso.png').convert_alpha(),
    "black cat": pygame.image.load('asset_item_black_cat.png').convert_alpha(),
    "orange cat": pygame.image.load('asset_item_orange_cat.png').convert_alpha()
}




# Setup the room
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 3000, 1080
room_obstacles = []
room_obstacles.append( pygame.Rect(0, 0, 370, 330) )          # top-left
room_obstacles.append( pygame.Rect(450, 0, 3000, 330) )       # top-right
room_obstacles.append( pygame.Rect(0, 0, 80, 1080) )          # left
room_obstacles.append( pygame.Rect(0, 1000, 3000, 1080) )     # bottom
room_obstacles.append( pygame.Rect(2940, 0, 3000, 1080) )     # right
room_exits = []
room_exits.append( pygame.Rect(330, 0, 450, 310))

# Entity class
class Entity:
    def __init__(self, position, collision_rect_offset=(), collision_rect_size=(), file_name='', is_dynamic=False, sprite_size=None):
        self.position = position
        self.collision_rect_offset = collision_rect_offset
        self.collision_rect_size = collision_rect_size
        self.file_name = file_name
        self.is_dynamic = is_dynamic
        self.image = None
        self.sprite_size = sprite_size
        self.dynamic_sprite = None
        self.collide_rect = None
        self.update_collide_rect()
        if not self.file_name == '':
            self.load_image()
    def update_collide_rect(self):
        self.collide_rect = pygame.Rect(self.position[0] + self.collision_rect_offset[0], self.position[1] + self.collision_rect_offset[1], self.collision_rect_size[0], self.collision_rect_size[1])
    def load_image(self):
        self.image = pygame.image.load(self.file_name).convert_alpha()
    def get_z_order(self):
        # Assuming y-coordinate determines depth
        return self.position[1] + self.collision_rect_offset[1] + (self.collision_rect_size[1] / 2)
    def set_dynamic_sprite(self, sprite):
        if self.is_dynamic:
            self.dynamic_sprite = sprite
    def collision_center(self):
        return [self.position[0] + self.collision_rect_offset[0] + (self.collision_rect_size[0] / 2), self.position[1] + self.collision_rect_offset[1] + (self.collision_rect_size[1] / 2)]
    def get_sprite(self, x, y):
        # Extracts and returns a single sprite from the sprite sheet.
        image = pygame.Surface((self.sprite_size, self.sprite_size))
        image.blit(sprite_sheet, (0, 0), (x * self.sprite_size, y * self.sprite_size, self.sprite_size, self.sprite_size))
        image.set_colorkey(image.get_at((0,0)))  # Assumes top-left pixel is the transparent color
        return image

# Actor class
class Actor(Entity):
    def __init__(self, position, energy, speed, collision_rect_offset, collision_rect_size, sprite_size=None):
        super().__init__(position, collision_rect_offset, collision_rect_size, sprite_size=sprite_size)
        self.energy = energy
        self.speed = speed
        self.current_direction = 'down'
        self.pose_index = 0
        self.sprite = {}
        self.is_moving = False
        self.bubble = None

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
    
        # Calculate new position to check for collission
        new_pos = [self.position[0] + dx, self.position[1] + dy]

        # Check for X-axis collision
        new_rect = self.real_rect(new_pos[0], self.position[1])
        x_collision = any(new_rect.colliderect(item.collide_rect) for item in items if item is not self)
        if not x_collision:
            x_collision = any(new_rect.colliderect(item) for item in room_obstacles)

        # Update actor's position if no collision on X-axis
        if not x_collision:
            self.position[0] = new_pos[0]
            self.update_collide_rect()

        # Check for Y-axis collision
        new_rect = self.real_rect(self.position[0], new_pos[1])
        y_collision = any(new_rect.colliderect(item.collide_rect) for item in items if item is not self)
        if not y_collision:
            y_collision = any(new_rect.colliderect(item) for item in room_obstacles)
        if not y_collision:
            y_collision = any(new_rect.colliderect(item) for item in room_exits)
            if y_collision:
                print("You left the room")
        
        # Update player position if no collision on Y-axis
        if not y_collision:
            self.position[1] = new_pos[1]
            self.update_collide_rect()
        
        # Actor doesn't move if collision on both x and y
        if x_collision and y_collision:
            self.is_moving = False

    def real_rect(self, x, y):
        # Return the actual rect size for the sprite
        return pygame.Rect(
            x + self.collision_rect_offset[0],
            y + self.collision_rect_offset[1],
            self.collision_rect_size[0],
            self.collision_rect_size[1]
        )

    def bubble_check(self):
        passa

# NPC class
class NPC(Actor):
    def __init__(self, position, energy, speed, collision_rect_offset, collision_rect_size, sprite_size=None):
        super().__init__(position, energy, speed, collision_rect_offset, collision_rect_size, sprite_size)
        self.fullness = 50
        self.bored = 50
        self.motivation = 0
        self.motivation_threshold = 75  # Define a threshold for motivation
        self.direction = 0
        self.task = ''
        self.subtask = ''
    def update(self):
        # Get hungrier over time
        self.fullness -= random.randint(0, 1)
        
        # Go eat if hungry
        if self.fullness < 10:
            self.task = 'eat'

        # Increase motivation if there are no tasks
        #if self.task == '':
        self.motivation += random.randint(0, 1)  # Adjust the range as needed

        # Check if motivation is above threshold
        if self.motivation > self.motivation_threshold:
            # Choose a random direction
            self.direction = (self.direction + random.randint(-20,20)) % 360
            
            # Move the cat
            self.move(self.direction, self.speed)

            # Lose the motivation
            self.motivation = 0
        
        if self.task == 'eat':
            # Point towards the cat food
            dx = item_cat_food.position[0] - self.collision_center()[0]
            dy = item_cat_food.collision_center()[1] - self.collision_center()[1]
            self.direction = math.degrees(math.atan2(-dy, dx)) % 360

            #Lower the motivation threshold
            self.motivation_threshold = 5

# Player class
class Player(Actor):
    def __init__(self, position, energy, speed, collision_rect_offset=(), collision_rect_size=(), sprite_size=None):
        super().__init__(position, energy, speed, collision_rect_offset, collision_rect_size, sprite_size)



# Player setup
player = Player(position=[SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], energy=100, speed=5, collision_rect_offset=(50,100), collision_rect_size=(40,20), sprite_size=128)
player.is_dynamic = True
sprite_sheet = pygame.image.load('sprite_player2_128.png')  # Update with the path to your sprite sheet
player.sprite = {
    'idle_down': player.get_sprite(0, 0),
    'idle_up': player.get_sprite(0, 1),
    'idle_right': player.get_sprite(0, 2),
    'idle_left': player.get_sprite(0, 3),
    'down': [player.get_sprite(1, 0), player.get_sprite(2, 0), player.get_sprite(3, 0), player.get_sprite(4, 0), player.get_sprite(5, 0), player.get_sprite(6, 0)],
    'up': [player.get_sprite(1, 1), player.get_sprite(2, 1), player.get_sprite(3, 1), player.get_sprite(4, 1), player.get_sprite(5, 1), player.get_sprite(6, 1)],
    'right': [player.get_sprite(1, 2), player.get_sprite(2, 2), player.get_sprite(3, 2), player.get_sprite(4, 2), player.get_sprite(5, 2), player.get_sprite(6, 2)],
    'left': [player.get_sprite(1, 3), player.get_sprite(2, 3), player.get_sprite(3, 3), player.get_sprite(4, 3), player.get_sprite(5, 3), player.get_sprite(6, 3)],
}

# Cat setup
cat = NPC(position=[550, 470], energy=20, speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), sprite_size=64)
cat.is_dynamic = True
sprite_sheet = pygame.image.load('sprite_cat2_64.png')  # Update with the path to your sprite sheet
cat.sprite = {
    'down': [cat.get_sprite(0, 0), cat.get_sprite(1, 0), cat.get_sprite(2, 0)],
    'left': [cat.get_sprite(0, 1), cat.get_sprite(1, 1), cat.get_sprite(2, 1)],
    'right': [cat.get_sprite(0, 2), cat.get_sprite(1, 2), cat.get_sprite(2, 2)],
    'up': [cat.get_sprite(0, 3), cat.get_sprite(1, 3), cat.get_sprite(2, 3)],
    'idle_down': cat.get_sprite(0, 0),
    'idle_left': cat.get_sprite(0, 1),
    'idle_right': cat.get_sprite(0, 2),
    'idle_up': cat.get_sprite(0, 3)
}

# Item setup
item_table = Entity([570,715], [7,50], [157,120], 'asset_table.png')
item_shelf = Entity([65,760], [7,110], [157,40], 'asset_shelf.png')
item_cat_food = Entity([875,330], [8,8], [40,20], 'asset_cat_food.png')

# Master list of all objects, includig the player and NPCs
items = []
items.append(item_table)
items.append(item_shelf)
items.append(item_cat_food)
items.append(player)
items.append(cat)



# Inventory setup
INV_DISPLAY_SIZE = 60    # Size of inventory items in pixels
INV_NUM = 12             # Number of inventory slots shown
MAX_INVENTORY_SIZE = 36  # Maximum number of items in the inventory
INV_PADDING = 10
INV_BASE_X = (SCREEN_WIDTH / 2) - (((INV_DISPLAY_SIZE + INV_PADDING) * INV_NUM) / 2)
INV_BASE_Y = 10
active_slot_index = 0
inventory = []
def add_to_inventory(item):
    # Adds an item to the inventory if there's space.
    if len(inventory) < MAX_INVENTORY_SIZE:
        inventory.append(item)
        return True
    return False
def remove_from_inventory(item):
    # Removes an item from the inventory.
    if item in inventory:
        inventory.remove(item)
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

        if i < len(inventory):
            # Draw item image
            item_image = item_images[inventory[i]]
            screen.blit(item_image, (item_x, item_y))
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
add_to_inventory("schmuppy")
add_to_inventory("queso")
add_to_inventory("black cat")
add_to_inventory("orange cat")



# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if an inventory item was clicked
            clicked_slot = check_inventory_click(mouse_x, mouse_y)
            if clicked_slot is not None:
                active_slot_index = clicked_slot

            # Adjust mouse position based on camera offset
            adjusted_mouse_x = mouse_x + camera_offset[0]
            adjusted_mouse_y = mouse_y + camera_offset[1]

            # Check if the player is near the cat
            player_rect = pygame.Rect(player.position[0], player.position[1], player.sprite_size, player.sprite_size)
            cat_rect = pygame.Rect(cat.position[0], cat.position[1], cat.sprite_size, cat.sprite_size)

            if player_rect.colliderect(cat_rect.inflate(20, 20)):  # Inflate the cat's rect for a proximity check
                # Check if the mouse click is on the cat
                if cat_rect.collidepoint(adjusted_mouse_x, adjusted_mouse_y):
                    # Implement interaction logic here
                    print("Player clicked on the cat!")

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

    # Update player game object sprite and position
    if player.is_moving:
        player.pose_index = (player.pose_index + 1) % 17
        sprite_to_draw = player.sprite[player.current_direction][round(player.pose_index / 3)]
    else:
        sprite_to_draw = player.sprite[f'idle_{player.current_direction}']
    player.set_dynamic_sprite(sprite_to_draw)

    # Update NPC states
    cat.update()

    # Update cat game object sprite and position
    if cat.is_moving:
        cat.pose_index = (cat.pose_index + 1) % 8
        sprite_to_draw = cat.sprite[cat.current_direction][round(cat.pose_index / 3)]
    else:
        sprite_to_draw = cat.sprite[f'idle_{cat.current_direction}']
    cat.set_dynamic_sprite(sprite_to_draw)

    # Calculate camera offset based on player position
    camera_offset = [max(0, min(player.position[0] - SCREEN_WIDTH // 2, BACKGROUND_WIDTH - SCREEN_WIDTH)), max(0, min(player.position[1] - SCREEN_HEIGHT // 2, BACKGROUND_HEIGHT - SCREEN_HEIGHT))]
    
    # Draw the background
    screen.blit(background_layer, (0 - camera_offset[0], 0 - camera_offset[1]))

    # Draw the rest of the items
    items.sort(key=lambda obj: obj.get_z_order())
    for obj in items:
        image_to_blit = obj.dynamic_sprite if obj.is_dynamic else obj.image
        if image_to_blit:
            screen.blit(image_to_blit, (obj.position[0] - camera_offset[0], obj.position[1] - camera_offset[1]))

    # Draw the player coordinates
    text = font.render(f"({player.position[0]}, {player.position[1]})", True, (255,255,255))
    screen.blit(text, (10, SCREEN_HEIGHT - 30))
    
    # Draw the inventory GUI
    draw_inventory_gui()

    # Flip
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
