import pygame as py
import math, time
from pathlib import Path

from entities.serialization import save_json, level_to_dict
from entities.spatial import collide, get_nearby_objects
from rendering.rendering import screen_to_world
from core.textbox import TextBox
from entities.object import Object
from constants import GRID_SIZE, PLAYER_X, FONT_SIZE, HEIGHT, CAMERA_MARGIN

def toggle_building(game):
    close_menu(game)
    game.building = not game.building
    if game.building:
        game.load_level(False)
        py.mouse.set_visible(True)
        py.mixer.music.stop()
        game.clicking = 0
        game.clicked = False
        game.layer = 1
        game.title = ["Objects", -1]

    else:
        for obj in game.selected_objects:
            obj.selected = False
        game.selected_objects = []

        game.editing_level = False
        if game.paused:
            open_user_settings_menu(game)
        else:
            py.mouse.set_visible(False)
        game.load_level()

def place_object(game):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse = Object(mouse_x, mouse_y, 1, 1, 0, "square", None, None)
    mouse_x -= mouse_x % GRID_SIZE
    mouse_y -= mouse_y % GRID_SIZE
    layer = (game.background, game.objects, game.decoration)[game.layer]
    name = ("background", "objects", "decoration")[game.layer]
    objects = get_nearby_objects(game.buckets[name], game.building_camera_x, game.building_camera_x + game.view_width)

    if not any(collide(mouse, obj) for obj in objects):
        game.capture_state("do")

        new_obj = Object(mouse_x, mouse_y, GRID_SIZE, GRID_SIZE, 0, "square", (255,)*3, (0,)*3)
        layer.append(new_obj)
        game.rebuild_buckets()

def select_object(game, shift, ctrl):
    if not game.editing_level:
        mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
        mouse = Object(mouse_x, mouse_y, 1, 1, 0, "square", None, None)
        name = ("background", "objects", "decoration")[game.layer]
        layer = get_nearby_objects(game.buckets[name], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0])
        checkpoints = get_nearby_objects(game.buckets["checkpoints"], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0]) if not game.layer_view else []
        objects = (*layer, *checkpoints) if name != "decoration" else (*checkpoints, *layer)
        
        if ctrl:
            for obj in objects:
                if collide(mouse, obj):
                    if not obj.selected:
                        obj.selected = True
                        game.selected_objects.append(obj)

                    if obj.group_id != 0:
                        for other_obj in game.group_ids[obj.group_id]:
                            if not obj.selected:
                                other_obj.selected = True
                                game.selected_objects.append(other_obj)

        elif shift:
            top_obj = None
            for obj in objects:
                if collide(mouse, obj):
                    top_obj = obj
                    
            if top_obj:
                if not top_obj.selected:
                    top_obj.selected = True   
                    game.selected_objects.append(top_obj)
                
                if top_obj.group_id != 0:
                    for obj in game.group_ids[top_obj.group_id]:
                        if id(obj) != id(top_obj) and not obj.selected:
                                obj.selected = True
                                game.selected_objects.append(obj)
        
        else:
            top_obj = None
            for obj in objects:
                if collide(mouse, obj):
                    top_obj = obj

            if top_obj:
                top_obj.selected = not top_obj.selected
                if top_obj.selected:
                    game.selected_objects.append(top_obj)

                    for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                        if id(obj) != id(top_obj):
                            if top_obj.group_id != 0 and obj.group_id == top_obj.group_id:
                                if not obj.selected:
                                    obj.selected = True
                                    game.selected_objects.append(obj)

                            elif obj.selected:
                                obj.selected = False
                                game.selected_objects.remove(obj)

                else:
                    if top_obj.group_id != 0:
                        for obj in game.group_ids[top_obj.group_id]:
                            obj.selected = False
                            game.selected_objects.remove(obj)
                    else:
                        game.selected_objects.remove(top_obj)

                    if not game.selected_objects:
                        close_menu(game)

        if game.selected_objects:
            open_objects_menu(game)

