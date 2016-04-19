import numpy as np
points_section = {
    (1, 1, 1): [(1, 0), (1, 1)],
    (1, 1, -1): [(0, 1), (1, 1)],
    (-1, 1, 1): [(-1, 0), (-1, 1)],
    (-1, 1, -1): [(0, 1), (-1, 1)],
    (1, -1, 1): [(1, 0), (1, -1)],
    (1, -1, -1): [(0, -1), (1, -1)],
    (-1, -1, 1): [(-1, 0), (-1, -1)],
    (-1, -1, -1): [(0, -1), (-1, -1)]
}

def get_points_nearby(gradx, grady):
    """Find the points around the current one located on the path."""

    section = tuple(np.sign((gradx, grady)))
    if abs(gradx) > abs(grady):
        steep = 1
    elif abs(gradx) < abs(grady):
        steep = -1
        gradx, grady = grady, gradx
    else:
        steep = 0

    if gradx == 0 or grady == 0 or steep == 0:
        ret = [section]*2
    else:
        ret = points_section[(*section, steep)]
        slope = abs(grady)/abs(gradx)
        if slope > 0.5:
            ret.reverse()
    return ret


def convert_coord(coord, shift):
    """Convert relative coordinate to absolute coordinate."""
    return [(coord[0] + x, coord[1] + y) for (x, y) in shift]


def find_next(grad_x, grad_y, point1, point2):
    """Find the next two points on path based on current two points."""
    x1, y1 = point1
    x2, y2 = point2
    shift1 = get_points_nearby(grad_x[y1, x1], grad_y[y1, x1])
    shift2 = get_points_nearby(grad_x[y2, x2], grad_y[y2, x2])
    next_points1 = convert_coord(point1, shift1)
    next_points2 = convert_coord(point2, shift2)
    common_points = set(next_points1) & set(next_points2)
    if len(common_points) == 1:
        diff_points = set([next_points1[0],next_points2[0]]) - common_points
        # diff_points = set(next_points1) | set(next_points2) - common_points
        if len(diff_points) == 2:
            # diff_points = list(diff_points)[np.random.randint(2)]
            # print(diff_points)
            diff_points = [diff_points, ]
        if diff_points:
            ret = list(common_points) + list(diff_points,)
        else:
            ret = list(common_points)*2
    elif len(common_points) == 2:
        ret = list(common_points)
    else:
        raise Error
    # ret = [next_points1[0], next_points2[0]]
    return ret


def find_path(grad_x, grad_y, starting_point, ending_point):
    """Find the points along the path."""
    sx, sy = starting_point
    ex, ey = ending_point
    points_path = [(sx, sy)]
    next_points = [(sx, sy)]*2
    while True:
        x0, y0 = points_path[-1]
        if abs(x0-ex) <= 1 and abs(y0-ey) <=1:
            break
        next_points = find_next(grad_x, grad_y, next_points[0], next_points[1])
        points_path.append(next_points[0])
        # points_path.extend(find_next(grad_x, grad_y, points_path[-2], points_path[-1]))
    return set(points_path)



