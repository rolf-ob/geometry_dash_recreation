from entities.collision import polygons_collide
from entities.object import Object
from rendering.rendering import within_view
from constants import HEIGHT, FIXED_STEP

def check_collision(game):
    hitbox_color = (0, 255, 0)

    game.min_height = 0
    game.max_height = HEIGHT - 40
    game.on_ground = False
    for (obj, points) in game.shapes:
        slide = False
        if within_view(game, points) and polygons_collide(game.player_points, points):
            if obj.shape == "square" and obj.rotation % 360 == 0:
                if game.player.y+40 - game.speed < obj.y <= game.player.y+40 and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                    game.max_height = game.player.y
                    game.on_ground = True
                    slide = True
                elif game.player.y <= obj.y+obj.height < game.player.y+game.speed and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                    game.min_height = game.player.y
                    slide = True

            if game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                game.wave_trail.append((game.player.x + 20, game.player.y))

            elif not slide:
                if not game.noclip:
                        game.dead = FIXED_STEP
                        hitbox_color = (255, 0, 0)
                        break
                else:
                    if game.hitbox_trail and game.hitbox_trail[-1].outline == (0, 255, 0):
                        game.cheated = True
                        game.noclip_deaths += 1
                    hitbox_color = (255, 0, 0)
                    break
            elif game.wave_trail[-1][1] != game.player.y:
                game.wave_trail.append((game.player.x + 20, game.player.y))

    for (obj, points) in game.ends:
        if within_view(game, points) and polygons_collide(game.player_points, points):
            game.completed = True
            if not game.cheated:
                game.victors[game.name][1] += 1

    for (obj, points) in game.gamemodes:
        if within_view(game, points) and polygons_collide(game.player_points, points) and obj.modifier:
            if game.gamemode != obj.modifier:
                game.gamemode = obj.modifier

    for (obj, points) in game.speeds:
        if within_view(game, points) and polygons_collide(game.player_points, points) and obj.modifier:
            if game.speed != float(obj.modifier):
                game.speed = float(obj.modifier)

    for (obj, points) in game.gravitys:
        if within_view(game, points) and polygons_collide(game.player_points, points) and obj.modifier:
            if game.gravity != float(obj.modifier):
                game.gravity = float(obj.modifier)
                game.wave_trail.append((game.player.x + 20, game.player.y))

    if game.player.y == game.max_height:
        game.on_ground = True

    hitbox = Object(game.player.x, game.player.y, 40, 40, 0, "square", (0,)*3, hitbox_color)
    game.hitbox_trail.append(hitbox)
    game.hitbox_trail_points.append(hitbox.get_points())

def update_position(game):
    game.camera_x += game.speed
    game.player.x += game.speed
    if game.gamemode == "wave":
        if game.clicking > 0:
            game.player.y = max(game.min_height, min(game.max_height, game.player.y - game.speed*game.gravity))
        elif game.clicking == 0:
            game.player.y = max(game.min_height, min(game.max_height, game.player.y + game.speed*game.gravity))
        
        if game.wave_trail[-1][1] != game.player.y and (game.player.y == HEIGHT - 40 or game.player.y == 0):
            game.wave_trail.append((game.player.x + 20, game.player.y))

    elif game.gamemode == "cube":
        if game.clicking > 0 and game.on_ground:
            game.y_vel = 12
        
        game.player.y = max(game.min_height, min(game.max_height, game.player.y - game.y_vel*game.speed*game.gravity))
        if game.y_vel > 2.5:
            game.y_vel = game.y_vel - game.y_vel / 3
        elif game.y_vel < -2.5:
            game.y_vel = game.y_vel + game.y_vel / 3
        elif game.y_vel > 0.5:
            game.y_vel = game.y_vel - game.y_vel / 5
        elif game.y_vel < -0.5:
            game.y_vel = game.y_vel + game.y_vel / 5
        else:
            game.y_vel -= 0.015

    game.player_points = game.player.get_points()
    game.percent = min(100.0, round((game.player.x - game.checkpoints[0].x) / (game.level_length - game.checkpoints[0].x - game.player.width)*100, 2))

def update_death_timer(game):
    if not game.speedhack:
        if game.dead >= game.respawn_time:
            game.restart()
        else:
            game.dead += FIXED_STEP
    else:
        if game.dead >= game.respawn_time * game.speedhack_multiplier:
            game.restart()
        else:
            game.dead += FIXED_STEP

def update(game):
    if not game.completed and game.dead == 0:

        check_collision(game)

        if not game.completed and game.dead == 0:
            update_position(game)

    elif game.dead > 0 or (game.completed and game.cheated):
        update_death_timer(game)