def project(polygon, axis):
    dots = [x * axis[0] + y * axis[1] for x, y in polygon]
    return min(dots), max(dots)

def polygons_collide(poly1, poly2):
    for polygon in (poly1, poly2):
        for i, point in enumerate(polygon):
            x1, y1 = point
            x2, y2 = polygon[(i + 1) % len(polygon)]
            axis = (y2 - y1, x1 - x2)
            min1, max1 = project(poly1, axis)
            min2, max2 = project(poly2, axis)
            if max1 < min2 or max2 < min1:
                return False
    return True