from entities.object import Object
from entities.spatial import collide

def make_shape(x, y, shape):
    return Object(
        x, y,
        40, 40,
        0,
        shape,
        (255, 255, 255),
        (0, 0, 0)
    )

for shape in ["square", "right slope"]:
    def test_touching_shapes_collide():
        a = make_shape(0, 0, shape)
        b = make_shape(40, 0, shape)
        assert collide(a, b)

    def test_separated_shapes_do_not_collide():
        a = make_shape(0, 0, shape)
        b = make_shape(41, 0, shape)
        assert not collide(a, b)

    def test_tiny_gap_is_treated_as_collision():
        a = make_shape(0, 0, shape)
        b = make_shape(40 + 1e-15, 0, shape)
        c = make_shape(40 + 1e-14, 0, shape)
        assert collide(a, b)
        assert not collide(a, c)