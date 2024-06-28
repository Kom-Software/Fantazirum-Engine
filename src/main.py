import math
import sys
import tkinter as tk
from tkinter import colorchooser, ttk

import numpy as np
import pygame
from pygame.locals import *
from objects import *
from ui import *

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Настройки окна Pygame
screen_width = 1280
screen_height = 720
screen_engine = pygame.display.set_mode(
    (screen_width, screen_height), flags=(pygame.DOUBLEBUF)
)
pygame.display.set_caption("Space Engine")
pygame.display.set_icon(pygame.image.load("icon.ico"))

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
EDGE_COLOR = (50, 50, 50)  # Цвет рёбер
FACE_COLOR = WHITE  # Белый цвет для граней куба

objects = {
    "default_cube": Cube(),
    "default_cube1": Cube(
        cube_params={
            "scale_x": 1,
            "scale_y": 1,
            "scale_z": 0.5,
            "pos_x": 3,
            "pos_y": 1,
            "pos_z": 0,
            "distance": 5,
        }
    ),
}

selected_object = objects["default_cube"]


# Флаг для открытия окна параметров
params_window_open = False

preview_window_open = False

cam_pos_of_cube = []
mode = "main"
music = "none"

# Функция для вращения вершин куба вокруг осей X, Y, Z
def rotate_vertices(vertices, angle_x, angle_y, angle_z):
    rotation_matrix_x = np.array(
        [
            [1, 0, 0],
            [0, math.cos(angle_x), -math.sin(angle_x)],
            [0, math.sin(angle_x), math.cos(angle_x)],
        ]
    )

    rotation_matrix_y = np.array(
        [
            [math.cos(angle_y), 0, math.sin(angle_y)],
            [0, 1, 0],
            [-math.sin(angle_y), 0, math.cos(angle_y)],
        ]
    )

    rotation_matrix_z = np.array(
        [
            [math.cos(angle_z), -math.sin(angle_z), 0],
            [math.sin(angle_z), math.cos(angle_z), 0],
            [0, 0, 1],
        ]
    )

    rotated_vertices = []
    for vertex in vertices:
        rotated_x = rotation_matrix_x.dot(np.array(vertex))
        rotated_xy = rotation_matrix_y.dot(rotated_x)
        rotated_xyz = rotation_matrix_z.dot(rotated_xy)
        rotated_vertices.append(rotated_xyz)

    return rotated_vertices


# Функция для преобразования трехмерных координат в экранные координаты
def project(vertex):
    for cube in objects.values():
        if isinstance(cube, Cube):
            scale = 200  # масштаб
            distance = cube.cube_params["distance"]  # расстояние до экрана
            if distance - vertex[2] == 0:
                distance -= 1
            x = vertex[0] * scale / (distance - vertex[2])
            y = vertex[1] * scale / (distance - vertex[2])
            return [x + screen_width / 2, y + screen_height / 2]
    else:
        pass


# Функция для создания градиентного неба
def draw_sky_gradient():
    sky_gradient = pygame.Surface((screen_width, screen_height))
    for y in range(screen_height):
        # Интерполяция цвета для создания градиента
        color = (
            int(135 + (y / screen_height) * (255 - 135)),  # R
            int(206 + (y / screen_height) * (255 - 206)),  # G
            int(235 + (y / screen_height) * (255 - 235)),  # B
        )
        pygame.draw.line(sky_gradient, color, (0, y), (screen_width, y))
    screen_engine.blit(sky_gradient, (0, 0))


