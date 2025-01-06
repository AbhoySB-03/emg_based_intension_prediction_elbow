import serial
import numpy as np
from ctypes import *
import time

EPOS_DLL_PATH=''
cdll.LoadLibrary(EPOS_DLL_PATH)


################################  CONSTANTS  #####################################
BAUD=56700

# Body Parameters  
g=9.8   # acceleration due to gravity
m_e=2.5 # elbow mass 
m_l=0
l_c=0.181479    # elbow to shoulder length 
l_l=0.25    # elbow to forearm length
a1= 0.05    # arm strap width
a2= 0.05    # forearm straop width 
b1= 0.17    # elbow to armstrap
b2= 0.210   # elbow to forearm strap length
Rm=0.035    #spool radius

m_t=m_e+m_l
l_t=(m_e*l_c+m_l*l_l)/(m_e+m_l)


# Actuation Related
gear_ratio=66
KPt=10
Kv=10
T2V=247


##################################################################################

class LoadCell:
    def __init__(self, com_port, baudrate, smoother_window=1, debug=False, debug_id=None):
        self.ser=serial.Serial(com_port, baudrate)
        self.last_data=[0.0]
        self.ma_window=smoother_window
        self.ref_load=0.0
        self.ser.read_all()
        self.debug=debug
        self.debug_id=f'LD{np.random.randint()}' if debug_id==None else debug_id

    def get_data(self, raw=False, absolute=False):
        try:
            r_data=float(self.ser.readline().decode('utf-8').strip())
            self.last_data.append(r_data)
            if len(self.last_data)>self.ma_window:
                self.last_data.pop(0)
        except:
            if self.debug:
                print('Error! Taking last ',end='')
            r_data=self.last_data[-1]
        
        data=np.mean(self.last_data)

        if not raw:
            data=self.convert_to_kg(data)

        if self.debug:
            print(f'LoadCell Data (ID {self.debug_id}) => RAW: {r_data}   PROCESSED: {data}', end='  ')


        if not absolute:
            data=data-self.ref_load
            if self.debug:
                print(f'RELATIVE: {data}')
        else:
            if self.debug:
                print('')

        return data
    
    def convert_to_kg(self, data):
        return 0.0017*data-0.097
    
    def calibrate(self):
        debug_mode=self.debug
        self.debug=False
        self.ser.read_all()
        time.sleep(0.1)
        self.ref_load=self.get_data(raw=True, absolute=True)
        self.debug=debug_mode
        self.ser.read_all()
    
class IMU:
    def __init__(self, com_port, baudrate, in_radians=False, debug=False, debug_id=None):
        self.ser=serial.Serial(com_port, baudrate)
        self.in_rads=in_radians
        self.last_data=np.zeros(3)
        self.ref_angle=np.zeros(3)
        self.ser.read_all()

        self.debug=debug
        self.debug_id=f'IM{np.random.randint()}' if debug_id==None else debug_id
        
    def get_orientation(self, absolute=False):
        try:
            data=self.ser.readline().decode('utf-8')
            angles=map(float, data.split('\t'))


            if len(angles)==3:
                angles=np.array(angles) * (np.pi/180.0 if self.in_rads else 1.0)
                self.last_data=angles
                return_data=angles
            else:
                return_data=self.last_data
        except:
            if self.debug:
                print('Error! Taking last ',end='')
            return_data= self.last_data
        if not absolute:
            return_data=return_data-self.ref_angle
        if self.debug:
            print(f'IMU Data (ID {self.debug_id}) : {return_data}')

        return return_data
        
    

    def calibrate(self):        
        self.ser.read_all()
        time.sleep(0.1)
        self.ref_angle=self.get_orientation(absolute=True)
        self.ser.read_all()


