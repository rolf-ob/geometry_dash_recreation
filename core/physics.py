from entities.collision import collide, polygons_collide
from entities.object import Object
from constants import HEIGHT, FIXED_STEP, gamemode_colors

def check_collision(game):
    fall_speed = -40 / game.speed*abs(game.gravity)
    hitbox_color = (0, 255, 0) if game.clicking == 0 else (0, 255, 255)

    game.min_height = 0
    game.max_height = HEIGHT - 40
    game.on_ground = False

    for obj in game.shapes:
        slide = False
        if collide(game.player, obj):
            if obj.shape == "square" and obj.rotation == 0:
                prev_player = game.hitbox_trail[-1].aabb if game.hitbox_trail else game.player.aabb
                player = game.player.aabb

                if (player["top"] <= obj.y+obj.height <= prev_player["top"] or player["top"] == obj.y+obj.height) and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                    game.min_height = max(game.min_height, obj.y+obj.height)
                    slide = True
                elif (prev_player["bottom"] <= obj.y <= player["bottom"] or player["bottom"] == obj.y) and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                    game.max_height = min(game.max_height, obj.y - 40)
                    slide = True

            if game.gamemode == "wave" and game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                game.wave_trail.append((game.player.x + 20, game.player.y))

            elif not slide and not game.player.x <= obj.x + obj.width < game.player.x+game.speed:
                if not game.noclip:
                    game.dead = FIXED_STEP
                    hitbox_color = (255, 0, 0) if game.clicking == 0 else (255, 0, 255)
                    break
                else:
                    if game.hitbox_trail and game.hitbox_trail[-1].outline in ((0, 255, 0), (0, 255, 255)):
                        game.cheated = True
                        game.noclip_deaths += 1
                    hitbox_color = (255, 0, 0) if game.clicking == 0 else (255, 0, 255)
                    break
            elif game.gamemode == "wave" and game.wave_trail[-1][1] != game.player.y:
                game.wave_trail.append((game.player.x + 20, game.player.y))

    for obj in game.ends:
        if collide(game.player, obj):
            game.completed = True
            if not game.cheated:
                if game.name in game.victors.keys():
                    game.victors[game.name][1] += 1
                    game.victors[game.name][2] = max(game.victors[game.name][2], game.collected_coins[0])
                    game.victors[game.name][3] = max(game.victors[game.name][3], game.collected_coins[1])
                else:
                    game.victors[game.name] = (1, 1, game.collected_coins[0], game.collected_coins[1])

    for obj in game.gamemodes:
        if collide(game.player, obj) and obj.modifier and (game.hitbox_trail and not polygons_collide(game.hitbox_trail[-1], obj)):
            if game.gamemode != obj.modifier:

                if game.gamemode == "wave":
                    game.wave_trail.append((game.player.x + 20, game.player.y))
                
                game.gamemode = obj.modifier
                game.player.color = gamemode_colors[game.gamemode]
                game.player.recompute()

                if game.gamemode == "wave":
                    game.wave_trail = [(game.player.x + 20, game.player.y)]

    for obj in game.speeds:
        if collide(game.player, obj) and obj.modifier and (game.hitbox_trail and not polygons_collide(game.hitbox_trail[-1], obj)):
            if game.speed != float(obj.modifier):
                game.speed = float(obj.modifier)

    for obj in game.gravitys:
        if collide(game.player, obj) and obj.modifier and (game.hitbox_trail and not polygons_collide(game.hitbox_trail[-1], obj)) and game.gravity != float(obj.modifier):
            if game.gravity != 0 and obj.modifier != 0 and game.gravity/abs(game.gravity) != float(obj.modifier)/abs(float(obj.modifier)): 
                game.y_vel *= -1
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
    
    for obj in game.orbs:
        if round(game.y_vel) != fall_speed:
            if obj.modifier and obj.modifier != "dash":
                if not obj.interacted and game.clicking > 0 and not game.clicked and not game.on_ground and collide(game.player, obj):
                    obj.interacted = True
                    game.clicked = True

                    ship_multiplier = 0.3
                    ufo_multiplier = 0.7

                    if obj.modifier == "small" and game.gamemode != "wave":
                        game.y_vel = max(game.y_vel, 2)
                        if game.gamemode == "ship":
                            game.y_vel *= ship_multiplier
                        elif game.gamemode == "ufo":
                            game.y_vel *= ufo_multiplier

                    elif obj.modifier == "normal" and game.gamemode != "wave":
                        game.y_vel = max(game.y_vel, 3)
                        if game.gamemode == "ship":
                            game.y_vel *= ship_multiplier
                        elif game.gamemode == "ufo":
                            game.y_vel *= ufo_multiplier

                    elif obj.modifier == "big" and game.gamemode != "wave":
                        game.y_vel = max(game.y_vel, 4)
                        if game.gamemode == "ship":
                            game.y_vel *= ship_multiplier
                        elif game.gamemode == "ufo":
                            game.y_vel *= ufo_multiplier

                    elif obj.modifier == "gravity" and game.gamemode != "wave":
                        game.gravity *= -1
                        game.y_vel = -1

                    elif obj.modifier == "heavy" and game.gamemode != "wave":
                        game.y_vel = min(game.y_vel, -4)

            elif obj.modifier and not game.clicked and not game.on_ground:
                if collide(game.player, obj) and game.clicking > 0:
                    obj.interacted = True
                    game.clicked = True
                elif obj.interacted and game.clicking == 0:
                    obj.interacted = False
                    game.y_vel = 0

                if obj.interacted:
                    game.dashing = True
                else:
                    game.dashing = False
    
    for obj in game.pads:
        if obj.modifier and collide(game.player, obj) and (game.hitbox_trail and not polygons_collide(game.hitbox_trail[-1], obj)):
            ship_multiplier = 0.5
            ufo_multiplier = 0.7
            
            if obj.modifier == "small" and game.gamemode != "wave":
                game.y_vel = max(game.y_vel, 2)
                if game.gamemode == "ship":
                    game.y_vel *= ship_multiplier
                elif game.gamemode == "ufo":
                    game.y_vel *= ufo_multiplier

            elif obj.modifier == "normal" and game.gamemode != "wave":
                game.y_vel = max(game.y_vel, 3)
                if game.gamemode == "ship":
                    game.y_vel *= ship_multiplier
                elif game.gamemode == "ufo":
                    game.y_vel *= ufo_multiplier

            elif obj.modifier == "big" and game.gamemode != "wave":
                game.y_vel = max(game.y_vel, 4)
                if game.gamemode == "ship":
                    game.y_vel *= ship_multiplier
                elif game.gamemode == "ufo":
                    game.y_vel *= ufo_multiplier

            elif obj.modifier == "gravity" and game.gamemode != "wave":
                game.gravity *= -1
                game.y_vel = -1
                if game.gamemode == "ship":
                    game.y_vel *= ship_multiplier
                elif game.gamemode == "ufo":
                    game.y_vel *= ufo_multiplier

            elif obj.modifier == "spider" and game.gamemode != "wave":
                game.gravity *= -1
                game.y_vel = fall_speed

    for obj in game.coins:
        if not obj.interacted and not game.cheated and collide(game.player, obj):
            obj.interacted = True
            game.collected_coins[0] += 1
            game.collected_coins[1] += obj.modifier

    game.hitbox_trail.append(Object(game.player.x, game.player.y, 40, 40, 0, "square", (0,)*3, hitbox_color))

