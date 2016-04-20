import numpy as np
from scipy.interpolate import RectBivariateSpline
from numpy.core.umath_tests import inner1d


def optimal_path_runge_kutta(gradx_interp,
                             grady_interp,
                             starting_point,
                             dx,
                             N=100):
    """
    Find the optimal path from starting_point to the zero contour
    of travel_time. dx is the grid spacing
    Solve the equation x_t = - grad t / | grad t |
    """

    def get_velocity(position):
        """ return normalized velocity at pos """
        x, y = position
        vel = np.array([gradx_interp(y, x)[0][0], grady_interp(y, x)[0][0]])
        # return vel / np.linalg.norm(vel)
        return vel / np.sqrt(inner1d(vel, vel))

    def runge_kutta(pos, ds):
        """ Fourth order Runge Kutta point update """
        k1 = ds * get_velocity(pos)
        k2 = ds * get_velocity(pos - k1 / 2.0)
        k3 = ds * get_velocity(pos - k2 / 2.0)
        k4 = ds * get_velocity(pos - k3)
        return pos - (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

    x = runge_kutta(starting_point, dx)
    xl, yl = [], []
    for i in range(N):
        xl.append(x[0])
        yl.append(x[1])
        x = runge_kutta(x, dx)
        distance = ((x[0] - xl[-1])**2 + (x[1] - yl[-1])**2)**0.5
        if distance < dx * 0.9:
            break
    return xl, yl


def optimal_path_euler(gradx_interp,
                       grady_interp,
                       starting_point,
                       ending_point,
                       dx,
                       N=100):
    def get_velocity(position):
        """ return normalized velocity at pos """
        x, y = position
        vel = np.array([gradx_interp(y, x)[0][0], grady_interp(y, x)[0][0]])
        # return vel / np.linalg.norm(vel)
        return vel / np.sqrt(inner1d(vel, vel))

    def euler_point_update(pos, ds):
        return pos - get_velocity(pos) * ds

    x = euler_point_update(starting_point, dx)
    ex, ey = ending_point
    xl, yl = [], []
    for i in range(N):
        xl.append(x[0])
        yl.append(x[1])
        x = euler_point_update(x, dx)
        distance = ((x[0] - ex)**2 + (x[1] - ey)**2)**0.5
        if distance < dx * 2:
            break
    return xl, yl
