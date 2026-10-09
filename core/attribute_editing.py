import pygame as py
from pathlib import Path
import re

from constants import gamemode_colors, speed_color, gravity_colors, size_colors, teleport_color, orb_pad_colors, coin_color
from entities.spatial import get_buckets
from core.building import toggle_building

def switch_attribute(game, way):
    if game.textboxes:
        if way == "previous":
            if not game.active_textbox:
                game.active_textbox = game.textboxes[-1]
                game.active_textbox.activate()
            else:
                game.active_textbox.deactivate()
                game.active_textbox = game.textboxes[(game.textboxes.index(game.active_textbox) - 1) % len(game.textboxes)]
                game.active_textbox.activate()

        elif way == "next":
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

def apply_edit(game, obj, real_field_name, text):
    field_name = real_field_name.split("_")[-1]
    real = "real_" if len(real_field_name.split("_")) > 1 else ""
    try:
        if game.building or real == "real_":
            if not game.editing_level:
                if obj.real_shape not in ("checkpoint", "trigger"):
                    if field_name == "width":
                        setattr(obj, real_field_name, max(0, int(text)))
                    elif field_name == "height":
                        setattr(obj, real_field_name, max(0, int(text)))
                    elif field_name == "rotation":
                        rotation = float(text)
                        rotation %= 360
                        if rotation < 0:
                            rotation += 360
                        setattr(obj, real_field_name, round(rotation, 1))
                    
                    elif field_name in ("color", "outline"):
                        rgb = text.split()
                        if len(rgb) == 3:
                            r, g, b = (max(0, min(255, int(value))) for value in rgb)
                            setattr(obj, real_field_name, (r, g, b))
                        elif len(rgb) == 1 and rgb[0] == "0":
                            setattr(obj, real_field_name, (0, 0))

                    elif field_name == "shape" and text in ("square", "spike", "circle", "end", "gamemode", "speed", "gravity", "size", "teleport", "orb", "pad", "trigger", "coin", "text"):
                        setattr(obj, real_field_name, text)

                        if real == "":
                            if text == "end":
                                obj.y = 0
                                obj.width = 1
                                obj.height = 720
                                obj.color = (0, 255, 0)
                                obj.outline = (255, 0, 0)

                            elif text == "gamemode":
                                obj.width = 40
                                obj.height = 120

                            elif text == "speed":
                                obj.width = 40
                                obj.height = 120
                                obj.color = speed_color

                            elif text == "gravity":
                                obj.width = 20
                                obj.height = 120

                            elif text == "size":
                                obj.width = 20
                                obj.height = 80

                            elif text == "teleport":
                                obj.width = 20
                                obj.height = 120
                                obj.color = teleport_color

                            elif text == "orb":
                                obj.width = 40
                                obj.height = 40

                            elif text == "pad":
                                obj.width = 40
                                obj.height = 10
                                obj.y += 10

                            elif text == "trigger":
                                obj.triggers = 0
                                obj.modifier = {"attribute": "", "value": "", "transition": ""}

                            elif text == "coin":
                                obj.width = 40
                                obj.height = 40
                                obj.color = coin_color

                    elif field_name == "shape" and text == "slope":
                        setattr(obj, real_field_name, "right slope")

                    elif field_name == "shape" and text == "checkpoint":
                        setattr(obj, real_field_name, text)
                        for layer, name in zip((game.background, game.objects, game.decoration), ("background", "objects", "decoration")):
                            if obj in layer:
                                layer.remove(obj)
                                game.checkpoints.append(obj)

                                for bucket in get_buckets(obj):
                                    game.buckets[name][bucket].remove(obj)
                                for bucket in get_buckets(obj):
                                    game.buckets["checkpoints"][bucket].append(obj)

                                break
                        
                        obj.width = 40
                        obj.height = 40
                        obj.rotation = 0
                        obj.color = (0, 255, 0)
                        obj.outline = (0,)*3
                        obj.modifier = {"gamemode": "cube", "speed": 2, "gravity": 1, "size": 1}
                        obj.recompute()

                    elif field_name == "modifier":
                        if obj.real_shape == "gamemode" and text in ("cube", "ship", "ball", "wave", "ufo", "robot", "spider"):
                            setattr(obj, real_field_name, text)
                            if real == "":
                                obj.color = gamemode_colors[text]

                        elif obj.real_shape == "speed":
                            setattr(obj, real_field_name, max(0.01, min(40, float(text))))

                        elif obj.real_shape == "gravity":
                            setattr(obj, real_field_name, float(text))
                            if real == "" and int(text) in gravity_colors:
                                obj.color = gravity_colors[int(text)]

                        elif obj.real_shape == "size":
                            setattr(obj, real_field_name, max(0.1, min(10, float(text))))
                            if real == "" and float(text) in size_colors:
                                obj.color = size_colors[float(text)]

                        elif obj.real_shape == "teleport":
                            setattr(obj, real_field_name, int(text))

                        elif obj.real_shape == "orb" and text in ("small", "normal", "big", "gravity", "heavy", "dash"):
                            setattr(obj, real_field_name, text)
                            if real == "":
                                obj.color = orb_pad_colors[text]

                        elif obj.real_shape == "pad" and text in ("small", "normal", "big", "gravity", "spider"):
                            setattr(obj, real_field_name, text)
                            if real == "":
                                obj.color = orb_pad_colors[text]

                        elif obj.real_shape == "coin":
                            setattr(obj, real_field_name, int(text))

                        elif obj.real_shape == "text":
                            setattr(obj, real_field_name, text)

                    elif field_name == "triggers":
                        triggers = [int(trigger) for trigger in text.split()]
                        setattr(obj, real_field_name, triggers)

                elif obj.shape == "checkpoint":
                    if field_name == "gamemode" and text in ("cube", "ship", "ball", "wave", "ufo", "robot", "spider"):
                        obj.modifier["gamemode"] = text
                        obj.color = gamemode_colors[text]

                    elif field_name == "speed":
                        obj.modifier["speed"] = max(0.01, min(40, float(text)))

                    elif field_name == "gravity":
                        obj.modifier["gravity"] = float(text)

                    elif field_name == "size":
                        obj.modifier["size"] = max(0.1, min(10, float(text)))

                elif obj.shape == "trigger":
                    if field_name in ("color", "outline"):
                        rgb = text.split()
                        if len(rgb) == 3:
                            r, g, b = (max(0, min(255, int(value))) for value in rgb)
                            setattr(obj, real_field_name, (r, g, b))
                        elif len(rgb) == 1 and rgb[0] == "0":
                            setattr(obj, real_field_name, (0, 0))

                    elif field_name == "attribute" and text in ("shape", "color", "outline", "rotation", "x", "y", "width", "height", "modifier", "length", "roof", "floor", "roof color", "floor color", "background"):
                        obj.modifier["attribute"] = text
                        obj.modifier["value"] = ""

                    elif field_name == "value":
                        if obj.modifier["attribute"] == "shape" and text in ("square", "spike", "slope", "circle", "end", "gamemode", "speed", "gravity", "size", "teleport", "orb", "pad", "trigger", "coin", "text"):
                            if text != "slope":
                                obj.modifier["value"] = text
                            else:
                                obj.modifier["value"] = "right slope"
                        
                        elif obj.modifier["attribute"] in ("color", "outline"):
                            rgb = text.split()
                            if len(rgb) == 3:
                                r, g, b = (max(0, min(255, int(value))) for value in rgb)
                                obj.modifier["value"] = (r, g, b)
                            elif len(rgb) == 1 and rgb[0] == "0":
                                obj.modifier["value"] = (0, 0)
                            
                        elif obj.modifier["attribute"] in ("x", "y", "width", "height"):
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "rotation":
                            rotation = float(text)
                            rotation %= 360
                            if rotation < 0:
                                rotation += 360
                            obj.modifier["value"] = round(rotation, 1)

                        elif obj.modifier["attribute"] == "modifier":
                            obj.modifier["value"] = text

                        elif obj.modifier["attribute"] == "length":
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "roof":
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "floor":
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "roof color":
                            rgb = text.split()
                            r, g, b = (max(0, min(255, int(value))) for value in rgb)
                            obj.modifier["value"] = (r, g, b)

                        elif obj.modifier["attribute"] == "floor color":
                            rgb = text.split()
                            r, g, b = (max(0, min(255, int(value))) for value in rgb)
                            obj.modifier["value"] = (r, g, b)

                        elif obj.modifier["attribute"] == "background":
                            rgb = text.split()
                            r, g, b = (max(0, min(255, int(value))) for value in rgb)
                            obj.modifier["value"] = (r, g, b)

                    elif field_name == "transition":
                        obj.modifier["transition"] = float(text)

                    elif field_name == "triggers":
                        obj.triggers = int(text)

                if field_name in ("shape", "rotation", "x", "y", "width", "height"):
                    if real == "":
                        obj.recompute()
                    elif real == "real_":
                        obj.recompute_triggered()
                    game.rebuild_buckets()

            else:
                if field_name == "length":
                    game.level["meta"]["length"] = max(0, int(text))
                    game.length = max(0, int(text))
                
                elif field_name == "roof":
                    game.level["meta"]["roof"] = min(game.level["meta"]["floor"] - 400, int(text))
                    game.roof = min(game.level["meta"]["floor"] - 400, int(text))

                elif field_name == "floor":
                    game.level["meta"]["floor"] = max(game.level["meta"]["roof"] + 400, int(text))
                    game.floor = max(game.level["meta"]["roof"] + 400, int(text))

                elif field_name == "roof color":
                    r, g, b = (max(0, min(255, int(value))) for value in text.split())
                    game.level["meta"]["roof color"] = (r, g, b)
                    game.roof_color = tuple(game.level["meta"]["roof color"])

                elif field_name == "floor color":
                    r, g, b = (max(0, min(255, int(value))) for value in text.split())
                    game.level["meta"]["floor color"] = (r, g, b)
                    game.floor_color = tuple(game.level["meta"]["floor color"])

                elif field_name == "background":
                    r, g, b = (max(0, min(255, int(value))) for value in text.split())
                    game.level["meta"]["background color"] = (r, g, b)
                    game.background_color = tuple(game.level["meta"]["background color"])

                elif field_name == "title":
                    if text != game.level['meta']['title']:
                        file = Path("levels") / f"{game.level['meta']['title']}.json"

                        base_name = text
                        base_name = re.sub('[<>:"/\\|?*& .]', '_', base_name)
                        name = base_name
                        number = 1
                    
                        while (Path("levels") / f"{name}.json").exists():
                            name = f"{base_name}({number})"
                            number += 1
                        
                        game.level["meta"]["title"] = name
                        file.rename(Path("levels") / f"{game.level['meta']['title']}.json")

                elif field_name == "points":
                    game.level["meta"]["points"] = int(text)
                    game.points = int(text)

                elif field_name == "level number":
                    new_number = max(1, min(len(game.levels)-1, int(text)))
                    game.levels.pop(game.current_level)
                    game.levels.insert(new_number, game.level)
                    game.current_level = new_number

                    for i, level in enumerate(game.levels):
                        level["meta"]["level number"] = i
                    
                    game.load_level(False)

                elif field_name == "song":
                    song_path = game.songs / (text + ".ogg")
                    if song_path.is_file():
                        game.level["meta"]["song"] = text + ".ogg"
                        game.song = text + ".ogg"
                
                elif field_name == "song start":
                    game.level["meta"]["song start"] = float(text)
                    game.song_start = float(text)

                elif field_name == "reset stats" and text == "reset":
                    game.level["victors"] = {}
                    game.victors = {}

                elif field_name == "delete" and text == "delete":
                    file = Path("levels") / f"{game.level['meta']['title']}.json"

                    game.current_level -= 1
                    game.levels.pop(game.current_level+1)
                    file.unlink()
                    toggle_building(game)

        else:
            if field_name == "speedhack":
                game.speedhack_multiplier = max(0.01, float(text))

            elif field_name == "fps":
                game.fps = max(48, int(text))

            elif field_name == "respawn time":
                game.respawn_time = float(text)

            elif field_name == "volume":
                game.volume = max(0, min(100, int(text)))
                py.mixer.music.set_volume(max(0, min(100, int(text))) / 100)

            elif field_name == "log out":
                game.open_login_page()

    except ValueError:
        pass