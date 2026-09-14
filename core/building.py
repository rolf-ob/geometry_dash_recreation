import pygame as py

from core.textbox import TextBox
from entities.object import Object
from entities.collision import polygons_collide
from rendering.rendering import screen_to_world
from constants import HEIGHT

def place_object(game):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse_pos = [(mouse_x - 1, mouse_y), (mouse_x, mouse_y), (mouse_x + 1, mouse_y)]
    mouse_x -= mouse_x % 40
    mouse_y -= mouse_y % 40

    if not any(polygons_collide(mouse_pos, points) for points in (game.background_points, game.object_points, game.decoration_points)[game.layer]):
        game.level_data[game.layer + 1].append(Object(game.shape, (255,)*3, (0,)*3, game.rotation, 40, 40, mouse_x, mouse_y))
        (game.background_points, game.object_points, game.decoration_points)[game.layer].append((game.background, game.objects, game.decoration)[game.layer][-1].get_points())

def select_object(game, shifting):
    mouse_x, mouse_y = screen_to_world(game, *py.mouse.get_pos())
    mouse_pos = [(mouse_x - 1, mouse_y), (mouse_x, mouse_y), (mouse_x + 1, mouse_y)]

    if polygons_collide(mouse_pos, game.end_points) and not game.editing_level:
        if shifting:
                game.end.selected = True
        else:
            game.end.selected = not game.end.selected
        if game.end.selected and game.textboxes == []:
                game.textboxes = [
                    TextBox(200, 40, 20, 20, "shape"),
                    TextBox(200, 40, 20, 60, "color"),
                    TextBox(200, 40, 20, 100, "outline"),
                    TextBox(200, 40, 20, 140, "rotation"),
                    TextBox(200, 40, 20, 180, "width"),
                    TextBox(200, 40, 20, 220, "height")
                ]
    
    for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
        for obj, points in zip(layer, layer_points):
            if polygons_collide(mouse_pos, points) and obj in (game.background, game.objects, game.decoration)[game.layer] and not game.editing_level:
                if shifting:
                    obj.selected = True
                else:
                    obj.selected = not obj.selected
                if obj.selected and game.textboxes == []:
                        game.textboxes = [
                            TextBox(200, 40, 20, 20, "shape"),
                            TextBox(200, 40, 20, 60, "color"),
                            TextBox(200, 40, 20, 100, "outline"),
                            TextBox(200, 40, 20, 140, "rotation"),
                            TextBox(200, 40, 20, 180, "width"),
                            TextBox(200, 40, 20, 220, "height")
                        ]

    if not game.end.selected and not any(obj.selected for obj in (*game.background, *game.objects, *game.decoration)) and not game.editing_level:
        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None

def move_object(game, direction, shift, ctrl):
    if game.building:
        if shift:
            distance = 1
        elif ctrl:
            distance = 200
        else:
            distance = 40
        add_x = 0
        add_y = 0
        
        if direction == "up":
            add_y = -distance
        elif direction == "left":
            add_x = -distance
        elif direction == "down":
            add_y = distance
        elif direction == "right":
            add_x = distance

        if game.end.selected:
            game.end.x += add_x
            game.end.y += add_y
            game.end_points = game.end.get_points()

        for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
            for i, obj in enumerate(layer):
                if obj.selected:
                    obj.x += add_x
                    obj.y += add_y
                    layer_points[i] = obj.get_points()

