import heapq
import time

import pygame


# Note we seem to be reinitializing the grid more often than necessary.


# GRID
GRID_CELL_SIZE = 50  # Size of each grid cell in pixels
grid_width = grid_height = 0


def initialize_grid(background_layer):
    global grid_width, grid_height
    # Get the dimensions of the background image
    background_width, background_height = background_layer.get_size()

    # Calculate the number of grid cells in each dimension
    grid_width = background_width // GRID_CELL_SIZE
    grid_height = background_height // GRID_CELL_SIZE

    # Create a 2D array with all cells set to passable (False)
    return [[False for _ in range(grid_width)] for _ in range(grid_height)]


def mark_obstacles_on_grid(background_layer, obstacles):
    # Reset the grid
    grid = initialize_grid(background_layer)

    # Now mark the impassable cells
    for obstacle in obstacles:

        if obstacle is not None and obstacle.collide_rect is not None:
            top_left_cell = (obstacle.collide_rect.left // GRID_CELL_SIZE, obstacle.collide_rect.top // GRID_CELL_SIZE)
            bottom_right_cell = (
            obstacle.collide_rect.right // GRID_CELL_SIZE, obstacle.collide_rect.bottom // GRID_CELL_SIZE)

            for x in range(top_left_cell[0], bottom_right_cell[0] + 1):
                for y in range(top_left_cell[1], bottom_right_cell[1] + 1):
                    if 0 <= x < grid_width and 0 <= y < grid_height:
                        grid[y][x] = True  # Mark cell as impassable
    return grid


def draw_grid(screen, grid, camera_offset, passable_color=(0, 255, 0), impassable_color=(255, 0, 0)):
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


def print_grid(grid, start=None, end=None, marked_positions=None):
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
                row_string += 'o  '  # Marked
            else:
                row_string += 'X  ' if cell else '.  '  # Obstacle or Empty
        print(row_string)


def initialize_connectivity_grid():
    connectivity_grid = [[[] for _ in range(grid_width)] for _ in range(grid_height)]
    return connectivity_grid


def populate_connectivity_grid(grid):
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


def is_path_possible(grid, start, end):
    connectivity_grid = populate_connectivity_grid(grid)
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

    def __lt__(self, other):
        return self.f < other.f

    def __gt__(self, other):
        return self.f > other.f

    def __hash__(self):
        return hash(self.position)


astar_times = []


def astar(grid, start, end):
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
    closed_list = set()

    # Add the start node
    heapq.heappush(open_list, (start_node.f, start_node))

    # Loop until you find the end
    while len(open_list) > 0:
        # Get the current node
        current_node = heapq.heappop(open_list)[1]

        # Skip processing if this node is outdated
        if current_node in closed_list:
            continue

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            timer_end = time.time()
            astar_times.append(timer_end - timer_start)
            return path[::-1]  # Return reversed path

        closed_list.add(current_node)

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[1] > (len(grid) - 1) or node_position[1] < 0 or node_position[0] > (
                    len(grid[len(grid) - 1]) - 1) or node_position[0] < 0:
                continue

            # Make sure walkable terrain, ignore any obstacles at our current position and the end position
            if grid[node_position[1]][
                node_position[0]] and node_position != end and node_position != current_node.position:
                continue

            # Make sure we don't cut corners
            if new_position == (-1, -1) or new_position == (-1, 1) or new_position == (1, -1) or new_position == (1, 1):
                if grid[current_node.position[1] + new_position[1]][current_node.position[0]] or \
                        grid[current_node.position[1]][current_node.position[0] + new_position[0]]:
                    continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            # Skip if child is in the closed list
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                        (child.position[1] - end_node.position[1]) ** 2)  # Squared Euclidean
            # child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])    #Manhattan
            child.f = child.g + child.h

            # Add to open list without updating existing entries (Lazy Updating)
            heapq.heappush(open_list, (child.f, child))
