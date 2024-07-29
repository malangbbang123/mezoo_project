from git.HICARDI.reverse_detection import *
from git.HICARDI.READ_MAT import *
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import pandas as pd
import re

def process_file(file_path, idx):
    id = re.sub(".mat", "", os.path.basename(file_path))
    result = {"id": id}

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
        reverse = []

        for i in range(beat_num, len(ensemble) + 1, beat_num):
            avg = np.average(arr[:i], axis=0)
            q_peak, q_index, p_min, p_max = p_detection(avg)
            pred_reverse = reverse_caculate(p_min, p_max)
            reverse.append(pred_reverse)
            fig, ax = plt.subplots(figsize=(10, 6))
            plt.title(f"{id}/{i}/{pred_reverse}")
            ax.plot(avg, label=f"{i}")
            ax.scatter(q_index, avg[q_index], color="red", label="q")
            ax.scatter(np.where(avg == p_min)[0][0], avg[np.where(avg == p_min)], color="green", label="p_min")
            ax.scatter(np.where(avg == p_max)[0][0], avg[np.where(avg == p_max)], color="purple", label="p_max")
            plt.legend()
            plt.grid()
            plt.savefig(f"/Volumes/Seagate/hicardi/code_check/check_{id}_{i}_{beat_num}.png")


        # result["pred_reverse"] = np.average(reverse)

        
    except Exception as e:
        result["error"] = str(e)

    return result

if __name__ == "__main__":
    path = "/Users/aimmo-aip-0168/Desktop/code/external_data"
    mat_data = glob.glob(os.path.join(path, "**", "*.mat"), recursive=True)
    results = []

    for idx, file_path in tqdm(enumerate(mat_data), total=len(mat_data)):
        result = process_file(file_path, idx)
        # if result:
        #     results.append(result)

    # df = pd.DataFrame(results)
    # df.to_csv("./reverse_detection.csv", index=False)
