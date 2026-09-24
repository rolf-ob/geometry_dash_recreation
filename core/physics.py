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
                if game.hitbox_trail:
                    prev_player_top = game.hitbox_trail[-1].y
                    prev_player_bottom = game.hitbox_trail[-1].y + 40
                else:
                    prev_player_top = game.player.y
                    prev_player_bottom = game.player.y + 40
                
                player_top = game.player.y
                player_bottom = game.player.y + 40

                if (player_top < obj.y+obj.height < prev_player_top or player_top == obj.y+obj.height) and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                    game.min_height = obj.y+obj.height
                    slide = True
                elif (prev_player_bottom < obj.y < player_bottom or obj.y == player_bottom) and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                    game.max_height = obj.y - 40
                    slide = True

            if game.gamemode == "wave" and game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                game.wave_trail.append((game.player.x + 20, game.player.y))

            elif not slide and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
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
            elif game.gamemode == "wave" and game.wave_trail[-1][1] != game.player.y:
                game.wave_trail.append((game.player.x + 20, game.player.y))

    for (obj, points) in game.ends:
        if within_view(game, points) and polygons_collide(game.player_points, points):
            game.completed = True
            if not game.cheated:
                game.victors[game.name][1] += 1

    for (obj, points) in game.gamemodes:
        if within_view(game, points) and polygons_collide(game.player_points, points) and obj.modifier:
            if game.gamemode != obj.modifier:

                if game.gamemode == "wave":
                    game.wave_trail.append((game.player.x + 20, game.player.y))
                
                game.gamemode = obj.modifier
                if game.gamemode == "wave":
                    game.player.color = (0, 255, 255)
                elif game.gamemode == "cube":
                    game.player.color = (0, 0, 255)
                elif game.gamemode == "ship":
                    game.player.color = (255, 255, 0)
                elif game.gamemode == "ball":
                    game.player.color = (255, 0, 0)
                elif game.gamemode == "ufo":
                    game.player.color = (255, 128, 0)
                elif game.gamemode == "robot":
                    game.player.color = (255, 255, 255)
                elif game.gamemode == "spider":
                    game.player.color = (128, 0, 255)

                if game.gamemode == "wave":
                    game.wave_trail = [(game.player.x + 20, game.player.y)]

    for (obj, points) in game.speeds:
        if within_view(game, points) and polygons_collide(game.player_points, points) and obj.modifier:
            if game.speed != float(obj.modifier):
                game.speed = float(obj.modifier)

    for (obj, points) in game.gravitys:
        if within_view(game, points) and polygons_collide(game.player_points, points) and obj.modifier:
            if game.gravity != float(obj.modifier):
                game.gravity = float(obj.modifier)
                if game.gamemode == "wave":
                    game.wave_trail.append((game.player.x + 20, game.player.y))

    if game.player.y == game.max_height:
        if game.gravity > 0:
            game.on_ground = True
        game.y_vel = 0
    elif game.player.y == game.min_height:
        if game.gravity < 0:
            game.on_ground = True
        game.y_vel = 0

    hitbox = Object(game.player.x, game.player.y, 40, 40, 0, "square", (0,)*3, hitbox_color)
    game.hitbox_trail.append(hitbox)
    game.hitbox_trail_points.append(hitbox.get_points())

def update_position(game):
    game.camera_x += game.speed
    game.player.x += game.speed

    if game.gamemode == "wave":
        game.y_vel = 1 if game.clicking > 0 else -1
        if game.wave_trail[-1][1] != game.player.y and (game.player.y == HEIGHT - 40 or game.player.y == 0):
            game.wave_trail.append((game.player.x + 20, game.player.y))

    elif game.gamemode == "cube":
        if game.clicking > 0 and game.on_ground:
            game.y_vel = 2.5
        game.y_vel = max(-5, game.y_vel - 0.05)

    elif game.gamemode == "ship":
        if game.clicking > 0:
            game.y_vel += 0.035
        game.y_vel = max(-5, game.y_vel - 0.015)

    elif game.gamemode == "ball":
        if game.clicking > 0 and game.on_ground and not game.clicked:
            game.clicked = True
            game.gravity *= -1
        game.y_vel = max(-5, game.y_vel - 0.05)

    elif game.gamemode == "ufo":
        if game.clicking > 0 and not game.clicked:
            game.clicked = True
            game.y_vel = 1.5
        game.y_vel = max(-5, game.y_vel - 0.025)

    elif game.gamemode == "robot":
        if game.clicking > 0 and game.on_ground and not game.clicked:
            game.robot_fuel = 100
            game.clicked = True
            game.y_vel = 1.2
        elif game.clicking > 0 and game.clicked and game.robot_fuel != 0:
            game.robot_fuel -= 1
            game.y_vel = 1.2
        game.y_vel = max(-5, game.y_vel - 0.05)

    elif game.gamemode == "spider":
        if game.clicking > 0 and game.on_ground and not game.clicked:
            game.clicked = True
            game.gravity *= -1
            game.y_vel = -40 / game.speed*abs(game.gravity)
        else:
            game.y_vel = max(-40, game.y_vel - 0.05)

    game.player.y = max(game.min_height, min(game.max_height, game.player.y - game.y_vel*game.speed*game.gravity))

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