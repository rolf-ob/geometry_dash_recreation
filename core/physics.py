from entities.collision import polygons_collide
from entities.object import Object
from constants import HEIGHT

def update(game):
    if not game.completed and game.dead == 0:
        #Update position
        game.camera_x += game.speed * 120/game.settings["fps"]
        game.player.x += game.speed * 120/game.settings["fps"]

        #Go up or down
        if game.clicking > 0 and game.player.y > 0:
            game.player.y = max(0, (game.player.y - game.speed * 120/game.settings["fps"]))
        elif game.clicking == 0 and game.player.y < HEIGHT - 40:
            game.player.y = min(680, (game.player.y + game.speed * 120/game.settings["fps"]))
        elif game.wave_trail[-1][1] != game.player.y:
            game.wave_trail.append((game.player.x + 20, game.player.y))
        
        #Collision
        game.player_points = game.player.get_points()
        hitbox_color = (0, 255, 0)

        for points in game.object_points:
            if polygons_collide(game.player_points, points):
                if not game.noclip:
                    game.dead = 1
                    hitbox_color = (255, 0, 0)
                    break
                else:
                    if game.hitbox_trail and game.hitbox_trail[-1].outline == (0, 255, 0):
                        game.noclip_deaths += 1
                    hitbox_color = (255, 0, 0)
                    break
            
        if polygons_collide(game.player_points, game.end_points):
            game.completed = True

        hitbox = Object("square", (0,)*3, hitbox_color, 0, 40, 40, game.player.x, game.player.y)
        game.hitbox_trail.append(hitbox)
        game.hitbox_trail_points.append(hitbox.get_points())

    elif game.dead > 0:
        if not game.speedhack:
            if game.dead >= game.settings["respawn time"] * game.settings["fps"]:
                game.restart()
            else:
                game.dead += 1
        else:
            if game.dead >= game.settings["respawn time"] * game.settings["fps"] * game.settings["speedhack multiplier"]:
                game.restart()
            else:
                game.dead += 1