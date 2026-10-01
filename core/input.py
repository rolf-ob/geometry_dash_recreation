import pygame as py
import time

from core.building import toggle_building, place_object, select_object, move_scale_objects, rotate_objects, flip_objects, deselect_objects, duplicate_objects, delete_objects, snap_grid_objects, group_objects, layer_objects, move_objects_to_layer, switch_layer, reset_camera, undo_edit, create_level, edit_level, close_menu, open_menu
from constants import HEIGHT, PLAYER_X, FONT_SIZE, CAMERA_MARGIN

def click(game, type, button, shift):
    if button in (0, 1) and not game.building:
        if type == "click":
            game.clicking += 1
            if game.gamemode == "wave":
                game.wave_trail.append((game.player.x + game.player.width/2, game.player.y))
        elif type == "release":
            game.clicking = max(0, game.clicking - 1)
            if game.clicking == 0:
                game.clicked = False
            
            if game.gamemode == "wave":
                game.wave_trail.append((game.player.x + game.player.width/2, game.player.y))
    
    elif button == 1 and type == "release" and not shift:
        place_object(game)
    
    elif button == 3 and game.building and type == "release" and not shift:
        select_object(game, False)

def toggle_pause(game):
    game.paused = not game.paused

    if game.paused:
        py.mouse.set_visible(True)
        open_menu(game, "settings")
        if not game.completed:
            game.cheated = True
    else:
        py.mouse.set_visible(False)
        close_menu(game)
        if not game.completed and (game.show_hitboxes or game.speedhack):
            game.cheated = True

        if game.player.x == game.checkpoints[game.checkpoint].x:
            if game.name not in game.victors.keys():
                game.victors[game.name] = [1, 0, 0, 0]
            else:
                game.victors[game.name][0] += 1
    
    if not game.paused and game.dead == 0 and not game.completed:
        game.camera_x = game.player.x - PLAYER_X
        game.camera_y = game.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN
        game.camera_zoom = 1
        game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")

def switch_checkpoint(game, way):
    if way == "previous":
        game.checkpoint = (game.checkpoint-1) % len(game.checkpoints)
    elif way == "next":
        game.checkpoint = (game.checkpoint+1) % len(game.checkpoints)
    game.restart()
    game.title = [f"Checkpoint {game.checkpoint}/{len(game.checkpoints) - 1}", time.perf_counter() + 0.5]

def switch_level(game, way):
    game.building_camera_x = 0
    game.building_camera_y = game.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN
    if way == "previous":
        game.current_level = (game.current_level-1) % len(game.levels)
    elif way == "next":
        game.current_level = (game.current_level+1) % len(game.levels)
    
    game.load_level()

def toggle_dark_mode(game):
    game.dark_mode = not game.dark_mode
    if game.dark_mode:
        game.primary_color = (255,)*3
        game.secondary_color = (0,)*3
    else:
        game.primary_color = (0,)*3
        game.secondary_color = (255,)*3

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

def zoom(game, y):
    if y > 0 and (game.paused or game.completed or game.building):
        game.camera_zoom += game.camera_zoom/10
        game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")
    elif y < 0 and (game.paused or game.completed or game.building) and game.camera_zoom > 1:
        game.camera_zoom = max(1, game.camera_zoom - game.camera_zoom/10)
        game.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * game.scale * game.camera_zoom)), "world")

