def get_curve(x_curve, y_curve, num_interval):
    """Curve Algorithm based on Bresenham's Line Algorithm
    Produces a list of tuples 
    """
    num = len(x_curve)
    if num < num_interval:
        print("num_interval is too large.")
    ret_set = set()
    x0 = x_curve[0]
    y0 = y_curve[0]
    for i in range(num_interval, num, num_interval):
        x1 = x_curve[i]
        y1 = y_curve[i]
        points_on_line = get_line((x0, y0), (x1, y1))
        ret_set.update(points_on_line)
        x0 = x1
        y0 = y1
    if num % num_interval != 0:
        n = int(num/num_interval)*num_interval
        x0 = x_curve[n]
        y0 = y_curve[n]
        x1 = x_curve[-1]
        y1 = y_curve[-1]
        points_on_line = get_line((x0, y0), (x1, y1))
        ret_set.update(points_on_line)
    return list(ret_set)


def get_line(start, end):
    """modifed version of Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = (int(x) for x in start)
    x2, y2 = (int(x) for x in end)
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points
