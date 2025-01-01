from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def rot_mat_2d(theta):
    return np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])

def arm_points(thetas, lengths):
    x=[0]
    y=[0]

    orig=np.array([[0],[0]])
    rot_mat=np.eye(2)
    if len(thetas)!=len(lengths):
        raise AssertionError('arrays "thetas" and "lengths" must be of same length')
    
    for t, l in zip(thetas, lengths):
        rot_mat=rot_mat @ rot_mat_2d(t)
        orig=orig+rot_mat @ (np.array([[l],[0]]))
        x.append(orig[0,0])
        y.append(orig[1,0])

    return x,y


if __name__=='__main__':
    thetas=[3.14/2,3.14/6,-3.14/4]
    lengths=[1.5,1,0.8]

    fig=plt.figure()
    axis=plt.axes(xlim=(-4,4), ylim=(-4,4))
    xp,yp=arm_points(thetas,lengths)

    axis.plot(xp,yp)

    plt.grid(True)
    plt.show()