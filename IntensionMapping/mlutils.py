import numpy as np
from signal_extraction import BASE_EXTRACTION_PATH, read_extracted_combined_data
import cv2
import os
from scipy.stats import mode

def generate_classifier_signal(angle, smoothing_window=2000, grad_thresh=15):
    '''
    generate_classifier_signal
    ===
    
    Generates the classifier signal as :
        0: held down
        1: flexion
        2: extension
        3: held up

    Parameters
    ---
    > smoothing_window : smoothening the signal
    > grad_thersh: if gradient is below this threshold, consider it to be in held position
        
    '''
    del_angle=(angle[1:]-angle[:-1])*2000
    del_angle=np.r_[angle[0], del_angle]

    del_angle=np.convolve(del_angle, np.ones(smoothing_window)/smoothing_window, 'same')
    # plt.plot(del_elbow_angle)

    flex_ex_sig=np.zeros(len(del_angle), dtype=np.int32)
    flex_ex_sig[del_angle>grad_thresh]=1
    flex_ex_sig[del_angle<-grad_thresh]=2
    flex_ex_sig[(flex_ex_sig==0) & (angle>45)]=3

    return flex_ex_sig

def generate_image(emg, widthpersignal=30):
    length=emg.shape[-1]
    total_image=np.zeros((3*widthpersignal, length))
    print(total_image.shape)
    for i in range(3):
        for j in range(widthpersignal):
            total_image[widthpersignal*i+j,emg[i]>=(j/30)]=1

    return total_image


def generate_classified_muscle_images(classifier_sig, emg_signals, selected_muscles, window_duration=0.1, sampling_freq=2000, num_examples=100):
    window_length=int(window_duration*sampling_freq) #ms

    split_pos=np.r_[True,(classifier_sig[1:]-classifier_sig[:-1])!=0,True]
    split_indices=np.linspace(0,len(split_pos)-1,len(split_pos), dtype=np.int32)[split_pos]
    category_split_indices=[[],[],[],[]]

    for i in range(len(split_indices)-1):
        val=classifier_sig[(split_indices[i]+split_indices[i+1])//2]

        category_split_indices[val].append((split_indices[i],split_indices[i+1]))

    muscle_images=[[],[],[],[]]
    for i in range(len(category_split_indices)):
        for _ in range(num_examples):
            rnd_inx=np.random.choice(range(len(category_split_indices[i])))
            indices=category_split_indices[i][rnd_inx]
            if indices[1]-indices[0]<=window_length:
                continue

            
            select_index=np.random.randint(indices[0], indices[1]-window_length-1)
            image=[]
            for m in selected_muscles:
                image.append(emg_signals[m-1][select_index:select_index+window_length])
            image=np.array(image)
            # image=generate_image(emg_signals[:,select_index:select_index+window_length])

            muscle_images[i].append(image)
           

    return muscle_images

# def generate_classified_muscle_images(classifier_sig, emg_signals, selected_muscles, window_duration=0.1, sampling_freq=2000, num_examples=100):
#     window_length=int(window_duration*sampling_freq) #samples

#     muscle_images=[[],[],[],[]]

#     for _ in range(num_examples):
#         index=np.random.randint(0, len(classifier_sig)-window_length)
#         classif=int(mode(classifier_sig).mode)

#         image=[]
#         for m in selected_muscles:
#             image.append(emg_signals[m][index:index+window_length])

#         muscle_images[classif].append(np.array(image))

#     return muscle_images








def save_muscle_images(subject_name,folder_index, muscle_images):
    for i in range(4):
        save_dir=f'{BASE_EXTRACTION_PATH}/{subject_name}/Dataset/{folder_index}/{i}'
        
        os.makedirs(save_dir,exist_ok=True)

        for filename in os.listdir(save_dir):
            file_path=os.path.join(save_dir, filename)

            if os.path.isfile(file_path):
                os.remove(file_path)

                
        for k,m in enumerate(muscle_images[i]):
            print()
            cv2.imwrite(f'{save_dir}/{k}.jpg', m*255)