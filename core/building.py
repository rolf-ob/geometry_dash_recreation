import pygame as py
import math, time

from core.textbox import TextBox
from entities.object import Object
from entities.collision import polygons_collide
from rendering.rendering import world_to_screen, screen_to_world
from constants import PLAYER_X, FONT_SIZE

def toggle_building(game):
    game.building = not game.building
    if game.building:
        game.clicking = 0
        game.clicked = False
        game.layer = 1
        game.title = ["Objects", -1]
        close_menu(game)

    else:
        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer:
                obj.selected = False

        game.editing_level = False
        close_menu(game)
        if game.paused:
            open_menu(game, "settings")
        game.load_level()

def place_object(game):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse_pos = [(mouse_x - 1, mouse_y), (mouse_x, mouse_y), (mouse_x + 1, mouse_y)]
    mouse_x -= mouse_x % 40
    mouse_y -= mouse_y % 40
    layer = (game.background, game.objects, game.decoration)[game.layer]
    layer_points = (game.background_points, game.object_points, game.decoration_points)[game.layer]

    if not any(polygons_collide(mouse_pos, points) for points in layer_points):
        new_obj = Object(mouse_x, mouse_y, 40, 40, 0, "square", (255,)*3, (0,)*3)
        layer.append(new_obj)
        layer_points.append(new_obj.get_points())

def select_object(game, shifting):
    if not game.editing_level:
        mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
        mouse_pos = [(mouse_x - 1, mouse_y), (mouse_x, mouse_y), (mouse_x + 1, mouse_y)]        
        layer = (game.background, game.objects, game.decoration)[game.layer]
        layer_points = (game.background_points, game.object_points, game.decoration_points)[game.layer]

        obj_selected = False
        cp_selected = False
        for obj, points in zip((*layer, *game.checkpoints), (*layer_points, *game.checkpoint_points)):
            if polygons_collide(mouse_pos, points):
                if shifting:
                    obj.selected = True
                else:
                    obj.selected = not obj.selected
            
            if obj.selected:
                if obj.shape != "checkpoint":
                    obj_selected = True
                else:
                    cp_selected = True

        if obj_selected:
            open_menu(game, "object attributes")
        elif cp_selected:
            open_menu(game, "checkpoint attributes")
        else:
            close_menu(game)

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

                        if obj.shape in ("square", "end", "pad", "gamemode", "speed", "gravity"):
                            obj.rotation -= obj.rotation * 2
                            
                        elif obj.shape == "slope":
                            obj.rotation -= 90 + obj.rotation * 2
                            width = obj.height
                            height = obj.width
                            obj.width = width
                            obj.height = height
                        
                        elif obj.shape == "spike":
                            obj.rotation -= obj.rotation * 2
                        
                        obj.rotation %= 360
                        if obj.rotation < 0:
                            obj.rotation += 360
                        layer_points[i] = obj.get_points()
                    
                    elif way == "vertically":
                        center = obj.y + obj.height / 2
                        flipped_center = center_pos - (center - center_pos)
                        obj.y = flipped_center - obj.height / 2

                        if obj.shape in ("square", "end", "pad", "gamemode", "speed", "gravity"):
                            obj.rotation -= 180 + obj.rotation * 2
                            
                        elif obj.shape == "slope":
                            obj.rotation -= 270 + obj.rotation * 2
                            width = obj.height
                            height = obj.width
                            obj.width = width
                            obj.height = height
                        
                        elif obj.shape == "spike":
                            obj.rotation -= 180 + obj.rotation * 2
                        
                        obj.rotation %= 360
                        if obj.rotation < 0:
                            obj.rotation += 360
                        layer_points[i] = obj.get_points()

def deselect_objects(game):
    if not game.editing_level:
        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer:
                obj.selected = False
        close_menu(game)

def duplicate_objects(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for obj in layer.copy():
            if obj.selected:
                modifier = obj.modifier if obj.shape != "checkpoint" else obj.modifier.copy()
                layer.append(Object(obj.x, obj.y, obj.width, obj.height, obj.rotation, obj.shape, obj.color, obj.outline, modifier))
                layer_points.append(layer[-1].get_points())

def delete_objects(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration, game.checkpoints), (game.background_points, game.object_points, game.decoration_points, game.checkpoint_points)):
        for obj, points in zip(layer.copy(), layer_points.copy()):
            if obj.selected:
                if obj != game.checkpoints[0]:
                    layer.remove(obj)
                    layer_points.remove(points)
    
    close_menu(game)

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
                        
                obj.rotation %= 360
                if obj.rotation < 0:
                    obj.rotation += 360
                layer_points[i] = obj.get_points()

def switch_layer(game, way):
    if way == "previous":
        game.layer = max(0, game.layer - 1)
    if way == "next":
        game.layer = min(2, game.layer + 1)
    
    game.title = [("Background", "Objects", "Decoration")[game.layer], -1]

def reset_camera(game):
    game.building_camera_x = 0
    game.building_camera_y = 0
    game.camera_zoom = 1
    game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale)))

def create_level(game):
    game.levels.insert(game.current_level + 1, {
        "meta": {"length": 100, "background color": (255,)*3, "title": "Unnamed level", "points": 0},
        "background": [],
        "objects": [],
        "decoration": [],
        "checkpoints": [Object(PLAYER_X, 680, 40, 40, 0, "checkpoint", (0, 255, 0), (0,)*3, {"gamemode": "cube", "speed": 2, "gravity": 1})],
        "victors": {}
    })
    game.title = ["Created New Level", time.perf_counter() + 2]

def edit_level(game):
    if game.current_level != 0:
        game.editing_level = not game.editing_level
        if game.editing_level:
            for layer in (game.background, game.objects, game.decoration, game.checkpoints):
                for obj in layer:
                    obj.selected = False
            open_menu(game, "level settings")
        else:
            close_menu(game)

def close_menu(game):
    game.textboxes = []
    if game.active_textbox:
        game.active_textbox.deactivate()
        game.active_textbox = None

def open_menu(game, menu):
    if menu == "settings":
        game.textboxes = [
            TextBox("Name", game.name),
            TextBox("Speedhack", game.speedhack_multiplier),
            TextBox("FPS", game.fps),
            TextBox("Respawn Time", game.respawn_time)
        ]
    
    elif menu == "level settings":
        r, g, b = game.level["meta"]["background color"]
        game.textboxes = [
            TextBox("Length", game.level["meta"]["length"]),
            TextBox("Background", f"{str(r)} {str(g)} {str(b)}"),
            TextBox("Title", game.level["meta"]["title"]),
            TextBox("Points", game.level["meta"]["points"]),
            TextBox("Level Number", game.current_level),
            TextBox("Reset stats", ""),
            TextBox("Delete", "")
        ]

    elif menu == "object attributes":
        game.textboxes = [
            TextBox("Shape", ""),
            TextBox("Color", ""),
            TextBox("Outline", ""),
            TextBox("Rotation", ""),
            TextBox("Width", ""),
            TextBox("Height", ""),
            TextBox("Modifier", "")
        ]

    elif menu == "checkpoint attributes":
        game.textboxes = [
            TextBox("Gamemode", ""),
            TextBox("Speed", ""),
            TextBox("Gravity", "")
        ]

    if game.active_textbox:     
        game.active_textbox.deactivate()
        game.active_textbox = None