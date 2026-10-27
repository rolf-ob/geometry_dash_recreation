import pygame as py
import re, math, time
from pathlib import Path

from entities.spatial import get_buckets
from core.building import toggle_building
from utils import clamp
from constants import GAMEMODE_COLORS, SPEED_COLOR, GRAVITY_COLORS, SIZE_COLORS, TELEPORT_COLOR, ORB_PAD_COLORS, COIN_COLOR

def check_illegal(text):
    if not math.isfinite(float(text)):
        return "easter egg!"
    return text

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

def apply_object_modifier(real_field_name, real, text, obj):
    if obj.real_shape == "gamemode" and text in ("cube", "ship", "ball", "wave", "ufo", "robot", "spider"):
        setattr(obj, real_field_name, text)
        if real == "" and text in GAMEMODE_COLORS:
            obj.color = GAMEMODE_COLORS[text]

    elif obj.real_shape == "speed":
        text = check_illegal(text)
        setattr(obj, real_field_name, clamp(float(text), 0.01, 400))

    elif obj.real_shape == "gravity":
        text = check_illegal(text)
        setattr(obj, real_field_name, float(text))
        if real == "" and float(text) in GRAVITY_COLORS:
            obj.color = GRAVITY_COLORS[float(text)]

    elif obj.real_shape == "size":
        text = check_illegal(text)
        setattr(obj, real_field_name, clamp(float(text), 0.5, 10))
        if real == "" and float(text) in SIZE_COLORS:
            obj.color = SIZE_COLORS[float(text)]

    elif obj.real_shape == "teleport":
        text = check_illegal(text)
        setattr(obj, real_field_name, int(text))

    elif obj.real_shape == "orb" and text in ("small", "normal", "big", "gravity", "heavy", "dash"):
        setattr(obj, real_field_name, text)
        if real == "" and text in ORB_PAD_COLORS:
            obj.color = ORB_PAD_COLORS[text]

    elif obj.real_shape == "pad" and text in ("small", "normal", "big", "gravity", "spider"):
        setattr(obj, real_field_name, text)
        if real == "" and text in ORB_PAD_COLORS:
            obj.color = ORB_PAD_COLORS[text]

    elif obj.real_shape == "coin":
        text = check_illegal(text)
        setattr(obj, real_field_name, int(text))

    elif obj.real_shape == "text":
        setattr(obj, real_field_name, text)

def apply_level_setting(game, field_name, text):
    if field_name == "length":
        text = check_illegal(text)
        game.level["meta"]["length"] = max(0, int(text))
        game.length = max(0, int(text))
    
    elif field_name == "roof":
        text = check_illegal(text)
        game.level["meta"]["roof"] = min(game.level["meta"]["floor"] - 400, int(text))
        game.roof = min(game.level["meta"]["floor"] - 400, int(text))

    elif field_name == "floor":
        text = check_illegal(text)
        game.level["meta"]["floor"] = max(game.level["meta"]["roof"] + 400, int(text))
        game.floor = max(game.level["meta"]["roof"] + 400, int(text))

    elif field_name == "roof_color":
        r, g, b = (clamp(int(value), 0, 255) for value in text.split("_"))
        game.level["meta"]["roof_color"] = (r, g, b)
        game.roof_color = tuple(game.level["meta"]["roof_color"])

    elif field_name == "floor_color":
        r, g, b = (clamp(int(value), 0, 255) for value in text.split("_"))
        game.level["meta"]["floor_color"] = (r, g, b)
        game.floor_color = tuple(game.level["meta"]["floor_color"])

    elif field_name == "background_color":
        r, g, b = (clamp(int(value), 0, 255) for value in text.split("_"))
        game.level["meta"]["background_color"] = (r, g, b)
        game.background_color = tuple(game.level["meta"]["background_color"])

    elif field_name == "title":
        if text != game.level["meta"]["title"]:
            file = Path("levels") / f"{game.level["meta"]["title"]}.json"

            base_name = text
            base_name = re.sub('[<>:"/\\|?*&.]', "_", base_name)
            name = base_name
            number = 1
        
            while (Path("levels") / f"{name}.json").exists():
                name = f"{base_name}({number})"
                number += 1
            
            game.level["meta"]["title"] = name
            file.rename(f"levels/{name}.json")

    elif field_name == "points":
        text = check_illegal(text)
        game.level["meta"]["points"] = int(text)
        game.points = int(text)

    elif field_name == "level_number":
        text = check_illegal(text)
        new_number = clamp(int(text), 1, len(game.levels)-1)
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
    
    elif field_name == "song_start":
        text = check_illegal(text)
        game.level["meta"]["song start"] = float(text)
        game.song_start = float(text)

    elif field_name == "reset_stats" and text == "reset":
        game.level["victors"] = {}
        game.victors = {}

    elif field_name == "delete" and text == "delete":
        file = Path("levels") / f"{game.level["meta"]["title"]}.json"

        game.current_level -= 1
        game.levels.pop(game.current_level+1)
        file.unlink()
        toggle_building(game)

