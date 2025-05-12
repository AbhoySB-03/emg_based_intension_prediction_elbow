'''
EMG Data Processing
===================

For processing of EMG Signals
'''
import numpy as np
import scipy.signal as sc


class Bandpass_Filter:
    def __init__(self, Order, Fl, Fh, Fs):
        self.sos=sc.butter(Order, [Fl,Fh], 'bandpass', False, 'sos', Fs)
    
    def filter(self,sig):
        return sc.sosfilt(self.sos,sig)

class EMG_Processor:
    def __init__(self, Fs, Fl,Fh,  rms_ma_interval, thresh=0.075,use_filter=True):
        self.Fs=Fs
        self.Fl=Fl
        self.Fh=Fh
        self.Fn=50
        self.threshold=thresh
        self.MVC=None
        self.use_filter=use_filter
        self.filter_order=6
        self.rms_ma_length=int(rms_ma_interval*Fs)

    def remove_noise(self, sig):
        # Filter LOW FREQ Noise
        sos=sc.butter(6, [self.Fl,self.Fh], 'bandpass', False, 'sos', self.Fs)
        b_notch, a_notch=sc.iirnotch(self.Fn, 20, self.Fs)
        filt_sig=sc.sosfilt(sos, sig)
        filt_sig=sc.filtfilt(b_notch, a_notch, filt_sig)

        return filt_sig
        
    def find_envelop(self,sig):
        sig=np.power(sig,2)
        window=np.ones(self.rms_ma_length)/self.rms_ma_length
        envelop_sig=np.sqrt(np.convolve(sig, window, 'same'))

        return envelop_sig

    def processed_signal(self,raw_data, with_lowpass=True, fc=1):
        filt_sig=self.remove_noise(raw_data)
        
        # Full Wave Rectification of signal
        rect_sig=abs(filt_sig)
        envelop=self.find_envelop(rect_sig)
        
        if with_lowpass:
            envelop=self.dlp_lpf(envelop, fc, self.Fs)
       
        return envelop
    

    def dlp_lpf(self, sig, fc, Fs):
        T=1/Fs
        lpfsig=[]
        for n in range(len(sig)):
            if n==0:
                lpfsig.append(2*np.pi*fc*T*sig[n])
            else:
                lpfsig.append(lpfsig[n-1]+2*np.pi*fc*T*(sig[n]-lpfsig[n-1]))

        return np.array(lpfsig)
    
    def activation_signal(self,raw_data):        
        envelop=self.processed_signal(raw_data)
        if self.MVC==None:
            self.MVC=max(raw_data)
        normalized_sig=envelop/self.MVC
        return normalized_sig>self.threshold