def move_scale_objects(game, direction, shift, ctrl, alt):
    if game.selected_objects:
        game.capture_state("do")
    
        if shift:
            distance = 1
        elif ctrl:
            distance = GRID_SIZE * 5
        elif alt:
            distance = GRID_SIZE / 2
        else:
            distance = GRID_SIZE
        
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
            for obj in game.selected_objects:
                obj.x += add_x
                obj.y += add_y
                obj.recompute_position("x", add_x)
                obj.recompute_position("y", add_y)
        else:
            for obj in game.selected_objects:
                if obj.shape != "checkpoint":
                    if add_x > 0 or obj.width > distance:
                        obj.width += add_x
                    if add_y > 0 or obj.height > distance:
                        obj.height += add_y
                    obj.recompute() #!
        
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

    for obj in game.selected_objects:
        x_positions.append(obj.x + obj.width / 2)
        y_positions.append(obj.y + obj.height / 2)

    if x_positions:
        game.capture_state("do")

        min_x = min(x_positions)
        max_x = max(x_positions)
        min_y = min(y_positions)
        max_y = max(y_positions)
        center_x = min_x + (max_x - min_x) / 2
        center_y = min_y + (max_y - min_y) / 2

        for obj in game.selected_objects:
            angle = math.radians(rotation)
            cos_a, sin_a = math.cos(angle), math.sin(angle)

            point_x = obj.x + obj.width / 2
            point_y = obj.y + obj.height / 2
            delta_x, delta_y = point_x - center_x, point_y - center_y
            rotated_x = delta_x * cos_a - delta_y * sin_a + center_x
            rotated_y = delta_x * sin_a + delta_y * cos_a + center_y

            if obj.shape != "checkpoint":
                obj.rotation = round((obj.rotation + rotation) % 360, 1)
            obj.x = rotated_x - obj.width / 2
            obj.y = rotated_y - obj.height / 2
            obj.recompute()
        
        game.rebuild_buckets()

def flip_objects(game, way):
    if way == "horizontally":
        axis = 0
    elif way == "vertically":
        axis = 1
    positions = []

    for obj in game.selected_objects:
        for point in obj.points:
            positions.append(point[axis])

    if positions:
        game.capture_state("do")

        min_pos = min(positions)
        max_pos = max(positions)
        center_pos = min_pos + (max_pos - min_pos) / 2

        for obj in game.selected_objects:
            if way == "horizontally":
                center = obj.x + obj.width / 2
                flipped_center = center_pos - (center - center_pos)
                obj.x = flipped_center - obj.width / 2

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
                obj.y = flipped_center - obj.height / 2

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
        for obj in game.selected_objects:
            obj.selected = False
        game.selected_objects = []
        close_menu(game)

def duplicate_objects(game):
    if game.selected_objects:
        game.capture_state("do")

        object_groups = {}

        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer.copy():
                if obj.selected:
                    modifier = obj.modifier if obj.shape not in ("checkpoint", "trigger") else obj.modifier.copy()
                    
                    new_obj = Object(obj.x, obj.y, obj.width, obj.height, obj.rotation, obj.shape, obj.color, obj.outline, modifier, True)
                    layer.append(new_obj)
                    obj.selected = False
                    game.selected_objects.remove(obj)
                    game.selected_objects.append(new_obj)

                    if obj.group_id != 0:
                        if obj.group_id in object_groups:
                            object_groups[obj.group_id].append(new_obj)
                        else:
                            object_groups[obj.group_id] = [new_obj]

        for group in object_groups.values():
            for obj in group:
                obj.group_id = game.current_group_id
                game.group_ids[game.current_group_id].append(obj)
            game.current_group_id += 1
        
        game.rebuild_buckets()

def delete_objects(game):
    if game.selected_objects:
        game.capture_state("do")

        for layer in (game.background, game.objects, game.decoration, game.checkpoints):
            for obj in layer.copy():
                if obj.selected and obj != game.checkpoints[0]:
                    game.selected_objects.remove(obj)
                    layer.remove(obj)
    
    game.rebuild_buckets()
    if not game.checkpoints[0].selected:
        close_menu(game)
    else:
        open_objects_menu(game)

def snap_grid_objects(game):
    if game.selected_objects:
        game.capture_state("do")

        for obj in game.selected_objects:
            if obj.x % GRID_SIZE > GRID_SIZE / 2:
                obj.x += GRID_SIZE - obj.x % GRID_SIZE
            else:
                obj.x -= obj.x % GRID_SIZE

            if obj.y % GRID_SIZE > GRID_SIZE / 2:
                obj.y += GRID_SIZE - obj.y % GRID_SIZE
            else:
                obj.y -= obj.y % GRID_SIZE

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
    if game.selected_objects:
        game.capture_state("do")

        if group == "group":
            for obj in game.selected_objects:
                obj.group_id = game.current_group_id
                game.group_ids[game.current_group_id].append(obj)
            game.current_group_id += 1

        elif group == "ungroup":
            for obj in game.selected_objects:
                game.group_ids[obj.group_id] = []
                obj.group_id = 0

def layer_objects(game, way):
    if game.selected_objects:
        game.capture_state("do")

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
    if game.selected_objects:
        game.capture_state("do")

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
    game.building_camera_y = game.floor - HEIGHT + CAMERA_MARGIN
    game.camera_zoom = 1
    game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")

def undo_edit(game, ctrl):
    deselect_objects(game)
    if ctrl:
        game.restore_state("undo")
    else:
        game.restore_state("redo")

