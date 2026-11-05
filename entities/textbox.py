import pygame as py

class TextBox:
    def __init__(self, field_name, text):
        self.field_name = field_name
        self.text = str(text)
        self.active = False

    def activate(self):
        self.active = True
        py.key.start_text_input()

    def deactivate(self):
        self.active = False
        py.key.stop_text_input()