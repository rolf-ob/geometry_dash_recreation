import pygame as py

from constants import FPS, PLAYER_X

def step_frame(game):
    if game.paused:
        if game.frame_steps >= FPS // 3:
            game.frame_steps = FPS // 3 - 2
        game.frame_steps += 1

def click(game, type):
    if type == "click":
        game.clicking += 1
        game.wave_trail.append((game.player.x + 20, game.player.y))
    elif type == "release":
        game.clicking -= 1
        game.wave_trail.append((game.player.x + 20, game.player.y))

def toggle_pause(game):
    game.paused = not game.paused
    if not game.paused and game.dead == 0 and not game.completed:
        game.camera_x = game.player.x - PLAYER_X
        game.camera_y = 0
        game.camera_zoom = 1

def switch_level(game, way):
    if way == "back":
        game.current_level -= 1
    elif way == "forth":
        game.current_level += 1
    game.load_level()

def toggle_building(game):
    game.building = not game.building
    print("coming soon")

def scroll(game, y):
    if y > 0 and (game.paused or game.completed):
        game.camera_y -= 100 / game.camera_zoom
    elif y < 0 and (game.paused or game.completed):
        game.camera_y += 100 / game.camera_zoom

def pan(game, y):
    if y > 0 and (game.paused or game.completed):
        game.camera_x -= 100 / game.camera_zoom
    elif y < 0 and (game.paused or game.completed):
        game.camera_x += 100 / game.camera_zoom

def zoom(game, y):
    if y > 0 and (game.paused or game.completed):
        game.camera_zoom += 0.1
    elif y < 0 and (game.paused or game.completed) and game.camera_zoom > 1:
        game.camera_zoom -= 0.1

def handle_input(game):
    keys = py.key.get_pressed()

    if keys[py.K_c] and game.paused:
        step_frame(game)
    else:
        game.frame_steps = 0
    
    for event in py.event.get():

        if event.type == py.QUIT:
            game.running = False

        elif event.type == py.VIDEORESIZE:
            game.width, game.height = event.size
            game.screen = py.display.set_mode((game.width, game.height), py.RESIZABLE)

        elif event.type == py.KEYDOWN:

            if event.key == py.K_RETURN:
                click(game, "click")
            elif event.key == py.K_w:
                click(game, "click")
            elif event.key == py.K_KP_ENTER:
                click(game, "click")
            elif event.key == py.K_F3:
                game.debug = not game.debug
            elif event.key == py.K_SPACE:
                toggle_pause(game)
            elif event.key == py.K_LEFT:
                switch_level(game, "back")
            elif event.key == py.K_RIGHT:
                switch_level(game, "forth")
            elif event.key == py.K_r:
                game.restart()
            elif event.key == py.K_z:
                game.show_heading = not game.show_heading
            elif event.key == py.K_x:
                game.show_hitboxes = not game.show_hitboxes
            elif event.key == py.K_v:
                game.noclip = not game.noclip
            elif event.key == py.K_b:
                toggle_building(game)

        elif event.type == py.KEYUP:
            if event.key == py.K_RETURN:
                click(game, "release")
            elif event.key == py.K_w:
                click(game, "release")
            elif event.key == py.K_KP_ENTER:
                click(game, "release")
        
        elif event.type == py.MOUSEBUTTONDOWN:
            click(game, "click")
        elif event.type == py.MOUSEBUTTONUP:
            click(game, "release")
        
        elif event.type == py.MOUSEWHEEL:
            if keys[py.K_LCTRL]:
                scroll(game, event.y)
            elif keys[py.K_LSHIFT]:
                pan(game, event.y)
            else:
                zoom(game, event.y)