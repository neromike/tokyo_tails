import pygame
import os

# Initialize pygame
pygame.init()

# Set up the display
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sprite Animation")

class Sprite:
    def __init__(self, name, file_name, pivot):
        self.name = name
        self.file_name = file_name
        self.pivot = pivot
        self.image = None
        self.load_image()
    def load_image(self):
        folder_path = "sprite/"
        self.image = pygame.image.load(os.path.join(folder_path, self.file_name + '.png')).convert_alpha()
    def draw_sprite(self, image, pos, originPos, angle):
        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        pygame.draw.rect(screen, (255,0,0), pygame.Rect(pos[0], pos[1], image_rect.width, image_rect.height), 1)
        #screen.blit(image, pos)
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-angle)
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
        screen.blit(rotated_image, (rotated_image_rect.x + originPos[0], rotated_image_rect.y + originPos[1]))
class Entity:
    def __init__(self, position, sprite_info, file_name='', is_dynamic=False, sprite_size=None):
        self.position = position
        self.sprite = []
        self.load_sprites(sprite_info)
    def load_sprites(self, sprite_info):
        for i in range(len(sprite_info)):
            self.sprite.append(Sprite(sprite_info[i]['name'], sprite_info[i]['file_name'], sprite_info[i]['pivot']))
    def draw_self(self):
        for i in range(len(self.sprite)):
            print(self.sprite[i].name)
            self.sprite[i].draw_sprite(self.sprite[i].image, self.position, self.sprite[i].pivot, 0)
        
class Actor(Entity):
    def __init__(self, position, sprite_info, energy, speed, sprite_size):
        super().__init__(position, sprite_info, sprite_size=sprite_size)
        self.energy = energy
        self.speed = speed
        self.current_direction = 'down'

class Player(Actor):
    def __init__(self, position, sprite_info, sprite_size, energy=100, speed=5):
        super().__init__(position, sprite_info, energy, speed, sprite_size)

player_sprite = [
    {'name':'head', 'file_name':'sprite_master_0003s_0012_head', 'pivot':(64,51)},
    {'name':'arm_left_lower', 'file_name':'sprite_master_0003s_0011_arm_left_lower', 'pivot':(52,61)},
    {'name':'arm_left_upper', 'file_name':'sprite_master_0003s_0010_arm_left_upper', 'pivot':(52,51)},
    {'name':'arm_right_lower', 'file_name':'sprite_master_0003s_0009_arm_right_lower', 'pivot':(78,621)},
    {'name':'arm_right_upper', 'file_name':'sprite_master_0003s_0008_arm_right_upper', 'pivot':(77,51)},
    {'name':'torso', 'file_name':'sprite_master_0003s_0007_torso', 'pivot':(64,64)},
    {'name':'left_hand', 'file_name':'sprite_master_0003s_0006_left_hand', 'pivot':(49,77)},
    {'name':'leg_left_lower', 'file_name':'sprite_master_0003s_0005_leg_left_lower', 'pivot':(60,92)},
    {'name':'leg_left_upper', 'file_name':'sprite_master_0003s_0004_leg_left_upper', 'pivot':(57,77)},
    {'name':'right_hand', 'file_name':'sprite_master_0003s_0003_right_hand', 'pivot':(79,77)},
    {'name':'leg_right_lower', 'file_name':'sprite_master_0003s_0002_leg_right_lower', 'pivot':(68,94)},
    {'name':'leg_right_upper', 'file_name':'sprite_master_0003s_0001_leg_right_upper', 'pivot':(70,78)},
    {'name':'hair', 'file_name':'sprite_master_0003s_0000_hair', 'pivot':(64,29)},
]
player = Player(position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), sprite_info=player_sprite, sprite_size=128)


player.draw_self()
pygame.display.update()
pygame.display.flip()


# Game loop
clockobject = pygame.time.Clock()
running = True
while running:
    clockobject.tick(30)
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    #screen.fill((0,0,0))

    


# Quit the game
pygame.quit()
