import time, json
import pygame as py

from core.input import handle_input
from core.physics import update
from rendering.rendering import draw
from entities.object import Object
from core.building import toggle_building
from entities.serialization import levels_to_data, data_to_levels
from rendering.textcache import TextCache
from constants import WIDTH, HEIGHT, PLAYER_X, FONT_SIZE, FIXED_STEP
from core.fps_counter import FpsCounter

class Game():
    def __init__(self):
        py.init()
        
        with open("entities/levels.json", "r") as f:
            self.levels = data_to_levels(json.load(f))
        
        with open("entities/settings.json", "r") as f:
            settings = json.load(f)
            self.accessibility = settings["accessibility"]
            self.controls = {}
            for action, keys in settings["controls"].items():
                self.controls[action] = [py.key.key_code(key) for key in keys]
        
        self.running = True

        self.operator = True
        self.name = self.accessibility["name"]
        self.player = Object(0, 0, 40, 40, 0, "square", tuple(self.accessibility["player color"]), (0,)*3)
        self.fps = self.accessibility["fps"]
        self.speedhack_multiplier = self.accessibility["speedhack multiplier"]
        self.respawn_time = self.accessibility["respawn time"]
        self.current_level = 0
        self.width = WIDTH
        self.height = HEIGHT
        self.view_width = WIDTH
        self.scale = 1
        self.last_frame_time = time.perf_counter()
        self.clicking = 0

        self.building = False
        self.shape = "square"
        self.rotation = 0
        self.layer = 1
        self.editing_level = False

        self.textboxes = []
        self.active_textbox = None

        self.cheated = False
        self.debug = False
        self.paused = False
        self.show_hitboxes = False
        self.noclip = False
        self.speedhack = False
        self.show_player = True

        self.load_level()

        self.font = py.font.SysFont("Arial", FONT_SIZE)
        self.text_cache = TextCache(self.font)
        self.screen = py.display.set_mode((WIDTH, HEIGHT), py.RESIZABLE)
        self.fps_counter = FpsCounter()
        py.display.set_caption("Geometry Dash")
        py.key.stop_text_input()

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
                if not self.editing_level:
                    if field_name == "width":
                        setattr(obj, field_name, max(0, int(text)))
                    elif field_name == "height":
                        setattr(obj, field_name, max(0, int(text)))
                    elif field_name == "rotation":
                        setattr(obj, field_name, int(text))
                        self.rotation = int(text)
                    
                    elif field_name in ("color", "outline"):
                        r, g, b = (max(0, min(255, int(value))) for value in text.split(" "))
                        setattr(obj, field_name, (r, g, b))

                    elif field_name == "shape" and text in ("square", "end", "spike", "slope"):
                        setattr(obj, field_name, text)
                        if text != "end":
                            self.shape = text

                else:
                    if field_name == "mode" and text in ("wave"):
                        self.level["meta"]["gamemode"] = text

                    elif field_name == "speed":
                        self.level["meta"]["speed"] = float(text)

                    elif field_name == "gravity":
                        self.level["meta"]["gravity"] = int(text)

                    elif field_name == "length":
                        self.level["meta"]["length"] = max(0, int(text))

                    elif field_name == "background":
                        r, g, b = (max(0, min(255, int(value))) for value in text.split(" "))
                        self.level["meta"]["background color"] = (r, g, b)
                        self.background_color = self.level["meta"]["background color"]

                    elif field_name == "title":
                        self.level["meta"]["title"] = text

                    elif field_name == "points":
                        self.level["meta"]["points"] = int(text)

                    elif field_name == "delete" and text == "delete":
                        self.current_level -= 1
                        self.levels.pop(self.current_level+1)
                        toggle_building(self)

            else:
                if field_name == "name":
                    self.name = text

                elif field_name == "player color":
                    r, g, b = (max(0, min(255, int(value))) for value in text.split(" "))
                    self.player.color = (r, g, b)

                elif field_name == "speedhack":
                    self.speedhack_multiplier = max(0, float(text))

                elif field_name == "fps":
                    self.fps = max(48, int(text))

                elif field_name == "respawn time":
                    self.respawn_time = float(text)

        except ValueError:
            pass

    def restart(self):
        self.camera_x = self.checkpoints[self.checkpoint].x - PLAYER_X
        self.camera_y = 0
        self.camera_zoom = 1
        self.player.x = self.checkpoints[self.checkpoint].x
        self.player.y = self.checkpoints[self.checkpoint].y
        self.player_points = self.player.get_points()
        self.percent = min(100.0, round((self.player.x - self.checkpoints[0].x) / (self.level_length - self.checkpoints[0].x - self.player.width)*100, 2))
        if self.checkpoint != 0:
            self.cheated = True
        else:
            self.cheated = self.show_hitboxes or self.speedhack
        self.noclip_deaths = 0
        self.dead = 0
        self.completed = False
        self.hitbox_trail = []
        self.hitbox_trail_points = []
        self.wave_trail = [(self.player.x + 20, self.player.y)]
    
    def load_level(self):
        self.level = self.levels[self.current_level]
        self.background = self.level["background"]
        self.objects = self.level["objects"]
        self.decoration = self.level["decoration"]
        self.checkpoints = self.level["checkpoints"]
        self.victors = self.level["victors"]
        self.speed = self.level["meta"]["speed"]
        self.gravity = self.level["meta"]["gravity"]
        self.level_length = self.level["meta"]["length"]
        self.background_color = self.level["meta"]["background color"]
        self.title = [self.level["meta"]["title"], -1] if self.current_level == 0 else [f"{self.level["meta"]["title"]} | Points: {str(self.level["meta"]["points"])}", -1]

        self.checkpoint = 0
        
        self.background_points = [obj.get_points() for obj in self.background]
        self.object_points = [obj.get_points() for obj in self.objects]
        self.decoration_points = [obj.get_points() for obj in self.decoration]
        self.checkpoint_points = [obj.get_points() for obj in self.checkpoints]

        self.restart()

    def save_to_file(self):
        with open("entities/levels.json", "w") as f:
            json.dump(levels_to_data(self.levels), f, indent=2)

        self.accessibility["name"] = self.name
        self.accessibility["player color"] = list(self.player.color)
        self.accessibility["fps"] = self.fps
        self.accessibility["speedhack multiplier"] = self.speedhack_multiplier
        self.accessibility["respawn time"] = self.respawn_time
        controls = {}
        for action, keys in self.controls.items():
            controls[action] = [py.key.name(key) for key in keys]
        
        settings = {"accessibility": self.accessibility, "controls": controls}
        with open("entities/settings.json", "w") as f:
            json.dump(settings, f, indent=2)

        self.title = ["Settings and levels saved", time.perf_counter() + 2]

    def limit_fps(self, target_fps):
        frame_duration = 1 / target_fps
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

            if self.speedhack:
                frame_time *= self.speedhack_multiplier
            accumulator += frame_time

            handle_input(self)

            can_update = (not self.paused or self.frame_steps == 1 or self.frame_steps >= self.fps // 3) and not self.building and self.current_level != 0
            while accumulator >= FIXED_STEP:
                if can_update:
                    update(self)
                accumulator -= FIXED_STEP

            if frame_time > 0.05 and can_update and not self.completed and self.dead == 0:
                self.restart()
                accumulator = 0
                self.title = ["You're too laggy!", time.perf_counter() + 2]
            
            draw(self)
            py.display.flip()
            self.limit_fps(self.fps * self.speedhack_multiplier if self.speedhack else self.fps)
            self.fps_counter.tick()

        self.save_to_file()
        py.quit()