import random
import Actor
import Pathing
import Map






# NPC class
class NPC(Actor.Actor):
    cat_toys = []
    cat_food = []
    cat_drink = []
    litter_boxes = []
    cat_beds = []

    def __init__(self, position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size=None):
        super().__init__(position, speed, collision_rect_offset, collision_rect_size, file_name, sprite_size)
        self.happiness = random.randint(30, 90)
        self.fullness = random.randint(50, 90)
        self.thirsty = random.randint(10, 30)
        self.digest_speed = random.randint(20, 80) / (1 * 1000)  # 80% per 5 minutes = 80 /(5 * 60 * 1000)
        self.poop = random.randint(10, 30)
        self.poop_generation_rate = random.random()
        self.pee = random.randint(10, 30)
        self.pee_generation_rate = random.random()
        self.thirsty_gain_speed = random.randint(20, 80) / (1 * 1000)
        self.energy_drain_speed = random.randint(20, 80) / (1 * 1000)
        self.happiness_drain_speed = random.randint(20, 80) / (1 * 1000)
        self.direction = 0
        self.task = ''
        self.path = None
        self.destination = ()
        self.currently_exploring = False
        self.time_since_last_activity_change = 0
        self.new_activity_every_x_seconds = random.randint(10,20)

    def update(self):

        grid = Map.loc_to_grid[self.loc]


        # DEBUG
        # print(f'doing self.task:{self.task}')
        if self.task != '':
            # self.show_bubble(text=self.task)
            pass
        # self.task = 'explore'

        # Update the activity change timer
        self.time_since_last_activity_change += 1

        # Digest food
        self.fullness -= self.digest_speed

        # Find food if hungry
        if self.fullness <= 20 and self.task in ['', 'explore']:
            self.task = 'find-food'
            # self.show_bubble(image=bubble['hunger'])

        # Lower the cat energy
        self.energy -= self.energy_drain_speed

        # Find bed if low on energy
        if self.energy <= 20 and self.task in ['', 'explore']:
            self.task = 'find-sleep'
            # self.show_bubble(image=bubble['tired']

        # Lower happiness
        self.happiness -= self.happiness_drain_speed

        # Find toy if not happy
        if self.happiness <= 20 and self.task in ['', 'explore']:
            self.task = 'find-toy'
            # self.show_bubble(image=bubble['sad'])

        # Get thirsty
        self.thirsty += self.thirsty_gain_speed

        # Find water bowl if thirsty
        if self.thirsty >= 80 and self.task in ['', 'explore']:
            self.task = 'find-water'
            # self.show_bubble(image=bubble['thirsty'])

        # Find litter box if need to pee or poop
        if (self.poop >= 80 or self.pee >= 80) and self.task in ['', 'explore']:
            self.task = 'find-litter-box'
            # self.show_bubble(image=bubble['bathroom'])

        # --- EAT ---
        if self.task == 'eat':
            self.is_moving = False
            # Check if there is a food bowl nearby
            b = False
            food_dish = ''
            for item in NPC.cat_food:
                if self.check_collision(item, proximity=40):
                    b = True
                    food_dish = item

            if b:
                # Can only eat if the bowl has food
                if food_dish.energy > 0:

                    # Eat the food
                    self.fullness += 1

                    # Make poop
                    self.poop += self.poop_generation_rate

                    # Stop eating when full
                    if self.fullness >= 100:
                        self.task = ''

                    # The bowl gets less full
                    # item_cat_food_bowl.energy -= 1
                    if food_dish.energy > 70:
                        food_dish.sprite = food_dish.sprite_sheet['full']
                    elif food_dish.energy > 30:
                        food_dish.sprite = food_dish.sprite_sheet['mid']
                    else:
                        food_dish.sprite = food_dish.sprite_sheet['empty']
            else:
                self.task = ''

        # --- DRINK ---
        if self.task == 'drink':
            self.is_moving = False
            # Check if there is a water bowl nearby
            b = False
            water_dish = ''
            for item in NPC.cat_drink:
                if self.check_collision(item, proximity=40):
                    b = True
                    water_dish = item
            if b:
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
            b = False
            litter_box = ''
            for item in NPC.litter_boxes:
                if self.check_collision(item, proximity=40):
                    b = True
                    litter_box = item
            if b:
                # Pee
                self.pee -= 1
                if self.pee < 0:
                    self.pee = 0

                # Poop
                self.poop -= 1
                if self.poop < 0:
                    self.poop = 0

                # Stop using the litter box when done
                if self.pee <= 0 and self.poop <= 0:
                    self.task = ''
            else:
                self.task = ''

        # --- PLAY ---
        if self.task == 'play':
            self.is_moving = False
            # Check if there is a toy nearby
            if any(self.check_collision(item, proximity=40) for item in NPC.cat_toys):
                # Play
                self.happiness += 1

                # Stop playing when happy
                if self.happiness >= 100:
                    self.task = ''
            else:
                self.task = ''

        # --- SLEEP ---
        if self.task == 'sleep':
            self.is_moving = False
            # Check if there is a bed nearby
            b = False
            cat_bed = ''
            for item in NPC.cat_beds:
                if self.check_collision(item, proximity=40):
                    b = True
                    cat_bed = item
            if b:
                # Sleep
                self.energy += 0.5

                # Stop sleeping when full of energy
                if self.energy >= 100:
                    self.task = ''
            else:
                self.task = ''

        # --- FIND-LITTER-BOX ---
        if self.task == 'find-litter-box':
            new_task = 'bathroom'

            target = random.choice(NPC.litter_boxes)

            if self.check_collision(target, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = Pathing.pixel_to_grid(self.collision_center())

                # Get the end position
                litter_box_position = Pathing.pixel_to_grid(target.collision_center())

                # Find a path to the cat litter box
                self.path = Pathing.astar(grid, cat_position, litter_box_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-TOY ---
        if self.task == 'find-toy':
            new_task = 'play'
            target = random.choice(NPC.cat_toys)
            if self.check_collision(target, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = Pathing.pixel_to_grid(self.collision_center())

                # Get the end position
                toy_position = Pathing.pixel_to_grid(target.collision_center())

                # Find a path to the cat toy
                self.path = Pathing.astar(grid, cat_position, toy_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-SLEEP ---
        if self.task == 'find-sleep':
            new_task = 'sleep'

            target = random.choice(NPC.cat_beds)

            if self.check_collision(target, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = Pathing.pixel_to_grid(self.collision_center())

                # Get the end position
                bed_position = Pathing.pixel_to_grid(target.collision_center())

                # Find a path to the cat toy
                self.path = Pathing.astar(grid, cat_position, bed_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-FOOD ---
        if self.task == 'find-food':
            new_task = 'eat'
            target = random.choice(NPC.cat_food)
            if self.check_collision(target, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = Pathing.pixel_to_grid(self.collision_center())

                # Get the end position
                food_position = Pathing.pixel_to_grid(target.collision_center())

                # Find a path to the cat food bowl
                self.path = Pathing.astar(grid, cat_position, food_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- FIND-WATER ---
        if self.task == 'find-water':
            new_task = 'drink'
            target = random.choice(NPC.cat_drink)
            if self.check_collision(target, proximity=40):
                self.task = new_task
            else:
                # Get start and end positions
                cat_position = Pathing.pixel_to_grid(self.collision_center())

                # Get the end position
                water_position = Pathing.pixel_to_grid(target.collision_center())

                # Find a path to the cat food bowl
                self.path = Pathing.astar(grid, cat_position, water_position)

                # Move towards the next step
                self.move_along_path(cat_position, new_task=new_task)

        # --- EXPLORE ---
        if self.task == 'explore':
            # Get start and end positions
            cat_position = Pathing.pixel_to_grid(self.collision_center())

            # Find a new path if not currently exploring
            if not self.currently_exploring:
                self.path = None
                while self.path is None:

                    # Get the end position
                    end_position = random.randint(0, Pathing.grid_width - 1), random.randint(0, Pathing.grid_height - 1)

                    # Find a path to the end_position if it's possible to this end position
                    if Pathing.is_path_possible(grid, cat_position, end_position):
                        self.path = Pathing.astar(grid, cat_position, end_position)

                # The NPC is now exploring
                self.currently_exploring = True
                self.destination = end_position
            else:
                # Update the path to the end_position
                self.path = Pathing.astar(grid, cat_position, self.destination)

            # Move towards the next step
            if not self.move_along_path(cat_position, new_task=''):
                self.currently_exploring = False

        # explore if nothing else is a priority
        if self.task == '' and (
                self.time_since_last_activity_change) >= self.new_activity_every_x_seconds:
            self.time_since_last_activity_change = 0
            self.task = 'explore'

    def move_along_path(self, curr_pos, new_task=''):
        if self.path is not None:
            if len(self.path) > 1:
                next_step = self.path[1]

                # DEBUG
                # print(f'curr_pos:{curr_pos} next_step:{next_step} self.path:{self.path}')

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
