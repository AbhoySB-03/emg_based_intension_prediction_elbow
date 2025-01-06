import serial
# from config import *
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time
import numpy as np

BAUD=57600
# COM_IMU_L='COM6'
COM_LOAD_L='COM4'
# COM_IMU_R='COM7'
# COM_LOAD_R='COM5'

load_ser=serial.Serial(COM_LOAD_L, BAUD)

load_data_list=[]

del_t=0.01
max_duration=30

def get_load_data(load_ser, block=False):
    try:
        return float(load_ser.readline().decode('utf-8').strip())
    except:
        if not block:
            return None
        
        return get_load_data(load_ser, block)

def animate(i):
    global ln,x_data,y_data,max_duration, start_time, load_ser, del_t, load_data_list

    x_data.append(time.time()-start_time)
    l_data=get_load_data(load_ser)

    if l_data==None:
        l_data=y_data[-1]

    print(l_data)
    load_data_list.append(l_data)

    y_data.append(l_data)

    if len(x_data)>max_duration*del_t:
        x_data.pop(0)

    if len(y_data)>max_duration*del_t:
        y_data.pop(0)

    ln.set_data(x_data,y_data)

    return ln,

x_data=[]
y_data=[]

fig=plt.figure()
ax=plt.axes(x_lim=max_duration*del_t)

ln, =ax.plot(x_data,y_data)

start_time=time.time()

ani=FuncAnimation(fig, animate, interval=1000*del_t, blit=True)
end_time=time.time()

plt.plot(np.linspace(0, time.time()-start_time,len(load_data_list)), load_data_list)
plt.show()