from visualizer import *
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation

angle_range=[0.0,120.0]

def lerp(a,b,t):
    return a+(b-a)*t

def protocol_to_signal(protocol, T, del_t=0.01):
    flex_sig=lerp(angle_range[0], angle_range[1],np.sin(np.linspace(0,np.pi/2,int(T/del_t))))
    ext_sig=lerp(angle_range[1], angle_range[0],np.sin(np.linspace(0,np.pi/2,int(T/del_t))))
    hold_up=np.ones(int(T/del_t))*angle_range[1]
    hold_down=np.ones(int(T/del_t))*angle_range[0]

    prot_dic={'F':flex_sig,'E':ext_sig,'H':hold_up,'h':hold_down}
    final_sig=np.ravel(np.array([prot_dic[l] for l in protocol]))

    return final_sig

    
del_t=0.01

T=1.5

protocol1='hh'+'FE' * 5+'h'
protocol2='hh'+'FHHEhh' * 3+'h'

selected_prot=[protocol1, protocol2][int(input('Enter Protocol Number: \n\t1. Flexion Extension (5 reps)\n\t2. Flexion Hold Extension Hold (3 reps)\n\n Ans:'))-1]
angle_values=protocol_to_signal(selected_prot,T,del_t)

# plt.plot(angle_values)
# plt.show()


fig=plt.figure()
fig.waitforbuttonpress()
axis=plt.axes(xlim=(-1,4), ylim=(-4,1))

ln, =axis.plot([],[],linewidth=10)


def animate(i):
    global angle_values,ln
    
    try:
        if i<len(angle_values): 
            print(i)       
            thetas=[-np.pi/2,angle_values[i]*np.pi/180]
            lengths=[1.2,1.5]

            xp,yp=arm_points(thetas, lengths)
            
            ln.set_data(xp,yp)
        else:
            print('Done')
            exit()
        return ln,
    except KeyboardInterrupt:
        print('Interupt...')

ani=FuncAnimation(fig, animate, interval=1000*del_t, blit=True)

plt.show()