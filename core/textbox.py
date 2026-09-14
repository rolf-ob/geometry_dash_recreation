import pygame as py

class TextBox:
    def __init__(self, width, height, x, y, field_name):
        self.rect = py.Rect(x, y, width, height)
        self.field_name = field_name
        self.text = ""
        self.active = False

    def activate(self):
        self.active = True
        py.key.start_text_input()

    def deactivate(self):
        self.active = False
        py.key.stop_text_input()

    def handle_event(self, event):
        if event.type == py.TEXTINPUT:
            self.text += event.text
        elif event.type == py.KEYDOWN:
            if event.key == py.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == py.K_RETURN:
                self.text = ""
        return False

    def draw(self, screen, font):
        color = (0, 200, 0) if self.active else (0,)*3
        py.draw.rect(screen, (255,)*3, self.rect)
        py.draw.rect(screen, color, self.rect, 2)
        text_surf = font.render(f"{self.field_name}: {self.text}", True, (0,)*3)
        screen.blit(text_surf, (self.rect.x + 4, self.rect.y + 4))