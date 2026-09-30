import math
from dataclasses import dataclass, asdict

@dataclass
class Object:
    x: int
    y: int
    width: int
    height: int
    rotation: float
    shape: str
    color: tuple[int, int, int]
    outline: tuple[int, int, int]

    modifier: str = None
    selected: bool = False
    interacted: bool = False
    group_id: int = 0

    def __post_init__(self):
        self.recompute()
    
    def recompute_points(self):
        if self.shape in ("square", "end", "checkpoint", "gamemode", "speed", "gravity", "size", "pad"):
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
        elif self.shape == "right slope":
            corners = [
                (self.x, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ]

        elif self.shape == "left slope":
            corners = [
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ]

        elif self.shape in ("circle", "orb", "coin"):
            sides = 20
            corners = []
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                corners.append((
                    self.x + self.width / 2 * math.cos(angle) + self.width / 2,
                    self.y + self.height / 2 * math.sin(angle) + self.height / 2
                ))

        if self.rotation == 0:
            self.points = corners
        else:
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            angle = math.radians(self.rotation)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            self.points = []
            for point_x, point_y in corners:
                delta_x, delta_y = point_x - center_x, point_y - center_y
                rotated_x = delta_x * cos_a - delta_y * sin_a + center_x
                rotated_y = delta_x * sin_a + delta_y * cos_a + center_y
                self.points.append((rotated_x, rotated_y))

    def recompute_axes(self):
        self.axes = []
        for i, point in enumerate(self.points):
            x1, y1 = point
            x2, y2 = self.points[(i + 1) % len(self.points)]
            self.axes.append((y2 - y1, x1 - x2))

    def recompute_aabb(self):
        self.aabb = {}
        x_values = [point[0] for point in self.points]
        y_values = [point[1] for point in self.points]

        self.aabb["top"] = min(y_values)
        self.aabb["bottom"] = max(y_values)
        self.aabb["left"] = min(x_values)
        self.aabb["right"] = max(x_values)

    def recompute(self):
        self.recompute_points()
        self.recompute_axes()
        self.recompute_aabb()

    def to_dict(self):
        d = asdict(self)
        del d["selected"]
        del d["interacted"]
        d["color"] = list(d["color"])
        d["outline"] = list(d["outline"])
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            x=d["x"], y=d["y"], width=d["width"], height=d["height"], rotation=d["rotation"],
            shape=d["shape"], color=tuple(d["color"]), outline=tuple(d["outline"]),
            modifier=d["modifier"], group_id=d["group_id"]
        )