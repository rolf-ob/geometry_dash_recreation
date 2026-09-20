import pygame as py
import math

from core.textbox import TextBox
from entities.object import Object
from entities.collision import polygons_collide
from rendering.rendering import screen_to_world
from constants import PLAYER_X, WIDTH, HEIGHT

def toggle_building(game):
    game.building = not game.building
    if game.building:
        game.clicking = 0
        game.layer = 1
        game.title = ["Objects", -1]

        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None

    else:
        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer:
                obj.selected = False

        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None
        game.editing_level = False

        if game.paused:
            game.textboxes = [
                TextBox(20, 20, 200, 40, "Name"),
                TextBox(20, 60, 200, 40, "Player Color"),
                TextBox(20, 100, 200, 40, "Speedhack"),
                TextBox(20, 140, 200, 40, "FPS"),
                TextBox(20, 180, 200, 40, "Respawn Time")
            ]
            game.textboxes[0].text = game.name
        
        game.load_level()

def place_object(game):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse_pos = [(mouse_x - 1, mouse_y), (mouse_x, mouse_y), (mouse_x + 1, mouse_y)]
    mouse_x -= mouse_x % 40
    mouse_y -= mouse_y % 40
    layer = (game.background, game.objects, game.decoration)[game.layer]
    layer_points = (game.background_points, game.object_points, game.decoration_points)[game.layer]

    if not any(polygons_collide(mouse_pos, points) for points in layer_points):
        new_obj = Object(mouse_x, mouse_y, 40, 40, game.rotation, game.shape, (255,)*3, (0,)*3)
        layer.append(new_obj)
        layer_points.append(new_obj.get_points())

def select_object(game, shifting):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse_pos = [(mouse_x - 1, mouse_y), (mouse_x, mouse_y), (mouse_x + 1, mouse_y)]

    if polygons_collide(mouse_pos, game.end_points) and not game.editing_level:
        if shifting:
                game.end.selected = True
        else:
            game.end.selected = not game.end.selected
        if game.end.selected and game.textboxes == []:
                game.textboxes = [
                    TextBox(20, 20, 200, 40, "Shape"),
                    TextBox(20, 60, 200, 40, "Color"),
                    TextBox(20, 100, 200, 40, "Outline"),
                    TextBox(20, 140, 200, 40, "Rotation"),
                    TextBox(20, 180, 200, 40, "Width"),
                    TextBox(20, 220, 200, 40, "Height")
                ]
    
    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for obj, points in zip(layer, layer_points):
            if polygons_collide(mouse_pos, points) and (obj in (game.background, game.objects, game.decoration)[game.layer] or obj.shape == "checkpoint") and not game.editing_level:
                if shifting:
                    obj.selected = True
                else:
                    obj.selected = not obj.selected
                if obj.selected and game.textboxes == []:
                        game.textboxes = [
                            TextBox(20, 20, 200, 40, "Shape"),
                            TextBox(20, 60, 200, 40, "Color"),
                            TextBox(20, 100, 200, 40, "Outline"),
                            TextBox(20, 140, 200, 40, "Rotation"),
                            TextBox(20, 180, 200, 40, "Width"),
                            TextBox(20, 220, 200, 40, "Height")
                        ]

    if not game.end.selected and not any(obj.selected for obj in (*game.background, *game.objects, *game.decoration)) and not game.editing_level:
        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None

def move_objects(game, direction, shift, ctrl, alt):
    if shift:
        distance = 1
    elif ctrl:
        distance = 200
    elif alt:
        distance = 20
    else:
        distance = 40
    add_x = 0
    add_y = 0
    if direction == "up":
        add_y = -distance
    elif direction == "left":
        add_x = -distance
    elif direction == "down":
        add_y = distance
    elif direction == "right":
        add_x = distance

    if game.end.selected:
        game.end.x += add_x
        game.end.y += add_y
        game.end_points = game.end.get_points()

    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for i, obj in enumerate(layer):
            if obj.selected:
                obj.x += add_x
                obj.y += add_y
                layer_points[i] = obj.get_points()

def rotate_objects(game, way):
    if way == "counter clockwise":
        rotation = -90
    elif way == "clockwise":
        rotation = 90

    x_positions = []
    y_positions = []

    for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
        for i, obj in enumerate(layer):
            if obj.selected:
                for point in layer_points[i]:
                    x_positions.append(point[0])
                    y_positions.append(point[1])

    if x_positions:
        min_x = min(x_positions)
        max_x = max(x_positions)
        min_y = min(y_positions)
        max_y = max(y_positions)
        center_x = min_x + (max_x - min_x) / 2
        center_y = min_y + (max_y - min_y) / 2

        for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
            for i, obj in enumerate(layer):
                if obj.selected:
                    angle = math.radians(rotation)
                    cos_a, sin_a = math.cos(angle), math.sin(angle)

                    point_x = obj.x + obj.width / 2
                    point_y = obj.y + obj.height / 2
                    delta_x, delta_y = point_x - center_x, point_y - center_y
                    rotated_x = delta_x * cos_a - delta_y * sin_a + center_x
                    rotated_y = delta_x * sin_a + delta_y * cos_a + center_y

                    obj.rotation = (obj.rotation + rotation) % 360
                    obj.x = rotated_x - obj.width / 2
                    obj.y = rotated_y - obj.height / 2
                    layer_points[i] = obj.get_points()

