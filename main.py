import pygame
import os
import sys
import math
import random
import time
import heapq
import Entity
import Map
import NPC
import Actor
from Constants import *
import Pathing

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()



# Set up the screen
pygame.display.set_caption("Tokyo Tails")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, FONT_SIZE)



# Load and play background music
#pygame.mixer.init()
#pygame.mixer.music.load(os.path.join(SOUND_ASSET_PATH, '1243769_Loneliness-Corrupts-Me-Lof.mp3'))
#pygame.mixer.music.set_volume(1.0)  # Set the volume to full
#pygame.mixer.music.play()  # The -1 makes the music loop indefinitely




# PLAYER class
class Player(Actor.Actor):
    def __init__(self, position, speed, collision_rect_offset=(), collision_rect_size=(), file_name='', sprite_size=None):
        super().__init__(position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size)
        self.hp = 100


# Player setup
player = Player(position=[SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], speed=5, collision_rect_offset=(50,100), collision_rect_size=(40,20), file_name='', sprite_size=128)
sprite_sheet = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'sprite_player2_128.png'))
player.sprite_sheet = {
    'idle_down': player.get_sprite(sprite_sheet, 0, 0),
    'idle_up': player.get_sprite(sprite_sheet,0, 1),
    'idle_right': player.get_sprite(sprite_sheet,0, 2),
    'idle_left': player.get_sprite(sprite_sheet,0, 3),
    'down': [player.get_sprite(sprite_sheet,1, 0), player.get_sprite(sprite_sheet,2, 0), player.get_sprite(sprite_sheet,3, 0), player.get_sprite(sprite_sheet,4, 0), player.get_sprite(sprite_sheet,5, 0), player.get_sprite(sprite_sheet,6, 0)],
    'up': [player.get_sprite(sprite_sheet,1, 1), player.get_sprite(sprite_sheet,2, 1), player.get_sprite(sprite_sheet,3, 1), player.get_sprite(sprite_sheet,4, 1), player.get_sprite(sprite_sheet,5, 1), player.get_sprite(sprite_sheet,6, 1)],
    'right': [player.get_sprite(sprite_sheet,1, 2), player.get_sprite(sprite_sheet,2, 2), player.get_sprite(sprite_sheet,3, 2), player.get_sprite(sprite_sheet,4, 2), player.get_sprite(sprite_sheet,5, 2), player.get_sprite(sprite_sheet,6, 2)],
    'left': [player.get_sprite(sprite_sheet,1, 3), player.get_sprite(sprite_sheet,2, 3), player.get_sprite(sprite_sheet,3, 3), player.get_sprite(sprite_sheet,4, 3), player.get_sprite(sprite_sheet,5, 3), player.get_sprite(sprite_sheet,6, 3)],
}

# cat setup
cat = NPC.NPC(position=[550, 470], speed=7, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
sprite_sheet = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'sprite_cat2_64.png'))
cat.sprite_sheet = {
    'down': [cat.get_sprite(sprite_sheet,0, 0), cat.get_sprite(sprite_sheet,1, 0), cat.get_sprite(sprite_sheet,2, 0)],
    'left': [cat.get_sprite(sprite_sheet,0, 1), cat.get_sprite(sprite_sheet,1, 1), cat.get_sprite(sprite_sheet,2, 1)],
    'right': [cat.get_sprite(sprite_sheet,0, 2), cat.get_sprite(sprite_sheet,1, 2), cat.get_sprite(sprite_sheet,2, 2)],
    'up': [cat.get_sprite(sprite_sheet,0, 3), cat.get_sprite(sprite_sheet,1, 3), cat.get_sprite(sprite_sheet,2, 3)],
    'idle_down': cat.get_sprite(sprite_sheet,0, 0),
    'idle_left': cat.get_sprite(sprite_sheet,0, 1),
    'idle_right': cat.get_sprite(sprite_sheet,0, 2),
    'idle_up': cat.get_sprite(sprite_sheet,0, 3)
}

