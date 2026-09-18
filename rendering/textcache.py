class TextCache:
    def __init__(self, font):
        self.font = font
        self._cache = {}
        self._width = {}

    def get_surface(self, text, color):
        key = (text, color)
        if key not in self._cache:
            self._cache[key] = self.font.render(text, True, color)
        return self._cache[key]

    def get_size(self, text, color):
        key = (text, color)
        if key not in self._width:
            self._width[key] = tuple(self._cache[key].get_rect()[-2:])
        return self._width[key]

    def clear(self):
        self._cache.clear()