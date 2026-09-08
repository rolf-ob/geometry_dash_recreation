class TextCache:
    def __init__(self, font):
        self.font = font
        self._cache = {}

    def get_surface(self, text, color):
        key = (text, color)
        if key not in self._cache:
            self._cache[key] = self.font.render(text, True, color)
        return self._cache[key]

    def clear(self):
        self._cache.clear()