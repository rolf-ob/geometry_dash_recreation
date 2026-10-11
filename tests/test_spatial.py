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

"""import pytest

@pytest.mark.parametrize("shape", ["square", "right slope"])
def test_touching_shapes_collide(shape):
    a = make_shape(0, 0, shape)
    b = make_shape(40, 0, shape)
    assert collide(a, b)

Rotated polygons, touching corners, zero-sized shapes

Slope collisions with normal and reversed gravity

Clicking, releasing, and adding trail points

One ID, multiple IDs, missing IDs, repeated activation

Several edits, undo all, redo all, then save

Save/load round-trip preserves object properties

New account, login, invalid password, invalid username

Empty directory, missing checkpoint, malformed JSON

Pause, resume, frame step, low FPS, temporary lag

First completion, repeat completion, cheated completion

For collision detection, I'd also use property-based testing with randomly generated rectangles and rotations. That can find geometry edge cases that hand-written examples miss.""" #!

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