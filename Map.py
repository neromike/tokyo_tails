import Pathing

loc_to_grid = {
    "house": []
}

loc_to_colliders = {
    "house": [[], [], []]
}

def update_grid(background, obsticles, loc):
    loc_to_grid[loc] = Pathing.mark_obstacles_on_grid(background,obsticles)

# Note colliders is a list of lists where the first list is items the secound is room and third is exits
def update_colliders(colliders, loc):
    loc_to_colliders[loc] = colliders