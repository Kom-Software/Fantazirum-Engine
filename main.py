import pygame
from pygame.locals import *
import sys
import math
import numpy as np
import tkinter as tk
from tkinter import colorchooser, ttk

# Инициализация Pygame
pygame.init()

# Настройки окна Pygame
screen_width = 1600
screen_height = 900
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Engine(on development!!!!!)')
pygame.display.set_icon(pygame.image.load('icon.ico'))

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
EDGE_COLOR = (50, 50, 50)  # Цвет рёбер
FACE_COLOR = WHITE  # Белый цвет для граней куба

# Вершины куба
vertices = [
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1]
]

# Грани куба, заданные через индексы вершин
faces = [
    (0, 1, 2, 3),  # front face
    (1, 5, 6, 2),  # right face
    (5, 4, 7, 6),  # back face
    (4, 0, 3, 7),  # left face
    (3, 2, 6, 7),  # top face
    (4, 5, 1, 0)  # bottom face
]

# Текущий материал (цвет)
current_material = WHITE

# Параметры куба (размеры и положение)
cube_params = {
    'scale_x': 1,
    'scale_y': 1,
    'scale_z': 1,
    'pos_x': 0,
    'pos_y': 0,
    'pos_z': 0
}

# Флаг для открытия окна параметров
params_window_open = False


# Функция для вращения вершин куба вокруг осей X, Y, Z
def rotate_vertices(vertices, angle_x, angle_y, angle_z):
    rotation_matrix_x = np.array([
        [1, 0, 0],
        [0, math.cos(angle_x), -math.sin(angle_x)],
        [0, math.sin(angle_x), math.cos(angle_x)]
    ])

    rotation_matrix_y = np.array([
        [math.cos(angle_y), 0, math.sin(angle_y)],
        [0, 1, 0],
        [-math.sin(angle_y), 0, math.cos(angle_y)]
    ])

    rotation_matrix_z = np.array([
        [math.cos(angle_z), -math.sin(angle_z), 0],
        [math.sin(angle_z), math.cos(angle_z), 0],
        [0, 0, 1]
    ])

    rotated_vertices = []
    for vertex in vertices:
        rotated_x = rotation_matrix_x.dot(np.array(vertex))
        rotated_xy = rotation_matrix_y.dot(rotated_x)
        rotated_xyz = rotation_matrix_z.dot(rotated_xy)
        rotated_vertices.append(rotated_xyz)

    return rotated_vertices


# Функция для преобразования трехмерных координат в экранные координаты
def project(vertex):
    scale = 200  # масштаб
    distance = cube_params['distance']  # расстояние до экрана
    if distance == 0:
        return [0, 0]  # Если расстояние равно нулю, возвращаем начало экрана
    x = vertex[0] * scale / (distance - vertex[2])
    y = vertex[1] * scale / (distance - vertex[2])
    return [x + screen_width / 2, y + screen_height / 2]


# Функция для создания градиентного неба
def draw_sky_gradient():
    sky_gradient = pygame.Surface((screen_width, screen_height))
    for y in range(screen_height):
        # Интерполяция цвета для создания градиента
        color = (
            int(135 + (y / screen_height) * (255 - 135)),  # R
            int(206 + (y / screen_height) * (255 - 206)),  # G
            int(235 + (y / screen_height) * (255 - 235))  # B
        )
        pygame.draw.line(sky_gradient, color, (0, y), (screen_width, y))
    screen.blit(sky_gradient, (0, 0))


