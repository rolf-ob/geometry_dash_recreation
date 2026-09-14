import pygame as py

from constants import WIDTH, HEIGHT

def world_to_screen(game, x, y):
    screen_x = ((x - game.camera_x - WIDTH / 2) * game.camera_zoom + WIDTH / 2) * game.height / HEIGHT
    screen_y = ((y - game.camera_y - HEIGHT / 2) * game.camera_zoom + HEIGHT / 2) * game.height / HEIGHT
    return int(screen_x), int(screen_y)

def screen_to_world(game, x, y):
    world_x = (x / (game.height / HEIGHT) - WIDTH / 2) / game.camera_zoom + WIDTH / 2 + game.camera_x
    world_y = (y / (game.height / HEIGHT) - HEIGHT / 2) / game.camera_zoom + HEIGHT / 2 + game.camera_y
    return int(world_x), int(world_y)

def draw_polygon(game, screen, points, color, width=1):
    screen_points = [world_to_screen(game, x, y) for x, y in points]
    py.draw.polygon(screen, color, screen_points, width)

def draw_background(game, screen):
    for obj, points in zip(game.background, game.background_points):
        if any(game.camera_x < point[0] < game.camera_x + game.width * (HEIGHT / game.height) for point in points):
            color = (200, 255, 200) if obj.selected else obj.color
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, obj.outline, 1)

def draw_objects(game, screen):
    for obj, points in zip(game.objects, game.object_points):
        if any(game.camera_x < point[0] < game.camera_x + game.width * (HEIGHT / game.height) for point in points):
            color = (200, 255, 200) if obj.selected else obj.color
            outline_color = obj.outline if not game.show_hitboxes else (255, 0, 0)
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, outline_color, 1)

def draw_end(game,screen):
    if any(game.camera_x < point[0] < game.camera_x + game.width * (HEIGHT / game.height) for point in game.end_points):
        if game.noclip_deaths == 0:
            color = (200, 255, 200) if game.end.selected else game.end.color
        else:
            color = game.end.outline
        draw_polygon(game, screen, game.end_points, color, 0)

def draw_decoration(game, screen):
    for obj, points in zip(game.decoration, game.decoration_points):
        if any(game.camera_x < point[0] < game.camera_x + game.width * (HEIGHT / game.height) for point in points):
            color = (200, 255, 200) if obj.selected else obj.color
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, obj.outline, 1)

def draw_hitbox_trail(game, screen):
    for box, points in zip(game.hitbox_trail[:-1], game.hitbox_trail_points[:-1]):
        if any(game.camera_x < point[0] < game.camera_x + game.width * (HEIGHT / game.height) for point in points):
            draw_polygon(game, screen, points, box.outline, 1)
    
    draw_polygon(game, screen, game.hitbox_trail_points[-1], game.player.color, 1)

def draw_wave_trail(game, screen):
    for i, point in enumerate(game.wave_trail):
        
        start_top = point
        start_bottom = (point[0], point[1] + 40)

        if i == len(game.wave_trail) - 1:
            end_top = (game.player.x + 20, game.player.y)
            end_bottom = (game.player.x + 20, game.player.y + 40)
        else:
            end_top = game.wave_trail[i + 1]
            end_bottom = (game.wave_trail[i + 1][0], game.wave_trail[i + 1][1] + 40)

        points = [
            world_to_screen(game, *start_top),
            world_to_screen(game, *end_top),
            world_to_screen(game, *end_bottom),
            world_to_screen(game, *start_bottom)
        ]

        if game.camera_x < end_top[0] < game.camera_x + game.width * (HEIGHT / game.height) or game.camera_x < start_top[0] < game.camera_x + game.width * (HEIGHT / game.height):
            py.draw.polygon(screen, game.player.color, points)
            py.draw.polygon(screen, (0,)*3, points, 1)

def draw_debug(game, screen):
    py.draw.rect(game.screen, (255,)*3, (0, HEIGHT - 130, 120, 130))
    py.draw.rect(game.screen, (0,)*3, (0, HEIGHT - 130, 120, 130), 2)
    screen.blit(game.text_cache.get_surface(f"FPS: {game.fps_counter.get_fps()}", (0,)*3), (10, game.height - 120))
    screen.blit(game.text_cache.get_surface(f"Clicking: {game.clicking}", (0,)*3), (10, game.height - 100))
    screen.blit(game.text_cache.get_surface(f"Level: {game.current_level % len(game.levels)}", (0,)*3), (10, game.height - 80))
    screen.blit(game.text_cache.get_surface(f"Zoom: {round(game.camera_zoom, 1)}", (0,)*3), (10, game.height - 60))
    screen.blit(game.text_cache.get_surface(f"Deaths: {game.noclip_deaths}", (0,)*3), (10, game.height - 40))

def draw(game):
    game.screen.fill(game.background_color)

    draw_background(game, game.screen)
    draw_objects(game, game.screen)
    draw_end(game, game.screen)
    draw_decoration(game, game.screen)
    
    if game.show_hitboxes and len(game.hitbox_trail) > 0:
        draw_hitbox_trail(game, game.screen)
    
    #render player and wave trail
    if not (game.building or game.show_hitboxes and (game.completed or game.dead > 0 or game.paused)):
        draw_wave_trail(game, game.screen)
        draw_polygon(game, game.screen, game.player_points, game.player.color, 0)
        draw_polygon(game, game.screen, game.player_points, (0,)*3, 1)

    if game.title[1] != 0:
        py.draw.rect(game.screen, (255,)*3, (0, 0, game.width, 50))
        py.draw.rect(game.screen, (0,)*3, (0, 0, game.width, 50), 1)
        game.screen.blit(game.text_cache.get_surface(f"{game.title[0]}", (0,)*3), (game.width / 2 - 100, 10))
        game.title[1] = -1 if game.title[1] == -1 else game.title[1] - 1
    elif game.building:
        game.title = [("Background", "Objects", "Decoration")[game.layer], -1]
 
    if game.debug:
        draw_debug(game, game.screen)

    for box in game.textboxes:
        box.draw(game.screen, game.font)