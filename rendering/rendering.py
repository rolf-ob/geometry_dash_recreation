import pygame as py
import time, math

from entities.spatial import get_nearby_objects
from constants import WIDTH, HEIGHT, BUCKET_WIDTH, controls_tutorial, operator_tutorial, settings_tutorial, building_tutorial

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

def draw_polygon(game, screen, points, color, width):
    screen_points = [world_to_screen(game, x, y) for x, y in points]
    py.draw.polygon(screen, color, screen_points, width)

def draw_floor_roof(game, screen):
    roof = world_to_screen(game, 0, game.level["meta"]["roof"])[1]
    floor = world_to_screen(game, 0, game.level["meta"]["floor"])[1]
    py.draw.rect(screen, game.roof_color, (0, 0, game.width, roof))
    py.draw.rect(screen, game.floor_color, (0, floor, game.width, game.height))
    py.draw.line(screen, game.primary_color, (0, roof), (game.width, roof), int(max(1, 1*game.camera_zoom)))
    py.draw.line(screen, game.primary_color, (0, floor), (game.width, floor), int(max(1, 1*game.camera_zoom)))

def draw_background(game, screen):
    camera_x = game.building_camera_x if game.building else game.camera_x
    objects = get_nearby_objects(game.buckets["background"], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0], game.z_order)
    for obj in objects:
        color = (200, 255, 200) if obj.selected else obj.color
        if color == (0, 0):
            if game.building:
                draw_polygon(game, screen, obj.points, (128, 255, 255), 0)
        else:
            draw_polygon(game, screen, obj.points, color, 0)
        draw_polygon(game, screen, obj.points, obj.outline, int(max(1, 1*game.camera_zoom)))

def draw_objects(game, screen):
    camera_x = game.building_camera_x if game.building else game.camera_x
    objects = get_nearby_objects(game.buckets["objects"], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0], game.z_order)
    for obj in objects:
        if obj.shape == "end":
            if game.building:
                color = (200, 255, 200) if obj.selected else obj.color
            else:
                color = obj.color if not game.cheated else obj.outline
            
            if color == (0, 0):
                if game.building:
                    draw_polygon(game, screen, obj.points, (128, 255, 255), 0)
            else:
                draw_polygon(game, screen, obj.points, color, 0)
            
            if obj.selected:
                screen.blit(game.text_cache.get_surface(str(obj.x), game.primary_color, "world"), world_to_screen(game, obj.x + 5, obj.aabb["bottom"]- 30))

        elif obj.shape == "orb" and obj.modifier == "dash":
            color = (200, 255, 200) if obj.selected else obj.color
            outline_color = (255, 0, 0) if game.show_hitboxes else obj.outline
            outline_thickness = 1 if game.show_hitboxes else int(max(1, 1*game.camera_zoom))

            if color == (0, 0):
                if game.building:
                    draw_polygon(game, screen, obj.points, (128, 255, 255), 0)
            else:
                draw_polygon(game, screen, obj.points, color, 0)
            
            if outline_color == (0, 0):
                if game.show_hitboxes:
                    draw_polygon(game, screen, obj.points, outline_color, outline_thickness)
            else:
                draw_polygon(game, screen, obj.points, outline_color, outline_thickness)

        elif obj.shape == "coin":
            if not obj.interacted:
                color = (200, 255, 200) if obj.selected else obj.color
                outline_color = (255, 0, 0) if game.show_hitboxes else obj.outline
                outline_thickness = 1 if game.show_hitboxes else int(max(1, 1*game.camera_zoom))

                if color == (0, 0):
                    if game.building:
                        draw_polygon(game, screen, obj.points, (128, 255, 255), 0)
                        screen.blit(game.text_cache.get_surface(str(obj.modifier), (0,)*3, "world"), world_to_screen(game, game.text_cache.get_size(str(obj.modifier))[0] / 2, obj.y + 5))
                else:
                    draw_polygon(game, screen, obj.points, color, 0)
                    screen.blit(game.text_cache.get_surface(str(obj.modifier), (0,)*3, "world"), world_to_screen(game, obj.x + obj.width / 2 - game.text_cache.get_size(str(obj.modifier), (0,)*3, "world")[0] / 2, obj.y + 5))
                
                if outline_color == (0, 0):
                    if game.show_hitboxes:
                        draw_polygon(game, screen, obj.points, outline_color, outline_thickness)
                else:
                    draw_polygon(game, screen, obj.points, outline_color, outline_thickness)

        elif obj.shape == "text":
            color = (200, 255, 200) if obj.selected else obj.color
            outline_color = (255, 0, 0) if game.show_hitboxes else obj.outline
            outline_thickness = 1 if game.show_hitboxes else int(max(1, 1*game.camera_zoom))

            if color == (0, 0):
                if game.building:
                    screen.blit(game.text_cache.get_surface(obj.modifier, color, "world"), world_to_screen(game, obj.x + obj.width / 2 - game.text_cache.get_size(obj.modifier, (0,)*3, "world")[0] / 2, obj.y + 5))
            else:
                screen.blit(game.text_cache.get_surface(obj.modifier, color, "world"), world_to_screen(game, obj.x + obj.width / 2 - game.text_cache.get_size(obj.modifier, (0,)*3, "world")[0] / 2, obj.y + 5))
            
            if outline_color == (0, 0):
                if game.show_hitboxes:
                    draw_polygon(game, screen, obj.points, outline_color, outline_thickness)
            else:
                draw_polygon(game, screen, obj.points, outline_color, outline_thickness)
        
        else:
            color = (200, 255, 200) if obj.selected else obj.color
            outline_color = (255, 0, 0) if game.show_hitboxes else obj.outline
            outline_thickness = 1 if game.show_hitboxes else int(max(1, 1*game.camera_zoom))

            if color == (0, 0):
                if game.building:
                    draw_polygon(game, screen, obj.points, (128, 255, 255), 0)
            else:
                draw_polygon(game, screen, obj.points, color, 0)
            
            if outline_color == (0, 0):
                if game.show_hitboxes:
                    draw_polygon(game, screen, obj.points, outline_color, outline_thickness)
            else:
                draw_polygon(game, screen, obj.points, outline_color, outline_thickness)

