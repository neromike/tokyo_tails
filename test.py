import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
SPRITE_SIZE = 256
SPEED = 5
FONT_SIZE = 20

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tokyo Tails")
font = pygame.font.Font(None, FONT_SIZE)

# Load background layers
background_layer_1 = pygame.image.load('background_frame.png').convert_alpha()
background_layer_2 = pygame.image.load('background_test.png').convert_alpha()

# Load the sprite sheet
sprite_sheet = pygame.image.load('sprite_player.png')  # Update with the path to your sprite sheet
#sprite_sheet = pygame.transform.scale(sprite_sheet, (SPRITE_SIZE * 4, SPRITE_SIZE * 4)) # Scale if needed

# Function to get sprite
def get_sprite(x, y):
    """Extracts and returns a single sprite from the sprite sheet."""
    image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE))
    image.blit(sprite_sheet, (0, 0), (x * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))
    image.set_colorkey(image.get_at((0,0)))  # Assumes top-left pixel is the transparent color
    return image

# Player setup
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_rect = pygame.Rect(player_pos[0], player_pos[1] + SPRITE_SIZE - 20, 80, 20)
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
obstacle_rect = pygame.Rect(obstacle_pos[0], obstacle_pos[1], 180, 130)
obstacle_color = (0, 128, 128)  # Some color for the obstacle

# Inventory setup
inventory = []
MAX_INVENTORY_SIZE = 5  # Maximum number of items in the inventory

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

def draw_inventory():
    """Draws the inventory on the screen."""
    for i, item in enumerate(inventory):
        text = font.render(f"{i + 1}: {item}", True, (255, 255, 255))
        screen.blit(text, (10, 10 + i * (FONT_SIZE + 5)))

add_to_inventory("schmuppy")
add_to_inventory("queso")
add_to_inventory("black cat")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle movement
    keys = pygame.key.get_pressed()
    is_moving = False
    new_pos = player_pos.copy()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_pos[0] -= SPEED
        current_direction = 'left'
        is_moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_pos[0] += SPEED
        current_direction = 'right'
        is_moving = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_pos[1] -= SPEED
        current_direction = 'up'
        is_moving = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_pos[1] += SPEED
        current_direction = 'down'
        is_moving = True

    # Collision detection
    new_rect = pygame.Rect(new_pos[0], new_pos[1] + SPRITE_SIZE - 20, 80, 20)
    if not new_rect.colliderect(obstacle_rect):
        player_pos = new_pos
        player_rect = new_rect
        if is_moving:
            pose_index = (pose_index + 1) % 4
            sprite_to_draw = player_sprites[current_direction][pose_index]
        else:
            sprite_to_draw = player_sprites[f'idle_{current_direction}']

    # Update the screen
    screen.blit(background_layer_2, (0, 0))  # Draw the second background layer
    screen.blit(background_layer_1, (0, 0))  # Draw the first background layer
    pygame.draw.rect(screen, obstacle_color, obstacle_rect)  # Draw the obstacle
    screen.blit(sprite_to_draw, player_pos)
    draw_inventory()

    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
