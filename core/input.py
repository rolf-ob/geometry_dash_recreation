import pygame as py

from entities.object import Object
from constants import FPS, PLAYER_X, WIDTH, HEIGHT

def screen_to_world(game, x, y):
    world_x = (x / (game.height / HEIGHT) - WIDTH / 2) / game.camera_zoom + WIDTH / 2 + game.camera_x
    world_y = (y / (game.height / HEIGHT) - HEIGHT / 2) / game.camera_zoom + HEIGHT / 2 + game.camera_y
    return int(world_x), int(world_y)

def step_frame(game):
    if game.paused:
        if game.frame_steps >= FPS // 3:
            game.frame_steps = FPS // 3 - 2
        game.frame_steps += 1

def click(game, type, button):
    if button in (0, 1):
            if type == "click":
                game.clicking += 1
                game.wave_trail.append((game.player.x + 20, game.player.y))
            elif type == "release":
                game.clicking -= 1
                game.wave_trail.append((game.player.x + 20, game.player.y))
    
    if button == 1 and game.building:
        if type == "click":
            pass
        elif type == "release":
            game.level_data[game.layer].append(Object("square", (255,)*3, (0,)*3, 0, 40, 40, *screen_to_world(game, *py.mouse.get_pos())))
            if game.layer == 1:
                game.background_points.append(game.background[-1].get_points())
            elif game.layer == 2:
                game.object_points.append(game.objects[-1].get_points())
            elif game.layer == 3:
                game.decoration_points.append(game.decoration[-1].get_points())
    #! Swiping to select and place, snapping to grid. copy-pasting, duplicating
    elif button == 2 and game.building: #! Right click to edit (change shape, color, outline, rotation, size, position and delete, change layer) using textboxes to type in values
        pass #! Ability to change level settings (player.y, speed, background color, title)
#! Read whatever claude wrote about moving click and switch level to another file
def toggle_pause(game):
    game.paused = not game.paused
    if not game.paused and game.dead == 0 and not game.completed and not game.building:
        game.camera_x = game.player.x - PLAYER_X
        game.camera_y = 0
        game.camera_zoom = 1

def switch_level(game, way):
    if way == "back":
        if game.current_level % game.level_amount == 0 and game.levels[-1][2] != []:
            game.levels.append([[680, 4, (255,)*3, "Unnamed level"], [], [], [], Object("end", (0, 255, 0), (255, 0, 0), 0, 1, HEIGHT, 3000, 0)])
        game.current_level -= 1
    elif way == "forth":
        if game.current_level % game.level_amount == game.level_amount and game.levels[-1][2] != []:
            game.levels.append([[680, 4, (255,)*3, "Unnamed level"], [], [], [], Object("end", (0, 255, 0), (255, 0, 0), 0, 1, HEIGHT, 3000, 0)])
        game.current_level += 1
    game.load_level()

def restart(game):
    if not game.building:
        game.restart()
    else:
        game.camera_x = 0
        game.camera_y = 0
        game.camera_zoom = 1

def toggle_building(game):
    game.building = not game.building
    if game.building:
        game.player.y = game.level_data[0][0]
        game.noclip_deaths = 0
        game.hitbox_trail = []
        game.hitbox_trail_points = []
        game.wave_trail = []
        game.layer = 2
        game.title = ["Objects", -1]
    else:
        game.load_level()

def switch_layer(game, way):
    if game.building:
        if way == "back":
            game.layer = max(1, game.layer - 1)
        if way == "forth":
            game.layer = min(3, game.layer + 1)
        
        layers = ["Background", "Objects", "Decoration"]
        game.title = [layers[game.layer - 1], -1]

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
    
    for event in py.event.get():

        if event.type == py.QUIT:
            game.running = False

        elif event.type == py.VIDEORESIZE:
            game.width, game.height = event.size
            game.screen = py.display.set_mode((game.width, game.height), py.RESIZABLE)

        elif event.type == py.KEYDOWN:

            if event.key == py.K_RETURN:
                click(game, "click", 0)
            elif event.key == py.K_w:
                click(game, "click", 0)
            elif event.key == py.K_KP_ENTER:
                click(game, "click", 0)
            elif event.key == py.K_F3:
                game.debug = not game.debug
            elif event.key == py.K_SPACE:
                toggle_pause(game)
            elif event.key == py.K_LEFT:
                switch_level(game, "back")
            elif event.key == py.K_RIGHT:
                switch_level(game, "forth")
            elif event.key == py.K_r:
                restart(game)
            elif event.key == py.K_x:
                game.show_hitboxes = not game.show_hitboxes
            elif event.key == py.K_v:
                game.noclip = not game.noclip
            elif event.key == py.K_b:
                toggle_building(game)
            elif event.key == py.K_q:
                switch_layer(game, "back")
            elif event.key == py.K_e:
                switch_layer(game, "forth")

        elif event.type == py.KEYUP:
            if event.key == py.K_RETURN:
                click(game, "release", 0)
            elif event.key == py.K_w:
                click(game, "release", 0)
            elif event.key == py.K_KP_ENTER:
                click(game, "release", 0)
        
        elif event.type == py.MOUSEBUTTONDOWN:
            click(game, "click", event.button)
        elif event.type == py.MOUSEBUTTONUP:
            click(game, "release", event.button)
        
        elif event.type == py.MOUSEWHEEL:
            if keys[py.K_LCTRL]:
                scroll(game, event.y)
            elif keys[py.K_LSHIFT]:
                pan(game, event.y)
            else:
                zoom(game, event.y)