def draw_decoration(game, screen):
    camera_x = game.building_camera_x if game.building else game.camera_x
    objects = get_nearby_objects(game.buckets["decoration"], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0], game.z_order)
    for obj in objects:
        color = (200, 255, 200) if obj.selected else obj.color
        if color == (0, 0):
            if game.building:
                draw_polygon(game, screen, obj.points, (128, 255, 255), 0)
        else:
            draw_polygon(game, screen, obj.points, color, 0)
        draw_polygon(game, screen, obj.points, obj.outline, int(max(1, 1*game.camera_zoom)))

def draw_checkpoints(game, screen):
    camera_x = game.building_camera_x if game.building else game.camera_x
    objects = get_nearby_objects(game.buckets["checkpoints"], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0])
    for obj in objects:
        text = "S" if obj == game.checkpoints[0] else "C"
        color = (200, 255, 200) if obj.selected else obj.color
        draw_polygon(game, screen, obj.points, color, 0)
        draw_polygon(game, screen, obj.points, obj.outline, int(max(1, 1*game.camera_zoom)))
        screen.blit(game.text_cache.get_surface(text, (0,)*3, "world"), world_to_screen(game, obj.x + 5, obj.y + 5))

def draw_hitboxes(game, screen):
    camera_x = game.building_camera_x if game.building else game.camera_x
    objects = get_nearby_objects(game.buckets["hitboxes"], screen_to_world(game, 0, 0)[0], screen_to_world(game, game.width, 0)[0])

    if game.show_hitboxes:
        for obj in objects[:len(objects) - game.current_hitbox]:
            draw_polygon(game, screen, obj.points, obj.outline, 1)
        draw_polygon(game, screen, game.player.points, game.player.color, 1)
    
    elif game.current_hitbox != 0:
        obj = game.hitboxes[-game.current_hitbox]
        draw_polygon(game, screen, obj.points, obj.outline, 1)

def draw_wave_trail(game, screen):
    for i, point in enumerate(game.wave_trail):

        start_top = point
        if game.gamemode == "wave":
            end_top = (game.player.x + game.player.width/2, game.player.y) if i == len(game.wave_trail) - 1 else game.wave_trail[i + 1]
        else:
            if i == len(game.wave_trail) - 1: break
            else: end_top = game.wave_trail[i + 1]

        screen_start = screen_to_world(game, 0, 0)[0]
        screen_end = screen_to_world(game, game.width, 0)[0]
        if screen_start < end_top[0] < screen_end or screen_start < start_top[0] < screen_end:
            start_bottom = (point[0], point[1] + game.player.height)
            end_bottom = (game.player.x + game.player.width/2, game.player.y + game.player.height) if i == len(game.wave_trail) - 1 else (game.wave_trail[i + 1][0], game.wave_trail[i + 1][1] + game.player.height)
            points = [
                world_to_screen(game, *start_top),
                world_to_screen(game, *end_top),
                world_to_screen(game, *end_bottom),
                world_to_screen(game, *start_bottom)
            ]
            py.draw.polygon(screen, (0, 255, 255), points)
            py.draw.line(screen, (0,)*3, points[0], points[1], int(max(1, 1*game.camera_zoom)))
            py.draw.line(screen, (0,)*3, points[2], points[3], int(max(1, 1*game.camera_zoom)))

