from constants import BUCKET_WIDTH

def project(polygon, axis):
    dots = [x * axis[0] + y * axis[1] for x, y in polygon]
    return min(dots) - 1e-9, max(dots) + 1e-9

def polygons_collide(obj1, obj2):
    for shape in (obj1, obj2):
        for axis in shape.axes:
            min1, max1 = project(obj1.points, axis)
            min2, max2 = project(obj2.points, axis)
            if max1 < min2 or max2 < min1:
                return False
    return True

def aabb_collide(obj1, obj2):
    return not (
        obj1.aabb["top"] > obj2.aabb["bottom"] or
        obj1.aabb["bottom"] < obj2.aabb["top"] or
        obj1.aabb["left"] > obj2.aabb["right"] or
        obj1.aabb["right"] < obj2.aabb["left"]
    )

def collide(collider, obj):
    return aabb_collide(collider, obj) and polygons_collide(collider, obj)

def get_buckets(obj):
    start_bucket = int(obj.aabb["left"] // BUCKET_WIDTH)
    end_bucket = int(obj.aabb["right"] // BUCKET_WIDTH)
    return range(start_bucket, end_bucket+1)

def get_nearby_objects(buckets, start, end, z_order=None):
    start_bucket = int(start // BUCKET_WIDTH)
    end_bucket = int(end // BUCKET_WIDTH)
    objects = []
    seen = set()

    for bucket in range(start_bucket, end_bucket+1):
        for obj in buckets.get(bucket, []):
            if id(obj) not in seen:
                seen.add(id(obj))
                objects.append(obj)

    if z_order:
        objects.sort(key=lambda obj: z_order[id(obj)])

    return objects