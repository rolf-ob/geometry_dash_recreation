import pygame as py
import math, time

from core.textbox import TextBox
from entities.object import Object
from entities.spatial import collide, get_nearby_objects
from rendering.rendering import screen_to_world
from constants import PLAYER_X, FONT_SIZE, HEIGHT, CAMERA_MARGIN

def toggle_building(game):
    game.building = not game.building
    if game.building:
        py.mouse.set_visible(True)
        py.mixer.music.stop()
        game.clicking = 0
        game.clicked = False
        game.layer = 1
        game.title = ["Objects", -1]
        close_menu(game)

    else:
        for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
            obj.selected = False

        game.level_states = []
        game.undone_states = []

        game.editing_level = False
        close_menu(game)
        if game.paused:
            open_menu(game, "settings")
        else:
            py.mouse.set_visible(False)
        game.load_level()

def place_object(game):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse = Object(mouse_x, mouse_y, 1, 1, 0, "square", None, None)
    mouse_x -= mouse_x % 40
    mouse_y -= mouse_y % 40
    layer = (game.background, game.objects, game.decoration)[game.layer]
    name = ("background", "objects", "decoration")[game.layer]
    objects = get_nearby_objects(game.buckets[name], game.building_camera_x, game.building_camera_x + game.view_width)

    if not any(collide(mouse, obj) for obj in objects):
        game.capture_level_state("do")

        new_obj = Object(mouse_x, mouse_y, 40, 40, 0, "square", (255,)*3, (0,)*3)
        layer.append(new_obj)
        game.rebuild_buckets()

def select_object(game, shift, ctrl):
    if not game.editing_level:
        mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
        mouse = Object(mouse_x, mouse_y, 1, 1, 0, "square", None, None)
        name = ("background", "objects", "decoration")[game.layer]
        layer = get_nearby_objects(game.buckets[name], game.building_camera_x, game.building_camera_x + game.view_width, game.z_order)
        checkpoints  = get_nearby_objects(game.buckets["checkpoints"], game.building_camera_x, game.building_camera_x + game.view_width)
        
        obj_selected = False
        cp_selected = False
        if ctrl:
            for obj in (*layer, *checkpoints):
                if collide(mouse, obj):
                    obj.selected = True
                    if obj.shape == "checkpoint": cp_selected = True
                    else: obj_selected = True

                    if obj.group_id != 0:
                        for other_obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                            if other_obj.group_id == obj.group_id:
                                other_obj.selected = True
                                if other_obj.shape == "checkpoint": cp_selected = True
                                else: obj_selected = True

        elif shift:
            top_obj = None
            for obj in (*layer, *checkpoints):
                if collide(mouse, obj):
                    top_obj = obj
                    
            if top_obj:
                top_obj.selected = True   
                if top_obj.shape == "checkpoint": cp_selected = True
                else: obj_selected = True
                
                if top_obj.group_id != 0:
                    for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                        if id(obj) != id(top_obj):
                            if obj.group_id == top_obj.group_id:
                                obj.selected = True
                                if obj.shape == "checkpoint": cp_selected = True
                                else: obj_selected = True
        
        else:
            top_obj = None
            for obj in (*layer, *checkpoints):
                if collide(mouse, obj):
                    top_obj = obj

            if top_obj:
                top_obj.selected = not top_obj.selected
                if top_obj.selected:
                    for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                        if id(obj) != id(top_obj):
                            if top_obj.group_id != 0 and obj.group_id == top_obj.group_id:
                                obj.selected = True
                                if obj.shape == "checkpoint": cp_selected = True
                                else: obj_selected = True
                            else:
                                obj.selected = False
                    
                    if top_obj.shape == "checkpoint": cp_selected = True
                    else: obj_selected = True

                else:
                    for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                        if id(obj) != id(top_obj):
                            if top_obj.group_id != 0 and obj.group_id == top_obj.group_id:
                                obj.selected = False
                    
                    if not any(obj.selected for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints)):
                        close_menu(game)

        if obj_selected:
            open_menu(game, "object attributes")
        elif cp_selected:
            open_menu(game, "checkpoint attributes")

def move_scale_objects(game, direction, shift, ctrl, alt):
    game.capture_level_state("do")
    
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

    if not game.scale_mode:
        for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
            if obj.selected:
                obj.x += add_x
                obj.y += add_y
                obj.recompute()
    else:
        for obj in (*game.background, *game.objects, *game.decoration):
            if obj.selected:
                if add_x > 0 or obj.width > distance:
                    obj.width += add_x
                if add_y > 0 or obj.height > distance:
                    obj.height += add_y
                obj.recompute()
    
    game.rebuild_buckets()

