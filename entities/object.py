import math
from dataclasses import dataclass, asdict

@dataclass
class Object:
    x: int
    y: int
    width: int
    height: int
    rotation: int
    shape: str
    color: tuple[int, int, int]
    outline: tuple[int, int, int]
    modifier: str = None
    selected: bool = False
    
    def get_points(self):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        if self.shape in ("square", "end", "checkpoint", "pad", "gamemode", "speed", "gravity"):
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

        elif self.shape in ("circle", "coin", "orb"):
            sides = 20
            radius = self.width / 2
            center_x = self.x + radius
            center_y = self.y + self.height / 2
            corners = []
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                corners.append((
                    center_x + radius * math.cos(angle),
                    center_y + radius * math.sin(angle)
                ))

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

    def to_dict(self):
        d = asdict(self)
        del d["selected"]
        d["color"] = list(d["color"])
        d["outline"] = list(d["outline"])
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            x=d["x"], y=d["y"], width=d["width"], height=d["height"], rotation=d["rotation"],
            shape=d["shape"], color=tuple(d["color"]), outline=tuple(d["outline"]), modifier=d["modifier"]
        )