class Motor:
    def __init__(self, debug=False, debug_id=None,unpowered=False):
        self.config_success=False
        self.epos=CDLL(EPOS_DLL_PATH)
        self.epos_keyhandle=0
        self.NodeID=1
        self.unpowered=unpowered
        self.pErrorCode=c_uint() 
        self.debug=debug
        self.debug_id=f'M{np.random.randint()}' if debug_id==None else debug_id

    def config(self):        
        self.debug_print('Configuring Motor...')
        self.epos_keyhandle=self.epos.VCS_OpenDevice(b'EPOS4', b'MAXON SERIAL V2', b'USB', b'USB0', byref(self.pErrorCode))

        if self.epos_keyhandle!=0:
            self.debug_print('Device Port opened succesfully!')
            if self.epos.VCS_SetProtocolStackSettings(self.epos_keyhandle, 1000000, 500, byref(self.pErrorCode)):
                self.debug_print("Protocol stack settings configured successfully!")
                if self.epos.VCS_ClearFault(self.keyhandle,self.NodeID,byref(self.pErrorCode))!=0:
                    self.debug_print("Fault cleared successfully")
                    if self.epos.VCS_ActivateVelocityMode(self.keyhandle, self.NodeID, byref(self.pErrorCode)) != 0:
                        self.debug_print("Velocity mode activated successfully!")
                        if self.epos.VCS_SetEnableState(self.keyhandle, self.NodeID, byref(self.pErrorCode))!=0:
                            self.set_velocity(0)
                            self.config_success=True
                        else:
                            self.debug_print("Unable to Enable Device!")
                    else:
                        self.debug_print("Failed to activate velocity mode!")
                else:
                    self.debug_print("Unable to clear fault!")
            else:
                self.debug_print("Failed to set protocol stack settings!")
        else:
            self.debug_print('Could not open Com-Port')
            self.debug_print('Keyhandle: %8d' % self.keyhandle)
            self.debug_print('Error Openening Port: %#5.8x' % self.pErrorCode.value)   


    def set_velocity(self, velocity):
        if not self.config_success or self.unpowered:
            print(f'Target Velocity: {velocity}')
            return
        
        if self.epos.VCS_SetVelocityMust(self.keyhandle, self.NodeID, velocity, byref(self.pErrorCode)) != 0:
            self.debug_print(f'Running Motor {self.debug_id} with Velocity: {velocity}')
        else:
            print(f'Motor {self.debug_id} not running. Target velocity: {velocity}')
            

    def stop_motor(self):
        self.set_velocity(0,self.keyhandle)
        self.epos.VCS_CloseDevice(self.keyhandle, byref(self.pErrorCode))
        self.debug_print(f"Motor {self.debug_id} Connection closed successfully!")
        if self.epos.VCS_SetDisableState(self.keyhandle, self.NodeID, byref(self.pErrorCode)):
            self.debug_print(f"Motor {self.debug_id} Disabled")
        else:
            self.debug_print(f"Unable to Disable Motor {self.debug_id}!")


    def debug_print(self, a):
        if self.debug:
            print(a)


def get_Jf(theta):
    Hf = np.sqrt((b2*np.sin(theta)+a2*np.cos(theta)-a1)**2+(a2*np.sin(theta)-b2*np.cos(theta)-b1)**2)-(b1+b2)
    Jf = -(((a1*a2 - b1*b2)*np.sin(theta) - (a1*b2 + a2*b1)*np.cos(theta))/(Hf + b1+b2))
    
    return Jf



def calculate_current_torque(theta, load):
    Jf=get_Jf(theta)

    weight=load * g
    weight=max(min(200,weight),0) # Limit weight between 0 to 200 N

    return weight * Jf , Jf

def calculate_angular_velocity(theta, last_theta, last_time):
    del_t=max(time.time()-last_time,0.0001)

    return (theta-last_theta)/del_t


def calculate_required_torque(theta):
    return m_t * g * l_t * np.sin(theta)


def control_loop():
    angle_values=imu1.get_orientation()
    theta=angle_values[2]   # Taking z-axis angle
    
    load=load1.get_data()

    curr_torque, Jf=calculate_current_torque(theta,load)
    velocity_comp=Kv * calculate_angular_velocity(theta, prev_theta, prev_time) * Rm * gear_ratio * 60/(Jf * 2 * np.pi)

    prev_theta=theta
    prev_time=time.time()

    torque_error=calculate_required_torque(theta)-curr_torque

    p_control_comp=KPt * T2V * torque_error

    target_rpm=velocity_comp+p_control_comp

    
    # # In case not much movement, dont move motor
    # thresh=20
    # if -thresh<velocity_comp and thresh>velocity_comp:
    #     target_rpm=0

    motor1.set_velocity(int(target_rpm))

    







def Init():
    global load1, imu1, motor1, prev_time, prev_theta

    load1=LoadCell('COM4', BAUD, debug=True, debug_id='LD1')
    imu1=IMU('COM6', BAUD, debug=True, debug_id='IM1' )
    motor1=Motor(debug=True, debug_id='M1', unpowered=True)

    load1.calibrate()
    imu1.calibrate()
    motor1.config()

    prev_time=time.time()
    prev_theta=0.0


def Loop():
    control_loop()

def End():    
    motor1.stop_motor()






if __name__=='__main__':
    try:
        Init()
        for _ in range(100000):  # Change to While True when finalized
            Loop()
    except KeyboardInterrupt:
        pass

    End()

        