def rotate_objects(game, way, shift, ctrl, alt):
    if shift:
        distance = 0.1
    elif ctrl:
        distance = 1
    elif alt:
        distance = 45
    else:
        distance = 90
    
    if way == "counter clockwise":
        rotation = -distance
    elif way == "clockwise":
        rotation = distance

    x_positions = []
    y_positions = []

    for obj in (*game.background, *game.objects, *game.decoration):
        if obj.selected:
            for point in obj.points:
                x_positions.append(point[0])
                y_positions.append(point[1])

    if x_positions:
        game.capture_level_state("do")

        min_x = min(x_positions)
        max_x = max(x_positions)
        min_y = min(y_positions)
        max_y = max(y_positions)
        center_x = min_x + (max_x - min_x) / 2
        center_y = min_y + (max_y - min_y) / 2

        for obj in (*game.background, *game.objects, *game.decoration):
            if obj.selected:
                angle = math.radians(rotation)
                cos_a, sin_a = math.cos(angle), math.sin(angle)

                point_x = obj.x + obj.width / 2
                point_y = obj.y + obj.height / 2
                delta_x, delta_y = point_x - center_x, point_y - center_y
                rotated_x = delta_x * cos_a - delta_y * sin_a + center_x
                rotated_y = delta_x * sin_a + delta_y * cos_a + center_y

                obj.rotation = round((obj.rotation + rotation) % 360, 1)
                obj.x = int(rotated_x - obj.width / 2)
                obj.y = int(rotated_y - obj.height / 2)
                obj.recompute()
        
        game.rebuild_buckets()

def flip_objects(game, way):
    if way == "horizontally":
        axis = 0
    elif way == "vertically":
        axis = 1
    positions = []

    for obj in (*game.background, *game.objects, *game.decoration):
        if obj.selected:
            for point in obj.points:
                positions.append(point[axis])

    if positions:
        game.capture_level_state("do")

        min_pos = min(positions)
        max_pos = max(positions)
        center_pos = min_pos + (max_pos - min_pos) / 2

        for obj in (*game.background, *game.objects, *game.decoration):
            if obj.selected:
                if way == "horizontally":
                    center = obj.x + obj.width / 2
                    flipped_center = center_pos - (center - center_pos)
                    obj.x = int(flipped_center - obj.width / 2)

                    if obj.shape in ("square", "end", "pad", "gamemode", "speed", "gravity", "size", "teleport", "text"):
                        obj.rotation = -obj.rotation
                        
                    elif obj.shape == "right slope":
                        obj.rotation = -obj.rotation
                        obj.shape = "left slope"
                    elif obj.shape == "left slope":
                        obj.rotation = -obj.rotation
                        obj.shape = "right slope"
                    
                    elif obj.shape == "spike":
                        obj.rotation = -obj.rotation
                    
                    obj.rotation = round(obj.rotation % 360, 1)
                    if obj.rotation < 0:
                        obj.rotation = round(obj.rotation + 360, 1)
                    obj.recompute()
                
                elif way == "vertically":
                    center = obj.y + obj.height / 2
                    flipped_center = center_pos - (center - center_pos)
                    obj.y = int(flipped_center - obj.height / 2)

                    if obj.shape in ("square", "end", "pad", "gamemode", "speed", "gravity", "size", "teleport", "text"):
                        obj.rotation = -obj.rotation
                        
                    elif obj.shape == "right slope":
                        obj.rotation = -obj.rotation + 180
                        obj.shape = "left slope"
                    elif obj.shape == "left slope":
                        obj.rotation = -obj.rotation + 180
                        obj.shape = "right slope"
                    
                    elif obj.shape == "spike":
                        obj.rotation = -obj.rotation + 180
                    
                    obj.rotation = round(obj.rotation % 360, 1)
                    if obj.rotation < 0:
                        obj.rotation = round(obj.rotation + 360, 1)
                    obj.recompute()
    
    game.rebuild_buckets()

def deselect_objects(game):
    if not game.editing_level:
        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer:
                obj.selected = False
        close_menu(game)

def duplicate_objects(game):
    game.capture_level_state("do")

    for layer in (game.background, game.objects, game.decoration, game.checkpoints):
        for obj in layer.copy():
            if obj.selected:
                modifier = obj.modifier if obj.shape != "checkpoint" else obj.modifier.copy()
                
                new_obj = Object(obj.x, obj.y, obj.width, obj.height, obj.rotation, obj.shape, obj.color, obj.outline, modifier, True)
                layer.append(new_obj)
                new_obj.selected = False
    
    game.rebuild_buckets()

