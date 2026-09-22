class TextCache:
    def __init__(self, font):
        self.font = font
        self._cache = {}
        self._sizes = {}

    def get_surface(self, text, color):
        key = (text, color)
        if key not in self._cache:
            self._cache[key] = self.font.render(text, True, color)
        return self._cache[key]

    def get_size(self, text, color):
        key = (text, color)
        if key not in self._sizes:
            self._sizes[key] = tuple(self._cache[key].get_rect()[-2:])
        return self._sizes[key]

    def change_font(self, font):
        self.font = font

    def clear(self):
        self._cache.clear()
        self._sizes.clear()