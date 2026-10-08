import pygame as py
import time

from core.building import toggle_building, place_object, select_object, move_scale_objects, rotate_objects, flip_objects, deselect_objects, duplicate_objects, delete_objects, snap_grid_objects, group_objects, layer_objects, move_objects_to_layer, switch_layer, reset_camera, undo_edit, create_level, edit_level, close_menu, open_menu
from constants import HEIGHT, PLAYER_X, FONT_SIZE, CAMERA_MARGIN
from core.attribute_editing import switch_attribute, apply_edit
from entities.spatial import get_buckets

def click(game, type, button, shift, ctrl):
    if button in (0, 1) and not game.building:
        if type == "click":
            game.clicking += 1
            if game.gamemode == "wave":
                wave_part = (game.player.x + game.player.width/2, game.player.y)
                game.wave_trail.append(wave_part)
                for bucket in get_buckets(wave_part):
                    game.buckets["hitboxes"][bucket].append(wave_part)
        elif type == "release":
            game.clicking = max(0, game.clicking - 1)
            if game.clicking == 0:
                game.clicked = False
            
            if game.gamemode == "wave":
                wave_part = (game.player.x + game.player.width/2, game.player.y)
                game.wave_trail.append(wave_part)
                for bucket in get_buckets(wave_part):
                    game.buckets["hitboxes"][bucket].append(wave_part)
    
    elif button == 1 and type == "release" and not shift:
        place_object(game)
    
    elif button == 3 and game.building and type == "release" and not (shift or ctrl):
        select_object(game, False, False)

def toggle_pause(game):
    game.paused = not game.paused

    if game.paused:
        py.mouse.set_visible(True)
        py.mixer.music.pause()
        open_menu(game, "settings")
        if not game.completed:
            game.cheated = True
    else:
        py.mouse.set_visible(False)
        py.mixer.music.unpause()
        close_menu(game)
        if not game.completed and (game.show_hitboxes or game.speedhack):
            game.cheated = True

        if game.player.x == game.checkpoints[game.checkpoint].x:
            game.record_attempt()
    
    if not game.paused and game.dead == 0 and not game.completed:
        game.camera_x = game.player.x - PLAYER_X
        game.camera_y = game.floor - HEIGHT + CAMERA_MARGIN
        game.camera_y = max(min(game.camera_y, game.player.y - CAMERA_MARGIN * 2), game.player.y + game.player.height - HEIGHT + CAMERA_MARGIN)
        game.camera_zoom = 1
        game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")

def toggle_dark_mode(game):
    game.dark_mode = not game.dark_mode
    if game.dark_mode:
        game.primary_color = (255,)*3
        game.secondary_color = (0,)*3
    else:
        game.primary_color = (0,)*3
        game.secondary_color = (255,)*3

def switch_checkpoint(game, way):
    if way == "previous":
        game.checkpoint = (game.checkpoint-1) % len(game.checkpoints)
    elif way == "next":
        game.checkpoint = (game.checkpoint+1) % len(game.checkpoints)
    game.restart()
    game.title = [f"Checkpoint {game.checkpoint}/{len(game.checkpoints) - 1}", time.perf_counter() + 0.5]

def switch_level(game, way):
    game.checkpoint = 0
    game.building_camera_x = 0
    game.building_camera_y = game.floor - HEIGHT + CAMERA_MARGIN
    if way == "previous":
        game.current_level = (game.current_level-1) % len(game.levels)
    elif way == "next":
        game.current_level = (game.current_level+1) % len(game.levels)
    
    game.load_level()

def toggle_speedhack(game):
    if len(game.hitboxes) > 1 and not game.completed:
        game.cheated = True
    game.speedhack = not game.speedhack

def toggle_hitboxes(game):
    if len(game.hitboxes) > 1 and not game.completed:
        game.cheated = True
    game.show_hitboxes = not game.show_hitboxes

def step_frame(game):
    if game.paused:
        if game.frame_steps >= game.fps // 3:
            game.frame_steps = game.fps // 3 - 2
        game.frame_steps += 1

