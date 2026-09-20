import pygame as py
from rendering.textcache import TextCache

class TextBox:
    def __init__(self, x, y, width, height, field_name):
        self.rect = py.Rect(x, y, width, height)
        self.field_name = field_name
        self.text = ""
        self.active = False

        self.font = py.font.SysFont("Arial", 24)
        self.text_cache = TextCache(self.font)

    def activate(self):
        self.active = True
        py.key.start_text_input()

    def deactivate(self):
        self.active = False
        py.key.stop_text_input()

    def handle_event(self, event):
        if event.type == py.TEXTINPUT:
            self.text += event.text
        return False

    def draw(self, screen, font):
        color = (0, 200, 0) if self.active else (0,)*3
        py.draw.rect(screen, (255,)*3, self.rect)
        py.draw.rect(screen, color, self.rect, 2)
        text_surf = self.text_cache.get_surface(f"{self.field_name}: {self.text}", (0,)*3)
        screen.blit(text_surf, (self.rect.x + 4, self.rect.y + 4))