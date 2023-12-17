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
item_images = {
    "schmuppy": pygame.image.load('asset_item_schmuppy.png').convert_alpha(),
    "queso": pygame.image.load('asset_item_queso.png').convert_alpha(),
    "black cat": pygame.image.load('asset_item_black_cat.png').convert_alpha(),
    "orange cat": pygame.image.load('asset_item_orange_cat.png').convert_alpha()
}
sprite_sheet = pygame.image.load('sprite_player_128.png')  # Update with the path to your sprite sheet

# Function to get sprite
def get_sprite(x, y):
    """Extracts and returns a single sprite from the sprite sheet."""
    image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE))
    image.blit(sprite_sheet, (0, 0), (x * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
    image.set_colorkey(image.get_at((0,0)))  # Assumes top-left pixel is the transparent color
    return image

# Player setup
class Player:
    def __init__(self, position=[SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], energy=100):
        self.position = position
        self.energy = energy
        self.speed = 5

player = Player()

player_rect = pygame.Rect(player.position[0], player.position[1] + SPRITE_SIZE - 20, 80, 20)
player_sprites = {
    'down': [get_sprite(0, 0), get_sprite(1, 0), get_sprite(2, 0), get_sprite(3, 0)],
    'left': [get_sprite(0, 1), get_sprite(1, 1), get_sprite(2, 1), get_sprite(3, 1)],
    'right': [get_sprite(0, 2), get_sprite(1, 2), get_sprite(2, 2), get_sprite(3, 2)],
    'up': [get_sprite(0, 3), get_sprite(1, 3), get_sprite(2, 3), get_sprite(3, 3)],
    'idle_down': get_sprite(0, 4),
    'idle_left': get_sprite(1, 4),
    'idle_right': get_sprite(2, 4),
    'idle_up': get_sprite(3, 4)
}
current_direction = 'down'
pose_index = 0
is_moving = False

# Obstacle setup
obstacle_pos = [570, 715]
obstacle_rect = pygame.Rect(obstacle_pos[0] + 7, obstacle_pos[1] + 50, 157, 120)
obstacle_color = (0, 128, 128)  # Some color for the obstacle

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
    spacing = INV_SIZE + 10  # Spacing between items

    for i, item in enumerate(inventory):
        # Calculate the position for each item
        item_x = base_x + i * spacing
        item_y = base_y

        # Draw item image
        item_image = item_images[item]
        screen.blit(item_image, (item_x, item_y))

        # Draw item name or any other details
        text = font.render(item, True, (255, 255, 255))
        screen.blit(text, (item_x, item_y - FONT_SIZE))

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

    # Handle movement
    keys = pygame.key.get_pressed()
    is_moving = False
    dx, dy = 0, 0   # Initialize movement changes
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= player.speed
        current_direction = 'left'
        is_moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += player.speed
        current_direction = 'right'
        is_moving = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= player.speed
        current_direction = 'up'
        is_moving = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += player.speed
        current_direction = 'down'
        is_moving = True
    if keys[pygame.K_ESCAPE]:
        running = False

    # Normalize diagonal movement
    if dx != 0 and dy != 0:
        factor = (player.speed / math.sqrt(dx**2 + dy**2))
        dx *= factor
        dy *= factor

    # Update position and collision
    new_pos = [player.position[0] + dx, player.position[1] + dy]

    # Collision detection
    new_rect = pygame.Rect(new_pos[0], new_pos[1] + SPRITE_SIZE - 20, 80, 20)
    if not new_rect.colliderect(obstacle_rect):
        player.position = new_pos
        player_rect = new_rect
        if is_moving:
            pose_index = (pose_index + 1) % 4
            sprite_to_draw = player_sprites[current_direction][pose_index]
        else:
            sprite_to_draw = player_sprites[f'idle_{current_direction}']

     # Calculate camera offset based on player position
    camera_offset = calculate_camera_offset(player.position)

    # Update the screen
    screen.blit(background_layer_1, (-camera_offset[0], -camera_offset[1]))
    screen.blit(furniture_table, (obstacle_pos[0] - camera_offset[0], obstacle_pos[1] - camera_offset[1]))
    screen.blit(sprite_to_draw, (player.position[0] - camera_offset[0], player.position[1] - camera_offset[1]))
    text = font.render(f"({player.position[0]}, {player.position[1]})", True, (255,255,255))
    screen.blit(text, (10, SCREEN_HEIGHT - 30))
    draw_inventory_gui()

    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