def scroll(game, y):
    camera_y = game.camera_y if not game.building else game.building_camera_y
    if y > 0 and (game.paused or game.completed or game.building):
        camera_y -= 100 / game.camera_zoom
    elif y < 0 and (game.paused or game.completed or game.building):
        camera_y += 100 / game.camera_zoom

    if game.building:
        game.building_camera_y = camera_y
    else:
        game.camera_y = camera_y

def pan(game, y):
    camera_x = game.camera_x if not game.building else game.building_camera_x
    if y > 0 and (game.paused or game.completed or game.building):
        camera_x -= 100 / game.camera_zoom
    elif y < 0 and (game.paused or game.completed or game.building):
        camera_x += 100 / game.camera_zoom
    
    if game.building:
        game.building_camera_x = camera_x
    else:
        game.camera_x = camera_x

def view_separate_hitboxes(game, y):
    if game.paused:
        if y > 0:
            game.current_hitbox = min(len(game.hitboxes), game.current_hitbox+1)
        elif y < 0:
            game.current_hitbox = max(0, game.current_hitbox-1)

def zoom(game, y):
    if y > 0 and (game.paused or game.completed or game.building):
        game.camera_zoom += game.camera_zoom/10
        game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")
    elif y < 0 and (game.paused or game.completed or game.building) and game.camera_zoom > 0.5:
        game.camera_zoom = max(0.5, game.camera_zoom - game.camera_zoom/10)
        game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")

