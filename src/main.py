import pygame
import numpy as np
from math import *

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (30, 31, 34)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (237,118,14)

WIDTH, HEIGHT = 800, 600

pygame.display.set_caption("Fantazirum Engine v1")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_icon(pygame.image.load("icon.ico"))


scale = 100
colorSelect = 0
colorDone = WHITE

circle_pos = [WIDTH/2, HEIGHT/2]  # x, y

angleX = 0.5
angleY = 0.5

FPS = 60
Speed = 0.01

points = []

point_x = []
point_y = []



# all the cube vertices

points.append(np.matrix([-1, -1, 1]))
points.append(np.matrix([1, -1, 1]))
points.append(np.matrix([1,  1, 1]))
points.append(np.matrix([-1, 1, 1]))
points.append(np.matrix([-1, -1, -1]))
points.append(np.matrix([1, -1, -1]))
points.append(np.matrix([1, 1, -1]))
points.append(np.matrix([-1, 1, -1]))

#points.append(np.matrix([-1, -1, -1]))
#points.append(np.matrix([1, -1, -1]))
#points.append(np.matrix([1, -1, 1]))
#points.append(np.matrix([-1, -1, 1]))
#points.append(np.matrix([0, 1, 0]))

projection_matrix = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])


projected_points = [
    [n, n] for n in range(len(points))
]


def connect_points(first_point_number, second_point_number, points):
    if colorSelect == 0: colorDone = WHITE
    if colorSelect == 1: colorDone = RED
    if colorSelect == 2: colorDone = GREEN
    if colorSelect == 3: colorDone = BLUE
    if colorSelect == 4: colorDone = ORANGE
    if colorSelect == 5: colorDone = BLACK
    #pygame.draw.polygon(screen, RED,[[point_x[0], point_y[0]], [point_x[1], point_y[1]], [point_x[2], point_y[2]], [point_x[3], point_y[3]]])
    #pygame.draw.polygon(screen, GREEN,[[point_x[0], point_y[0]], [point_x[1], point_y[1]], [point_x[4], point_y[4]], [point_x[4], point_y[4]]])
    #pygame.draw.polygon(screen, BLUE,[[point_x[1], point_y[1]], [point_x[2], point_y[2]], [point_x[4], point_y[4]], [point_x[4], point_y[4]]])
    #pygame.draw.polygon(screen, WHITE, [[point_x[2],point_y[2]], [point_x[3], point_y[3]], [point_x[4], point_y[4]],[point_x[4], point_y[4]]])
    #pygame.draw.polygon(screen, ORANGE,[[point_x[3], point_y[3]], [point_x[0], point_y[0]], [point_x[4], point_y[4]], [point_x[4], point_y[4]]])
    #pygame.draw.polygon(screen, BLACK, [[point_x[5], point_y[5]], [point_x[6], point_y[6]], [point_x[2], point_y[2]],[point_x[1], point_y[1]]])
    pygame.draw.aaline(screen, colorDone, (points[first_point_number][0], points[first_point_number][1]), (points[second_point_number][0], points[second_point_number][1]))  # Линии

clock = pygame.time.Clock()

# Главный цикл

while True:

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                colorSelect += 1
            if colorSelect > 5: colorSelect = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                scale += 1
            if event.button == 5:
                scale -= 1
            if scale < 0 : scale = 0
            if scale > 190: scale = 190

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        angleY += Speed
    if keys[pygame.K_d]:
        angleY -= Speed
    if keys[pygame.K_w]:
        angleX += Speed
    if keys[pygame.K_s]:
        angleX -= Speed

    # Отрисовка поворотов

    rotation_y = np.matrix([
        [cos(angleY), 0, sin(angleY)],
        [0, 1, 0],
        [-sin(angleY), 0, cos(angleY)],
    ])

    rotation_x = np.matrix([
        [1, 0, 0],
        [0, cos(angleX), -sin(angleX)],
        [0, sin(angleX), cos(angleX)],
    ])

    screen.fill(GRAY) # Цвет фона

    first_point_number = 0                                  # Отрисовка

    point_x = [8] * 8
    point_y = [8] * 8
    i = 0

    for point in points:
        rotated2d = np.dot(rotation_y, point.reshape((3, 1)))
        rotated2d = np.dot(rotation_x, rotated2d)

        projected2d = np.dot(projection_matrix, rotated2d)

        x = int(projected2d[0][0] * scale) + circle_pos[0]
        y = int(projected2d[1][0] * scale) + circle_pos[1]


        projected_points[first_point_number] = [x, y]
        pygame.draw.circle(screen, RED, (x, y), 4) # Точки
        first_point_number += 1

        point_x[i] = x
        point_y[i] = y
        i += 1

    for p in range(4):
        connect_points(p, (p + 1) % 4, projected_points)
        connect_points(p + 4, ((p + 1) % 4) + 4, projected_points)
        connect_points(p, (p + 4), projected_points)

    #connect_points(0, 1, projected_points)
    #connect_points(1, 2, projected_points)
    #connect_points(2, 3, projected_points)
    #connect_points(3, 0, projected_points)
    #connect_points(0, 4, projected_points)
    #connect_points(1, 4, projected_points)
    #connect_points(2, 4, projected_points)
    #connect_points(3, 4, projected_points)

    #print(point_x[0])
    #print(point_y[0])
    #print(point_x[1])
    #print(point_y[1])
    #print(point_x[6])
    #print(point_y[6])
    print(point_x)
    print(point_y)
    pygame.display.update()                                     # Обновление

#(300, 200), (500, 200) горизонталь
#(300, 200), (500, 400 вертикаль

#100 = x (горизонталь)
#100 = y (вертикаль)
