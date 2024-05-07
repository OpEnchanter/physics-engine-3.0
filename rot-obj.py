import pygame
import math

pygame.init()
win = pygame.display.set_mode([500,500])

obj_matrix = []
obj_matrix.append([[-10, -10],[10, -10]])
obj_matrix.append([[10, 10],[-10, 10]])

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    win.fill((255, 255, 255))

    winX, winY = win.get_size()

    V1 = (obj_matrix[0][0][0] + winX/2, obj_matrix[0][0][1] + winY/2)
    V2 = (obj_matrix[0][1][0] + winX/2, obj_matrix[0][1][1] + winY/2)
    V3 = (obj_matrix[1][0][0] + winX/2, obj_matrix[1][0][1] + winY/2)
    V4 = (obj_matrix[1][1][0] + winX/2, obj_matrix[1][1][1] + winY/2)

    pygame.draw.polygon(win, (0,0,0), [V1, V2, V3, V4], 1)

    pygame.display.flip()

pygame.quit()