class Cube():
    def __init__(self, name = 'Cube', vertices = [
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1]
], faces = [
    (0, 1, 2, 3),  # front face
    (1, 5, 6, 2),  # right face
    (5, 4, 7, 6),  # back face
    (4, 0, 3, 7),  # left face
    (3, 2, 6, 7),  # top face
    (4, 5, 1, 0)  # bottom face
], current_material = (255, 255, 255), cube_params = {
    'scale_x': 1,
    'scale_y': 1,
    'scale_z': 0.5,
    'pos_x': 0,
    'pos_y': 0,
    'pos_z': 0,
    'distance' : 5
}):
        self.name = name
        self.vertices = vertices
        self.faces = faces
        self.current_material = current_material,
        self.cube_params = cube_params