def draw_player(game, screen):
    if game.hitboxes:
        prev_player = game.hitboxes[-1]
    else:
        prev_player = game.player

    x_diff = game.speed
    y_diff = game.player.y - prev_player.y
    radians = math.atan(y_diff / x_diff)
    angle = math.degrees(radians)
    theta = math.radians(abs(angle))
    dip_amount = (
        game.player.width / 2 *
        (math.sin(theta) + math.cos(theta) - 1)
    )
    if angle < 0: dip_amount *= -1
    dip = -game.sliding * dip_amount
    game.player_render.x = game.player.x + dip
    game.player_render.y = game.player.y
    game.player_render.rotation = angle
    game.player_render.recompute()

    draw_polygon(game, screen, game.player_render.points, game.player.color, 0)
    draw_polygon(game, screen, game.player_render.points, game.primary_color, int(max(1, 1*game.camera_zoom)))

def draw_buckets(game, screen):
    camera_x = game.building_camera_x if game.building else game.camera_x 
    start_bucket = int(camera_x // BUCKET_WIDTH)
    end_bucket = int((camera_x + game.view_width) // BUCKET_WIDTH)

    for bucket in range(start_bucket, end_bucket+2):
        top = world_to_screen(game, bucket*400, game.camera_y)
        bottom = world_to_screen(game, bucket*400, game.camera_y + game.view_height)
        py.draw.line(screen, (0, 255, 0), top, bottom, 1)

def draw_leaderboard(game, screen):
    if game.current_level != 0:
        text = game.text_cache.get_surface(f"Leaderboard:", game.primary_color, "world")
        margin = 5
        width, height = game.text_cache.get_size(f"Leaderboard:", game.primary_color, "world")
        x, y = (world_to_screen(game, game.level_length + 40, 125))
        py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
        py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
        screen.blit(text, (x, y))

        if game.victors:
            sorted_victors = sorted(
                game.victors.items(),
                key=lambda item: item[1][1],
                reverse=True
            )
            for i, (victor, stats) in enumerate(sorted_victors):
                text = game.text_cache.get_surface(f"{i+1}: {victor} | Completions: {stats[1]} | Coins: {stats[2]} | Attempts: {stats[0]}", game.primary_color, "world")
                margin = 5
                width, height = game.text_cache.get_size(f"{i+1}: {victor} | Completions: {stats[1]} | Coins: {stats[2]} | Attempts: {stats[0]}", game.primary_color, "world")
                x, y = (world_to_screen(game, game.level_length + 40, 160 + 36*i))
                py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
                py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
                screen.blit(text, (x, y))
        
        else:
            text = game.text_cache.get_surface(f"No stats yet", game.primary_color, "world")
            margin = 5
            width, height = game.text_cache.get_size(f"No stats yet", game.primary_color, "world")
            x, y = x, y = (world_to_screen(game, game.level_length + 40, 160))
            py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
            py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
            screen.blit(text, (x, y))
        
    else:
        players = {}
        for level in game.levels:
            for (victor, stats) in level["victors"].items():
                if stats[1] > 0:
                    if victor in players.keys():
                        players[victor] += level["meta"]["points"]
                        players[victor] += stats[3]
                    else:
                        players[victor] = level["meta"]["points"]
                        players[victor] += stats[3]
        
        sorted_players = sorted(
            players.items(),
            reverse=True
        )
        
        screen.blit(game.text_cache.get_surface(f"Total Points Leaderboard:", game.primary_color, "world"), world_to_screen(game, 50, 60))
        for i, (player, points) in enumerate(sorted_players):
            screen.blit(game.text_cache.get_surface(f"{i+1}: {player} | Points: {points}", game.primary_color, "world"), world_to_screen(game, 50, 85 + 25*i))
        
        if not game.building:
            for i, line in enumerate(controls_tutorial):
                screen.blit(game.text_cache.get_surface(line, game.primary_color, "world"), world_to_screen(game, 350, 60 + 25*i))
            
            if game.operator:
                for i, line in enumerate(operator_tutorial):
                    screen.blit(game.text_cache.get_surface(line, game.primary_color, "world"), world_to_screen(game, 350, 60 + 25*(len(controls_tutorial)+1) + 25*i))

        else:
            for i, line in enumerate(building_tutorial):
                screen.blit(game.text_cache.get_surface(line, game.primary_color, "world"), world_to_screen(game, 350, 60 + 25*i))
        
        for i, line in enumerate(settings_tutorial):
            screen.blit(game.text_cache.get_surface(line, game.primary_color, "world"), world_to_screen(game, 850, 60 + 25*i))

def draw_title(game, screen):
    text = game.text_cache.get_surface(f"{game.title[0]}", game.primary_color, "screen")
    margin = 10
    width, height = game.text_cache.get_size(f"{game.title[0]}", game.primary_color, "screen")
    x, y = (game.width/2 - width/2, 20)
    py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
    py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
    screen.blit(text, (x, y))
    if not game.building and game.current_level != 0:
        text = game.text_cache.get_surface(f"{game.starting_percent}%-{game.percent}%", game.primary_color, "screen")
        margin = 10
        width, height = game.text_cache.get_size(f"{game.starting_percent}%-{game.percent}%", game.primary_color, "screen")
        x, y = (game.width - width - 20, 20)
        py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
        py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
        screen.blit(text, (x, y))

def draw_textboxes(game, screen):
    for i, box in enumerate(game.textboxes):
        if not box.active:
            text = game.text_cache.get_surface(f"{box.field_name}: {box.text}", game.primary_color, "screen")
            margin = 5
            width, height = game.text_cache.get_size(f"{box.field_name}: {box.text}", game.primary_color, "screen")
            x, y = (20, i*(height + margin*2 - 2) + height)
            py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
            py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
            screen.blit(text, (x, y))
    
    for i, box in enumerate(game.textboxes):
        if box.active:
            text = game.text_cache.get_surface(f"{box.field_name}: {box.text}", game.primary_color, "screen")
            margin = 5
            width, height = game.text_cache.get_size(f"{box.field_name}: {box.text}", game.primary_color, "screen")
            x, y = (20, i*(height + margin*2 - 2) + height)
            py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
            py.draw.rect(screen, (0, 200, 0), (x - margin, y - margin, width + margin*2, height + margin*2), 2)
            screen.blit(text, (x, y))

def draw_debug(game, screen):
    debug_items = [
        f"FPS: {game.fps_counter.get_fps()}",
        f"Clicking: {game.clicking}",
        f"Velocity: {round(game.y_vel, 2)}",
        f"Speed: {game.speed}",
        f"Gravity: {game.gravity}",
        f"Level: {game.current_level}",
        f"Zoom: {round(game.camera_zoom, 1)}",
        f"Deaths: {game.noclip_deaths}",
        f"Cheated: {game.cheated}"
    ]
    for i, item in enumerate(debug_items):
        text = game.text_cache.get_surface(item, game.primary_color, "screen")
        margin = 5
        width, height = game.text_cache.get_size(item, game.primary_color, "screen")
        x, y = (20, game.height - (len(debug_items)+1)*(height + margin*2 - 2) + i*(height + margin*2 - 2) + height)
        py.draw.rect(screen, game.secondary_color, (x - margin, y - margin, width + margin*2, height + margin*2))
        py.draw.rect(screen, game.primary_color, (x - margin, y - margin, width + margin*2, height + margin*2), 2)
        screen.blit(text, (x, y))

def draw(game):
    screen = game.screen

    if game.background_color == (0,)*3:
        game.screen.fill(game.primary_color)
    elif game.background_color == (255,)*3:
        game.screen.fill(game.secondary_color)
    else:
        game.screen.fill(game.background_color)

    if game.current_level != 0:
        draw_floor_roof(game, screen)
    
    if game.building:
        if game.layer_view:
            if game.layer == 0:
                draw_background(game, screen)
            elif game.layer == 1:
                draw_objects(game, screen)
            elif game.layer == 2:
                draw_decoration(game, screen)
        else:
            draw_background(game, screen)
            draw_objects(game, screen)
            draw_decoration(game, screen)
            draw_checkpoints(game, screen)
    else:
        draw_background(game, screen)
        draw_objects(game, screen)
        draw_decoration(game, screen)
    
    if game.hitboxes:
        draw_hitboxes(game, screen)
    
    if game.show_player and game.current_level != 0:
        draw_wave_trail(game, screen)
        draw_player(game, screen)

    if game.show_buckets:
        draw_buckets(game, screen)

    if game.completed or game.paused or game.current_level == 0:
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