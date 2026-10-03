from collections import defaultdict
from copy import deepcopy
import time, json
import pygame as py

from entities.spacial import get_buckets
from core.input import handle_input
from core.physics import update
from rendering.rendering import draw
from entities.object import Object
from core.building import toggle_building
from entities.serialization import level_to_dict, dict_to_level, levels_to_data, data_to_levels, save_json
from rendering.textcache import TextCache
from constants import WIDTH, HEIGHT, PLAYER_X, FONT_SIZE, FIXED_STEP, AUTOSAVE_INTERVAL, CAMERA_MARGIN, MAX_EDIT_HISTORY, gamemode_colors, speed_color, gravity_colors, size_colors, teleport_color, orb_pad_colors, coin_color
from core.fps_counter import FpsCounter

class Game():
    def __init__(self):
        py.init()
        
        with open("entities/levels.json", "r") as f:
            self.levels = data_to_levels(json.load(f))
        
        with open("players/settings.json", "r") as f:
            settings = json.load(f)
            self.accessibility = settings["accessibility"]
            self.controls = {}
            for action, keys in settings["controls"].items():
                self.controls[action] = [py.key.key_code(key) for key in keys]
        
        self.running = True

        self.operator = True

        self.name = self.accessibility["name"]
        self.fps = self.accessibility["fps"]
        self.speedhack_multiplier = self.accessibility["speedhack multiplier"]
        self.respawn_time = self.accessibility["respawn time"]
        self.dark_mode = self.accessibility["dark mode"]
        if self.dark_mode:
            self.primary_color = (255,)*3
            self.secondary_color = (0,)*3
        else:
            self.primary_color = (0,)*3
            self.secondary_color = (255,)*3

        self.current_level = 0

        self.width = WIDTH
        self.height = HEIGHT
        self.view_width = WIDTH
        self.view_height = HEIGHT
        self.scale = 1
        self.on_ground = False
        self.slid = 0
        self.sliding = 0

        self.last_frame_time = time.perf_counter()
        self.last_save_time = time.perf_counter()
        self.clicking = 0
        self.clicked = False
        self.robot_fuel = 0

        self.building = False
        self.layer = 1
        self.layer_view = False
        self.scale_mode = False
        self.editing_level = False
        self.buckets = {"hitboxes": defaultdict(list)}

        self.level_states = []
        self.undone_states = []

        self.textboxes = []
        self.active_textbox = None

        self.cheated = False
        self.debug = False
        self.show_buckets = False
        self.paused = False
        self.show_hitboxes = False
        self.noclip = False
        self.speedhack = False
        self.show_player = True

        py.mouse.set_visible(False)
        self.font = py.font.SysFont("Arial", FONT_SIZE)
        self.text_cache = TextCache(self.font)
        self.screen = py.display.set_mode((WIDTH, HEIGHT), py.RESIZABLE)
        self.fps_counter = FpsCounter()
        py.display.set_caption("Geometry Dash")
        py.key.stop_text_input()

        self.load_level()

    def switch_attribute(self, way):
        if self.textboxes != []:
            if way == "previous":
                if not self.active_textbox:
                    self.active_textbox = self.textboxes[-1]
                    self.active_textbox.activate()
                else:
                    self.active_textbox.deactivate()
                    self.active_textbox = self.textboxes[(self.textboxes.index(self.active_textbox) - 1) % len(self.textboxes)]
                    self.active_textbox.activate()

            elif way == "next":
                if not self.active_textbox:
                    self.active_textbox = self.textboxes[0]
                    self.active_textbox.activate()
                else:
                    self.active_textbox.deactivate()
                    self.active_textbox = self.textboxes[(self.textboxes.index(self.active_textbox) + 1) % len(self.textboxes)]
                    self.active_textbox.activate()

            elif way == "deselect":
                if self.active_textbox:
                    self.active_textbox.deactivate()
                    self.active_textbox = None

    def apply_edit(self, obj, field_name, text):
        try:
            if self.building:
                self.capture_level_state("do")

                if not self.editing_level:
                    if obj.shape != "checkpoint":
                        if field_name == "width":
                            setattr(obj, field_name, max(0, int(text)))
                        elif field_name == "height":
                            setattr(obj, field_name, max(0, int(text)))
                        elif field_name == "rotation":
                            rotation = float(text)
                            rotation %= 360
                            if rotation < 0:
                                rotation += 360
                            setattr(obj, field_name, round(rotation, 1))
                        
                        elif field_name in ("color", "outline"):
                            rgb = text.split(" ")
                            if len(rgb) == 3:
                                r, g, b = (max(0, min(255, int(value))) for value in rgb)
                                setattr(obj, field_name, (r, g, b))
                            elif len(rgb) == 1 and rgb[0] == "0":
                                setattr(obj, field_name, (0, 0))

                        elif field_name == "shape" and text in ("square", "spike", "circle", "end", "gamemode", "speed", "gravity", "size", "teleport", "orb", "pad", "coin"):
                            setattr(obj, field_name, text)

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

                            elif text == "coin":
                                obj.width = 40
                                obj.height = 40
                                obj.color = coin_color

                        elif field_name == "shape" and text == "slope":
                            setattr(obj, field_name, "right slope")

                        elif field_name == "shape" and text == "checkpoint":
                            setattr(obj, field_name, text)
                            for layer, name in zip((self.background, self.objects, self.decoration), ("background", "objects", "decoration")):
                                if obj in layer:
                                    layer.remove(obj)
                                    self.checkpoints.append(obj)

                                    for bucket in get_buckets(obj):
                                        self.buckets[name][bucket].remove(obj)
                                    for bucket in get_buckets(obj):
                                        self.buckets["checkpoints"][bucket].append(obj)

                                    break
                            
                            obj.width = 40
                            obj.height = 40
                            obj.rotation = 0
                            obj.color = (0, 255, 0)
                            obj.outline = (0,)*3
                            obj.modifier = {"gamemode": "cube", "speed": 2, "gravity": 1, "size": 1}
                            obj.recompute()

                        elif obj.shape == "gamemode" and field_name == "modifier" and text in ("cube", "ship", "ball", "wave", "ufo", "robot", "spider"):
                            setattr(obj, field_name, text)
                            obj.color = gamemode_colors[text]

                        elif obj.shape == "speed" and field_name == "modifier":
                            setattr(obj, field_name, max(0.01, min(40, float(text))))

                        elif obj.shape == "gravity" and field_name == "modifier":
                            setattr(obj, field_name, float(text))
                            if int(text) in gravity_colors.keys():
                                obj.color = gravity_colors[int(text)]

                        elif obj.shape == "size" and field_name == "modifier":
                            setattr(obj, field_name, max(0.1, min(10, float(text))))
                            if float(text) in size_colors.keys():
                                obj.color = size_colors[float(text)]

                        elif obj.shape == "teleport" and field_name == "modifier":
                            setattr(obj, field_name, int(text))

                        elif obj.shape == "orb" and field_name == "modifier" and text in ("small", "normal", "big", "gravity", "heavy", "dash"):
                            setattr(obj, field_name, text)
                            obj.color = orb_pad_colors[text]

                        elif obj.shape == "pad" and field_name == "modifier" and text in ("small", "normal", "big", "gravity", "spider"):
                            setattr(obj, field_name, text)
                            obj.color = orb_pad_colors[text]

                        elif obj.shape == "coin" and field_name == "modifier":
                            setattr(obj, field_name, int(text))

                    else:
                        if field_name == "gamemode" and text in ("cube", "ship", "ball", "wave", "ufo", "robot", "spider"):
                            obj.modifier["gamemode"] = text
                            obj.color = gamemode_colors[text]

                        elif field_name == "speed":
                            obj.modifier["speed"] = max(0.01, min(40, float(text)))

                        elif field_name == "gravity":
                            obj.modifier["gravity"] = float(text)

                        elif field_name == "size":
                            obj.modifier["size"] = max(0.1, min(10, float(text)))

                else:
                    if field_name == "length":
                        self.level["meta"]["length"] = max(0, int(text))
                    
                    elif field_name == "roof":
                        self.level["meta"]["roof"] = min(0, int(text))

                    elif field_name == "floor":
                        self.level["meta"]["floor"] = max(720, int(text))

                    elif field_name == "background":
                        r, g, b = (max(0, min(255, int(value))) for value in text.split(" "))
                        self.level["meta"]["background color"] = (r, g, b)
                        self.background_color = tuple(self.level["meta"]["background color"])

                    elif field_name == "title":
                        self.level["meta"]["title"] = text

                    elif field_name == "points":
                        self.level["meta"]["points"] = int(text)

                    elif field_name == "level number":
                        new_number = max(1, min(len(self.levels)-1, int(text)))
                        self.levels.pop(self.current_level)
                        self.levels.insert(new_number, self.level)
                        self.current_level = new_number
                        self.load_level()

                    elif field_name == "reset stats" and text == "reset":
                        self.level["victors"] = {}

                    elif field_name == "delete" and text == "delete":
                        self.current_level -= 1
                        self.levels.pop(self.current_level+1)
                        toggle_building(self)

            else:
                if field_name == "name":
                    self.name = text

                elif field_name == "speedhack":
                    self.speedhack_multiplier = max(0.01, float(text))

                elif field_name == "fps":
                    self.fps = max(48, int(text))

                elif field_name == "respawn time":
                    self.respawn_time = float(text)

        except ValueError:
            pass

    def capture_level_state(self, edit):
        if edit == "undo":
            self.undone_states.append(deepcopy(level_to_dict(self.level)))

        elif edit == "redo":
            self.level_states.append(deepcopy(level_to_dict(self.level)))
        
        elif edit == "do":
            self.undone_states = []
            self.level_states.append(deepcopy(level_to_dict(self.level)))
            if len(self.level_states) > MAX_EDIT_HISTORY:
                self.level_states.pop(0)

    def restore_level_state(self, edit):
        if edit == "undo" and self.level_states:
            self.capture_level_state(edit)

            self.level = dict_to_level(self.level_states[-1])
            self.levels[self.current_level] = self.level
            self.load_level(False)
            self.level_states.pop()
            
        elif edit == "redo" and self.undone_states:
            self.capture_level_state(edit)

            self.level = dict_to_level(self.undone_states[-1])
            self.levels[self.current_level] = self.level
            self.load_level(False)
            self.undone_states.pop()

    def rebuild_buckets(self):
        self.buckets = {
            "background": defaultdict(list),
            "objects": defaultdict(list),
            "decoration": defaultdict(list),
            "checkpoints": defaultdict(list),
            "hitboxes": self.buckets["hitboxes"]
        }
        self.z_order = {
            id(obj): i for i, obj in enumerate((*self.background, *self.objects, *self.decoration))
        }

        for layer, name in (
            (self.background, "background"),
            (self.objects, "objects"),
            (self.decoration, "decoration"),
            (self.checkpoints, "checkpoints")
        ):
            for obj in layer:
                for bucket in get_buckets(obj):
                    self.buckets[name][bucket].append(obj)

    def restart(self):
        if not self.paused:
            if self.name not in self.victors.keys():
                self.victors[self.name] = [1, 0, 0, 0]
            else:
                self.victors[self.name][0] += 1

        self.gamemode = self.checkpoints[self.checkpoint].modifier["gamemode"]
        self.speed = self.checkpoints[self.checkpoint].modifier["speed"]
        self.gravity = self.checkpoints[self.checkpoint].modifier["gravity"]
        
        size = self.checkpoints[self.checkpoint].modifier["size"]*40

        self.player = Object(0, 0, size, size, 0, "square", gamemode_colors[self.gamemode], (0,)*3)
        self.player_render = Object(0, 0, size, size, 0, "square", gamemode_colors[self.gamemode], (0,)*3)
        self.player.recompute()
        self.player_render.recompute()

        self.player.x = self.checkpoints[self.checkpoint].x
        self.player.y = self.checkpoints[self.checkpoint].y
        self.y_vel = 0
        self.sliding = 0
        self.dashing = None

        self.camera_x = self.checkpoints[self.checkpoint].x - PLAYER_X
        self.camera_y = self.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN
        self.camera_zoom = 1
        self.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * self.scale * self.camera_zoom)), "world")

        start_x = self.player.x - self.checkpoints[0].x
        checkpoint_x = self.checkpoints[self.checkpoint].x - self.checkpoints[0].x
        end_x = self.level_length - self.checkpoints[0].x - self.player.width
        self.starting_percent = 0 if end_x == 0 else min(100, round(checkpoint_x / end_x * 100))
        self.percent = 0 if end_x == 0 else min(100, round(start_x / end_x * 100))

        self.cheated = True if self.checkpoint != 0 or (not self.paused and (self.speedhack or self.show_hitboxes)) else False
        self.noclip_deaths = 0
        self.dead = 0
        self.completed = False
        self.collected_coins = [0, 0]
        for obj in (*self.background, *self.objects, *self.decoration, *self.checkpoints):
            obj.interacted = False
        
        self.hitboxes = []
        self.current_hitbox = 0
        self.buckets["hitboxes"] = defaultdict(list)
        self.wave_trail = [(self.player.x + self.player.width/2, self.player.y)] if self.gamemode == "wave" else []
    
    def load_level(self, restart=True):
        if restart:
            self.level = self.levels[self.current_level]

        self.background = self.level["background"]
        self.objects = self.level["objects"]
        self.decoration = self.level["decoration"]

        rest = sorted(
            self.level["checkpoints"][1:],
            key=lambda cp: cp.x
        )
        self.level["checkpoints"] = [self.level["checkpoints"][0]] + rest
        self.checkpoints = self.level["checkpoints"]
        if not hasattr(self, "checkpoint"):
            self.checkpoint = 0
        elif self.checkpoint > len(self.checkpoints)-1:
            self.checkpoint = len(self.checkpoints)-1

        self.rebuild_buckets()

        self.victors = self.level["victors"]
        self.level_length = self.level["meta"]["length"]
        self.level_roof = self.level["meta"]["roof"]
        self.level_floor = self.level["meta"]["floor"]
        self.background_color = tuple(self.level["meta"]["background color"])
        if restart:
            self.title = [self.level["meta"]["title"], -1] if self.current_level == 0 else [f"{self.level["meta"]["title"]} | Points: {str(self.level["meta"]["points"])}", -1]

        self.building_camera_x = 0
        self.building_camera_y = self.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN

        self.current_group_id = 0
        for obj in (*self.background, *self.objects, *self.decoration, *self.checkpoints):
            if obj.group_id >= self.current_group_id:
                self.current_group_id = obj.group_id + 1

        if restart:
            self.restart()

    def save_to_file(self):
        save_json("entities/levels.json", levels_to_data(self.levels))

        self.accessibility["name"] = self.name
        self.accessibility["fps"] = self.fps
        self.accessibility["speedhack multiplier"] = self.speedhack_multiplier
        self.accessibility["respawn time"] = self.respawn_time
        self.accessibility["dark mode"] = self.dark_mode
        controls = {action: [py.key.name(key) for key in keys] for action, keys in self.controls.items()}
        settings = {"accessibility": self.accessibility, "controls": controls}
        save_json("players/settings.json", settings)

        self.title = ["Settings and levels saved", time.perf_counter() + 2]

    def limit_fps(self, target_fps):
        frame_duration = 1 / target_fps

        remaining = frame_duration - (time.perf_counter() - self.last_frame_time)
        if remaining > 0.001:
            time.sleep(remaining - 0.0005)
        
        while time.perf_counter() - self.last_frame_time < frame_duration:
            pass
        
        self.last_frame_time = time.perf_counter()

    def run(self):
        accumulator = 0
        previous = time.perf_counter()

        while self.running:
            now = time.perf_counter()
            frame_time = now - previous
            previous = now
            can_update = not self.paused and not self.building and self.current_level != 0

            if frame_time > 0.05 and can_update and not self.completed and self.dead == 0:
                self.restart()
                accumulator = 0
                frame_time = 0
                self.title = ["You're too laggy!", time.perf_counter() + 2]
            
            if self.speedhack:
                frame_time *= self.speedhack_multiplier
            accumulator += frame_time

            handle_input(self)

            while accumulator >= FIXED_STEP:
                if can_update:
                    update(self)
                accumulator -= FIXED_STEP
            if self.frame_steps == 1 or self.frame_steps >= self.fps // 3:
                update(self)
            
            draw(self)
            py.display.flip()
            self.limit_fps(self.fps * self.speedhack_multiplier if self.speedhack else self.fps)
            self.fps_counter.tick()

            if self.building and now - self.last_save_time >= AUTOSAVE_INTERVAL:
                self.last_save_time = time.perf_counter()
                self.save_to_file()

        self.save_to_file()
        py.quit()