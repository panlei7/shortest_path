import numpy as np

def optimal_path(gradx_interp,
                 grady_interp,
                 starting_point,
                 dx,
                 N=100):
    """
    Find the optimal path from starting_point to the zero contour
    of travel_time. dx is the grid spacing
    Solve the equation x_t = - grad t / | grad t |
    """

    def get_velocity(double x, double y):
        """ return normalized velocity at pos """
        cdef double vel[2], norm
        vel[0] = gradx_interp(y, x)[0][0]
        vel[1] = grady_interp(y, x)[0][0]
        norm = (vel[0]**2 + vel[1]**2)**0.5
        vel[0] = vel[0] / norm
        vel[1] = vel[1] / norm
        return vel

    def runge_kutta(double x, double y, double ds):
        """ Fourth order Runge Kutta point update """
        cdef double k1[2], k2[2], k3[2], k4[2], r[2]
        k1 = get_velocity(x, y)
        k2 = get_velocity(x - k1[0] / 2.0*ds, y - k1[1]/2.0*ds)
        k3 = get_velocity(x - k2[0] / 2.0*ds, y - k2[1]/2.0*ds)
        k4 = get_velocity(x - k3[0] / 2.0*ds, y - k3[1]/2.0*ds)
        r[0] = x - ds *(k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) / 6.0
        r[1] = y - ds *(k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) / 6.0
        return r

    x = runge_kutta(*starting_point, dx)
    xl, yl = [], []
    for i in range(N):
        xl.append(x[0])
        yl.append(x[1])
        x = runge_kutta(*x, dx)
        distance = ((x[0] - xl[-1])**2 + (x[1] - yl[-1])**2)**0.5
        if distance < dx * 0.9999:
            break
    return xl, yl