def create_level(game):
    base_name = "Unnamed level"
    name = base_name
    number = 1

    while (Path("levels") / f"{name}.json").exists():
        name = f"{base_name}({number})"
        number += 1

    new_level = {
        "meta": {
            "length": 100,
            "roof": 0,
            "floor": 720,
            "roof_color": (255,)*3,
            "floor_color": (255,)*3,
            "background_color": (255,)*3,
            "title": name,
            "points": 0,
            "level number": game.current_level + 1,
            "song": "",
            "song start": 0
        },
        "background": [],
        "objects": [],
        "decoration": [],
        "checkpoints": [
            Object(
                PLAYER_X, 680, GRID_SIZE, GRID_SIZE, 0, "checkpoint",
                (0, 255, 0), (0,)*3,
                {"gamemode": "cube", "speed": 2, "gravity": 1, "size": 1}
            )
        ],
        "victors": {}
    }

    game.levels.insert(game.current_level + 1, new_level)

    for i, level in enumerate(game.levels):
        level["meta"]["level number"] = i
    
    save_json(f"levels/{name}.json", level_to_dict(new_level))
    
    game.title = ["Created New Level", time.perf_counter() + 2]

def edit_level(game):
    if game.current_level != 0:
        game.editing_level = not game.editing_level

        if game.editing_level:
            for obj in game.selected_objects:
                obj.selected = False
            game.selected_objects = []
            open_level_settings_menu(game)
        
        else:
            close_menu(game)

def close_menu(game):
    game.textboxes = []
    if game.active_textbox:
        game.active_textbox.deactivate()
        game.active_textbox = None

def open_user_settings_menu(game):
    game.textboxes = [
        TextBox("Speedhack", game.speedhack_multiplier),
        TextBox("FPS", game.fps),
        TextBox("Respawn Time", game.respawn_time),
        TextBox("Volume", game.volume),
        TextBox("Log Out", "")
    ]
    if game.active_textbox:     
        game.active_textbox.deactivate()
        game.active_textbox = None

def open_level_settings_menu(game):
    r1, g1, b1 = game.roof_color
    r2, g2, b2 = game.floor_color
    r3, g3, b3 = game.background_color
    game.textboxes = [
        TextBox("Length", game.length),
        TextBox("Roof", game.roof),
        TextBox("Floor", game.floor),
        TextBox("Roof Color", f"{str(r1)} {str(g1)} {str(b1)}"),
        TextBox("Floor Color", f"{str(r2)} {str(g2)} {str(b2)}"),
        TextBox("Background Color", f"{str(r3)} {str(g3)} {str(b3)}"),
        TextBox("Title", game.level["meta"]["title"]),
        TextBox("Points", game.points),
        TextBox("Level Number", game.level["meta"]["level number"]),
        TextBox("Song", game.song),
        TextBox("Song Start", game.song_start),
        TextBox("Reset stats", ""),
        TextBox("Delete", "")
    ]
    if game.active_textbox:     
        game.active_textbox.deactivate()
        game.active_textbox = None

def open_objects_menu(game):
    if any(obj.shape not in ("checkpoint", "trigger") for obj in game.selected_objects):
        if not game.textboxes or game.textboxes[0].field_name != "Shape":
            common_triggers = None
            for obj in game.selected_objects:
                if not common_triggers and obj.triggers:
                    common_triggers = obj.triggers
                
                elif obj.triggers != common_triggers:
                    common_triggers = "-"
                    break
            
            if not common_triggers: 
                shown_triggers = "-"
            else:
                shown_triggers = ""
                for trigger in [str(trigger) for trigger in common_triggers]:
                    shown_triggers += trigger + " "
    
            game.textboxes = [
                TextBox("Shape", ""),
                TextBox("Color", ""),
                TextBox("Outline", ""),
                TextBox("Rotation", ""),
                TextBox("Width", ""),
                TextBox("Height", ""),
                TextBox("Modifier", ""),
                TextBox("Triggers", shown_triggers)
            ]
            if game.active_textbox:     
                game.active_textbox.deactivate()
                game.active_textbox = None

    elif any(obj.shape == "checkpoint" for obj in game.selected_objects):
        if not game.textboxes or game.textboxes[0].field_name != "Gamemode":
            game.textboxes = [
                TextBox("Gamemode", ""),
                TextBox("Speed", ""),
                TextBox("Gravity", ""),
                TextBox("Size", "")
            ]
            if game.active_textbox:     
                game.active_textbox.deactivate()
                game.active_textbox = None
    
    elif any(obj.shape == "trigger" for obj in game.selected_objects):
        if not game.textboxes or game.textboxes[0].field_name != "Color":
            game.textboxes = [
                TextBox("Color", ""),
                TextBox("Outline", ""),
                TextBox("Attribute", ""),
                TextBox("Value", ""),
                TextBox("Transition", ""),
                TextBox("Triggers", "")
            ]
            if game.active_textbox:     
                game.active_textbox.deactivate()
                game.active_textbox = None