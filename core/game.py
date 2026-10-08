from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import time, json
import pygame as py

from entities.spatial import get_buckets
from core.input import handle_input
from core.physics import update
from rendering.rendering import draw
from entities.object import Object
from entities.serialization import level_to_dict, dict_to_level, save_json
from rendering.textcache import TextCache
from constants import WIDTH, HEIGHT, PLAYER_X, FONT_SIZE, FIXED_STEP, AUTOSAVE_INTERVAL, CAMERA_MARGIN, MAX_EDIT_HISTORY, gamemode_colors
from core.fps_handler import FpsHandler

class Game:
    def __init__(self):
        py.init()

        self.levels = []
        for file in Path("levels").glob("*.json"):
            with open(file, "r") as f:
                self.levels.append(dict_to_level(json.load(f)))
        self.levels.sort(key=lambda level: level["meta"]["level number"])

        self.users = []
        for user in Path("users").iterdir():
            self.users.append(str(user))
        self.users.sort()
        print(self.users)

        self.songs = Path("songs")
        self.operator = True
        self.running = True

        self.width = WIDTH
        self.height = HEIGHT
        self.view_width = WIDTH
        self.view_height = HEIGHT
        self.scale = 1

        self.building = False
        self.layer = 1
        self.layer_view = False
        self.scale_mode = False
        self.editing_level = False
        self.buckets = {"hitboxes": defaultdict(list), "wave trail": defaultdict(list)}

        self.done_states = []
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

        self.last_frame_time = time.perf_counter()
        self.last_save_time = time.perf_counter()

        self.font = py.font.SysFont("Arial", FONT_SIZE)
        self.text_cache = TextCache(self.font)
        self.fps_handler = FpsHandler()
        self.screen = py.display.set_mode((WIDTH, HEIGHT), py.RESIZABLE)
        py.display.set_caption("Geometry Dash")
        py.mouse.set_visible(False)
        py.key.stop_text_input()

        self.load_user("Rolf")

    def load_user(self, username):
        self.name = username

        with open(f"users/{self.name}/accessibility.json", "r") as f:
            settings = json.load(f)
            self.accessibility = settings

        with open(f"users/{self.name}/controls.json", "r") as f:
            settings = json.load(f)
            self.controls = {
                action: [py.key.key_code(key) for key in keys]
                for action, keys in settings.items()
            }
        
        self.fps = self.accessibility["fps"]
        self.speedhack_multiplier = self.accessibility["speedhack multiplier"]
        self.respawn_time = self.accessibility["respawn time"]
        self.volume = self.accessibility["volume"]
        py.mixer.music.set_volume(self.volume / 100)
        self.dark_mode = self.accessibility["dark mode"]
        if self.dark_mode:
            self.primary_color = (255,)*3
            self.secondary_color = (0,)*3
        else:
            self.primary_color = (0,)*3
            self.secondary_color = (255,)*3
        
        self.current_level = 0
        self.load_level()
    
    def load_level(self, restart=True):
        self.level = self.levels[self.current_level]
        
        self.points = self.level["meta"]["points"]
        self.song = self.level["meta"]["song"] if self.level["meta"]["song"] else None
        self.song_start = self.level["meta"]["song start"]

        self.background = self.level["background"]
        self.objects = self.level["objects"]
        self.decoration = self.level["decoration"]
        self.victors = self.level["victors"]
        self.trigger_ids = defaultdict(list)

        for obj in (*self.background, *self.objects, *self.decoration):
            if obj.shape != "trigger" and obj.triggers:
                for id in obj.triggers:
                    self.trigger_ids[id].append(obj)

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

        if self.song:
            py.mixer.music.load(self.songs / self.song)
        else:
            py.mixer.music.unload()

        self.current_group_id = 0
        for obj in (*self.background, *self.objects, *self.decoration, *self.checkpoints):
            if obj.group_id >= self.current_group_id:
                self.current_group_id = obj.group_id + 1

        if restart:
            self.title = [self.level["meta"]["title"], -1] if self.current_level == 0 else [f"{self.level["meta"]["title"]} | Points: {str(self.points)}", -1]
            self.building_camera_x = 0
            self.building_camera_y = self.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN
            self.restart()

    def restart(self):
        if not self.paused and not self.building and self.current_level != 0:
            self.record_attempt()

        for obj in (*self.background, *self.objects, *self.decoration):
            obj.recompute()
        self.rebuild_buckets()
        
        self.length = self.level["meta"]["length"]
        self.roof = self.level["meta"]["roof"]
        self.floor = self.level["meta"]["floor"]
        self.roof_color = tuple(self.level["meta"]["roof color"])
        self.floor_color = tuple(self.level["meta"]["floor color"])
        self.background_color = tuple(self.level["meta"]["background color"])

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
        self.slid = 0
        self.on_ground = False
        self.clicking = 0
        self.clicked = False
        self.robot_fuel = 0
        self.dashing = None

        self.camera_x = self.checkpoints[self.checkpoint].x - PLAYER_X
        self.camera_y = max(
            min(
                self.level["meta"]["floor"] - HEIGHT + CAMERA_MARGIN,
                self.player.y - CAMERA_MARGIN * 2
            ),
            self.player.y + self.player.height - HEIGHT + CAMERA_MARGIN
        )
        self.camera_zoom = 1
        self.text_cache.change_font(py.font.SysFont("Arial", int(FONT_SIZE * self.scale * self.camera_zoom)), "world")

        start_x = self.player.x - self.checkpoints[0].x
        checkpoint_x = self.checkpoints[self.checkpoint].x - self.checkpoints[0].x
        end_x = self.length - self.checkpoints[0].x - self.player.width
        self.starting_percent = 0 if end_x == 0 else min(100, round(checkpoint_x / end_x * 100))
        self.percent = 0 if end_x == 0 else min(100, round(start_x / end_x * 100))

        self.cheated = True if self.checkpoint != 0 or (not self.paused and (self.speedhack or self.show_hitboxes)) else False
        self.noclip_deaths = 0
        self.dead = 0
        self.completed = False
        self.collected_coins = [0, 0]
        for obj in (*self.background, *self.objects, *self.decoration, *self.checkpoints):
            obj.interacted = False

        self.activated_triggers = {}
        self.current_hitbox = 0
        self.hitboxes = [self.player]
        self.wave_trail = [(self.player.x + self.player.width/2, self.player.y)] if self.gamemode == "wave" else []
        self.buckets["hitboxes"] = defaultdict(list)
        self.buckets["wave trail"] = defaultdict(list)

        self.restart_time = time.perf_counter()

        if self.song:
            speeds = []
            for obj in self.objects:
                if obj.shape == "speed" and obj.x < self.checkpoints[self.checkpoint].x:
                    speeds.append(obj)
            speeds.sort(key=lambda obj: obj.x)

            if speeds:
                steps_into_level = (speeds[0].x - self.checkpoints[0].x) / self.checkpoints[0].modifier["speed"]
                for i, speed in enumerate(speeds):
                    if speed != speeds[-1]:
                        steps_into_level += (speeds[i+1].x - speed.x) / speed.modifier
                    else:
                        steps_into_level += (self.checkpoints[self.checkpoint].x - speed.x) / speed.modifier
            else:
                steps_into_level = (self.checkpoints[self.checkpoint].x - self.checkpoints[0].x) / self.checkpoints[0].modifier["speed"]
            
            seconds_into_song = steps_into_level * FIXED_STEP + self.song_start
            py.mixer.music.play(-1, seconds_into_song)
            
            if self.paused:
                py.mixer.music.pause()

    def rebuild_buckets(self):
        self.buckets = {
            "background": defaultdict(list),
            "objects": defaultdict(list),
            "decoration": defaultdict(list),
            "checkpoints": defaultdict(list),
            "hitboxes": self.buckets["hitboxes"],
            "wave trail": self.buckets["wave trail"]
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

    def record_attempt(self):
        if self.name not in self.victors:
            self.victors[self.name] = [1, 0, 0, 0, 0]
        else:
            self.victors[self.name][0] += 1

    def capture_state(self, edit, all=False):
        if self.editing_level or all:
            state = {
                "all": True,
                "levels": deepcopy([level_to_dict(level) for level in self.levels]),
                "current level": self.current_level
            }
        else:
            state = {
                "all": False,
                "level": deepcopy(level_to_dict(self.level))
            }

        if edit == "undo":
            self.undone_states.append(state)

        elif edit == "redo":
            self.done_states.append(state)
        
        elif edit == "do":
            self.done_states.append(state)
            self.undone_states.clear()
            if len(self.done_states) > MAX_EDIT_HISTORY:
                self.done_states.pop(0)
    
    def restore_state(self, edit):
        if edit == "undo":
            if not self.done_states:
                return

            state = self.done_states[-1]
            self.capture_state("undo", all=state["all"])
            
            if state["all"]:
                self.levels = [dict_to_level(level) for level in deepcopy(state["levels"])]

                self.current_level = state["current level"]
                self.level = self.levels[self.current_level]

            else:
                self.level = dict_to_level(deepcopy(state["level"]))
                self.levels[self.current_level] = self.level

            self.load_level(False)
            self.done_states.pop()
            
        elif edit == "redo":
            if not self.undone_states:
                return

            state = self.undone_states[-1]
            self.capture_state("redo", all=state["all"])

            if self.done_states["all"]:
                self.levels = [dict_to_level(level) for level in deepcopy(state["levels"])]
            
                self.current_level = state["current level"]
                self.level = self.levels[self.current_level]

            else:
                self.level = dict_to_level(deepcopy(state["level"]))
                self.levels[self.current_level] = self.level

            self.load_level(False)
            self.undone_states.pop()

    def save_to_file(self):
        for level in self.levels:
            save_json(f"levels/{level["meta"]["title"]}.json", level_to_dict(level))

        self.accessibility["fps"] = self.fps
        self.accessibility["speedhack multiplier"] = self.speedhack_multiplier
        self.accessibility["respawn time"] = self.respawn_time
        self.accessibility["volume"] = self.volume
        self.accessibility["dark mode"] = self.dark_mode
        save_json(f"users/{self.name}/accessibility.json", self.accessibility)
        save_json(f"users/{self.name}/controls.json", self.controls)

        self.title = ["Settings and levels saved", time.perf_counter() + 2]

    def run(self):
        accumulator = 0
        previous = time.perf_counter()

        while self.running:
            now = time.perf_counter()
            frame_time = now - previous
            previous = now

            if hasattr(self, "name") and self.name:
                can_update = not self.paused and not self.building and self.current_level != 0

                if frame_time > 0.05 and can_update and not self.completed and self.dead == 0 and now - self.restart_time > 0.1:
                    self.restart()
                    accumulator = 0
                    frame_time = 0
                    self.title = ["You're too laggy!", time.perf_counter() + 2]
                
                if self.speedhack:
                    frame_time *= self.speedhack_multiplier
                accumulator += frame_time

            else:
                can_update = False

            handle_input(self)

            while accumulator >= FIXED_STEP:
                if can_update:
                    update(self)
                accumulator -= FIXED_STEP
            if self.frame_steps == 1 or self.frame_steps >= self.fps // 3:
                update(self)
            
            draw(self)
            py.display.flip()

            if self.building and now - self.last_save_time >= AUTOSAVE_INTERVAL:
                self.last_save_time = time.perf_counter()
                self.save_to_file()
            
            self.last_frame_time = self.fps_handler.limit_fps(self.fps * self.speedhack_multiplier if self.speedhack else self.fps, self.last_frame_time)
            self.fps_handler.tick()

        self.save_to_file()
        py.quit()