import serial
from config import *
import numpy as np
from visualizer import *

imu_ser1=serial.Serial('COM4',BAUD)
imu_ser2=serial.Serial('COM5',BAUD)

def get_angle_from_imu(L,H):
    ang=((H<<8)|L)/32768*180
    if ang>180:
        ang=ang-360
    return ang

def get_imu_orientation(imu_ser):
    if not imu_ser.read(2)[1]==83:
        return
    
    angles=np.zeros(3)
    for i in range(3):
        ang=imu_ser.read(2)
        angles[i]=get_angle_from_imu(ang[0],ang[1])

    return angles[0],angles[1],angles[2]


fig=plt.figure()
ax=plt.axes(xlim=(-4,4),ylim=(-4,4))

ln, = ax.plot([],[],linewidth=5)

ref_angle1=(0,0,0)
ref_angle2=(0,0,0)

def animate(i):
    global ln

    angles1=get_imu_orientation(imu_ser1)
    angles2=get_imu_orientation(imu_ser2)

    if angles1==None or angles2==None:
        return ln,
    thetas=[angles1[0]*3.14/180,angles2[0]*3.14/180]
    lengths=[1.2,1.5]
    print(thetas)
    xp,yp=arm_points(thetas,lengths)
    
    ln.set_data(xp,yp)

    return ln,


    
try:   
    ani=FuncAnimation(fig, animate, interval=10, blit=True, cache_frame_data=False)
    plt.show()

except KeyboardInterrupt:
    print("Done.")