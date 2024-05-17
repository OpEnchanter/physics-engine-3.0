import pygame
import math

def rotate_point(point, angle):
    """Rotate a point (x, y) by a given angle (in radians)"""
    x, y = point[0], point[1]
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    new_x = x * cos_theta - y * sin_theta
    new_y = x * sin_theta + y * cos_theta
    return [new_x, new_y]

pygame.init()
win = pygame.display.set_mode([500,500])

obj_matrix = [
    [-10, -10],
    [10, -10],
    [10, 10],
    [-10, 10]
]

rad_angle = math.radians(45)

for pt in obj_matrix:
        obj_matrix[obj_matrix.index(pt)] = rotate_point(obj_matrix[obj_matrix.index(pt)], rad_angle)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    rad_angle += math.radians(15)

    win.fill((255, 255, 255))

    winX, winY = win.get_size()

    V1 = (obj_matrix[0][0] + winX/2, obj_matrix[0][1] + winY/2)
    V2 = (obj_matrix[1][0] + winX/2, obj_matrix[1][1] + winY/2)
    V3 = (obj_matrix[2][0] + winX/2, obj_matrix[2][1] + winY/2)
    V4 = (obj_matrix[3][0] + winX/2, obj_matrix[3][1] + winY/2)

    pygame.draw.polygon(win, (0,0,0), [V1, V2, V3, V4], 0)

    pygame.display.flip()




pygame.quit()