# cat2 setup
cat2 = NPC.NPC(position=[1550, 670], speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat2.sprite_sheet = {
    'down': [cat2.get_sprite(sprite_sheet,3, 0), cat2.get_sprite(sprite_sheet,4, 0), cat2.get_sprite(sprite_sheet,5, 0)],
    'left': [cat2.get_sprite(sprite_sheet,3, 1), cat2.get_sprite(sprite_sheet,4, 1), cat2.get_sprite(sprite_sheet,5, 1)],
    'right': [cat2.get_sprite(sprite_sheet,3, 2), cat2.get_sprite(sprite_sheet,4, 2), cat2.get_sprite(sprite_sheet,5, 2)],
    'up': [cat2.get_sprite(sprite_sheet,3, 3), cat2.get_sprite(sprite_sheet,4, 3), cat2.get_sprite(sprite_sheet,5, 3)],
    'idle_down': cat2.get_sprite(sprite_sheet,3, 0),
    'idle_left': cat2.get_sprite(sprite_sheet,3, 1),
    'idle_right': cat2.get_sprite(sprite_sheet,3, 2),
    'idle_up': cat2.get_sprite(sprite_sheet,3, 3)
}

# cat3 setup
cat3 = NPC.NPC(position=[1550, 730], speed=3, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat3.sprite_sheet = {
    'down': [cat3.get_sprite(sprite_sheet,6, 0), cat3.get_sprite(sprite_sheet,7, 0), cat3.get_sprite(sprite_sheet,8, 0)],
    'left': [cat3.get_sprite(sprite_sheet,6, 1), cat3.get_sprite(sprite_sheet,7, 1), cat3.get_sprite(sprite_sheet,8, 1)],
    'right': [cat3.get_sprite(sprite_sheet,6, 2), cat3.get_sprite(sprite_sheet,7, 2), cat3.get_sprite(sprite_sheet,8, 2)],
    'up': [cat3.get_sprite(sprite_sheet,6, 3), cat3.get_sprite(sprite_sheet,7, 3), cat3.get_sprite(sprite_sheet,8, 3)],
    'idle_down': cat3.get_sprite(sprite_sheet,6, 0),
    'idle_left': cat3.get_sprite(sprite_sheet,6, 1),
    'idle_right': cat3.get_sprite(sprite_sheet,6, 2),
    'idle_up': cat3.get_sprite(sprite_sheet,6, 3)
}

# cat4 setup
cat4 = NPC.NPC(position=[1550, 700], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat4.sprite_sheet = {
    'down': [cat4.get_sprite(sprite_sheet,9, 0), cat4.get_sprite(sprite_sheet,10, 0), cat4.get_sprite(sprite_sheet,11, 0)],
    'left': [cat4.get_sprite(sprite_sheet,9, 1), cat4.get_sprite(sprite_sheet,10, 1), cat4.get_sprite(sprite_sheet,11, 1)],
    'right': [cat4.get_sprite(sprite_sheet,9, 2), cat4.get_sprite(sprite_sheet,10, 2), cat4.get_sprite(sprite_sheet,11, 2)],
    'up': [cat4.get_sprite(sprite_sheet,9, 3), cat4.get_sprite(sprite_sheet,10, 3), cat4.get_sprite(sprite_sheet,11, 3)],
    'idle_down': cat4.get_sprite(sprite_sheet,9, 0),
    'idle_left': cat4.get_sprite(sprite_sheet,9, 1),
    'idle_right': cat4.get_sprite(sprite_sheet,9, 2),
    'idle_up': cat4.get_sprite(sprite_sheet,9, 3)
}

# cat5 setup
cat5 = NPC.NPC(position=[1200, 500], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
sprite_sheet = pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'sprite_cat_fluffy.png'))
cat5.sprite_sheet = {
    'down': [cat5.get_sprite(sprite_sheet,0, 0), cat5.get_sprite(sprite_sheet,1, 0), cat5.get_sprite(sprite_sheet,2, 0)],
    'left': [cat5.get_sprite(sprite_sheet,0, 1), cat5.get_sprite(sprite_sheet,1, 1), cat5.get_sprite(sprite_sheet,2, 1)],
    'right': [cat5.get_sprite(sprite_sheet,0, 2), cat5.get_sprite(sprite_sheet,1, 2), cat5.get_sprite(sprite_sheet,2, 2)],
    'up': [cat5.get_sprite(sprite_sheet,0, 3), cat5.get_sprite(sprite_sheet,1, 3), cat5.get_sprite(sprite_sheet,2, 3)],
    'idle_down': cat5.get_sprite(sprite_sheet,0, 0),
    'idle_left': cat5.get_sprite(sprite_sheet,0, 1),
    'idle_right': cat5.get_sprite(sprite_sheet,0, 2),
    'idle_up': cat5.get_sprite(sprite_sheet,0, 3)
}

# cat6 setup
cat6 = NPC.NPC(position=[1200, 550], speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat6.sprite_sheet = {
    'down': [cat6.get_sprite(sprite_sheet,3, 0), cat6.get_sprite(sprite_sheet,4, 0), cat6.get_sprite(sprite_sheet,5, 0)],
    'left': [cat6.get_sprite(sprite_sheet,3, 1), cat6.get_sprite(sprite_sheet,4, 1), cat6.get_sprite(sprite_sheet,5, 1)],
    'right': [cat6.get_sprite(sprite_sheet,3, 2), cat6.get_sprite(sprite_sheet,4, 2), cat6.get_sprite(sprite_sheet,5, 2)],
    'up': [cat6.get_sprite(sprite_sheet,3, 3), cat6.get_sprite(sprite_sheet,4, 3), cat6.get_sprite(sprite_sheet,5, 3)],
    'idle_down': cat6.get_sprite(sprite_sheet,3, 0),
    'idle_left': cat6.get_sprite(sprite_sheet,3, 1),
    'idle_right': cat6.get_sprite(sprite_sheet,3, 2),
    'idle_up': cat6.get_sprite(sprite_sheet,3, 3)
}

# cat7 setup
cat7 = NPC.NPC(position=[1200, 500], speed=3, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat7.sprite_sheet = {
    'down': [cat7.get_sprite(sprite_sheet,6, 0), cat7.get_sprite(sprite_sheet,7, 0), cat7.get_sprite(sprite_sheet,8, 0)],
    'left': [cat7.get_sprite(sprite_sheet,6, 1), cat7.get_sprite(sprite_sheet,7, 1), cat7.get_sprite(sprite_sheet,8, 1)],
    'right': [cat7.get_sprite(sprite_sheet,6, 2), cat7.get_sprite(sprite_sheet,7, 2), cat7.get_sprite(sprite_sheet,8, 2)],
    'up': [cat7.get_sprite(sprite_sheet,6, 3), cat7.get_sprite(sprite_sheet,7, 3), cat7.get_sprite(sprite_sheet,8, 3)],
    'idle_down': cat7.get_sprite(sprite_sheet,6, 0),
    'idle_left': cat7.get_sprite(sprite_sheet,6, 1),
    'idle_right': cat7.get_sprite(sprite_sheet,6, 2),
    'idle_up': cat7.get_sprite(sprite_sheet,6, 3)
}

# cat8 setup
cat8 = NPC.NPC(position=[1200, 450], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat8.sprite_sheet = {
    'down': [cat8.get_sprite(sprite_sheet,9, 0), cat8.get_sprite(sprite_sheet,10, 0), cat8.get_sprite(sprite_sheet,11, 0)],
    'left': [cat8.get_sprite(sprite_sheet,9, 1), cat8.get_sprite(sprite_sheet,10, 1), cat8.get_sprite(sprite_sheet,11, 1)],
    'right': [cat8.get_sprite(sprite_sheet,9, 2), cat8.get_sprite(sprite_sheet,10, 2), cat8.get_sprite(sprite_sheet,11, 2)],
    'up': [cat8.get_sprite(sprite_sheet,9, 3), cat8.get_sprite(sprite_sheet,10, 3), cat8.get_sprite(sprite_sheet,11, 3)],
    'idle_down': cat8.get_sprite(sprite_sheet,9, 0),
    'idle_left': cat8.get_sprite(sprite_sheet,9, 1),
    'idle_right': cat8.get_sprite(sprite_sheet,9, 2),
    'idle_up': cat8.get_sprite(sprite_sheet,9, 3)
}

# cat9 setup
cat9 = NPC.NPC(position=[1200, 400], speed=4, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat9.sprite_sheet = {
    'down': [cat9.get_sprite(sprite_sheet,9, 0), cat9.get_sprite(sprite_sheet,10, 0), cat9.get_sprite(sprite_sheet,11, 0)],
    'left': [cat9.get_sprite(sprite_sheet,9, 1), cat9.get_sprite(sprite_sheet,10, 1), cat9.get_sprite(sprite_sheet,11, 1)],
    'right': [cat9.get_sprite(sprite_sheet,9, 2), cat9.get_sprite(sprite_sheet,10, 2), cat9.get_sprite(sprite_sheet,11, 2)],
    'up': [cat9.get_sprite(sprite_sheet,9, 3), cat9.get_sprite(sprite_sheet,10, 3), cat9.get_sprite(sprite_sheet,11, 3)],
    'idle_down': cat9.get_sprite(sprite_sheet,9, 0),
    'idle_left': cat9.get_sprite(sprite_sheet,9, 1),
    'idle_right': cat9.get_sprite(sprite_sheet,9, 2),
    'idle_up': cat9.get_sprite(sprite_sheet,9, 3)
}

# cat10 setup
cat10 = NPC.NPC(position=[1200, 350], speed=5, collision_rect_offset=(17,50), collision_rect_size=(30,17), file_name='', sprite_size=64)
cat10.sprite_sheet = {
    'down': [cat10.get_sprite(sprite_sheet,3, 0), cat10.get_sprite(sprite_sheet,4, 0), cat10.get_sprite(sprite_sheet,5, 0)],
    'left': [cat10.get_sprite(sprite_sheet,3, 1), cat10.get_sprite(sprite_sheet,4, 1), cat10.get_sprite(sprite_sheet,5, 1)],
    'right': [cat10.get_sprite(sprite_sheet,3, 2), cat10.get_sprite(sprite_sheet,4, 2), cat10.get_sprite(sprite_sheet,5, 2)],
    'up': [cat10.get_sprite(sprite_sheet,3, 3), cat10.get_sprite(sprite_sheet,4, 3), cat10.get_sprite(sprite_sheet,5, 3)],
    'idle_down': cat10.get_sprite(sprite_sheet,3, 0),
    'idle_left': cat10.get_sprite(sprite_sheet,3, 1),
    'idle_right': cat10.get_sprite(sprite_sheet,3, 2),
    'idle_up': cat10.get_sprite(sprite_sheet,3, 3)
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
item_table = Entity.Entity([570,715], [7,50], [157,120], 'item_table.png')
item_shelf = Entity.Entity([65,760], [7,110], [157,40], 'item_shelf.png')
item_computer_desk = Entity.Entity([1300,250], [15,60], [120,55], 'item_computer_desk.png')
item_cat_food_bowl = Entity.Entity([1300,450], [8,8], [40,20], 'item_cat_food_bowl_full.png', holdable=True, held_y_offset=10, icon_file_name='icon_cat_food_bowl.png')
item_cat_food_bowl.sprite_sheet = {
    'full': pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'item_cat_food_bowl_full.png')),
    'mid': pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'item_cat_food_bowl_mid.png')),
    'empty': pygame.image.load(os.path.join(IMAGE_ASSET_PATH, 'item_cat_food_bowl_empty.png')),
}
NPC.NPC.cat_food.append(item_cat_food_bowl)

item_cat_water_bowl = Entity.Entity([1300,650], [8,8], [40,20], 'item_cat_water_bowl.png', holdable=True, held_y_offset=10, icon_file_name='icon_cat_water_bowl.png')
NPC.NPC.cat_drink.append(item_cat_water_bowl)

item_cat_food_bag = Entity.Entity([1200,700], [5,50], [44,14], 'item_cat_food_bag.png', holdable=True, held_y_offset=40, icon_file_name='icon_cat_food_bag.png')

item_cat_litter_box = Entity.Entity([1000,700], [13,37], [67,54], 'item_cat_litter_box.png', draggable=True)
NPC.NPC.litter_boxes.append(item_cat_litter_box)

item_cat_scratcher = Entity.Entity([1000,500], [12,39], [58,39], 'item_cat_scratcher.png')
NPC.NPC.cat_toys.append(item_cat_scratcher)

item_cat_bed = Entity.Entity([900,400], [17,14], [67,43], 'item_cat_bed.png')
NPC.NPC.cat_beds.append(item_cat_bed)

item_bed = Entity.Entity([75,657], [13,19], [100,10], 'item_bed.png')



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
room_obstacles.append(Entity.Entity((0, 0), collision_rect_offset=(0,0), collision_rect_size=(370,330)) )      # top-left
room_obstacles.append(Entity.Entity((450, 0), collision_rect_offset=(0,0), collision_rect_size=(3000,330)) )   # top-right
room_obstacles.append(Entity.Entity((0, 0), collision_rect_offset=(0,0), collision_rect_size=(80,1080)) )      # left
room_obstacles.append(Entity.Entity((0, 1000), collision_rect_offset=(0,0), collision_rect_size=(3000,1080)) ) # bottom
room_obstacles.append(Entity.Entity((2940, 0), collision_rect_offset=(0,0), collision_rect_size=(3000,1080)) ) # right
room_exits = []
room_exits.append(Entity.Entity((330, 0), collision_rect_offset=(0,0), collision_rect_size=(450,310)) )




# GAME LOOP
running = True
current_day = None
current_time = None
camera_offset = [max(0, min(player.position[0] - SCREEN_WIDTH // 2, BACKGROUND_WIDTH - SCREEN_WIDTH)), max(0, min(player.position[1] - SCREEN_HEIGHT // 2, BACKGROUND_HEIGHT - SCREEN_HEIGHT))]
Map.update_grid(background_layer,room_obstacles+items, "house")
Map.update_colliders([items,room_obstacles,room_exits],"house")

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
            for entity in Entity.Entity.entities:
                if check_interaction(player, entity):
                    if(entity.interact() and add_to_inventory(entity)):
                        entity.pick_up()

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
    colliders = [items, room_obstacles, room_exits]
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
        print(f'mean:{sum(Pathing.astar_times) / len(Pathing.astar_times)} total:{sum(Pathing.astar_times)}')

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
    grid = Pathing.mark_obstacles_on_grid(background_layer,items+room_obstacles)

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