# Функция для отображения всплывающего окна с подтверждением
def show_confirmation_window():
    font = pygame.font.Font(None, 36)
    text_surface = font.render('Вы уверены, что хотите удалить куб?', True, WHITE)
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))

    button_yes = pygame.Rect(screen_width // 2 - 80, screen_height // 2 + 40, 60, 40)
    button_no = pygame.Rect(screen_width // 2 + 20, screen_height // 2 + 40, 60, 40)

    pygame.draw.rect(screen, WHITE, button_yes)
    pygame.draw.rect(screen, WHITE, button_no)

    font_button = pygame.font.Font(None, 32)
    text_yes = font_button.render('Да', True, BLACK)
    text_no = font_button.render('Нет', True, BLACK)

    screen.blit(text_surface, text_rect)
    screen.blit(text_yes, (button_yes.x + 10, button_yes.y + 10))
    screen.blit(text_no, (button_no.x + 10, button_no.y + 10))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_yes.collidepoint(mouse_pos):
                    return True
                elif button_no.collidepoint(mouse_pos):
                    return False


# Функция для создания материала (цвета)
def create_material():
    global current_material
    color_dialog = colorchooser.askcolor()[0]
    if color_dialog:
        current_material = color_dialog


# Функция для отрисовки куба с текущим материалом
def draw_cube(vertices, angle_x, angle_y, angle_z):
    rotated_vertices = rotate_vertices(vertices, angle_x, angle_y, angle_z)
    scaled_vertices = []
    for vertex in rotated_vertices:
        scaled_vertex = [
            vertex[0] * cube_params['scale_x'],
            vertex[1] * cube_params['scale_y'],
            vertex[2] * cube_params['scale_z']
        ]
        scaled_vertices.append(scaled_vertex)

    translated_vertices = []
    for vertex in scaled_vertices:
        translated_vertex = [
            vertex[0] + cube_params['pos_x'],
            vertex[1] + cube_params['pos_y'],
            vertex[2] + cube_params['pos_z']
        ]
        translated_vertices.append(translated_vertex)

    for face in faces:
        polygon = [project(translated_vertices[vertex_index]) for vertex_index in face]
        pygame.draw.polygon(screen, current_material, polygon)
        # Рисуем рёбра грани (тёмные)
        for i in range(len(polygon)):
            start = polygon[i]
            end = polygon[(i + 1) % len(polygon)]
            pygame.draw.line(screen, EDGE_COLOR, start, end, 1)


# Функция для обновления параметров куба из GUI
def update_cube_params_x(value):
    cube_params['scale_x'] = float(value) / 10


def update_cube_params_y(value):
    cube_params['scale_y'] = float(value) / 10


def update_cube_params_z(value):
    cube_params['scale_z'] = float(value) / 10


def update_cube_pos_x(value):
    cube_params['pos_x'] = int(value)


def update_cube_pos_y(value):
    cube_params['pos_y'] = int(value)


def update_cube_pos_z(value):
    cube_params['pos_z'] = int(value)


# Функция для отображения окна с параметрами куба
def show_cube_params_window():
    global params_window_open
    params_window_open = True

    root = tk.Tk()
    root.title("Параметры куба")

    def on_closing():
        global params_window_open
        params_window_open = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    scale_x_label = ttk.Label(root, text="Масштаб по X")
    scale_x_label.grid(row=0, column=0)
    scale_x_slider = ttk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, command=update_cube_params_x)
    scale_x_slider.grid(row=0, column=1)

    scale_y_label = ttk.Label(root, text="Масштаб по Y")
    scale_y_label.grid(row=1, column=0)
    scale_y_slider = ttk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, command=update_cube_params_y)
    scale_y_slider.grid(row=1, column=1)

    scale_z_label = ttk.Label(root, text="Масштаб по Z")
    scale_z_label.grid(row=2, column=0)
    scale_z_slider = ttk.Scale(root, from_=1, to=200, orient=tk.HORIZONTAL, command=update_cube_params_z)
    scale_z_slider.grid(row=2, column=1)

    pos_x_label = ttk.Label(root, text="Положение по X")
    pos_x_label.grid(row=3, column=0)
    pos_x_slider = ttk.Scale(root, from_=-400, to=400, orient=tk.HORIZONTAL, command=update_cube_pos_x)
    pos_x_slider.grid(row=3, column=1)

    pos_y_label = ttk.Label(root, text="Положение по Y")
    pos_y_label.grid(row=4, column=0)
    pos_y_slider = ttk.Scale(root, from_=-300, to=300, orient=tk.HORIZONTAL, command=update_cube_pos_y)
    pos_y_slider.grid(row=4, column=1)

    pos_z_label = ttk.Label(root, text="Положение по Z")
    pos_z_label.grid(row=5, column=0)
    pos_z_slider = ttk.Scale(root, from_=-200, to=200, orient=tk.HORIZONTAL, command=update_cube_pos_z)
    pos_z_slider.grid(row=5, column=1)

    root.mainloop()


# Основная функция отрисовки и управления
def main():
    clock = pygame.time.Clock()
    angle_x, angle_y, angle_z = 0, 0, 0
    alt_pressed = False
    mouse_pressed = False
    prev_mouse_pos = None
    cube_visible = True
    cube_stack = []  # Стек для хранения состояний видимости куба

    global params_window_open

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LALT or event.key == K_RALT:
                    alt_pressed = True
                elif event.key == K_x:
                    # Отображаем окно подтверждения удаления
                    if cube_visible:
                        if show_confirmation_window():
                            cube_stack.append(cube_visible)  # Сохраняем текущее состояние видимости
                            cube_visible = False
                elif event.key == K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Отменяем последнее действие с помощью Ctrl + Z
                    if cube_stack:
                        cube_visible = cube_stack.pop()
                elif event.key == K_c:
                    # Создание нового материала (цвета)
                    create_material()
                elif event.key == K_RETURN:
                    # Накладывание текущего материала на куб
                    draw_cube(vertices, angle_x, angle_y, angle_z)
                elif event.key == K_o:
                    # Загрузка куба из файла
                    filename = input("Введите имя файла для загрузки куба: ")
                    loaded_vertices = load_cube_from_file(filename)
                    if loaded_vertices is not None:
                        vertices[:] = loaded_vertices
                        cube_visible = True
                elif event.key == K_s:
                    # Сохранение куба в файл
                    filename = input("Введите имя файла для сохранения куба: ")
                    save_cube_to_file(filename, vertices)
                elif event.key == K_p:
                    # Показать окно параметров куба
                    show_cube_params_window()
                elif event.key == K_n:
                    # Показать/скрыть окно параметров куба
                    if not params_window_open:
                        show_cube_params_window()
                    else:
                        root.destroy()
                        params_window_open = False

            elif event.type == KEYUP:
                if event.key == K_LALT or event.key == K_RALT:
                    alt_pressed = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and alt_pressed:  # Левая кнопка мыши при зажатой Alt
                    mouse_pressed = True
                    prev_mouse_pos = pygame.mouse.get_pos()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_pressed = False

        screen.fill(BLACK)

        # Рисуем небо (градиент)
        draw_sky_gradient()

        # Поворот куба с помощью мыши и зажатой клавиши Alt
        if mouse_pressed and alt_pressed:
            current_mouse_pos = pygame.mouse.get_pos()
            if prev_mouse_pos:
                dx = current_mouse_pos[0] - prev_mouse_pos[0]
                dy = current_mouse_pos[1] - prev_mouse_pos[1]
                angle_x += dy * 0.01
                angle_y += dx * 0.01
            prev_mouse_pos = current_mouse_pos

        # Отрисовка куба, если он видим
        if cube_visible:
            draw_cube(vertices, angle_x, angle_y, angle_z)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
