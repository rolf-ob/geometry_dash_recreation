import pygame as py
import time

from constants import WIDTH, HEIGHT, FIXED_STEP, controls_tutorial, operator_tutorial, settings_tutorial, building_tutorial

def world_to_screen(game, x, y):
    camera_x = game.camera_x if not game.building else game.building_camera_x
    camera_y = game.camera_y if not game.building else game.building_camera_y
    screen_x = ((x - camera_x - WIDTH / 2) * game.camera_zoom + WIDTH / 2) * game.scale
    screen_y = ((y - camera_y - HEIGHT / 2) * game.camera_zoom + HEIGHT / 2) * game.scale
    return int(screen_x), int(screen_y)

def screen_to_world(game, x, y):
    camera_x = game.camera_x if not game.building else game.building_camera_x
    camera_y = game.camera_y if not game.building else game.building_camera_y
    world_x = (x / game.scale - WIDTH / 2) / game.camera_zoom + WIDTH / 2 + camera_x
    world_y = (y / game.scale - HEIGHT / 2) / game.camera_zoom + HEIGHT / 2 + camera_y
    return int(world_x), int(world_y)

def within_view(game, points):
    camera_x = game.camera_x if not game.building else game.building_camera_x
    camera_y = game.camera_y if not game.building else game.building_camera_y
    all_left = all(point[0] < camera_x for point in points)
    all_right = all(point[0] > camera_x + game.view_width for point in points)
    return False if all_left or all_right else True

def draw_polygon(game, screen, points, color, width):
    screen_points = [world_to_screen(game, x, y) for x, y in points]
    py.draw.polygon(screen, color, screen_points, width)

def draw_background(game, screen):
    for obj, points in zip(game.background, game.background_points):
        if within_view(game, points):
            color = (200, 255, 200) if obj.selected else obj.color
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, obj.outline, 1)

def draw_objects(game, screen):
    for obj, points in zip(game.objects, game.object_points):
        if obj.shape == "end":
            if within_view(game, points):
                if game.building:
                    color = (200, 255, 200) if obj.selected else obj.color
                else:
                    color = obj.color if not game.cheated else obj.outline
                draw_polygon(game, screen, points, color, 0)
                if obj.selected:
                    screen.blit(game.text_cache.get_surface(str(obj.x), (0,)*3), world_to_screen(game, obj.x + 5, obj.y + 5))
        
        elif within_view(game, points):
            color = (200, 255, 200) if obj.selected else obj.color
            outline_color = obj.outline if not game.show_hitboxes else (255, 0, 0)
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, outline_color, 1)

def draw_decoration(game, screen):
    for obj, points in zip(game.decoration, game.decoration_points):
        if within_view(game, points):
            color = (200, 255, 200) if obj.selected else obj.color
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, obj.outline, 1)

def draw_checkpoints(game, screen):
    for obj, points in zip(game.checkpoints, game.checkpoint_points):
        text = "S" if obj == game.checkpoints[0] else "C"
        if within_view(game, points):
            color = (200, 255, 200) if obj.selected else obj.color
            draw_polygon(game, screen, points, color, 0)
            draw_polygon(game, screen, points, obj.outline, 1)
            screen.blit(game.text_cache.get_surface(text, (0,)*3), world_to_screen(game, obj.x + 5, obj.y + 5))

def draw_hitbox_trail(game, screen):
    for box, points in zip(game.hitbox_trail, game.hitbox_trail_points):
        if within_view(game, points):
            draw_polygon(game, screen, points, box.outline, 1)
    draw_polygon(game, screen, game.player_points, game.player.color, 1)

def draw_wave_trail(game, screen):
    for i, point in enumerate(game.wave_trail):

        start_top = point
        if game.gamemode == "wave":
            end_top = (game.player.x + 20, game.player.y) if i == len(game.wave_trail) - 1 else game.wave_trail[i + 1]
        else:
            if i == len(game.wave_trail) - 1:
                break
            else:
                end_top = game.wave_trail[i + 1]

        camera_x = game.camera_x if not game.building else game.building_camera_x
        if camera_x < end_top[0] < camera_x + game.view_width or camera_x < start_top[0] < camera_x + game.view_width:
            start_bottom = (point[0], point[1] + 40)

            end_bottom = (game.player.x + 20, game.player.y + 40) if i == len(game.wave_trail) - 1 else (game.wave_trail[i + 1][0], game.wave_trail[i + 1][1] + 40)

            points = [
                world_to_screen(game, *start_top),
                world_to_screen(game, *end_top),
                world_to_screen(game, *end_bottom),
                world_to_screen(game, *start_bottom)
            ]

            py.draw.polygon(screen, game.player.color, points)
            py.draw.polygon(screen, (0,)*3, points, 1)

def draw_player(game, screen):
    draw_polygon(game, screen, game.player_points, game.player.color, 0)
    draw_polygon(game, screen, game.player_points, (0,)*3, 1)

