from config import *
import serial

class Load_Cell:
    def __init__(self, com_port, baud):
        self.ser=serial.Serial(com_port, baud)

    def get_data(self):
        line=self.ser.readline().decode('utf-8').strip()
        try:
            data=float(line)
        except ValueError:
            return
        return data
    

class IMU:
    def __init__(self, com_port, baud):
        self.ser=serial.Serial(com_port, baud)

    def get_orientation(self):
        ang_r=0
        ang_y=0
        ang_p=0

        return ang_r, ang_y, ang_p
    