def handle_input(game):
    keys = py.key.get_pressed()

    shift = True if keys[py.K_LSHIFT] else False
    ctrl = True if keys[py.K_LCTRL] else False
    alt = True if keys[py.K_LALT] else False

    #Held events
    if any(keys[key] for key in game.controls["step frame"]) and not game.building:
        step_frame(game)
    else:
        game.frame_steps = 0

    if shift and py.mouse.get_pressed()[0] and game.building:
        place_object(game)
    if shift and py.mouse.get_pressed()[2] and game.building:
        select_object(game, shift)

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
                        obj_selected = False
                        cp_selected = False

                        for obj in (*game.background, *game.objects, *game.decoration, *game.checkpoints):
                            if obj.selected:
                                game.apply_edit(obj, game.active_textbox.field_name.lower(), game.active_textbox.text)
                                obj.recompute()
                                game.rebuild_buckets()
                                if obj.shape == "checkpoint": cp_selected = True
                                else: obj_selected = True

                        if not obj_selected and cp_selected:
                            open_menu(game, "checkpoint attributes")
                        else:
                            game.active_textbox.text = ""
                    
                    else:
                        game.apply_edit(None, game.active_textbox.field_name.lower(), game.active_textbox.text)

                elif event.key == py.K_BACKSPACE:
                    game.active_textbox.text = game.active_textbox.text[:-1]
                
                else:
                    if any(event.key == key for key in game.controls["previous attribute"]):
                        game.switch_attribute("previous")
                    elif any(event.key == key for key in game.controls["next attribute"]):
                        game.switch_attribute("next")
                    elif any(event.key == key for key in game.controls["deselect attribute"]):
                        game.switch_attribute("deselect")

            else:
                if not game.building: #Playing controls
                    if any(event.key == key for key in game.controls["click"]):
                        click(game, "click", 0, shift)
                    
                    elif any(event.key == key for key in game.controls["toggle pause"]):
                        toggle_pause(game)
                    
                    elif any(event.key == key for key in game.controls["restart level"]):
                        game.restart()

                    elif any(event.key == key for key in game.controls["previous checkpoint"]):
                        switch_checkpoint(game, "previous")
                    elif any(event.key == key for key in game.controls["next checkpoint"]):
                        switch_checkpoint(game, "next")
                    
                    elif any(event.key == key for key in game.controls["previous level"]):
                        switch_level(game, "previous")
                    elif any(event.key == key for key in game.controls["next level"]):
                        switch_level(game, "next")

                    elif any(event.key == key for key in game.controls["toggle speedhack"]):
                        if game.hitboxes and not game.completed:
                            game.cheated = True
                        game.speedhack = not game.speedhack
                    
                    elif any(event.key == key for key in game.controls["toggle noclip"]):
                        game.noclip = not game.noclip

                else: #Building controls
                    if any(event.key == key for key in game.controls["move or scale"]):
                        game.scale_mode = not game.scale_mode
                    elif any(event.key == key for key in game.controls["up"]):
                        move_scale_objects(game, "up", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["left"]):
                        move_scale_objects(game, "left", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["down"]):
                        move_scale_objects(game, "down", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["right"]):
                        move_scale_objects(game, "right", shift, ctrl, alt)

                    elif any(event.key == key for key in game.controls["rotate counter clockwise"]):
                        rotate_objects(game, "counter clockwise", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["rotate clockwise"]):
                        rotate_objects(game, "clockwise", shift, ctrl, alt)

                    elif any(event.key == key for key in game.controls["flip horizontally"]):
                        flip_objects(game, "horizontally")
                    elif any(event.key == key for key in game.controls["flip vertically"]):
                        flip_objects(game, "vertically")
                    
                    elif any(event.key == key for key in game.controls["deselect objects"]):
                        deselect_objects(game)
                    elif any(event.key == key for key in game.controls["duplicate objects"]):
                        duplicate_objects(game)
                    elif any(event.key == key for key in game.controls["delete objects"]):
                        delete_objects(game)

                    elif any(event.key == key for key in game.controls["snap grid objects"]):
                        snap_grid_objects(game)

                    elif any(event.key == key for key in game.controls["group objects"]):
                        group_objects(game, "group")
                    elif any(event.key == key for key in game.controls["ungroup objects"]):
                        group_objects(game, "ungroup")

                    elif any(event.key == key for key in game.controls["layer objects last"]):
                        layer_objects(game, "last")
                    elif any(event.key == key for key in game.controls["layer objects back"]):
                        layer_objects(game, "back")
                    elif any(event.key == key for key in game.controls["layer objects forward"]):
                        layer_objects(game, "forward")
                    elif any(event.key == key for key in game.controls["layer objects first"]):
                        layer_objects(game, "first")

                    elif any(event.key == key for key in game.controls["move objects to background"]):
                        move_objects_to_layer(game, "background")
                    elif any(event.key == key for key in game.controls["move objects to objects"]):
                        move_objects_to_layer(game, "objects")
                    elif any(event.key == key for key in game.controls["move objects to decoration"]):
                        move_objects_to_layer(game, "decoration")
                    
                    elif any(event.key == key for key in game.controls["switch layer"]):
                        switch_layer(game, shift)
                    elif any(event.key == key for key in game.controls["toggle layer view"]):
                        game.layer_view = not game.layer_view

                    elif any(event.key == key for key in game.controls["reset camera"]):
                        reset_camera(game, ctrl)

                    elif any(event.key == key for key in game.controls["undo edit"]):
                        undo_edit(game, ctrl)
                    
                    elif any(event.key == key for key in game.controls["edit level"]):
                        edit_level(game)

                #Universal controls
                if any(event.key == key for key in game.controls["toggle dark mode"]):
                    toggle_dark_mode(game)
                elif any(event.key == key for key in game.controls["toggle debug"]):
                    game.debug = not game.debug
                elif any(event.key == key for key in game.controls["toggle buckets"]):
                    game.show_buckets = not game.show_buckets
                elif any(event.key == key for key in game.controls["save to file"]):
                    game.save_to_file()
                    
                elif any(event.key == key for key in game.controls["previous attribute"]):
                    game.switch_attribute("previous")
                elif any(event.key == key for key in game.controls["next attribute"]):
                    game.switch_attribute("next")

                elif any(event.key == key for key in game.controls["toggle hitboxes"]):
                    if game.hitboxes and not game.completed:
                        game.cheated = True
                    game.show_hitboxes = not game.show_hitboxes

                elif any(event.key == key for key in game.controls["toggle player visibility"]):
                    game.show_player = not game.show_player

                elif any(event.key == key for key in game.controls["create level"]) and game.operator:
                    create_level(game)
                    
                elif any(event.key == key for key in game.controls["toggle building"]) and game.operator:
                    toggle_building(game)

        elif event.type == py.KEYUP:
            if any(event.key == key for key in game.controls["click"]):
                click(game, "release", 0, shift)
        
        elif event.type == py.MOUSEBUTTONDOWN:
            click(game, "click", event.button, shift)
        elif event.type == py.MOUSEBUTTONUP:
            click(game, "release", event.button, shift)
        
        elif event.type == py.MOUSEWHEEL:
            if ctrl:
                scroll(game, event.y)
            elif shift:
                pan(game, event.y)
            else:
                zoom(game, event.y)