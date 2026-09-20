from entities.collision import polygons_collide
from entities.object import Object
from constants import HEIGHT, FIXED_STEP

def update(game):
    if not game.completed and game.dead == 0:
        game.camera_x += game.speed
        game.player.x += game.speed

        if game.clicking > 0 and game.player.y > 0:
            game.player.y = max(0, (game.player.y - game.speed))
        elif game.clicking == 0 and game.player.y < HEIGHT - 40:
            game.player.y = min(680, (game.player.y + game.speed))
        elif game.wave_trail[-1][1] != game.player.y:
            game.wave_trail.append((game.player.x + 20, game.player.y))
        
        game.player_points = game.player.get_points()
        hitbox_color = (0, 255, 0)

        for points in game.object_points:
            if any(game.camera_x < point[0] < game.camera_x + game.view_width for point in points):
                if polygons_collide(game.player_points, points):
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
            
        if polygons_collide(game.player_points, game.end_points):
            game.completed = True
            if not game.cheated and game.name not in game.victors.keys():
                game.victors[game.name] = 1
            elif not game.cheated:
                game.victors[game.name] += 1

        hitbox = Object(game.player.x, game.player.y, 40, 40, 0, "square", (0,)*3, hitbox_color)
        game.hitbox_trail.append(hitbox)
        game.hitbox_trail_points.append(hitbox.get_points())

    elif game.dead > 0:
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