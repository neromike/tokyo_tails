import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
SPRITE_SIZE = 128
FONT_SIZE = 20
INV_SIZE = 60            # Size of inventory items in pixels
INV_NUM = 12             # Number of inventory slots shown
MAX_INVENTORY_SIZE = 36  # Maximum number of items in the inventory

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tokyo Tails")
font = pygame.font.Font(None, FONT_SIZE)

# Load image assets
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 3000, 1080
background_layer_1 = pygame.image.load('background_cafe3.png').convert_alpha()
furniture_table = pygame.image.load('asset_table.png').convert_alpha()
furniture_shelf = pygame.image.load('asset_shelf.png').convert_alpha()
item_images = {
    "schmuppy": pygame.image.load('asset_item_schmuppy.png').convert_alpha(),
    "queso": pygame.image.load('asset_item_queso.png').convert_alpha(),
    "black cat": pygame.image.load('asset_item_black_cat.png').convert_alpha(),
    "orange cat": pygame.image.load('asset_item_orange_cat.png').convert_alpha()
}

# Function to get sprite
def get_sprite(x, y):
    """Extracts and returns a single sprite from the sprite sheet."""
    image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE))
    image.blit(sprite_sheet, (0, 0), (x * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
    image.set_colorkey(image.get_at((0,0)))  # Assumes top-left pixel is the transparent color
    return image

# Actor superclass
class Actor:
    def __init__(self, position, energy, speed):
        self.position = position
        self.energy = energy
        self.speed = speed
        self.current_direction = 'down'
        self.pose_index = 0
        self.sprites = {}
        self.is_moving = False
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
    
        # Update position and collision
        new_pos = [self.position[0] + dx, self.position[1] + dy]

        # Check for X-axis collision
        new_rect = pygame.Rect(new_pos[0], self.position[1] + SPRITE_SIZE - 20, 40, 20)
        x_collision = any(new_rect.colliderect(obstacle) for obstacle in obstacles)

        # Update actor's position if no collision on X-axis
        if not x_collision:
            self.position[0] = new_pos[0]

        # Check for Y-axis collision
        new_rect = pygame.Rect(self.position[0], new_pos[1] + SPRITE_SIZE - 20, 40, 20)
        y_collision = any(new_rect.colliderect(obstacle) for obstacle in obstacles)

        # Update player position if no collision on Y-axis
        if not y_collision:
            self.position[1] = new_pos[1]
        
        # Actor doesn't move if collision on both x and y
        if x_collision and y_collision:
            self.is_moving = False

# Player setup
class Player(Actor):
    def __init__(self, position, energy, speed):
        super().__init__(position, energy, speed)
player = Player(position=[SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], energy=100, speed=5)
sprite_sheet = pygame.image.load('sprite_player_128.png')  # Update with the path to your sprite sheet
player.sprites = {
    'down': [get_sprite(0, 0), get_sprite(1, 0), get_sprite(2, 0), get_sprite(3, 0)],
    'left': [get_sprite(0, 1), get_sprite(1, 1), get_sprite(2, 1), get_sprite(3, 1)],
    'right': [get_sprite(0, 2), get_sprite(1, 2), get_sprite(2, 2), get_sprite(3, 2)],
    'up': [get_sprite(0, 3), get_sprite(1, 3), get_sprite(2, 3), get_sprite(3, 3)],
    'idle_down': get_sprite(0, 4),
    'idle_left': get_sprite(1, 4),
    'idle_right': get_sprite(2, 4),
    'idle_up': get_sprite(3, 4)
}

# Cat setup
class Cat(Actor):
    def __init__(self, position, energy, speed):
        super().__init__(position, energy, speed)
        self.fullness = 50
        self.bored = 50
cat = Cat(position=[550, 470], energy=20, speed=2)
sprite_sheet = pygame.image.load('sprite_cat_128.png')  # Update with the path to your sprite sheet
cat.sprites = {
    'down': [get_sprite(0, 0), get_sprite(1, 0), get_sprite(2, 0), get_sprite(3, 0)],
    'left': [get_sprite(0, 1), get_sprite(1, 1), get_sprite(2, 1), get_sprite(3, 1)],
    'right': [get_sprite(0, 2), get_sprite(1, 2), get_sprite(2, 2), get_sprite(3, 2)],
    'up': [get_sprite(0, 3), get_sprite(1, 3), get_sprite(2, 3), get_sprite(3, 3)],
    'idle_down': get_sprite(0, 4),
    'idle_left': get_sprite(1, 4),
    'idle_right': get_sprite(2, 4),
    'idle_up': get_sprite(3, 4)
}

# Obstacle setup
obstacles = []
table_pos = [570, 715]
shelf_pos = [65, 760]
table_obstacle = pygame.Rect(table_pos[0] + 7, table_pos[1] + 50, 157, 120)
shelf_obstacle = pygame.Rect(shelf_pos[0] + 7, shelf_pos[1] + 110, 157, 40)
obstacles.append(table_obstacle)
obstacles.append(shelf_obstacle)

#Populate the game objects
class GameObject:
    def __init__(self, image, position, is_dynamic=False):
        self.image = image
        self.position = position
        self.is_dynamic = is_dynamic
        self.dynamic_sprite = None
    def get_z_order(self):
        # Assuming y-coordinate determines depth
        return self.position[1]
    def set_dynamic_sprite(self, sprite):
        if self.is_dynamic:
            self.dynamic_sprite = sprite
game_objects = [
    GameObject(background_layer_1, (0, 0)),
    GameObject(furniture_table, (table_pos[0], table_pos[1])),
    GameObject(furniture_shelf, (shelf_pos[0], shelf_pos[1])),
]
player_game_object = GameObject(None, player.position, is_dynamic=True)
game_objects.append(player_game_object)
cat_game_object = GameObject(None, cat.position, is_dynamic=True)
game_objects.append(cat_game_object)

# Inventory setup
inventory = []
def add_to_inventory(item):
    """Adds an item to the inventory if there's space."""
    if len(inventory) < MAX_INVENTORY_SIZE:
        inventory.append(item)
        return True
    return False
def remove_from_inventory(item):
    """Removes an item from the inventory."""
    if item in inventory:
        inventory.remove(item)
        return True
    return False
def draw_inventory_gui():
    base_x, base_y = (SCREEN_WIDTH / 2) - ((INV_SIZE * INV_NUM) / 2), 10  # Starting position for the inventory GUI
    padding = 10

    bar_width = (INV_SIZE * INV_NUM) + (padding * (INV_NUM - 1))
    bar_height = INV_SIZE + 20  # Adjust the height as needed
    orange_color = (255, 165, 0)  # RGB color for orange
    pygame.draw.rect(screen, orange_color, (base_x - 10, base_y - 10, bar_width + 20, bar_height))
    empty_slot_color = (255, 0, 0)  # Color for empty slots

    for i in range(INV_NUM):
        # Calculate the position for each item
        item_x = base_x + (i * (INV_SIZE + padding))
        item_y = base_y

        if i < len(inventory):
            # Draw item image
            item_image = item_images[inventory[i]]
            screen.blit(item_image, (item_x, item_y))
        else:
            # Draw empty slot
            pygame.draw.rect(screen, empty_slot_color, (item_x, item_y, INV_SIZE, INV_SIZE))
add_to_inventory("schmuppy")
add_to_inventory("queso")
add_to_inventory("black cat")
add_to_inventory("orange cat")

# Function to calculate camera offset
def calculate_camera_offset(player_position):
    x_offset = max(0, min(player_position[0] - SCREEN_WIDTH // 2, BACKGROUND_WIDTH - SCREEN_WIDTH))
    y_offset = max(0, min(player_position[1] - SCREEN_HEIGHT // 2, BACKGROUND_HEIGHT - SCREEN_HEIGHT))
    return x_offset, y_offset

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    if player.is_moving:
        player.pose_index = (player.pose_index + 1) % 4
        sprite_to_draw = player.sprites[player.current_direction][player.pose_index]
    else:
        sprite_to_draw = player.sprites[f'idle_{player.current_direction}']

    # Update player game object sprite and position
    player_game_object.set_dynamic_sprite(sprite_to_draw)
    player_game_object.position = player.position

    cat_game_object.set_dynamic_sprite(sprite_to_draw)

    # Calculate camera offset based on player position
    camera_offset = calculate_camera_offset(player.position)

    # Sort objects by their z-order
    game_objects.sort(key=lambda obj: obj.get_z_order())

    # Render the objects in sorted order
    for obj in game_objects:
        image_to_blit = obj.dynamic_sprite if obj.is_dynamic else obj.image
        if image_to_blit:
            screen.blit(image_to_blit, (obj.position[0] - camera_offset[0], obj.position[1] - camera_offset[1]))


    text = font.render(f"({player.position[0]}, {player.position[1]})", True, (255,255,255))
    screen.blit(text, (10, SCREEN_HEIGHT - 30))
    draw_inventory_gui()

    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