def apply_setting(game, field_name, text):
    if field_name == "speedhack":
        text = check_illegal(text)
        game.speedhack_multiplier = clamp(float(text), 0.01, 10)

    elif field_name == "fps":
        text = check_illegal(text)
        game.fps = max(60, int(text))

    elif field_name == "respawn_time":
        text = check_illegal(text)
        game.respawn_time = float(text)

    elif field_name == "volume":
        text = check_illegal(text)
        game.volume = clamp(int(text), 0, 100)
        py.mixer.music.set_volume(game.volume / 100)

    elif field_name == "log_out":
        game.open_login_page()

def apply_edit(game, obj, real_field_name, text):
    real_field_name = real_field_name.replace(" ", "_")
    if real_field_name not in ("title", "modifier"):
        text = text.replace(" ", "_")
    real = "real_" if real_field_name.split("_")[0] == "real" else ""
    field_name = real_field_name.split("_")[-1] if real == "real_" else real_field_name

    try:
        if game.building or real == "real_":
            if not game.editing_level:
                if field_name in ("shape", "rotation", "width", "height"):
                    old_buckets = get_buckets(obj)
                
                if obj.real_shape not in ("checkpoint", "trigger"):
                    if field_name == "width":
                        text = check_illegal(text)
                        setattr(obj, real_field_name, max(0, int(text)))
                    elif field_name == "height":
                        text = check_illegal(text)
                        setattr(obj, real_field_name, max(0, int(text)))
                    elif field_name == "rotation":
                        text = check_illegal(text)
                        rotation = float(text)
                        rotation %= 360
                        if rotation < 0:
                            rotation += 360
                        setattr(obj, real_field_name, round(rotation, 1))
                    
                    elif field_name in ("color", "outline"):
                        rgb = text.split("_")
                        if len(rgb) == 3:
                            r, g, b = (clamp(int(value), 0, 255) for value in rgb)
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
                                obj.color = SPEED_COLOR

                            elif text == "gravity":
                                obj.width = 20
                                obj.height = 120

                            elif text == "size":
                                obj.width = 20
                                obj.height = 80

                            elif text == "teleport":
                                obj.width = 20
                                obj.height = 120
                                obj.color = TELEPORT_COLOR

                            elif text == "orb":
                                obj.width = 40
                                obj.height = 40

                            elif text == "pad":
                                obj.width = 40
                                obj.height = 10
                                obj.y += 10

                            elif text == "trigger":
                                obj.triggers = 0
                                obj.modifier = {"attribute": "", "value": "", "transition": 0}

                            elif text == "coin":
                                obj.width = 40
                                obj.height = 40
                                obj.color = COIN_COLOR

                            elif text == "text":
                                obj.color = (0, 0, 0)

                    elif field_name == "shape" and text == "slope":
                        setattr(obj, real_field_name, "right slope")

                    elif field_name == "shape" and text in ("checkpoint", "cp"):
                        setattr(obj, real_field_name, "checkpoint")

                        getattr(game, obj.layer).remove(obj)
                        game.checkpoints.append(obj)

                        for bucket in get_buckets(obj):
                            game.buckets[obj.layer][bucket].remove(obj)
                        for bucket in get_buckets(obj):
                            game.buckets["checkpoints"][bucket].append(obj)

                        obj.width = 40
                        obj.height = 40
                        obj.rotation = 0
                        obj.color = (0, 255, 0)
                        obj.outline = (0,)*3
                        obj.modifier = {"gamemode": "cube", "speed": 2, "gravity": 1, "size": 1}
                        obj.layer = "checkpoints"

                    elif field_name == "modifier":
                        apply_object_modifier(real_field_name, real, text, obj)

                    elif field_name == "triggers":
                        triggers = [int(trigger) for trigger in text.split("_")]
                        setattr(obj, real_field_name, triggers)

                elif obj.shape == "checkpoint":
                    if field_name == "gamemode" and text in ("cube", "ship", "ball", "wave", "ufo", "robot", "spider"):
                        obj.modifier["gamemode"] = text
                        obj.color = GAMEMODE_COLORS[text]

                    elif field_name == "speed":
                        text = check_illegal(text)
                        obj.modifier["speed"] = clamp(float(text), 0.01, 400)

                    elif field_name == "gravity":
                        text = check_illegal(text)
                        obj.modifier["gravity"] = float(text)

                    elif field_name == "size":
                        text = check_illegal(text)
                        obj.modifier["size"] = clamp(float(text), 0.5, 10)
                        obj.width = obj.modifier["size"] * 40
                        obj.height = obj.modifier["size"] * 40

                elif obj.shape == "trigger":
                    if field_name in ("color", "outline"):
                        rgb = text.split("_")
                        if len(rgb) == 3:
                            r, g, b = (clamp(int(value), 0, 255) for value in rgb)
                            setattr(obj, real_field_name, (r, g, b))
                        elif len(rgb) == 1 and rgb[0] == "0":
                            setattr(obj, real_field_name, (0, 0))

                    elif field_name == "attribute" and text in ("shape", "color", "outline", "rotation", "x", "y", "width", "height", "modifier", "length", "roof", "floor", "roof_color", "floor_color", "background_color"):
                        obj.modifier["attribute"] = text
                        obj.modifier["value"] = ""

                    elif field_name == "value":
                        if obj.modifier["attribute"] == "shape" and text in ("square", "spike", "slope", "circle", "end", "gamemode", "speed", "gravity", "size", "teleport", "orb", "pad", "coin", "text"):
                            obj.modifier["value"] = text
                        
                        elif obj.modifier["attribute"] in ("color", "outline"):
                            rgb = text.split("_")
                            if len(rgb) == 3:
                                r, g, b = (clamp(int(value), 0, 255) for value in rgb)
                                obj.modifier["value"] = (r, g, b)
                            elif len(rgb) == 1 and rgb[0] == "0":
                                obj.modifier["value"] = (0, 0)
                            
                        elif obj.modifier["attribute"] in ("x", "y", "width", "height"):
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "rotation":
                            text = check_illegal(text)
                            rotation = float(text)
                            obj.modifier["value"] = round(rotation, 1)

                        elif obj.modifier["attribute"] == "modifier":
                            obj.modifier["value"] = text

                        elif obj.modifier["attribute"] == "length":
                            text = check_illegal(text)
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "roof":
                            text = check_illegal(text)
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] == "floor":
                            text = check_illegal(text)
                            obj.modifier["value"] = int(text)

                        elif obj.modifier["attribute"] in ("roof_color", "floor_color", "background_color"):
                            rgb = text.split("_")
                            if len(rgb) == 3:
                                r, g, b = (clamp(int(value), 0, 255) for value in rgb)
                                obj.modifier["value"] = (r, g, b)
                            elif len(rgb) == 1 and rgb[0] == "0":
                                obj.modifier["value"] = (0, 0)

                    elif field_name == "transition":
                        text = check_illegal(text)
                        obj.modifier["transition"] = 0 if float(text) == 0 else max(0.1, float(text))

                    elif field_name == "triggers":
                        text = check_illegal(text)
                        obj.triggers = int(text)

                if field_name in ("shape", "rotation", "width", "height"):
                    obj.recompute(real == "real_")
                    game.rebuild_buckets(obj, old_buckets)
                elif field_name in ("color", "outline", "modifier"):
                    if real == "":
                        obj.recompute_design()

            else:
                apply_level_setting(game, field_name, text)
        else:
            apply_setting(game, field_name, text)

    except ValueError:
        game.title = [f"Invalid value for {real_field_name}; {text}", time.perf_counter() + 2]