import math
from dataclasses import dataclass

@dataclass
class Object:
    shape: str
    color: tuple[int, int, int]
    outline: tuple[int, int, int]
    rotation: int
    width: int
    height: int
    x: int
    y: int
    selected: bool = False
    
    def get_points(self):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        if self.shape in ("end", "square"):
            corners = [
                (self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height),
            ]
        elif self.shape == "spike":
            corners = [
                (self.x, self.y + self.height),
                (self.x + self.width / 2, self.y),
                (self.x + self.width, self.y + self.height),
            ]
        elif self.shape == "slope":
            corners = [
                (self.x, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ]


        if self.rotation == 0:
            return corners
        
        angle = math.radians(self.rotation)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        rotated = []
        for point_x, point_y in corners:
            delta_x, delta_y = point_x - center_x, point_y - center_y
            rotated_x = delta_x * cos_a - delta_y * sin_a + center_x
            rotated_y = delta_x * sin_a + delta_y * cos_a + center_y
            rotated.append((rotated_x, rotated_y))
        return rotated