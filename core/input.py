import pygame as py

from core.building import place_object, select_object, move_object, delete_object, duplicate, unselect_all, switch_attribute, apply_edit, create_level, edit, switch_layer, toggle_building
from constants import PLAYER_X

def step_frame(game):
    if game.paused:
        if game.frame_steps >= game.settings["fps"] // 3:
            game.frame_steps = game.settings["fps"] // 3 - 2
        game.frame_steps += 1

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

def switch_level(game, way):
    if way == "back":
        if game.current_level % len(game.levels) == 0 and game.levels[-1][2] != []:
            create_level(game)
        game.current_level -= 1
    
    elif way == "forth":
        if game.current_level % len(game.levels) == len(game.levels) - 1 and game.levels[-1][2] != []:
            create_level(game)
        game.current_level += 1
    
    game.load_level()

def restart(game):
    if not game.building:
        game.restart()
    else:
        game.camera_x = 0
        game.camera_y = 0
        game.camera_zoom = 1

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

    if keys[py.K_c] and game.paused:
        step_frame(game)
    else:
        game.frame_steps = 0

    if keys[py.K_LSHIFT] and py.mouse.get_pressed()[0] and game.building:
        place_object(game)
    if keys[py.K_LSHIFT] and py.mouse.get_pressed()[2] and game.building:
        select_object(game, True)
    
    for event in py.event.get():

        if event.type == py.QUIT:
            game.running = False

        elif event.type == py.VIDEORESIZE:
            game.width, game.height = event.size
            game.screen = py.display.set_mode((game.width, game.height), py.RESIZABLE)

        elif event.type == py.TEXTINPUT:
            game.active_textbox.handle_event(event)

        elif event.type == py.KEYDOWN:
            if game.active_textbox:
                if event.key == py.K_RETURN:
                    if game.building:

                        if not game.editing_level:
                            if not game.active_textbox.field_name in ("shape", "rotation", "height") and game.end.selected:
                                apply_edit(game, game.end, game.active_textbox.field_name, game.active_textbox.text)
                                game.end_points = game.end.get_points()

                            for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
                                for i, obj in enumerate(layer):
                                    if obj.selected:
                                        apply_edit(game, obj, game.active_textbox.field_name, game.active_textbox.text)
                                        layer_points[i] = obj.get_points()
                        else:
                            apply_edit(game, None, game.active_textbox.field_name, game.active_textbox.text)

                    else:
                        apply_edit(game, None, game.active_textbox.field_name, game.active_textbox.text)

                    game.active_textbox.handle_event(event)

                elif event.key == py.K_BACKSPACE:
                    game.active_textbox.handle_event(event)
                
                else:
                    for key, way in zip((py.K_UP, py.K_DOWN, py.K_RSHIFT), ("up", "down", "deselect")):
                        if event.key == key:
                            switch_attribute(game, way)

            else:
                if event.key == py.K_RETURN:
                    click(game, "click", 0, keys[py.K_LSHIFT])
                elif event.key == py.K_w:
                    move_object(game, "up", keys[py.K_LSHIFT], keys[py.K_LCTRL])
                    click(game, "click", 0, keys[py.K_LSHIFT])
                elif event.key == py.K_KP_ENTER:
                    click(game, "click", 0, keys[py.K_LSHIFT])
                
                elif event.key == py.K_F3:
                    game.debug = not game.debug
                
                elif event.key == py.K_SPACE:
                    toggle_pause(game)
                
                elif event.key == py.K_LEFT:
                    switch_level(game, "back")
                elif event.key == py.K_RIGHT:
                    switch_level(game, "forth")
                
                elif event.key == py.K_UP:
                    switch_attribute(game, "up")
                elif event.key == py.K_DOWN:
                    switch_attribute(game, "down")
                
                elif event.key == py.K_r:
                    restart(game)

                elif event.key == py.K_z:
                    game.speedhack = not game.speedhack
                
                elif event.key == py.K_x:
                    game.show_hitboxes = not game.show_hitboxes
                
                elif event.key == py.K_v:
                    game.noclip = not game.noclip
                
                elif event.key == py.K_a:
                    move_object(game, "left", keys[py.K_LSHIFT], keys[py.K_LCTRL])
                elif event.key == py.K_s:
                    move_object(game, "down", keys[py.K_LSHIFT], keys[py.K_LCTRL])
                elif event.key == py.K_d:
                    move_object(game, "right", keys[py.K_LSHIFT], keys[py.K_LCTRL])
                
                elif event.key == py.K_BACKSPACE:
                    delete_object(game)
                
                elif event.key == py.K_y:
                    duplicate(game)
                
                elif event.key == py.K_u:
                    unselect_all(game)
                
                elif event.key == py.K_t:
                    edit(game)
                
                elif event.key == py.K_q:
                    switch_layer(game, "back")
                elif event.key == py.K_e:
                    switch_layer(game, "forth")
                
                elif event.key == py.K_b:
                    toggle_building(game)

                elif event.key == py.K_f:
                    game.save_to_file()

        elif event.type == py.KEYUP:
            if event.key == py.K_RETURN:
                click(game, "release", 0, keys[py.K_LSHIFT])
            elif event.key == py.K_w:
                click(game, "release", 0, keys[py.K_LSHIFT])
            elif event.key == py.K_KP_ENTER:
                click(game, "release", 0, keys[py.K_LSHIFT])
        
        elif event.type == py.MOUSEBUTTONDOWN:
            click(game, "click", event.button, keys[py.K_LSHIFT])
        elif event.type == py.MOUSEBUTTONUP:
            click(game, "release", event.button, keys[py.K_LSHIFT])
        
        elif event.type == py.MOUSEWHEEL:
            if keys[py.K_LCTRL]:
                scroll(game, event.y)
            elif keys[py.K_LSHIFT]:
                pan(game, event.y)
            else:
                zoom(game, event.y)