def update_position(game):
    fall_speed = -40 / game.speed*abs(game.gravity)

    if round(game.y_vel) != fall_speed:
        if game.gamemode == "cube":
            if game.clicking > 0 and game.on_ground:
                game.clicked = True
                game.y_vel = max(game.y_vel, 2.5)
            game.y_vel = max(fall_speed, game.y_vel - 0.05)

        elif game.gamemode == "ship":
            if game.clicking > 0:
                game.clicked = True
                game.y_vel += 0.035
            game.y_vel = max(fall_speed, game.y_vel - 0.015)

        elif game.gamemode == "ball":
            if game.clicking > 0 and game.on_ground and not game.clicked:
                game.clicked = True
                game.gravity *= -1
            game.y_vel = max(fall_speed, game.y_vel - 0.05)

        elif game.gamemode == "wave":
            game.y_vel = 1 if game.clicking > 0 else -1
            if game.wave_trail[-1][1] != game.player.y and (game.player.y == HEIGHT - 40 or game.player.y == 0):
                game.wave_trail.append((game.player.x + 20, game.player.y))

        elif game.gamemode == "ufo":
            if game.clicking > 0 and not game.clicked:
                game.clicked = True
                game.y_vel = max(game.y_vel, 1.5)
            game.y_vel = max(fall_speed, game.y_vel - 0.025)

        elif game.gamemode == "robot":
            if game.clicking > 0 and game.on_ground and not game.clicked:
                game.robot_fuel = 100
                game.clicked = True
                game.y_vel = max(game.y_vel, 1.2)
            elif game.clicking > 0 and game.clicked and game.robot_fuel != 0:
                game.robot_fuel -= 1
                game.y_vel = max(game.y_vel, 1.2)
            game.y_vel = max(fall_speed, game.y_vel - 0.05)

        elif game.gamemode == "spider":
            if game.clicking > 0 and game.on_ground and not game.clicked:
                game.clicked = True
                game.gravity *= -1
                game.y_vel = fall_speed
            else:
                game.y_vel = max(fall_speed, game.y_vel - 0.05)
    
    game.camera_x += game.speed
    game.player.x += game.speed
    game.player.y = max(game.min_height, min(game.max_height, game.player.y - game.y_vel*game.speed*game.gravity)) if not game.dashing else game.player.y
    game.player.recompute()

    start_x = game.player.x - game.checkpoints[0].x
    checkpoint_x = game.checkpoints[game.checkpoint].x - game.checkpoints[0].x
    end_x = game.level_length - game.checkpoints[0].x - game.player.width
    game.starting_percent = 0 if end_x == 0 else min(100, round(checkpoint_x / end_x * 100))
    game.percent = 0 if end_x == 0 else min(100, round(start_x / end_x * 100))

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