def flip_objects(game, way):
    if way == "horizontally":
        axis = 0
    elif way == "vertically":
        axis = 1
    positions = []

    for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
        for i, obj in enumerate(layer):
            if obj.selected:
                for point in layer_points[i]:
                    positions.append(point[axis])

    if positions:
        min_pos = min(positions)
        max_pos = max(positions)
        center_pos = min_pos + (max_pos - min_pos) / 2

        for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
            for i, obj in enumerate(layer):
                if obj.selected:
                    if way == "horizontally":
                        center = obj.x + obj.width / 2
                        flipped_center = center_pos - (center - center_pos)
                        obj.x = flipped_center - obj.width / 2

                        if obj.shape == "square":
                            obj.rotation -= obj.rotation * 2
                            
                        elif obj.shape == "slope":
                            obj.rotation -= (90 + obj.rotation * 2) % 360
                        
                        elif obj.shape == "spike":
                            obj.rotation -= obj.rotation * 2

                        layer_points[i] = obj.get_points()
                    
                    elif way == "vertically":
                        center = obj.y + obj.height / 2
                        flipped_center = center_pos - (center - center_pos)
                        obj.y = flipped_center - obj.height / 2

                        if obj.shape == "square":
                            obj.rotation -= 180 + obj.rotation * 2
                            
                        elif obj.shape == "slope":
                            obj.rotation -= 270 + obj.rotation * 2
                        
                        elif obj.shape == "spike":
                            obj.rotation -= 180 + obj.rotation * 2

                        layer_points[i] = obj.get_points()

def deselect_objects(game):
    game.end.selected = False
    for layer in (game.background, game.objects, game.decoration, game.checkpoints):
        for obj in layer:
            obj.selected = False
    game.textboxes = []
    if game.active_textbox:
        game.active_textbox.deactivate()
        game.active_textbox = None

def duplicate_objects(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for obj in layer.copy():
            if obj.selected:
                layer.append(Object(obj.x, obj.y, obj.width, obj.height, obj.rotation, obj.shape, obj.color, obj.outline))
                layer_points.append(layer[-1].get_points())

def delete_objects(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for obj, points in zip(layer.copy(), layer_points.copy()):
            if obj.selected:
                if obj != game.checkpoints[0]:
                    layer.remove(obj)
                    layer_points.remove(points)
    
    game.textboxes = []
    if game.active_textbox:
        game.active_textbox.deactivate()
        game.active_textbox = None

def snap_grid_objects(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for i, obj in enumerate(layer):
            if obj.selected:
                if obj.x % 40 > 20:
                    obj.x += 40 - obj.x % 40
                else:
                    obj.x -= obj.x % 40
                
                if obj.y % 40 > 20:
                    obj.y += 40 - obj.y % 40
                else:
                    obj.y -= obj.y % 40

                if obj.rotation % 90 > 45:
                    obj.rotation += 90 - obj.rotation % 90
                else:
                    obj.rotation -= obj.rotation % 90

                layer_points[i] = obj.get_points()

def switch_layer(game, way):
    if way == "previous":
        game.layer = max(0, game.layer - 1)
    if way == "next":
        game.layer = min(2, game.layer + 1)
    
    game.title = [("Background", "Objects", "Decoration")[game.layer], -1]

def reset_camera(game):
    game.camera_x = 0
    game.camera_y = 0
    game.camera_zoom = 1
    game.zoom_center = game.camera_zoom + WIDTH / 2

def create_level(game):
    game.levels.insert((game.current_level % len(game.levels)) + 1, {
        "meta": {"gamemode": "wave", "speed": 2, "gravity": 0, "background color": (255,)*3, "title": "Unnamed level", "points": 0},
        "background": [],
        "objects": [],
        "decoration": [],
        "checkpoints": [Object(PLAYER_X, 680, 40, 40, 0, "checkpoint", (255,)*3, (0,)*3)],
        "end": Object(1000, 0, 1, HEIGHT, 0, "end", (0, 255, 0), (255, 0, 0)),
        "victors": {}
    })
    game.title = ["Created New Level", 2]

def edit_level(game):
    game.editing_level = not game.editing_level
    if game.editing_level:

        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer:
                obj.selected = False
        game.textboxes = [
            TextBox(20, 20, 200, 40, "Gamemode"),
            TextBox(20, 60, 200, 40, "Speed"),
            TextBox(20, 100, 200, 40, "Gravity"),
            TextBox(20, 140, 200, 40, "Background"),
            TextBox(20, 180, 200, 40, "Title"),
            TextBox(20, 220, 200, 40, "Points"),
            TextBox(20, 260, 200, 40, "Delete")
        ]
        if game.active_textbox:     
            game.active_textbox.deactivate()
            game.active_textbox = None

    else:
        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None