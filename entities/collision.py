from rendering.rendering import within_view

def project(polygon, axis):
    dots = [x * axis[0] + y * axis[1] for x, y in polygon]
    return min(dots), max(dots)

def polygons_collide(obj1, obj2):
    for shape in (obj1, obj2):
        for axis in shape.axes:
            min1, max1 = project(obj1.points, axis)
            min2, max2 = project(obj2.points, axis)
            if max1 < min2 or max2 < min1:
                return False
    return True

def aabb_collide(obj1, obj2):
    return obj1.aabb["top"] < obj2.aabb["bottom"] and obj1.aabb["bottom"] > obj2.aabb["top"] and obj1.aabb["left"] < obj2.aabb["right"] and obj1.aabb["right"] > obj2.aabb["left"]

def collide(game, collider, obj):
    return within_view(game, obj.points) and aabb_collide(collider, obj) and polygons_collide(collider, obj)