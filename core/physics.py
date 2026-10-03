from entities.spacial import collide, polygons_collide, get_buckets, get_nearby_objects
from entities.object import Object
from constants import HEIGHT, FIXED_STEP, CAMERA_MARGIN, gamemode_colors

def check_collision(game):
    fall_speed = -game.player.height / game.speed*abs(game.gravity)
    hitbox_color = (0, 255, 0) if game.clicking == 0 else (0, 255, 255)

    game.min_height = game.level["meta"]["roof"]
    game.max_height = game.level["meta"]["floor"] - game.player.height
    game.on_ground = False
    game.slid = game.sliding
    game.sliding = 0
    objects = get_nearby_objects(game.buckets["objects"], game.player.aabb["left"], game.player.aabb["right"])

    for obj in objects:
        if obj.shape in ("square", "spike", "right slope", "left slope", "circle"):
            if collide(game.player, obj):
                this_sliding = False
                prev_player = game.hitboxes[-1].aabb if game.hitboxes else game.player.aabb
                player = game.player.aabb
                on_right_edge = player["left"] <= obj.aabb["right"] < player["left"]+game.speed
                on_left_edge = prev_player["left"] <= obj.aabb["left"] <= player["left"]

                if obj.shape == "square" and obj.rotation == 0:
                    if (player["top"] < obj.aabb["bottom"] < prev_player["top"]) or obj.aabb["bottom"] == player["top"] and not on_right_edge:
                        game.min_height = max(game.min_height, obj.aabb["bottom"])
                        game.y_vel = min(game.y_vel, 0) if game.gravity > 0 else max(game.y_vel, 0)
                        game.sliding = -1
                        this_sliding = True
                    elif (prev_player["bottom"] < obj.aabb["top"] < player["bottom"]) or obj.aabb["top"] == player["bottom"] and not on_right_edge:
                        game.max_height = min(game.max_height, obj.y - game.player.height)
                        game.y_vel = max(game.y_vel, 0) if game.gravity > 0 else min(game.y_vel, 0)
                        game.sliding = 1
                        this_sliding = True

                elif obj.shape in ("right slope", "left slope") and obj.rotation == 0:
                    prev_player_y = (prev_player["bottom"] - obj.y) / obj.height
                    player_y = (player["bottom"] - obj.y) / obj.height

                    if obj.shape == "right slope":
                        prev_y = (prev_player["left"] - obj.x) / obj.width
                        y = (player["left"] - obj.x) / obj.width
                        next_y = (player["left"]+game.speed - obj.x) / obj.width
                        slope_vel = -obj.height / (obj.width * game.gravity)
                    else:
                        prev_y = 1-(prev_player["right"] - obj.x) / obj.width
                        y = 1-(player["right"] - obj.x) / obj.width
                        next_y = 1-(player["right"]+game.speed - obj.x) / obj.width
                        slope_vel = obj.height / (obj.width * game.gravity)
                    
                    if (prev_player["bottom"] < obj.aabb["top"] < player["bottom"]) or obj.aabb["top"] == player["bottom"] and not (on_left_edge or on_right_edge):
                        game.max_height = min(game.max_height, obj.y - game.player.height)
                        game.y_vel = max(game.y_vel, 0) if game.gravity > 0 else min(game.y_vel, 0)
                        game.sliding = 1
                        this_sliding = True
                    elif (prev_player_y <= prev_y and y < player_y) or abs(y - player_y) < 1e-2 and not on_right_edge:
                        game.max_height = min(game.max_height, obj.y - game.player.height + next_y*obj.height)
                        game.y_vel = max(game.y_vel, slope_vel) if game.gravity > 0 else min(game.y_vel, slope_vel)
                        game.sliding = 1
                        this_sliding = True

                elif obj.shape in ("right slope", "left slope") and obj.rotation == 180:
                    prev_player_y = (prev_player["top"] - obj.y) / obj.height
                    player_y = (player["top"] - obj.y) / obj.height

                    if obj.shape == "right slope":
                        prev_y = (prev_player["right"] - obj.x) / obj.width
                        y = (player["right"] - obj.x) / obj.width
                        next_y = (player["right"]+game.speed - obj.x) / obj.width
                        slope_vel = -obj.height / (obj.width * game.gravity)
                    else:
                        prev_y = 1-(prev_player["left"] - obj.x) / obj.width
                        y = 1-(player["left"] - obj.x) / obj.width
                        next_y = 1-(player["left"]+game.speed - obj.x) / obj.width
                        slope_vel = obj.height / (obj.width * game.gravity)

                    if (player["top"] < obj.aabb["bottom"] < prev_player["top"]) or obj.aabb["bottom"] == player["top"] and not (on_left_edge or on_right_edge):
                        game.min_height = max(game.min_height, obj.aabb["bottom"])
                        game.y_vel = min(game.y_vel, 0) if game.gravity > 0 else max(game.y_vel, 0)
                        game.sliding = -1
                        this_sliding = True
                    elif (prev_player_y >= prev_y and y > player_y) or abs(y - player_y) < 1e-2 and not on_right_edge:
                        game.min_height = max(game.min_height, obj.aabb["top"] + next_y*obj.height)
                        game.y_vel = min(game.y_vel, slope_vel) if game.gravity > 0 else max(game.y_vel, slope_vel)
                        game.sliding = -1
                        this_sliding = True

                if not this_sliding and not on_right_edge:
                    if not game.noclip:
                        game.dead = FIXED_STEP
                        hitbox_color = (255, 0, 0) if game.clicking == 0 else (255, 0, 255)
                        break
                    else:
                        if game.hitboxes and game.hitboxes[-1].outline in ((0, 255, 0), (0, 255, 255)):
                            game.cheated = True
                            game.noclip_deaths += 1
                        hitbox_color = (255, 0, 0) if game.clicking == 0 else (255, 0, 255)
                        break

        elif obj.shape == "end":
            if collide(game.player, obj):
                game.completed = True
                if not game.cheated:
                    if game.name in game.victors.keys():
                        game.victors[game.name][1] += 1
                        game.victors[game.name][2] = max(game.victors[game.name][2], game.collected_coins[0])
                        game.victors[game.name][3] = max(game.victors[game.name][3], game.collected_coins[1])
                    else:
                        game.victors[game.name] = (1, 1, game.collected_coins[0], game.collected_coins[1])

        elif obj.shape == "gamemode":
            if collide(game.player, obj) and obj.modifier and (game.hitboxes and not polygons_collide(game.hitboxes[-1], obj)):
                if game.gamemode != obj.modifier:

                    if game.gamemode == "wave":
                        game.wave_trail.append((game.player.x + game.player.width/2, game.player.y))
                    
                    game.gamemode = obj.modifier
                    game.player.color = gamemode_colors[game.gamemode]
                    game.player_render.color = gamemode_colors[game.gamemode]
                    game.player.recompute()

                    if game.gamemode == "wave":
                        game.wave_trail = [(game.player.x + game.player.width/2, game.player.y)]

        elif obj.shape == "speed":
            if collide(game.player, obj) and obj.modifier and (game.hitboxes and not polygons_collide(game.hitboxes[-1], obj)):
                game.speed = float(obj.modifier)

        elif obj.shape == "gravity":
            if collide(game.player, obj) and obj.modifier != None and (game.hitboxes and not polygons_collide(game.hitboxes[-1], obj)) and game.gravity != float(obj.modifier):
                if game.gravity != 0 and obj.modifier != 0 and game.gravity/abs(game.gravity) != float(obj.modifier)/abs(float(obj.modifier)): 
                    game.y_vel *= -1
                game.gravity = float(obj.modifier)
                if game.gamemode == "wave":
                    game.wave_trail.append((game.player.x + game.player.width/2, game.player.y))

        elif obj.shape == "size":
            if collide(game.player, obj) and obj.modifier and (game.hitboxes and not polygons_collide(game.hitboxes[-1], obj)):
                size = float(obj.modifier)*40
                game.player.width = size
                game.player.height = size
                game.player_render.width = size
                game.player_render.height = size
                game.player.recompute()

        elif obj.shape == "teleport":
            if collide(game.player, obj) and obj.modifier != None and (game.hitboxes and not polygons_collide(game.hitboxes[-1], obj)):
                game.player.y = max(game.level["meta"]["roof"], min(game.level["meta"]["floor"] - game.player.height, obj.modifier))
        
        elif obj.shape == "orb":
            if round(game.y_vel) != fall_speed:
                if obj.modifier and obj.modifier != "dash":
                    if not obj.interacted and game.clicking > 0 and not game.clicked and collide(game.player, obj):
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

                elif obj.modifier and not game.clicked:
                    if collide(game.player, obj) and game.clicking > 0:
                        obj.interacted = True
                        game.dashing = obj
                        game.clicked = True
                    elif obj.interacted and game.clicking == 0:
                        obj.interacted = False
                        game.dashing = None
                        game.y_vel = 0
        
        elif obj.shape == "pad":
            if obj.modifier and collide(game.player, obj) and (game.hitboxes and not polygons_collide(game.hitboxes[-1], obj)):
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

        elif obj.shape == "coin":
            if not obj.interacted and not game.cheated and collide(game.player, obj):
                obj.interacted = True
                game.collected_coins[0] += 1
                game.collected_coins[1] += obj.modifier

    if game.dashing and game.clicking == 0:
        game.dashing.interacted = False
        game.dashing = None
        game.y_vel = 0

    if game.player.y == game.max_height:
        if game.gravity > 0:
            game.on_ground = True
            game.y_vel = max(0, game.y_vel)
        else:
            game.y_vel = min(0, game.y_vel)
    elif game.player.y == game.min_height:
        if game.gravity < 0:
            game.on_ground = True
            game.y_vel = max(0, game.y_vel)
        else:
            game.y_vel = min(0, game.y_vel)

    hitbox = Object(game.player.x, game.player.y, game.player.width, game.player.height, 0, "square", (0,)*3, hitbox_color)
    game.hitboxes.append(hitbox)
    for bucket in get_buckets(hitbox):
        game.buckets["hitboxes"][bucket].append(hitbox)

