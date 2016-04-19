import skfmm
import numpy as np
import matplotlib.pyplot as plt

nx = 100
ny = 100
src = (10, 10)
rec = (70, 90)
coordx = np.arange(nx)
coordy = np.arange(ny)
X, Y = np.meshgrid(coordx, coordy)
speed = np.sin(2*np.pi*X/200)*np.sin(2*np.pi*Y/200)
speed = speed + 1.2
phi = -1*np.ones_like(X)
phi[np.logical_and(np.abs(X-src[0]) <=1, np.abs(Y-src[1])<=1)] = 1
t1 = skfmm.travel_time(phi, speed)
phi = -1*np.ones_like(X)
phi[np.logical_and(np.abs(X-rec[0]) <= 1, np.abs(Y-rec[1]) <= 1)] = 1
t2 = skfmm.travel_time(phi, speed)

t = t1 + t2
print(t.min())
a = np.zeros_like(t)
a[t <t.min()*1.005] = 1
print((a == 1).sum())
plt.figure()
plt.subplot(211)
plt.pcolormesh(X, Y, a, cmap='Greys')
plt.colorbar()
plt.subplot(212)
plt.hist(t.flatten(), 500, color='k')
plt.show()

