import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display\
map_width, map_height = 8000, 6000
screen_width, screen_height = 800, 600
# center = (400, 300)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Circle Follows Cursor')

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 50, 0, 10)

# Helpers
def get_distance(x1, y1, x2, y2):
    return math.sqrt((x2- x1)**2 + (y2- y1)**2)

def get_angle(x1, y1, x2, y2):
   
    # Calculate the angle in radians
    angle_radians = math.atan2(y2 - y1, x2 - x1)

    return angle_radians

def sign( x_1, y_1, x_2, y_2, x_3, y_3):
    return (x_1 - x_3) * (y_2 - y_3) - (x_2 - x_3) * (y_1 - y_3)

def in_triangle(x_c, y_c, x_1, y_1, x_2, y_2, x_3, y_3):
    d1 = sign(x_c, y_c, x_1, y_1, x_2, y_2)
    d2 = sign(x_c, y_c, x_2, y_2, x_3, y_3)
    d3 = sign(x_c, y_c, x_3, y_3, x_1, y_1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)

def snap_pos(x, max_x):
    return min(max_x, max(x,0))

class Cat():
    def __init__(self):
        self.radius = 20
        self.pos = 50, 50
        self.vel = 100
        self.angle = 0
        self.ang_vel = 0
        self.spread = 45
        self.range = 400
        self.fov = self.get_fov()
        self.walk_state = -1
        self.counter = 0
        self.fovcolor = GREEN
        original_image1 = pygame.image.load('sprite_1.png')
        original_image2 = pygame.image.load('sprite_2.png')
        original_image3 = pygame.image.load('sprite_3.png')
        scale_factor = 2.0
        self.images = []
        new_size = (int(original_image1.get_width() * scale_factor), int(original_image1.get_height() * scale_factor))
        self.images.append(pygame.transform.scale(original_image1, new_size))
        new_size = (int(original_image2.get_width() * scale_factor), int(original_image2.get_height() * scale_factor))
        self.images.append(pygame.transform.scale(original_image2, new_size))
        new_size = (int(original_image3.get_width() * scale_factor), int(original_image3.get_height() * scale_factor))
        self.images.append(pygame.transform.scale(original_image3, new_size))
        self.image = self.images[1]
        self.image_rect = self.image.get_rect()

    def get_fov(self):
        x1, y1 = self.range * math.cos(self.angle + math.radians(self.spread)), self.range * math.sin(self.angle + math.radians(self.spread))
        x2, y2 = self.range * math.cos(self.angle - math.radians(self.spread)), self.range * math.sin(self.angle - math.radians(self.spread))
        anchor_x, anchor_y = self.pos[0] - self.radius * math.cos(self.angle), self.pos[1] - self.radius * math.sin(self.angle)
        return (anchor_x, anchor_y, anchor_x + x1, anchor_y + y1, anchor_x + x2, anchor_y + y2)
   
    def check_fov(self, point):
        x_1, y_1, x_2, y_2, x_3, y_3 = self.fov
        midx, midy = (x_2 + x_3)/2, (y_2 + y_3)/2
        upper = in_triangle(point[0], point[1], x_1, y_1, x_2, y_2, midx, midy)
        lower = in_triangle(point[0], point[1], x_1, y_1, midx, midy, x_3, y_3)
        return upper or lower, upper - lower
   
    def update_velocity(self, rot):
        self.ang_vel = 0.5 * (rot) + 0.5 * (self.ang_vel)

    def update_fov(self):
        self.fov = self.get_fov()

    def update_pos(self):
        self.angle += 0.05 * self.ang_vel
        pos_x = 0.01 * self.vel * math.cos(self.angle) + self.pos[0]
        pos_y = 0.01 * self.vel * math.sin(self.angle) + self.pos[1]
        pos_x = snap_pos(pos_x, map_width)
        pos_y = snap_pos(pos_y, map_height)
        self.pos = (pos_x, pos_y)
   
    def update_walk(self):
        self.counter +=1
        if self.counter >= 5:
            self.walk_state = (self.walk_state + 1)%2
            self.counter = 0
   
    def draw_cat(self):
        pos_x, pos_y = self.pos
        if current_anchor[0] <= pos_x < current_anchor[0] + screen_width and  current_anchor[1] <= pos_y < current_anchor[1] + screen_height:
            pos_x , pos_y = pos_x - current_anchor[0], pos_y - current_anchor[1]
            self.image_rect.center = (pos_x, pos_y)
            if self.walk_state == 0:
                self.image = self.images[0]
            elif self.walk_state == 1:
                self.image = self.images[2]
            else:
                self.image = self.images[1]
            self.image = pygame.transform.rotate(self.image, 90 -math.degrees(self.angle))
            screen.blit(self.image, self.image_rect)
            #pygame.draw.polygon(screen, self.fovcolor, ((self.fov[0] - current_anchor[0], self.fov[1] - current_anchor[1]), (self.fov[2] - current_anchor[0] , self.fov[3] - current_anchor[1]), (self.fov[4] - current_anchor[0], self.fov[5] - current_anchor[1])))

def update_cats(cats, mouse_x, mouse_y):
    mouse_x , mouse_y = mouse_x + current_anchor[0], mouse_y + current_anchor[1]
    for i in range(len(cats)):
        cats[i].update_walk()
        in_fov, rot = cats[i].check_fov((mouse_x, mouse_y))
        if not in_fov:
            # dist = get_distance(*cats[i].pos, mouse_x, mouse_y)
            # rot = dist/max_dist * + (2* random.random() - 1)
            rot = 2* random.random() - 1
        cats[i].update_fov()
        cats[i].update_velocity(rot)
        cats[i].update_pos()

def draw_cats(cats):
    for i in range(len(cats)):
        cats[i].draw_cat()

cats = []
for i in range(1):
    cats.append(Cat())
# Circle properties
pointer_radius = 2
mouse_x, mouse_y = 0, 0

current_anchor = (0,0)

max_dist = get_distance(800, 600, 400, 300)
panx = 0
pany = 0

# Main game loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                panx = -10
            elif event.key == pygame.K_RIGHT:
                panx = 10
            if event.key == pygame.K_UP:
                pany = -10
            elif event.key == pygame.K_DOWN:
                pany = 10
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                panx = 0
            if event.key == pygame.K_RIGHT:
                panx = 0
            if event.key == pygame.K_UP:
                pany = 0
            if event.key == pygame.K_DOWN:
                pany = 0

    current_anchor = (snap_pos(panx + current_anchor[0], map_width), snap_pos(pany + current_anchor[1], map_height))
    update_cats(cats, mouse_x, mouse_y)
    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Fill the screen with white color
    screen.fill(WHITE)

    # Create 'cat'
    # pygame.draw.polygon(screen, GREEN, ((fov_x1, fov_y1), (fov_x2 , fov_y2), (fov_x3, fov_y3)))
    # pygame.draw.circle(screen, BLUE, (pos_x, pos_y), cat_radius)
    # Draw the circle at the mouse position
    draw_cats(cats)
    pygame.draw.circle(screen, RED, (mouse_x, mouse_y), pointer_radius)
   
    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()