# Функция для отображения всплывающего окна с подтверждением
def show_confirmation_window():
    font = pygame.font.Font(None, 36)
    text_surface = font.render("Вы уверены, что хотите удалить куб?", True, WHITE)
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))

    button_yes = pygame.Rect(screen_width // 2 - 80, screen_height // 2 + 40, 60, 40)
    button_no = pygame.Rect(screen_width // 2 + 20, screen_height // 2 + 40, 60, 40)

    pygame.draw.rect(screen_engine, WHITE, button_yes)
    pygame.draw.rect(screen_engine, WHITE, button_no)

    font_button = pygame.font.Font(None, 32)
    text_yes = font_button.render("Да", True, BLACK)
    text_no = font_button.render("Нет", True, BLACK)

    screen_engine.blit(text_surface, text_rect)
    screen_engine.blit(text_yes, (button_yes.x + 10, button_yes.y + 10))
    screen_engine.blit(text_no, (button_no.x + 10, button_no.y + 10))

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


global polygon


# Функция для отрисовки куба с текущим материалом
def draw_cube(vertices, angle_x, angle_y, angle_z):
    global polygon
    for cube in objects.values():
        if isinstance(cube, Cube):
            rotated_vertices = rotate_vertices(vertices, angle_x, angle_y, angle_z)
            scaled_vertices = []
            for vertex in rotated_vertices:
                scaled_vertex = [
                    vertex[0] * cube.cube_params["scale_x"],
                    vertex[1] * cube.cube_params["scale_y"],
                    vertex[2] * cube.cube_params["scale_z"],
                ]
                scaled_vertices.append(scaled_vertex)

            translated_vertices = []
            for vertex in scaled_vertices:
                cam_pos_of_cube = [
                    cube.cube_params["pos_x"] - camera_pos[0],
                    cube.cube_params["pos_y"] - camera_pos[1],
                    cube.cube_params["pos_z"] - camera_pos[2],
                ]
                translated_vertex = [
                    vertex[0] + cam_pos_of_cube[0],
                    vertex[1] + cam_pos_of_cube[1],
                    vertex[2] + cam_pos_of_cube[2],
                ]

                translated_vertices.append(translated_vertex)

            # Отсортируем грани куба по их дальности от камеры (по Z координате центра грани)
            sorted_faces = sorted(
                selected_object.faces,
                key=lambda face: np.mean([translated_vertices[idx][2] for idx in face]),
                reverse=True,
            )

            for face in sorted_faces:
                # Найдём центр грани
                face_center = np.mean(
                    [translated_vertices[idx] for idx in face], axis=0
                )

                # Вектор от камеры к центру грани
                ray_direction = np.array(face_center) - np.array(
                    [0, 0, cube.cube_params["distance"]]
                )
                ray_direction /= np.linalg.norm(ray_direction)  # Нормализуем вектор

                # Вектор от камеры к вершине грани (первой вершине в face)
                ray_origin = np.array([0, 0, cube.cube_params["distance"]])
                face_vertex = translated_vertices[face[0]]
                ray_to_vertex = np.array(face_vertex) - ray_origin

                # Проверка на видимость грани
                cosine_angle = np.dot(ray_to_vertex, ray_direction)
                if cosine_angle <= 0:
                    continue  # Грань не видна (луч направлен в противоположную сторону или перпендикулярен)
                global polygon
                polygon = [
                    project(translated_vertices[vertex_index]) for vertex_index in face
                ]
                print(polygon)
                pygame.draw.polygon(screen_engine, cube.current_material, polygon)
                # Рисуем рёбра грани (тёмные)
                for i in range(len(polygon)):
                    start = polygon[i]
                    end = polygon[(i + 1) % len(polygon)]
                    pygame.draw.line(screen_engine, EDGE_COLOR, start, end, 1)


# Функция для обновления параметров куба из GUI
def update_cube_params_x(value):
    selected_object.cube_params["scale_x"] = float(value) / 10


def update_cube_params_y(value):
    selected_object.cube_params["scale_y"] = float(value) / 10


def update_cube_params_z(value):
    selected_object.cube_params["scale_z"] = float(value) / 10


def update_cube_pos_x(value):
    selected_object.cube_params["pos_x"] = float(value)


def update_cube_pos_y(value):
    selected_object.cube_params["pos_y"] = float(value)


def update_cube_pos_z(value):
    selected_object.cube_params["pos_z"] = float(value)


# Функция для обновления положения камеры
global camera_pos
camera_pos = [0, 0, 0]


# Функция для обновления положения камеры при нажатии стрелок
def move_camera(direction):
    global camera_pos
    camera_pos = update_camera_position(camera_pos + direction)


def update_camera_position(camera_pos):
    for cube in objects.values():
        if isinstance(cube, Cube):
            cam_pos_of_cube = [
                cube.cube_params["pos_x"] - camera_pos[0],
                cube.cube_params["pos_y"] - camera_pos[1],
                cube.cube_params["pos_z"] - camera_pos[2],
            ]


def increase_distance():
    for cube in objects.values():
        if isinstance(cube, Cube):
            cube.cube_params["distance"] -= 0.5


def decrease_distance():
    for cube in objects.values():
        if isinstance(cube, Cube):
            cube.cube_params["distance"] += 0.5


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

    scale_x_label = ttk.Label(root, text="Масштаб X")
    scale_x_label.pack()
    scale_x_scale = ttk.Scale(
        root, from_=1, to=20, orient=tk.HORIZONTAL, command=update_cube_params_x
    )
    scale_x_scale.set(selected_object.cube_params["scale_x"] * 10)
    scale_x_scale.pack()

    scale_y_label = ttk.Label(root, text="Масштаб Y")
    scale_y_label.pack()
    scale_y_scale = ttk.Scale(
        root, from_=1, to=20, orient=tk.HORIZONTAL, command=update_cube_params_y
    )
    scale_y_scale.set(selected_object.cube_params["scale_y"] * 10)
    scale_y_scale.pack()

    scale_z_label = ttk.Label(root, text="Масштаб Z")
    scale_z_label.pack()
    scale_z_scale = ttk.Scale(
        root, from_=1, to=20, orient=tk.HORIZONTAL, command=update_cube_params_z
    )
    scale_z_scale.set(selected_object.cube_params["scale_z"] * 10)
    scale_z_scale.pack()

    pos_x_label = ttk.Label(root, text="Позиция X")
    pos_x_label.pack()
    pos_x_scale = ttk.Scale(
        root, from_=-200, to=200, orient=tk.HORIZONTAL, command=update_cube_pos_x
    )
    pos_x_scale.set(selected_object.cube_params["pos_x"])
    pos_x_scale.pack()

    pos_y_label = ttk.Label(root, text="Позиция Y")
    pos_y_label.pack()
    pos_y_scale = ttk.Scale(
        root, from_=-200, to=200, orient=tk.HORIZONTAL, command=update_cube_pos_y
    )
    pos_y_scale.set(selected_object.cube_params["pos_y"])
    pos_y_scale.pack()

    pos_z_label = ttk.Label(root, text="Позиция Z")
    pos_z_label.pack()
    pos_z_scale = ttk.Scale(
        root, from_=-200, to=200, orient=tk.HORIZONTAL, command=update_cube_pos_z
    )
    pos_z_scale.set(selected_object.cube_params["pos_z"])
    pos_z_scale.pack()

    root.mainloop()


global polygon


def mouse_choose_check_cube():
    can_choose_mouse: bool
    can_choose_mouse = True
    global polygon
    global mouse_pressed
    start = polygon[0]
    if current_mouse_pos[0] <= start[0]:
        can_choose_mouse = False
    if current_mouse_pos[1] <= start[1]:
        can_choose_mouse = False

    start = polygon[1]
    if current_mouse_pos[0] >= start[0]:
        can_choose_mouse = False
    start = polygon[3]
    if current_mouse_pos[1] >= start[1]:
        can_choose_mouse = False

    if current_mouse_pos <= polygon[0]:
        can_choose_mouse = False
    if current_mouse_pos >= polygon[1]:
        can_choose_mouse = False
    global current_material
    if can_choose_mouse == True:
        # print("в зоне нажатия")
        if mouse_pressed:
            current_material = BLUE
    if can_choose_mouse == False:
        current_material = WHITE


# Основная функция отрисовки и управления
def main():
    clock = pygame.time.Clock()
    angle_x, angle_y, angle_z = 0, 0, 0
    alt_pressed = False
    global mouse_pressed
    mouse_pressed = False
    prev_mouse_pos = None
    cube_visible = True
    cube_stack = []  # Стек для хранения состояний видимости куба

    global params_window_open
    global cube_params
    global fullscreen
    global preview_window_open
    play_button = Play()
    stop_button = Stop()

    start_button = pygame.Rect(20, 20, 120, 50)
    start_button_text = pygame.font.Font(None, 36).render("Start/Stop", True, WHITE)
    start_button_text_rect = start_button_text.get_rect(center=start_button.center)

    global current_mouse_pos
    pygame.draw.rect(screen_engine, pygame.Color("gray"), (0, 0, 1280, 32))
    if preview_window_open == False:
        screen_engine.blit(play_button.image, (1248, 0))
        play_button.update()
    else:
        screen_engine.blit(stop_button.image, (1248, 0))
        stop_button.update()
    while True:
        print(selected_object)
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
                            cube_stack.append(
                                cube_visible
                            )  # Сохраняем текущее состояние видимости
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
                    draw_cube(selected_object.vertices, angle_x, angle_y, angle_z)
                elif event.key == K_o:
                    # Загрузка куба из файла
                    filename = input("Введите имя файла для загрузки куба: ")
                    loaded_vertices = load_cube_from_file(filename)
                    if loaded_vertices is not None:
                        selected_object.vertices[:] = loaded_vertices
                        cube_visible = True
                elif event.key == K_s:
                    # Сохранение куба в файл
                    filename = input("Введите имя файла для сохранения куба: ")
                    # save_cube_to_file(filename, selected_object.vertices)
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
                elif event.key == K_EQUALS or event.key == K_PLUS:
                    increase_distance()  # Увеличение расстояния (отдаление)
                elif event.key == K_MINUS:
                    decrease_distance()  # Уменьшение расстояния (приближение)
                elif event.key == K_SPACE:
                    # Запуск или остановка куба
                    cube_visible = not cube_visible
                elif event.key == K_UP:
                    try:
                        camera_pos[2] += 1
                    except:
                        print("Oops! Some error has occured!")
                elif event.key == K_DOWN:
                    try:
                        camera_pos[2] -= 1
                    except:
                        print("Oops! Some error has occured!")
                elif event.key == K_LEFT:
                    camera_pos[0] -= 1
                elif event.key == K_RIGHT:
                    camera_pos[0] += 1
                elif event.key == K_F11:
                    fullscreen = not fullscreen
            elif event.type == KEYUP:
                if event.key == K_LALT or event.key == K_RALT:
                    alt_pressed = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши при зажатой Alt
                    mouse_pressed = True
                    if alt_pressed:
                        prev_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Прокрутка колёсика мыши вверх
                    try:
                        increase_distance()
                    except:
                        pass
                elif event.button == 5:  # Прокрутка колёсика мыши вниз
                    try:
                        decrease_distance()
                    except:
                        pass

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_pressed = False

        screen_engine.fill(BLACK)
        update_camera_position(camera_pos)
        # Рисуем кнопку Start/Stop
        pygame.draw.rect(screen_engine, GRAY, start_button)
        screen_engine.blit(start_button_text, start_button_text_rect)

        # Рисуем небо (градиент)
        draw_sky_gradient()
        current_mouse_pos = pygame.mouse.get_pos()
        # Поворот куба с помощью мыши и зажатой клавиши Alt
        if mouse_pressed and alt_pressed:
            # current_mouse_pos = pygame.mouse.get_pos()
            if prev_mouse_pos:
                dx = current_mouse_pos[0] - prev_mouse_pos[0]
                dy = current_mouse_pos[1] - prev_mouse_pos[1]
                angle_x += dy * 0.01
                angle_y += dx * 0.01
            prev_mouse_pos = current_mouse_pos

        # Отрисовка куба, если он видим
        if cube_visible:
            draw_cube(selected_object.vertices, angle_x, angle_y, angle_z)

        pygame.display.flip()
        clock.tick(60)

    def preview():
        global preview_window_open
        root = tk.Tk()
        root.title("Preview")

        def on_closing():
            global preview_window_open
            preview_window_open = False
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        will_be_soon = ttk.Label(text="Will be soon")
        okay = ttk.Button(text="Okay", command=on_closing())
        root.mainloop()


if mode == "main":
    main()
