from git.SHHS.HRV_240516 import *
import pickle
import time
from noise_detection import median_filter, squared_signal_detection

def save_dict(file_path, file):
    with open(file_path,'wb') as fw:
        pickle.dump(file, fw)

def main(): 
    df = pd.read_csv("/Users/aimmo-aip-0168/Desktop/shhs/samplingrate_info_full_data_cvd_events.csv")
    data_path = "/Volumes/Seagate/SHHS/polysomnography/edfs/shhs2/"
    label_path = "/Volumes/Seagate/SHHS/polysomnography/annotations-events-nsrr/shhs2/"
    # temp_df = pd.DataFrame()
    # txt_path = "/Volumes/Seagate/SHHS/shhs2_txt"
    shhs2_files = glob.glob(data_path+"*.edf")
    cvd_events = df.columns[4:]
    x = []
    y = []
    step = 0
    c_ = 0
    # temp_df = pd.DataFrame()
    min_ = 330
    for i, file_path in tqdm(enumerate(shhs2_files)):
        try:
            if i % 500==0 and i != 0:
                X = np.array(x)
                Y = np.array(y)
                print(X.shape, Y.shape)
                np.savez(f"/Users/aimmo-aip-0168/Desktop/shhs/PREPROCESS/shhs2_dataset_apnea_{min_}_{i}.npz", x=X, y=Y)
                x = []
                y = []
                print(f".............. Saved step .............. {i}")
            if re.search("shhs2", file_path):
                id = re.findall(r"shhs2-\d{6}", file_path)[0]
            else: 
                id = re.findall(r"shhs1-\d{6}", file_path)[0]

            cvd_y = 0
            for cvd in cvd_events:
                e_list = (df.loc[df['id'] == int(re.sub("shhs2-", '', id)), cvd].tolist())
                if 1 in e_list:
                    print("CVD events patients ! {}".format(id))
                    cvd_y = 1
                    # temp_df.loc[c, "id"] = id
                    # temp_df.loc[c, "cvd"] = True
                    break
    
            if cvd_y == 0:
                signal, sr = read_edf(file_path)
                apnea = labeling_apnea_nsrr(signal, label_path, id)
                print("""{}'s Sampling Rate is {}... """.format(id, sr))
                # remove baseline wander 
                file = median_filter(signal[0][0])
                idx_ = ((len(file))+1)//2
                idx = 0
                
     
                for j in range(idx_ , (len(file)), 100):
                    distance, threshold = squared_signal_detection(file[j:j+100])
                    if distance < threshold:
                        idx = j
                        break
                if idx == 0:
                    file_ = file
                    label_apnea = apnea
                    # label_stage = stage
                    

                else:
                    print("abnormal data")
                    # temp_df.loc[c, "removed"] = True
                    file_ = file[:idx]
                    label_apnea = apnea[:idx]
                    # label_stage = stage[:idx]
    

            print("..................{} ............. {}............. ".format(sr, id))
        

            print("{} not exist R peak labeling ... ".format(id))
            bp = butter_bandpass_filter(file_, sr)
            r_peaks, rr_interval = rri_ver_2(bp, sr)
            filtered_rri, filtered_r_peaks = rri_filtering(rr_interval, r_peaks, margin=6, filtering_ratio=0.3)
            rri = filtered_rri.reshape(-1, 1)
            rpeaks = filtered_r_peaks.reshape(-1, 1)
            hrv = np.concatenate((rpeaks, rri), axis=1)
            n_r_peaks, n_rr_interval = hr_resampling(file_, sr, filtered_r_peaks, filtered_rri, method="hard")
      



            for s in range(0, (len(file_)//sr)+1, (min_)):

                # f = (filtered_r_peaks[np.where((n_r_peaks >= s*sr) & (n_r_peaks < s*sr + (min_*sr)))])
                # interval = (filtered_rri[np.where((filtered_r_peaks >= s*sr) & (filtered_r_peaks < s*sr + (min_*sr)))])
                f_2 = n_r_peaks[s*4:(s*4)+(min_*4)]
                i_2 = n_rr_interval[s*4:(s*4)+(min_*4)]
                temp_apnea = label_apnea[(s*sr):(s*sr)+(min_*sr)]
                # temp_stage = label_stage[(s*sr):(s*sr)+(min_*sr)]
                # temp_dict = sorted(Counter(temp_stage).items(), key =lambda x: x[1], reverse=True)
                # stg = temp_dict[0][0]
                if (temp_apnea[np.where(temp_apnea != 0)].shape)[0] >= sr*10:
                    apn = 1
                else:
                    apn = 0
                x.append(i_2)
                y.append(apn)
            


                   
                
                

                
                  

            

                    





        except Exception as e:
             print(e)
    
    X = np.array(x)
    Y = np.array(y)
    print(X.shape, Y.shape)
    np.savez(f"/Users/aimmo-aip-0168/Desktop/shhs/PREPROCESS/shhs2_dataset_apnea_{min_}_{i}.npz", x=X, y=Y)
   
    

        
if __name__ == "__main__":
    main()
        
            
             
