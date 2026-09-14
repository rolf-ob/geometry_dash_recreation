import time, pickle
import pygame as py

from core.input import handle_input
from core.physics import update
from rendering.rendering import draw
from entities.object import Object
from rendering.textcache import TextCache
from constants import WIDTH, HEIGHT, PLAYER_X
from fps_counter import FpsCounter

class Game():
    def __init__(self):
        py.init()
        with open("entities/levels.pkl", "rb") as f:
            self.levels = pickle.load(f)
        with open("settings.pkl", "rb") as f:
            self.settings = pickle.load(f)
        self.running = True

        self.player = Object("square", None, (0,)*3, 0, 40, 40, 0, 0)

        self.player.color = self.settings["player color"]
        self.speedhack_multiplier = self.settings["speedhack multiplier"]
        self.fps = self.settings["fps"]
        self.respawn_time = self.settings["respawn time"]

        self.current_level = 0
        self.width = WIDTH
        self.height = HEIGHT
        self.last_frame_time = time.perf_counter()
        self.clicking = 0

        self.building = False
        self.shape = "square"
        self.rotation = 0
        self.layer = 1
        self.editing_level = False
        self.textboxes = []
        self.active_textbox = None

        self.debug = False
        self.editing_settings = False
        self.paused = False
        self.show_hitboxes = False
        self.noclip = False
        self.speedhack = False

        self.load_level()

        self.font = py.font.SysFont("Arial", 24)
        self.text_cache = TextCache(self.font)
        self.screen = py.display.set_mode((WIDTH, HEIGHT), py.RESIZABLE)
        self.fps_counter = FpsCounter()
        py.display.set_caption("Geometry Dash")
        py.key.stop_text_input()

    def limit_fps(self, target_fps):
        frame_duration = 1 / target_fps
        while time.perf_counter() - self.last_frame_time < frame_duration:
            pass
        self.last_frame_time = time.perf_counter()

    def save_to_file(self):
        with open("entities/levels.pkl", "wb") as f:
            pickle.dump(self.levels, f)

        self.settings["player color"] = self.player.color
        with open("settings.pkl", "wb") as f:
            pickle.dump(self.settings, f)

        self.title = ["Saved all levels", self.fps * 2]
    
    def load_level(self):
        self.level_data = self.levels[self.current_level % len(self.levels)]
        self.background_color = self.level_data[0][4]
        self.background = self.level_data[1]
        self.objects = self.level_data[2]
        self.decoration = self.level_data[3]
        self.end = self.level_data[4]
        self.speed = self.level_data[0][2]
        self.title = [self.level_data[0][5], self.fps * 2]
        
        self.background_points = [obj.get_points() for obj in self.background]
        self.object_points = [obj.get_points() for obj in self.objects]
        self.decoration_points = [obj.get_points() for obj in self.decoration]
        self.end_points = self.end.get_points()

        self.restart()

    def restart(self):
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1
        self.player.x = PLAYER_X
        self.player.y = self.level_data[0][1]
        self.player_points = self.player.get_points()
        self.noclip_deaths = 0
        self.dead = 0
        self.completed = False
        self.hitbox_trail = []
        self.hitbox_trail_points = []
        self.wave_trail = [(PLAYER_X + 20, self.level_data[0][1])]

    def run(self):
        while self.running:
            handle_input(self)
            if (not self.paused or self.frame_steps == 1 or self.frame_steps >= self.fps // 3) and not self.building:
                update(self)
            draw(self)
            py.display.flip()
            if self.speedhack:
                self.limit_fps(self.fps * self.speedhack_multiplier)
            else:
                self.limit_fps(self.fps)
            self.fps_counter.tick()

        self.save_to_file()
        py.quit()