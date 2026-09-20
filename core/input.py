import pygame as py

from core.building import toggle_building, place_object, select_object, move_objects, rotate_objects, flip_objects, deselect_objects, duplicate_objects, delete_objects, snap_grid_objects, switch_layer, reset_camera, create_level, edit_level, close_menu, open_menu
from core.textbox import TextBox
from constants import PLAYER_X, WIDTH, HEIGHT

def click(game, type, button, shift):
    if button in (0, 1) and not game.building:
        if type == "click":
            game.clicking += 1
            game.wave_trail.append((game.player.x + 20, game.player.y))
        elif type == "release":
            game.clicking = max(0, game.clicking - 1)
            game.wave_trail.append((game.player.x + 20, game.player.y))
    
    elif button == 1 and type == "release" and not shift:
        place_object(game)
    
    elif button == 3 and game.building and type == "release" and not shift:
        select_object(game, False)

def toggle_pause(game):
    game.paused = not game.paused
    if not game.paused and game.dead == 0 and not game.completed and not game.building:
        game.camera_x = game.player.x - PLAYER_X
        game.camera_y = 0
        game.camera_zoom = 1

    if not game.building:
        if game.paused:
            open_menu(game, "settings")
        else:
            close_menu(game)

def switch_checkpoint(game, way):
    if way == "previous":
        game.checkpoint += 1
    elif way == "next":
        game.checkpoint -= 1
    game.restart()
    game.title = [f"Checkpoint {game.checkpoint % len(game.checkpoints)}/{len(game.checkpoints) - 1}", 0.5]

def switch_level(game, way):
    if way == "previous":
        game.current_level -= 1
    elif way == "next":
        game.current_level += 1
    
    game.load_level()

def step_frame(game):
    if game.paused:
        game.cheated = True
        if game.frame_steps >= game.fps // 3:
            game.frame_steps = game.fps // 3 - 2
        game.frame_steps += 1

def scroll(game, y):
    if y > 0 and (game.paused or game.completed or game.building):
        game.camera_y -= 100 / game.camera_zoom
    elif y < 0 and (game.paused or game.completed or game.building):
        game.camera_y += 100 / game.camera_zoom

def pan(game, y):
    if y > 0 and (game.paused or game.completed or game.building):
        game.camera_x -= 100 / game.camera_zoom
    elif y < 0 and (game.paused or game.completed or game.building):
        game.camera_x += 100 / game.camera_zoom

def zoom(game, y):
    if y > 0 and (game.paused or game.completed or game.building):
        game.camera_zoom += 0.1
    elif y < 0 and (game.paused or game.completed or game.building) and game.camera_zoom > 1:
        game.camera_zoom -= 0.1

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
            game.scale = game.height / HEIGHT
            game.screen = py.display.set_mode((game.width, game.height), py.RESIZABLE)

        elif event.type == py.TEXTINPUT:
            game.active_textbox.handle_event(event)

        elif event.type == py.KEYDOWN:
            if game.active_textbox:
                if event.key == py.K_RETURN:
                    if game.building:
                        if not game.editing_level:
                            if not game.active_textbox.field_name in ("Shape", "Rotation", "Height") and game.end.selected:
                                game.apply_edit(game.end, game.active_textbox.field_name.lower(), game.active_textbox.text)
                                game.end_points = game.end.get_points()

                            for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
                                for i, obj in enumerate(layer):
                                    if obj.selected:
                                        game.apply_edit(obj, game.active_textbox.field_name.lower(), game.active_textbox.text)
                                        layer_points[i] = obj.get_points()
                        
                        else:
                            game.apply_edit(None, game.active_textbox.field_name.lower(), game.active_textbox.text)
                    else:
                        game.apply_edit(None, game.active_textbox.field_name.lower(), game.active_textbox.text)
                    
                    if game.active_textbox.field_name == "Delete" and game.active_textbox.text == "delete":
                        game.building = False
                
                        close_menu(game)
                        game.editing_level = False
                        
                        if game.paused:
                            open_menu(game, "settings")
                        
                        game.load_level()

                    elif game.active_textbox.field_name != "Name":
                        game.active_textbox.text = ""
                            
                    elif not game.end.selected and not any(obj.selected for obj in (*game.background, *game.objects, *game.decoration)) and not game.editing_level:
                        close_menu(game)

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
                        game.cheated = True
                        game.speedhack = not game.speedhack
                    
                    elif any(event.key == key for key in game.controls["toggle noclip"]):
                        game.noclip = not game.noclip

                else: #Building controls
                    if any(event.key == key for key in game.controls["move up"]):
                        move_objects(game, "up", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["move left"]):
                        move_objects(game, "left", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["move down"]):
                        move_objects(game, "down", shift, ctrl, alt)
                    elif any(event.key == key for key in game.controls["move right"]):
                        move_objects(game, "right", shift, ctrl, alt)

                    elif any(event.key == key for key in game.controls["rotate counter clockwise"]):
                        rotate_objects(game, "counter clockwise")
                    elif any(event.key == key for key in game.controls["rotate clockwise"]):
                        rotate_objects(game, "clockwise")

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
                    
                    elif any(event.key == key for key in game.controls["previous layer"]):
                        switch_layer(game, "previous")
                    elif any(event.key == key for key in game.controls["next layer"]):
                        switch_layer(game, "next")

                    elif any(event.key == key for key in game.controls["reset camera"]):
                        reset_camera(game)
                    
                    elif any(event.key == key for key in game.controls["edit level"]):
                        edit_level(game)

                #Universal controls
                if any(event.key == key for key in game.controls["toggle debug"]):
                    game.debug = not game.debug
                elif any(event.key == key for key in game.controls["save to file"]):
                    game.save_to_file()
                    
                elif any(event.key == key for key in game.controls["previous attribute"]):
                    game.switch_attribute("previous")
                elif any(event.key == key for key in game.controls["next attribute"]):
                    game.switch_attribute("next")

                elif any(event.key == key for key in game.controls["toggle hitboxes"]):
                    game.cheated = True
                    game.show_hitboxes = not game.show_hitboxes

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