def update_position(game):
    fall_speed = -game.player.height / game.speed*abs(game.gravity)
    if round(game.y_vel) != fall_speed:
        if game.gamemode == "cube":
            if game.clicking > 0 and (game.on_ground or game.sliding * game.gravity > 0):
                game.clicked = True
                game.y_vel = max(game.y_vel, 2.5)
            game.y_vel = max(fall_speed, game.y_vel - 0.05)

        elif game.gamemode == "ship":
            if game.clicking > 0:
                game.clicked = True
                game.y_vel = min(-fall_speed, game.y_vel + 0.035)
            game.y_vel = max(fall_speed, game.y_vel - 0.015)

        elif game.gamemode == "ball":
            if game.clicking > 0 and game.on_ground and not game.clicked:
                game.clicked = True
                game.gravity *= -1
            game.y_vel = max(fall_speed, game.y_vel - 0.05)

        elif game.gamemode == "wave":
            if game.clicking > 0:
                game.clicked = True
                game.y_vel = 1
            else: 
                game.y_vel = -1
            
            if game.wave_trail[-1][1] != game.player.y and (game.player.y in (game.min_height, game.max_height)):
                game.wave_trail.append((game.player.x + game.player.width/2, game.player.y))
            elif game.slid and not game.sliding or not game.slid and game.sliding:
                game.wave_trail.append((game.player.x + game.player.width/2, game.player.y))

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

    if game.dashing:
        y_movement = -max(-90, min(90, (game.dashing.rotation+90) % 360 - 90)) / 45 * game.speed
    else:
        y_movement = game.y_vel*game.speed*game.gravity

    game.player.x += game.speed
    game.player.y = max(game.min_height, min(game.max_height, game.player.y - y_movement))
    game.player.recompute()
    game.camera_x += game.speed
    game.camera_y = max(min(game.camera_y, game.player.y - CAMERA_MARGIN), game.player.y + game.player.height - HEIGHT + CAMERA_MARGIN)

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