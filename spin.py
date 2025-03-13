import os
import sys
import time
import math

if not len(sys.argv) == 2:
    print(f"Usage: python {sys.argv[0]} <obj_file>")
    sys.exit(1)

# Get terminal size
size = os.get_terminal_size()
WIDTH = size.columns
HEIGHT = size.lines

# Set realism factor (higher = smoother animation) and speed
realisme = 100
speed = 10

# Load .obj file and extract vertices and edges
def load_obj(filename):
    vertices = []
    edges = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == "v":
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))
            elif parts[0] == "f":
                indices = [int(i.split("/")[0]) - 1 for i in parts[1:]]
                for i in range(len(indices)):
                    edges.append((indices[i], indices[(i + 1) % len(indices)]))
    return vertices, edges

# Auto-scale object to fit the terminal with an extra resize factor
def auto_scale(vertices, resize_factor):
    min_x = min(v[0] for v in vertices)
    max_x = max(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_y = max(v[1] for v in vertices)
    min_z = min(v[2] for v in vertices)
    max_z = max(v[2] for v in vertices)

    scale_x = (WIDTH // 4) / (max_x - min_x) if max_x - min_x != 0 else 1
    scale_y = (HEIGHT // 4) / (max_y - min_y) if max_y - min_y != 0 else 1
    scale_z = 10 / (max_z - min_z) if max_z - min_z != 0 else 1

    scale = min(scale_x, scale_y, scale_z) * 0.8  # scale down to fit comfortably
    scale *= resize_factor  # apply additional resizing
    return [(x * scale, y * scale, z * scale) for x, y, z in vertices]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Draw a line using Bresenham’s algorithm
def draw_line(screen, x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        if 0 <= x1 < WIDTH and 0 <= y1 < HEIGHT:
            screen[y1][x1] = "#"
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# Rotate vertices around X, Y, and Z axes (in that order)
def rotate(vertices, x_rot, y_rot, z_rot):
    cos_x = math.cos(math.radians(x_rot))
    sin_x = math.sin(math.radians(x_rot))
    cos_y = math.cos(math.radians(y_rot))
    sin_y = math.sin(math.radians(y_rot))
    cos_z = math.cos(math.radians(z_rot))
    sin_z = math.sin(math.radians(z_rot))

    rotated_vertices = []
    for x, y, z in vertices:
        # Rotation around X-axis
        x1 = x
        y1 = y * cos_x - z * sin_x
        z1 = y * sin_x + z * cos_x

        # Rotation around Y-axis
        x2 = x1 * cos_y + z1 * sin_y
        y2 = y1
        z2 = -x1 * sin_y + z1 * cos_y

        # Rotation around Z-axis
        x3 = x2 * cos_z - y2 * sin_z
        y3 = x2 * sin_z + y2 * cos_z
        z3 = z2

        rotated_vertices.append((x3, y3, z3))
    return rotated_vertices

# Project and draw the 3D object on the terminal
def draw_object(vertices, edges, x_rot, y_rot, z_rot):
    rotated = rotate(vertices, x_rot, y_rot, z_rot)
    projected = []
    for x, y, z in rotated:
        factor = 10 / (z + 10)  # Depth scaling
        proj_x = int(x * factor * 15) + WIDTH // 2
        proj_y = int(y * factor * 10) + HEIGHT // 2
        projected.append((proj_x, proj_y))
    screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for start, end in edges:
        draw_line(screen, projected[start][0], projected[start][1],
                  projected[end][0], projected[end][1])
    clear_screen()
    for row in screen:
        print("".join(row))

# Load object and scale it
filename = sys.argv[1]  # Change to your .obj filename
vertices, edges = load_obj(filename)

# Variable for resizing: Adjust this value to change overall object size
resize_factor = 1  # Set to values less than 1.0 to shrink, greater than 1.0 to enlarge

vertices = auto_scale(vertices, resize_factor)

# Base (fixed) rotation values for axes
base_x_rot = 90
base_y_rot = 0
base_z_rot = 0

# Set which axis will be animated: choose "x", "y", "z", or "none"
animate_axis = "z"

angle = 0
while True:
    effective_x = base_x_rot + (angle if animate_axis == "x" else 0)
    effective_y = base_y_rot + (angle if animate_axis == "y" else 0)
    effective_z = base_z_rot + (angle if animate_axis == "z" else 0)
    draw_object(vertices, edges, effective_x, effective_y, effective_z)
    angle += 50 / realisme
    time.sleep(1 / realisme / (speed - 1))