def draw_leaderboard(game, screen):
    if game.current_level != 0:
        text = game.text_cache.get_surface(f"Leaderboard:", (0,)*3)
        margin = 5
        width, height = game.text_cache.get_size(f"Leaderboard:", (0,)*3)
        x, y = (world_to_screen(game, game.level_length + 40, 118))
        py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
        py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
        screen.blit(text, (x, y))

        if game.victors == {}:
            text = game.text_cache.get_surface(f"No victors yet", (0,)*3)
            margin = 5
            width, height = game.text_cache.get_size(f"No victors yet", (0,)*3)
            x, y = (world_to_screen(game, game.level_length + 40, 125 + height))
            py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
            py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
            screen.blit(text, (x, y))
        else:
            for i, (victor, stats) in enumerate(game.victors.items()):
                text = game.text_cache.get_surface(f"{i+1}: {victor} | Completions: {stats[1]} | Attempts: {stats[0]}", (0,)*3)
                margin = 5
                width, height = game.text_cache.get_size(f"{i+1}: {victor} | Completions: {stats[1]} | Attempts: {stats[0]}", (0,)*3)
                x, y = (world_to_screen(game, game.level_length + 40, 125 + i*(height + margin*2 - 2) + height))
                py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
                py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
                screen.blit(text, (x, y))
        
    else:
        players = {}
        for level in game.levels:
            for (victor, stats) in level["victors"].items():
                if stats[1] > 0:
                    if victor in players.keys():
                        players[victor] += level["meta"]["points"]
                    else:
                        players[victor] = level["meta"]["points"]
        
        sorted_players = {}
        for i in range(len(players)):
            for player in players.copy():
                if players[player] == max(players.values()):
                    sorted_players[player] = players[player]
                    del players[player]
        
        screen.blit(game.text_cache.get_surface(f"Total Points Leaderboard:", (0,)*3), world_to_screen(game, 50, 60))
        for i, (player, points) in enumerate(sorted_players.items()):
            screen.blit(game.text_cache.get_surface(f"{i+1}: {player} | Points: {points}", (0,)*3), world_to_screen(game, 50, 85 + 25*i))
        
        if not game.building:
            for i, line in enumerate(controls_tutorial):
                screen.blit(game.text_cache.get_surface(line, (0,)*3), world_to_screen(game, 350, 60 + 25*i))
            
            if game.operator:
                for i, line in enumerate(operator_tutorial):
                    screen.blit(game.text_cache.get_surface(line, (0,)*3), world_to_screen(game, 350, 60 + 25*(len(controls_tutorial)+1) + 25*i))

        else:
            for i, line in enumerate(building_tutorial):
                screen.blit(game.text_cache.get_surface(line, (0,)*3), world_to_screen(game, 350, 60 + 25*i))
        
        for i, line in enumerate(settings_tutorial):
            screen.blit(game.text_cache.get_surface(line, (0,)*3), world_to_screen(game, 850, 60 + 25*i))

def draw_title(game, screen):
    text = game.text_cache.get_surface(f"{game.title[0]}", (0,)*3)
    margin = 10
    width, height = game.text_cache.get_size(f"{game.title[0]}", (0,)*3)
    x, y = (game.width/2 - width/2, 20)
    py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
    py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
    screen.blit(text, (x, y))
    if not game.building and game.current_level != 0:
        text = game.text_cache.get_surface(f"{game.percent}%", (0,)*3)
        margin = 10
        width, height = game.text_cache.get_size("100.0%", (0,)*3)
        x, y = (game.width - width - 20, 20)
        py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
        py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
        screen.blit(text, (x, y))

def draw_textboxes(game, screen):
    for i, box in enumerate(game.textboxes):
        if not box.active:
            text = game.text_cache.get_surface(f"{box.field_name}: {box.text}", (0,)*3)
            margin = 5
            width, height = game.text_cache.get_size(f"{box.field_name}: {box.text}", (0,)*3)
            x, y = (20, i*(height + margin*2 - 2) + height)
            py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
            py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
            screen.blit(text, (x, y))
    
    for i, box in enumerate(game.textboxes):
        if box.active:
            text = game.text_cache.get_surface(f"{box.field_name}: {box.text}", (0,)*3)
            margin = 5
            width, height = game.text_cache.get_size(f"{box.field_name}: {box.text}", (0,)*3)
            x, y = (20, i*(height + margin*2 - 2) + height)
            py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
            py.draw.rect(screen, (0, 200, 0), (x - margin, y - margin, width + margin*2, height + margin*2), 2)
            screen.blit(text, (x, y))

def draw_debug(game, screen):
    debug_items = [
        f"FPS: {game.fps_counter.get_fps()}",
        f"Clicking: {game.clicking}",
        f"Velocity: {round(game.y_vel, 2)}",
        f"Level: {game.current_level}",
        f"Zoom: {round(game.camera_zoom, 1)}",
        f"Deaths: {game.noclip_deaths}",
        f"Cheated: {game.cheated}"
    ]
    for i, item in enumerate(debug_items):
        text = game.text_cache.get_surface(item, (0,)*3)
        margin = 5
        width, height = game.text_cache.get_size(item, (0,)*3)
        x, y = (20, game.height - (len(debug_items)+1)*(height + margin*2 - 2) + i*(height + margin*2 - 2) + height)
        py.draw.rect(screen, (255,)*3, (x - margin, y - margin, width + margin*2, height + margin*2))
        py.draw.rect(screen, (0,)*3, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
        screen.blit(text, (x, y))

def draw(game):
    game.screen.fill(game.background_color)
    screen = game.screen

    draw_background(game, screen)
    draw_objects(game, screen)
    draw_decoration(game, screen)

    if game.building:
        draw_checkpoints(game, screen)
    
    if game.show_hitboxes and len(game.hitbox_trail) > 0:
        draw_hitbox_trail(game, screen)
    
    if game.show_player and game.current_level != 0:
        draw_wave_trail(game, screen)
        draw_player(game, screen)

    if game.completed or game.current_level == 0:
        draw_leaderboard(game, screen)

    if game.title:
        if game.title[1] == -1:
            draw_title(game, screen)
        else:
            if time.perf_counter() > game.title[1]:
                if not game.building:
                    game.title = [game.level["meta"]["title"], -1] if game.current_level == 0 else [f"{game.level["meta"]["title"]} | Points: {str(game.level["meta"]["points"])}", -1]
                else:
                    game.title = [("Background", "Objects", "Decoration")[game.layer], -1]
            else:
                draw_title(game, screen)
    
    draw_textboxes(game, screen)

    if game.debug:
        draw_debug(game, screen)