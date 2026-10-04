class TextCache:
    def __init__(self, font):
        self.font = {
            "screen": font,
            "world": font
        }
        self._cache = {
            "screen": {},
            "world": {}
        }
        self._sizes = {
            "screen": {},
            "world": {}
        }

    def get_surface(self, text, color, layer):
        key = (text, color)
        if key not in self._cache[layer]:
            self._cache[layer][key] = self.font[layer].render(text, True, color)
        return self._cache[layer][key]

    def get_size(self, text, color, layer):
        key = (text, color)
        if key not in self._sizes[layer]:
            self._sizes[layer][key] = tuple(self.get_surface(*key, layer).get_rect()[2:])
        return self._sizes[layer][key]

    def change_font(self, font, layer):
        self.clear(layer)
        self.font[layer] = font

    def clear(self, layer):
        self._cache[layer].clear()
        self._sizes[layer].clear()