def handle_input(game):
    keys = py.key.get_pressed()
    shift = True if keys[py.K_LSHIFT] else False
    ctrl = True if keys[py.K_LCTRL] else False
    alt = True if keys[py.K_LALT] else False

    if any(keys[key] for key in game.controls["step frame"]) and not game.building:
        step_frame(game)
    else:
        game.frame_steps = 0

    if shift and py.mouse.get_pressed()[0] and game.building:
        place_object(game)
    if (shift or ctrl) and py.mouse.get_pressed()[2] and game.building:
        select_object(game, shift, ctrl)

    for event in py.event.get():
        if event.type == py.QUIT:
            game.running = False

        elif event.type == py.VIDEORESIZE:
            game.width, game.height = event.size
            game.view_width = game.width * (HEIGHT / game.height)
            game.view_height = game.height * (HEIGHT / game.height)
            game.scale = game.height / HEIGHT
            game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale)), "screen")
            game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")
            game.screen = py.display.set_mode((game.width, game.height), py.RESIZABLE)

        elif event.type == py.TEXTINPUT and game.active_textbox:
            game.active_textbox.text += event.text

        elif event.type == py.KEYDOWN:
            if game.active_textbox:
                if event.key == py.K_RETURN:
                    if game.building and not game.editing_level:
                        cp_selected = False
                        trigger_selected = False
                        obj_selected = False

                        for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                            if obj.selected:
                                apply_edit(game, obj, game.active_textbox.field_name.lower(), game.active_textbox.text)
                                if obj.shape == "checkpoint": cp_selected = True
                                elif obj.shape == "trigger": trigger_selected = True
                                else: obj_selected = True
                        game.capture_state("do")

                        if not obj_selected and cp_selected:
                            open_menu(game, "checkpoint attributes")
                        elif not obj_selected and trigger_selected:
                            open_menu(game, "trigger attributes")
                        else:
                            game.active_textbox.text = ""
                    
                    else:
                        apply_edit(game, None, game.active_textbox.field_name.lower(), game.active_textbox.text)
                        game.capture_state("do")

                elif event.key == py.K_BACKSPACE:
                    game.active_textbox.text = game.active_textbox.text[:-1]
                
                else:
                    if any(event.key == key for key in game.controls["previous attribute"]):
                        switch_attribute(game, "previous")
                    elif any(event.key == key for key in game.controls["next attribute"]):
                        switch_attribute(game, "next")
                    elif any(event.key == key for key in game.controls["deselect attribute"]):
                        switch_attribute(game, "deselect")

            else:
                if hasattr(game, "name") and game.name:
                    if not game.building:
                        playing_controls = {
                            "click": lambda: click(game, "click", 0, shift, ctrl),
                            "toggle pause": lambda: toggle_pause(game),
                            "restart level": game.restart,

                            "previous checkpoint": lambda: switch_checkpoint(game, "previous"),
                            "next checkpoint": lambda: switch_checkpoint(game, "next"),

                            "previous level": lambda: switch_level(game, "previous"),
                            "next level": lambda: switch_level(game, "next"),

                            "toggle speedhack": lambda: toggle_speedhack(game),
                            "toggle noclip": lambda: setattr(game, "noclip", not game.noclip)
                        }
                        for action, function in playing_controls.items():
                            if any(event.key == key for key in game.controls[action]):
                                function()
                        
                    else:
                        building_controls = {
                            "move or scale": lambda: setattr(game, "scale_mode", not game.scale_mode),
                    
                            "up": lambda: move_scale_objects(game, "up", shift, ctrl, alt),
                            "left": lambda: move_scale_objects(game, "left", shift, ctrl, alt),
                            "down": lambda: move_scale_objects(game, "down", shift, ctrl, alt),
                            "right": lambda: move_scale_objects(game, "right", shift, ctrl, alt),
                    
                            "rotate counter clockwise": lambda: rotate_objects(game, "counter clockwise", shift, ctrl, alt),
                            "rotate clockwise": lambda: rotate_objects(game, "clockwise", shift, ctrl, alt),
                    
                            "flip horizontally": lambda: flip_objects(game, "horizontally"),
                            "flip vertically": lambda: flip_objects(game, "vertically"),
                    
                            "deselect objects": lambda: deselect_objects(game),
                            "duplicate objects": lambda: duplicate_objects(game),
                            "delete objects": lambda: delete_objects(game),
                    
                            "snap grid objects": lambda: snap_grid_objects(game),
                    
                            "group objects": lambda: group_objects(game, "group"),
                            "ungroup objects": lambda: group_objects(game, "ungroup"),
                    
                            "layer objects last": lambda: layer_objects(game, "last"),
                            "layer objects back": lambda: layer_objects(game, "back"),
                            "layer objects forward": lambda: layer_objects(game, "forward"),
                            "layer objects first": lambda: layer_objects(game, "first"),
                    
                            "move objects to background": lambda: move_objects_to_layer(game, "background"),
                            "move objects to objects": lambda: move_objects_to_layer(game, "objects"),
                            "move objects to decoration": lambda: move_objects_to_layer(game, "decoration"),
                    
                            "switch layer": lambda: switch_layer(game, shift),
                            "toggle layer view": lambda: setattr(game, "layer_view", not game.layer_view),
                    
                            "reset camera": lambda: reset_camera(game, ctrl),
                    
                            "undo edit": lambda: undo_edit(game, ctrl),

                            "edit level": lambda: edit_level(game),
                        }
                        for action, function in building_controls.items():
                            if any(event.key == key for key in game.controls[action]):
                                function()
                    
                    universal_controls = {
                        "toggle dark mode": lambda: toggle_dark_mode(game),
                        "toggle debug": lambda: setattr(game, "debug", not game.debug),
                        "toggle buckets": lambda: setattr(game, "show_buckets", not game.show_buckets),
                        "save to file": game.save_to_file,
                
                        "previous attribute": lambda: switch_attribute(game, "previous"),
                        "next attribute": lambda: switch_attribute(game, "next"),
                
                        "toggle hitboxes": lambda: toggle_hitboxes(game),
                
                        "toggle player visibility": lambda: setattr(game, "show_player", not game.show_player),
                    }
                    for action, function in universal_controls.items():
                        if any(event.key == key for key in game.controls[action]):
                            function()

                    operator_controls = {
                        "create level": create_level(game),
                        "toggle building": toggle_building(game)
                    }
                    for action, function in operator_controls.items():
                        if any(event.key == key for key in game.controls[action]):
                            function()

        elif event.type == py.KEYUP:
            if any(event.key == key for key in game.controls["click"]):
                click(game, "release", 0, shift, ctrl)
        
        elif event.type == py.MOUSEBUTTONDOWN:
            click(game, "click", event.button, shift, ctrl)
        elif event.type == py.MOUSEBUTTONUP:
            click(game, "release", event.button, shift, ctrl)
        
        elif event.type == py.MOUSEWHEEL:
            if ctrl:
                scroll(game, event.y)
            elif shift:
                pan(game, event.y)
            elif alt:
                view_separate_hitboxes(game, event.y)
            else:
                zoom(game, event.y)