import skfmm
import numpy as np
import matplotlib.pyplot as plt

nx = 200
ny = 200
x = np.arange(nx)
y = np.arange(ny)
X, Y = np.meshgrid(x, y)
loc_src = [10, 10]
nr = 5
loc_rec = []
for i in range(nr):
    loc_rec.append((170, 20 + i*30))


speed = np.sin(2*np.pi*X/200)*np.sin(2*np.pi*Y/200)
speed = speed + 1.2

phi = -1*np.ones_like(X)
phi[np.logical_and(np.abs(X-loc_src[0]) <=1, np.abs(Y-loc_src[1])<=1)] = 1
time_src = skfmm.travel_time(phi, speed)

phi = -1*np.ones_like(X)
for i in range(nr):
    phi[np.logical_and(np.abs(X-loc_rec[i][0]) <=1, np.abs(Y-loc_rec[i][1])<=1)] = 1
time_rec = skfmm.travel_time(phi, speed)

time_sum = time_src + time_rec

plt.figure()
plt.subplot(221)
plt.pcolormesh(X, Y, speed)
plt.colorbar()
plt.subplot(222)
plt.pcolormesh(X, Y, time_src)
plt.colorbar()
plt.subplot(223)
plt.pcolormesh(X, Y, time_rec)
plt.colorbar()
plt.subplot(224)
plt.pcolormesh(X, Y, time_sum)
plt.colorbar()
plt.show()
