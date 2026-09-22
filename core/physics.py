from entities.collision import polygons_collide
from entities.object import Object
from rendering.rendering import within_view
from constants import HEIGHT, FIXED_STEP

def update(game):
    if not game.completed and game.dead == 0:
        hitbox_color = (0, 255, 0)
        for obj, points in zip(game.objects, game.object_points):
            if obj.shape != "end":
                if within_view(game, points):
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

        for obj, points in zip(game.objects, game.object_points):
            if obj.shape == "end":
                if within_view(game, points):
                    if polygons_collide(game.player_points, points):
                        game.completed = True
                        if not game.cheated:
                            if game.name not in game.victors.keys():
                                game.victors[game.name] = 1
                            else:
                                game.victors[game.name] += 1

        if not game.completed and game.dead == 0:
            game.camera_x += game.speed
            game.player.x += game.speed

            if game.clicking > 0:
                game.player.y = max(0, min(680, (game.player.y - game.speed*game.gravity)))
            elif game.clicking == 0:
                game.player.y = max(0, min(680, (game.player.y + game.speed*game.gravity)))

            if game.wave_trail[-1][1] != game.player.y and (game.player.y == HEIGHT - 40 or game.player.y == 0):
                game.wave_trail.append((game.player.x + 20, game.player.y))

            game.player_points = game.player.get_points()
            game.percent = min(100.0, round((game.player.x - game.checkpoints[0].x) / (game.level_length - game.checkpoints[0].x - game.player.width)*100, 2))
            hitbox = Object(game.player.x, game.player.y, 40, 40, 0, "square", (0,)*3, hitbox_color)
            game.hitbox_trail.append(hitbox)
            game.hitbox_trail_points.append(hitbox.get_points())

    elif game.dead > 0 or (game.completed and game.cheated):
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