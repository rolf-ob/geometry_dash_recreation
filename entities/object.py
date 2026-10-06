import math
from dataclasses import dataclass, field, asdict

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
    triggers: list = field(default_factory=list)

    def __post_init__(self):
        self.recompute()
    
    def recompute_points(self):
        if self.real_shape in ("square", "end", "checkpoint", "gamemode", "speed", "gravity", "size", "teleport", "pad", "trigger", "text"):
            corners = [
                (self.real_x, self.real_y),
                (self.real_x + self.real_width, self.real_y),
                (self.real_x + self.real_width, self.real_y + self.real_height),
                (self.real_x, self.real_y + self.real_height),
            ]
        elif self.real_shape == "spike":
            corners = [
                (self.real_x, self.real_y + self.real_height),
                (self.real_x + self.real_width / 2, self.real_y),
                (self.real_x + self.real_width, self.real_y + self.real_height),
            ]
        elif self.real_shape == "right slope":
            corners = [
                (self.real_x, self.real_y),
                (self.real_x + self.real_width, self.real_y + self.real_height),
                (self.real_x, self.real_y + self.real_height)
            ]

        elif self.real_shape == "left slope":
            corners = [
                (self.real_x + self.real_width, self.real_y),
                (self.real_x + self.real_width, self.real_y + self.real_height),
                (self.real_x, self.real_y + self.real_height)
            ]

        elif self.real_shape in ("circle", "orb", "coin"):
            sides = 20
            corners = []
            for i in range(sides):
                angle = 2 * math.pi * i / sides
                corners.append((
                    self.real_x + self.real_width / 2 * math.cos(angle) + self.real_width / 2,
                    self.real_y + self.real_height / 2 * math.sin(angle) + self.real_height / 2
                ))

        if self.real_rotation == 0:
            self.points = corners
        else:
            center_x = self.real_x + self.real_width / 2
            center_y = self.real_y + self.real_height / 2
            angle = math.radians(self.real_rotation)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            self.points = []
            for point_x, point_y in corners:
                delta_x, delta_y = point_x - center_x, point_y - center_y
                rotated_x = delta_x * cos_a - delta_y * sin_a + center_x
                rotated_y = delta_x * sin_a + delta_y * cos_a + center_y
                self.points.append((rotated_x, rotated_y))

    def recompute_axes(self):
        all_axes = []
        for i, point in enumerate(self.points):
            x1, y1 = point
            x2, y2 = self.points[(i + 1) % len(self.points)]
            all_axes.append((y2 - y1, x1 - x2))

        self.axes = []
        for axis in all_axes:
            parallel = False

            for other in self.axes:
                cross = axis[0] * other[1] - axis[1] * other[0]
                if abs(cross) < 1e-9:
                    parallel = True
                    break

            if not parallel:
                self.axes.append(axis)

    def recompute_aabb(self):
        self.aabb = {}
        x_values = [point[0] for point in self.points]
        y_values = [point[1] for point in self.points]

        self.aabb["top"] = min(y_values)
        self.aabb["bottom"] = max(y_values)
        self.aabb["left"] = min(x_values)
        self.aabb["right"] = max(x_values)

    def recompute(self):
        self.real_x = self.x
        self.real_y = self.y
        self.real_width = self.width
        self.real_height = self.height
        self.real_rotation = self.rotation
        self.real_shape = self.shape
        self.real_color = self.color
        self.real_outline = self.outline
        self.real_modifier = self.modifier

        self.recompute_points()
        self.recompute_axes()
        self.recompute_aabb()

    def recompute_triggered(self):
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
            modifier=d["modifier"], group_id=d["group_id"], triggers=d["triggers"]
        )