from search_path import get_points_nearby, convert_coord, find_path
import pytest
import numpy as np
import skfmm
from scipy.interpolate import RectBivariateSpline
from optimal_path import optimal_path_runge_kutta, optimal_path_euler
import optimal_path_cython
from skimage.graph import route_through_array

from bresenham import get_curve


def test_0_1():
    x = get_points_nearby(0, 1)
    assert x == [(0, 1), (0, 1)]

def test_20_0():
    x = get_points_nearby(20, 0)
    assert x == [(1, 0), (1, 0)]


def test_1_1():
    x = get_points_nearby(1, 1)
    assert x == [(1, 1), (1, 1)]


def test_1_2():
    x = get_points_nearby(1, 2)
    assert x == [(0, 1), (1, 1)]

def test_1_3():
    x = get_points_nearby(2, 3)
    assert x == [(1, 1), (0, 1)]

def test__2_1():
    x = get_points_nearby(-2, 1)
    assert x == [(-1, 0), (-1, 1)]

def test_3_2():
    x = get_points_nearby(3, 2)
    assert x == [(1, 1), (1, 0)]

def test_1_3():
    x = get_points_nearby(1, -3)
    assert x == [(0, -1), (1, -1)]

def test_coord_convert():
    x = convert_coord((10, 10), [(0, -1), (1, -1)])
    assert x == [(10, 9), (11, 9)]

def test_find_path1():
    x = np.arange(0, 20)
    y = np.arange(0, 20)
    X, Y = np.meshgrid(x, y)
    Z = (X-10)**2 + (Y-10)**2
    grad_x = -2*(X-10)
    grad_y = -2*(Y-10)
    starting_point = (15, 10)
    ending_point = (10, 10)
    path_points = find_path(grad_x, grad_y, starting_point, ending_point)
    target = {(i, 10) for i in range(15, 10, -1)}
    assert len(target - path_points) == 0 or len(path_points - target) == 0


def test_find_path2():
    x = np.arange(0, 20)
    y = np.arange(0, 20)
    X, Y = np.meshgrid(x, y)
    Z = (X-10)**2 + (Y-10)**2
    grad_x = -2*(X-10)
    grad_y = -2*(Y-10)
    starting_point = (15, 15)
    ending_point = (10, 10)
    path_points = find_path(grad_x, grad_y, starting_point, ending_point)
    target = {(i, i) for i in range(15, 10, -1)}
    assert len(target - path_points) == 0 or len(path_points - target) == 0

def test_find_path3():
    x = np.arange(0, 200)
    y = np.arange(0, 200)
    X, Y = np.meshgrid(x, y)
    Z = (X-100)**2/100 + (Y-100)**2/200
    np.save('z.npy', Z)
    grad_x = -2*(X-100)/100
    grad_y = -2*(Y-100)/200
    starting_point = (120, 170)
    ending_point = (100, 100)
    path_points = find_path(grad_x, grad_y, starting_point, ending_point)
    print(path_points)
    np.save('temp.npy', list(path_points))
    assert 0

@profile
def test_find_path4():
    nx = 100
    ny = 100
    loc_src = (10, 10)
    loc_rec = (70, 90)
    coordx = np.arange(nx)
    coordy = np.arange(ny)
    X, Y = np.meshgrid(coordx, coordy)
    phi = -1*np.ones_like(X)
    phi[np.logical_and(np.abs(X-loc_src[0]) <=1, np.abs(Y-loc_src[1])<=1)] = 1
    speed = np.sin(2*np.pi*X/200)*np.sin(2*np.pi*Y/200)
    speed = speed + 1.2
    t = skfmm.travel_time(phi, speed)
    # t = (X-loc_src[0])**2/5 + (Y-loc_src[1])**2/10
    dx = 1.
    grad_t_y, grad_t_x = np.gradient(t, dx)
    if isinstance(t, np.ma.MaskedArray):
        grad_t_y[grad_t_y.mask] = 0.0
        grad_t_y = grad_t_y.data
        grad_t_x[grad_t_x.mask] = 0.0
        grad_t_x = grad_t_x.data

    gradx_interp = RectBivariateSpline(coordy, coordx, grad_t_x)
    grady_interp = RectBivariateSpline(coordy, coordx, grad_t_y)

    ### 1. the modified version base on the original
    #--------------------------------------------------
    xl, yl = optimal_path_runge_kutta(gradx_interp, grady_interp, loc_rec, dx)
    grid_indx = get_curve(xl, yl, 5)
    ix1_1, iy1_1 = zip(*grid_indx)
    xl, yl = optimal_path_euler(gradx_interp, grady_interp, loc_rec, loc_src, dx)
    grid_indx = get_curve(xl, yl, 5)
    ix1_2, iy1_2 = zip(*grid_indx)


    ### 2. Cython version
    #--------------------------------------------------
    xl, yl = optimal_path_cython.optimal_path(gradx_interp, grady_interp, loc_rec, dx)
    grid_indx = get_curve(xl, yl, 5)
    ix2, iy2 = zip(*grid_indx)


    ### 3. A version that I try to use the Bresenham's algorithm on discrete points directly
    ###    There are some problems for the curve path.
    #--------------------------------------------------
    path_points = find_path(-grad_t_x, -grad_t_y, loc_rec, loc_src)
    ix3, iy3 = zip(*path_points)


    ### 4. Use two travel time addition to get the path.
    ###    The path is not a line, but it's enough for me.
    ###    the parameter "percent" is trival.
    #--------------------------------------------------
    phi2 = -1*np.ones_like(X)
    phi2[np.logical_and(np.abs(X-loc_rec[0]) <=1, np.abs(Y-loc_rec[1])<=1)] = 1
    t2 = skfmm.travel_time(phi2, speed)
    t_sum = t + t2
    t_min = t_sum.min()
    percent = 0.003
    iy4, ix4 = np.where(t_sum < t_min*(1 + percent))
    t_max = t_sum.max()
    w = np.exp(-300*(t_sum-t_min)/(t_max-t_min))

    # 5. skimage.graph.route_through_array
    loc_src = (10, 10)
    loc_rec = (90, 70)  # x, y  < -- > y, x
    slowness = 1./speed
    grid_indx, weight = route_through_array(slowness, loc_src, loc_rec)
    iy5_1, ix5_1 = zip(*grid_indx)
    grid_indx, weight = route_through_array(slowness, loc_src, loc_rec, fully_connected=False)
    iy5_2, ix5_2 = zip(*grid_indx)


    # import pylab as pl
    # pl.figure()
    # pl.pcolormesh(X, Y, w)
    # pl.colorbar()
    # pl.figure()
    # pl.pcolormesh(X, Y, speed)
    # pl.colorbar()
    # pl.plot(ix1_1, iy1_1, 'k*', label='runge-kutta')
    # # pl.plot(ix5_1, iy5_1, 'ro', label='skimage-diagnoal-permit')
    # # pl.plot(ix5_2, iy5_2, 'b^', label='skimage-axis-only')
    # pl.plot(ix1_2, iy1_2, 'ro', label='euler')
    # pl.legend(loc=4)
    # pl.show()

    # pl.figure()
    # pl.pcolormesh(X, Y, grad_t_x)
    # pl.colorbar()
    # pl.figure()
    # pl.pcolormesh(X, Y, grad_t_y)
    # pl.colorbar()
    # pl.show()
    # np.save('t.npy', t)
    # np.save('a.npy', grid_indx)
    # np.save('b.npy', list(path_points))
    # assert len(set(grid_indx) - path_points) == 0
    assert 1

if __name__ == '__main__':
    test_find_path4()