def delete_object(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
        for obj, points in zip(layer.copy(), layer_points.copy()):
            if obj.selected:
                layer.remove(obj)
                layer_points.remove(points)
    
    game.textboxes = []
    if game.active_textbox:
        game.active_textbox.deactivate()
        game.active_textbox = None

def duplicate(game):
    for layer, layer_points in zip((game.background, game.objects, game.decoration), (game.background_points, game.object_points, game.decoration_points)):
        for obj in layer.copy():
            if obj.selected:
                layer.append(Object(obj.shape, obj.color, obj.outline, obj.rotation, obj.width, obj.height, obj.x, obj.y))
                layer_points.append(layer[-1].get_points())

def unselect_all(game):
    game.end.selected = False
    for layer in (game.background, game.objects, game.decoration):
        for obj in layer:
            obj.selected = False
    game.textboxes = []
    if game.active_textbox:
        game.active_textbox.deactivate()
        game.active_textbox = None

def switch_attribute(game, way):
    if game.textboxes != []:
        if way == "up":
            if not game.active_textbox:
                game.active_textbox = game.textboxes[-1]
                game.active_textbox.activate()
            else:
                game.active_textbox.deactivate()
                game.active_textbox = game.textboxes[(game.textboxes.index(game.active_textbox) - 1) % len(game.textboxes)]
                game.active_textbox.activate()

        elif way == "down":
            if not game.active_textbox:
                game.active_textbox = game.textboxes[0]
                game.active_textbox.activate()
            else:
                game.active_textbox.deactivate()
                game.active_textbox = game.textboxes[(game.textboxes.index(game.active_textbox) + 1) % len(game.textboxes)]
                game.active_textbox.activate()

        elif way == "deselect":
            if game.active_textbox:
                game.active_textbox.deactivate()
                game.active_textbox = None

def apply_edit(game, obj, field_name, text):
    try:
        if game.building:
            if not game.editing_level:
                if field_name in ("rotation", "width", "height"):
                    setattr(obj, field_name, min(720, max(1, int(text))))
                    if field_name == "rotation":
                        game.rotation = int(text)
                
                elif field_name in ("color", "outline"):
                    r, g, b = (max(0, min(255, int(value))) for value in text.split(","))
                    setattr(obj, field_name, (r, g, b))

                elif field_name == "shape" and text in ("square", "spike", "slope"):
                    setattr(obj, field_name, text)
                    game.shape = text

            else:
                if field_name == "gamemode" and text in ("wave"):
                    game.level_data[0][0] = text

                elif field_name == "starting height":
                    game.level_data[0][1] = max(0, min(680, int(text)))

                elif field_name == "speed":
                    game.level_data[0][2] = int(text)

                elif field_name == "gravity":
                    game.level_data[0][3] = int(text)

                elif field_name == "background":
                    r, g, b = (max(0, min(255, int(value))) for value in text.split(","))
                    game.level_data[0][4] = (r, g, b)
                    game.background_color = game.level_data[0][4]

                elif field_name == "title":
                    game.level_data[0][5] = text

        else:
            if field_name == "player color":
                r, g, b = (max(0, min(255, int(value))) for value in text.split(","))
                game.player.color = (r, g, b)

            elif field_name == "speedhack":
                game.settings["speedhack multiplier"] = max(0, float(text))

            elif field_name == "fps":
                game.settings["fps"] = int(text)

            elif field_name == "respawn time":
                game.settings["respawn time"] = float(text)

    except ValueError:
        pass

def create_level(game):
    game.levels.append([["wave", 680, 4, 0, (255,)*3, "Unnamed level"], [], [], [], Object("end", (0, 255, 0), (255, 0, 0), 0, 1, HEIGHT, 500, 0)])

def edit(game):
    if game.building:
        game.editing_level = not game.editing_level
        if game.editing_level:

            for layer in (game.background, game.objects, game.decoration):
                for obj in layer:
                    obj.selected = False
            game.textboxes = [
                TextBox(200, 40, 20, 20, "gamemode"),
                TextBox(200, 40, 20, 60, "starting height"),
                TextBox(200, 40, 20, 100, "speed"),
                TextBox(200, 40, 20, 140, "gravity"),
                TextBox(200, 40, 20, 180, "background"),
                TextBox(200, 40, 20, 220, "title")
            ]
            if game.active_textbox:     
                game.active_textbox.deactivate()
                game.active_textbox = None

        else:
            game.textboxes = []
            if game.active_textbox:
                game.active_textbox.deactivate()
                game.active_textbox = None

    else:
        game.editing_settings = not game.editing_settings
        if game.editing_settings:
            game.textboxes = [
                TextBox(200, 40, 20, 20, "player color"),
                TextBox(200, 40, 20, 60, "speedhack"),
                TextBox(200, 40, 20, 100, "fps"),
                TextBox(200, 40, 20, 140, "respawn time")
            ]
        else:
            game.textboxes = []
            if game.active_textbox:
                game.active_textbox.deactivate()
                game.active_textbox = None

def switch_layer(game, way):
    if game.building:
        if way == "back":
            game.layer = max(0, game.layer - 1)
        if way == "forth":
            game.layer = min(2, game.layer + 1)
        
        game.title = [("Background", "Objects", "Decoration")[game.layer], -1]

def toggle_building(game):
    game.building = not game.building
    if game.building:
        game.player.y = game.level_data[0][1]
        game.noclip_deaths = 0
        game.hitbox_trail = []
        game.hitbox_trail_points = []
        game.wave_trail = []
        game.layer = 1
        game.title = ["Objects", -1]

        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None
        game.editing_settings = False

    else:
        for obj in game.background:
            obj.selected = False
        for obj in game.objects:
            obj.selected = False
        for obj in game.decoration:
            obj.selected = False

        game.textboxes = []
        if game.active_textbox:
            game.active_textbox.deactivate()
            game.active_textbox = None
        game.editing_level = False
        
        game.load_level()