
import matplotlib.pyplot as plt
import glob
import numpy as np
import re 
import neurokit2 as nk
import time 
from tqdm import tqdm
import pandas as pd
from scipy.signal import medfilt

def rri_ver_2(signal, sr=250):
    peaks, _ = nk.ecg_peaks(signal, sampling_rate=sr)
    r_peaks = peaks[peaks["ECG_R_Peaks"] == 1].index.tolist()
    rr_interval = np.diff(r_peaks)
    r_peaks.pop(0)
    return np.array(r_peaks), np.average(rr_interval)

def p_detection(temp):
    q = np.argmin(temp[40:80]) 
    p_min = np.argmin(temp[30:q+30])
    p_max = np.argmax(temp[30:q+30])
    t_min = np.argmin(temp[120:])
    t_max = np.argmax(temp[120:])
    return q, p_min, p_max, t_min, t_max

def reverse_caculate(temp, q, p_min, p_max, t_min, t_max):
    # if temp[p_min+20] > 0:
    #     title = 0
    p_min_abs = np.abs(temp[p_min+30])
    p_max_abs = np.abs(temp[p_max+30])
    if p_min_abs >= p_max_abs:
        if (p_min_abs - p_max_abs) <= 0.005:
            if np.abs(temp[t_min+120]) <= np.abs(temp[t_max+120]):
                title = 0
            else:
                title = 1
    else:
        title = 0
    return title 

def median_filter(signal):
    xx1 = medfilt(signal, 29)
    baseline = medfilt(xx1, 99)
    return signal - baseline


def plot_pq(id, reverse, pred_reverse, temp, q, p_min, p_max, t_max, t_min):
    plt.title(f"{id}/{pred_reverse}")
    plt.plot(temp)
    plt.scatter(q+40, temp[q+40], color="red", label="q")
    plt.scatter(p_min+30, temp[p_min+30], color="purple", label="p min")
    plt.scatter(p_max+30, temp[p_max+30], color="yellow", label="p max")
    plt.scatter(t_max+120, temp[t_max+120],color="blue", label="t_max")
    plt.scatter(t_min+120, temp[t_min+120], color="darkkhaki", label="t_min")
    plt.legend()
    plt.show()
   
def compute_gradients(x, y):
    gradients = np.gradient(y, x)
    return gradients
                
            




        





