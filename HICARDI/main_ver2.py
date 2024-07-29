from git.HICARDI.reverse_detection import *
from git.HICARDI.READ_MAT import *
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pandas as pd
import re
from scipy.signal import find_peaks

def process_file(file_path, idx):
    x = []
    y = []
    reverse = 0
    id = re.sub(".mat", "", os.path.basename(file_path))
    result = {"id": id}
    reverse_list = [
        'A00112_20230425_1110', 'A00112_20230425_1110', 'A00118_20220623_0931', 'A00109_20220623_0347', 
        'A00109_20220622_2155', 'A00113_20220620_1112', 'A00116_20220624_1336', 'A00112_20220623_0943', 
        'A00200_20230425_1334', 'A00116_20221018_1800', 'A00117_20221013_1813', 'A00115_20221017_1729', 
        'A00194_20221014_1949', 'A00115_20221019_1745', 'A00117_20221017_1717', 'A00109_20221020_1728', 
        'A00193_20221013_2044', 'A00117_20221019_1715', 'A00118_20221014_1805', 'A00118_20221018_1733', 
        'A00110_20221103_1702', 'A00109_20221101_0028', 'A00109_20221020_0204', 'A00110_20221101_1710', 
        'A00110_20221018_2036', 'A00109_20221018_0147', 'A00201_20220713_0904', 'A00193_20221031_1901', 
        'A00193_20221102_2032', 'A00194_20221015_0255', 'A00193_20221014_0357', 'A00194_20221101_2040', 
        'A00194_20221013_0130', 'A00194_20221012_2057', 'A00109_20221031_1705'
    ]   
    if id in reverse_list:
        reverse = 1

    try:
        file = load_mat(file_path)
        data = read_ecg(file)
        data = data[file['data_lost'] == False]
        sr = read_sr(file)
        r_peaks, mean_interval = read_rpeaks(file)

        beat_length = int(mean_interval * 0.7)
        beat_num = 5000
        split_3 = len(r_peaks) // 5
        ensemble = []

        for split_idx in range(0, len(r_peaks), split_3):
            if len(r_peaks) < split_idx + beat_num:
                continue
            for temp_idx in range(beat_num):
                rpeak = int(r_peaks[split_idx + temp_idx])
                segment = data[rpeak - int(beat_length * 0.4):rpeak + int(beat_length * 0.6)]
                filtered_segment = median_filter(segment)
                ensemble.append(filtered_segment)

        if len(ensemble) <= beat_num:
            return None

        arr = np.array(ensemble)
        for i in range(beat_num, len(ensemble) + 1, beat_num):
            avg = np.average(arr[:i], axis=0)
            x.append(avg)
            y.append(reverse)

    except Exception as e:
        pass

    return x, y

if __name__ == "__main__":
    path = "/Users/aimmo-aip-0168/Desktop/code/external_data"
    mat_data = glob.glob(os.path.join(path, "**", "*.mat"), recursive=True)
    X = []
    Y = []
    max_len = 0

    # First pass to determine the maximum length of the segments
    for idx, file_path in tqdm(enumerate(mat_data), total=len(mat_data)):
        try:
            x, _ = process_file(file_path, idx)
            if x:
                max_len = max(max_len, len(x[0]))
        except Exception as e:
            print(e)
            pass

    # Second pass to process the files and pad sequences
    for idx, file_path in tqdm(enumerate(mat_data), total=len(mat_data)):
        try:
            x, y = process_file(file_path, idx)
            if x:
                x_padded = [np.pad(segment, (0, max_len - len(segment)), 'constant') for segment in x]
                X.extend(x_padded)
                Y.extend(y)
        except Exception as e:
            print(e)
            pass
        
    X = np.array(X)
    Y = np.array(Y)
    np.savez(f"/Volumes/Seagate/hicardi/code_check/test.npz", x=X, y=Y)

