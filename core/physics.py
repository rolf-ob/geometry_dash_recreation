from entities.collision import polygons_collide
from entities.object import Object
from constants import HEIGHT, RESPAWN_TIMER, FPS

def update(game):
    if not game.completed and game.dead == 0:
        #Update position
        game.camera_x += game.speed * 120/FPS
        game.player.x += game.speed * 120/FPS

        #Go up or down
        if game.clicking > 0 and game.player.y > 0:
            game.player.y -= game.speed * 120/FPS
        elif game.clicking == 0 and game.player.y < HEIGHT - 40:
            game.player.y += game.speed * 120/FPS
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
        if game.dead >= RESPAWN_TIMER * FPS:
            game.restart()
        else:
            game.dead += 1