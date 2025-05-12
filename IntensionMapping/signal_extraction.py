import os
from scipy.io import loadmat
import numpy as np
import pandas as pd
# from mat4py import loadmat

BASE_DATA_DIR="D:/IIT_D/Sem2/BTP/emg_based_intension_prediction_elbow/EMG_Data"
BASE_EXTRACTION_PATH='D:/IIT_D/Sem2/BTP/emg_based_intension_prediction_elbow/Extracted_Data'

def get_item_from_mat(key, d):
    '''
    get_value
    ===
    Recursively searches nested dictionary for a particular key and returns its value

    Parameters
    ---
    key: int
        The key to be searched in the dictionary

    d: dict
        The nested dictionary where the key is present
    
    Returns
    ---
    any
    '''

    if type(d)!=dict:
        return None
    
    keys=d.keys()
    if keys==[]:
        return None
    if key in keys:
        return d[key]
    for k in keys:
        a=get_item_from_mat(key,d[k])
        if (a!=None):
            return a
    return None

def read_xsens_data(sub,num):
    file_name=f'{num}.xlsx'
    if num==0:
        file_name='mvc.xlsx'

    file_path=f'{BASE_DATA_DIR}/{sub}/xsens/{file_name}'
    data=pd.read_excel(file_path, sheet_name='Joint Angles ZXY')['Right Elbow Flexion/Extension']

    return data.to_numpy()


def read_emg_data(sub, num):
    file_name=f'{num}.mat'
    if num==0:
        file_name='mvc.mat'

    file_path=f'{BASE_DATA_DIR}/{sub}/EMG/{file_name}'
    signal_data=[]
    data_file=loadmat(file_path,simplify_cells=True)
    for i in range(1,10):
        sig=get_item_from_mat(f'signal_{i}',data_file)['data']
        signal_data.append(sig)

    return signal_data


def read_extracted_combined_data(subject_name: str, folder_index):
    '''
    read_extracted_combined_data
    ===
    
    Parameters
    ---
    
    subject_name : string
    
    Returns
    ---
    t, angle, emgs
     
    t : Numpy 1D Array for time data
    angle : Numpy 1D Array for elbow angle data
    emgs : List of Numpy 1D Arrays for processed emg signals
     
    '''
    # Get MVC data
    mvc=pd.read_csv(f'{BASE_EXTRACTION_PATH}/{subject_name}/9/COMBINED/angle_emg.csv')
    max_mvcs=np.zeros(9)
    for i in range(9):
        max_mvcs[i]=max(mvc[f'emg_mus_{i+1}'])


    file_folder=f'{folder_index}'
    data_combined=pd.read_csv(f'{BASE_EXTRACTION_PATH}/{subject_name}/{file_folder}/COMBINED/angle_emg.csv')


    t=data_combined['time'].to_numpy()
    angle=data_combined['elbow_angle'].to_numpy()
    emgs=[data_combined[f'emg_mus_{i+1}'].to_numpy()/max_mvcs[i] for i in range(9)]

    return t, angle, emgs