def delete_objects(game):
    game.capture_level_state("do")

    for layer in (game.background, game.objects, game.decoration, game.checkpoints):
        for obj in layer.copy():
            if obj.selected and obj != game.checkpoints[0]:
                layer.remove(obj)
    
    game.rebuild_buckets()
    close_menu(game)

def snap_grid_objects(game):
    game.capture_level_state("do")

    for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
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
                obj.rotation = round(obj.rotation + 90 - obj.rotation % 90, 1)
            else:
                obj.rotation = round(obj.rotation - obj.rotation % 90, 1)
                    
            obj.rotation = round(obj.rotation % 360, 1)
            if obj.rotation < 0:
                obj.rotation = round(obj.rotation + 360, 1)
            obj.recompute()
    
    game.rebuild_buckets()

def group_objects(game, group):
    game.capture_level_state("do")

    if group == "group":
        for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
            if obj.selected:
                obj.group_id = game.current_group_id
        game.current_group_id += 1

    elif group == "ungroup":
        for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
            if obj.selected:
                obj.group_id = 0

def layer_objects(game, way):
    game.capture_level_state("do")

    if way == "last":
        for layer in (game.background, game.objects, game.decoration):
            for obj in reversed(layer.copy()):
                if obj.selected:
                    layer.remove(obj)
                    layer.insert(0, obj)

    elif way == "back":
        for layer in (game.background, game.objects, game.decoration):
            for i, obj in enumerate(layer.copy()):
                if obj.selected:
                    layer.remove(obj)
                    layer.insert(max(0, i-1), obj)

    elif way == "forward":
        for layer in (game.background, game.objects, game.decoration):
            for i, obj in reversed(list(enumerate(layer.copy()))):
                if obj.selected:
                    layer.remove(obj)
                    layer.insert(i+1, obj)

    elif way == "first":
        for layer in (game.background, game.objects, game.decoration):
            for obj in layer.copy():
                if obj.selected:
                    layer.remove(obj)
                    layer.append(obj)

    game.rebuild_buckets()

def move_objects_to_layer(game, layer_name):
    game.capture_level_state("do")

    target_layer = {
        "background": game.background,
        "objects": game.objects,
        "decoration": game.decoration
    }[layer_name]

    for layer in (game.background, game.objects, game.decoration):
        for obj in layer.copy():
            if obj.selected:
                layer.remove(obj)
                target_layer.append(obj)

    game.rebuild_buckets()

def switch_layer(game, shift):
    if shift:
        game.layer = max(0, game.layer - 1)
    else:
        game.layer = min(2, game.layer + 1)
    
    game.title = [("Background", "Objects", "Decoration")[game.layer], -1]

def reset_camera(game, ctrl):
    if ctrl: game.building_camera_x = 0
    game.building_camera_y = game.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN
    game.camera_zoom = 1
    game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")

def undo_edit(game, ctrl):
    deselect_objects(game)
    if ctrl:
        game.restore_level_state("undo")
    else:
        game.restore_level_state("redo")

def create_level(game):
    game.levels.insert(game.current_level + 1, {
        "meta": {"length": 100, "roof": 0, "floor": 720, "roof color": (255,)*3, "floor color": (255,)*3, "background color": (255,)*3, "title": "Unnamed level", "points": 0, "song": "", "song start": 0},
        "background": [],
        "objects": [],
        "decoration": [],
        "checkpoints": [Object(PLAYER_X, 680, 40, 40, 0, "checkpoint", (0, 255, 0), game.primary_color, {"gamemode": "cube", "speed": 2, "gravity": 1, "size": 1})],
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
            TextBox("Respawn Time", game.respawn_time),
            TextBox("Volume", game.volume),
        ]
    
    elif menu == "level settings":
        r1, g1, b1 = game.level["meta"]["roof color"]
        r2, g2, b2 = game.level["meta"]["floor color"]
        r3, g3, b3 = game.level["meta"]["background color"]
        game.textboxes = [
            TextBox("Length", game.level["meta"]["length"]),
            TextBox("Roof", game.level["meta"]["roof"]),
            TextBox("Floor", game.level["meta"]["floor"]),
            TextBox("Roof Color", f"{str(r1)} {str(g1)} {str(b1)}"),
            TextBox("Floor Color", f"{str(r2)} {str(g2)} {str(b2)}"),
            TextBox("Background", f"{str(r3)} {str(g3)} {str(b3)}"),
            TextBox("Title", game.level["meta"]["title"]),
            TextBox("Points", game.level["meta"]["points"]),
            TextBox("Level Number", game.current_level),
            TextBox("Song", game.song),
            TextBox("Song Start", game.song_start),
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
            TextBox("Gravity", ""),
            TextBox("Size", "")
        ]

    if game.active_textbox:     
        game.active_textbox.deactivate()
        game.active_textbox = None