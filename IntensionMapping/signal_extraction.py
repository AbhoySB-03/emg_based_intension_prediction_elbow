import os
from scipy.io import loadmat
import pandas as pd
# from mat4py import loadmat

BASE_DATA_DIR="../EMG_Data"
BASE_EXTRACTION_PATH='../Extracted_Data'

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
