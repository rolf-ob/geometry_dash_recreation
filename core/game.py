import time
import pygame as py

from core.input import handle_input
from core.physics import update
from rendering.rendering import draw
from entities.levels import levels
from entities.object import Object
from rendering.textcache import TextCache
from constants import WIDTH, HEIGHT, FPS, PLAYER_X
from fps_counter import FpsCounter

class Game():
    def __init__(self):
        py.init()
        self.running = True

        self.levels = levels
        self.current_level = 0
        self.level_amount = len(levels)
        self.width = WIDTH
        self.height = HEIGHT
        self.last_frame_time = time.perf_counter()
        self.clicking = 0
        self.building = False
        self.layer = 2
        self.debug = False
        self.paused = False
        self.show_hitboxes = False
        self.noclip = False

        self.player = Object("square", (0, 255, 0), (0,)*3, 0, 40, 40, 0, 0)
        self.load_level()

        self.text_cache = TextCache(py.font.SysFont("Arial", 24))
        self.screen = py.display.set_mode((WIDTH, HEIGHT), py.RESIZABLE)
        self.fps_counter = FpsCounter()
        py.display.set_caption("Geometry Dash")

    def limit_fps(self, target_fps):
        frame_duration = 1 / target_fps
        while time.perf_counter() - self.last_frame_time < frame_duration:
            pass
        self.last_frame_time = time.perf_counter()

    def load_level(self):
        self.level_data = levels[self.current_level % len(levels)]
        self.background_color = self.level_data[0][2]
        self.background = self.level_data[1]
        self.objects = self.level_data[2]
        self.decoration = self.level_data[3]
        self.end = self.level_data[4]
        self.speed = self.level_data[0][1]
        self.title = [self.level_data[0][3], FPS * 2]
        
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
        self.player.y = self.level_data[0][0]
        self.player_points = self.player.get_points()
        self.noclip_deaths = 0
        self.dead = 0
        self.completed = False
        self.hitbox_trail = []
        self.hitbox_trail_points = []
        self.wave_trail = [(PLAYER_X + 20, self.level_data[0][0])]

    def run(self):
        while self.running:
            handle_input(self)
            if not self.paused and not self.building or self.frame_steps == 1 or self.frame_steps >= FPS // 3:
                update(self)
            draw(self)
            py.display.flip()
            self.limit_fps(FPS)
            self.fps_counter.tick()

        py.quit()