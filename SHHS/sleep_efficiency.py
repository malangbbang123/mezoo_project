import numpy as np
import os 
import glob
import matplotlib.pyplot as plt
import re
import time 
from tqdm import tqdm
from test.HRV_shhs1 import *

def ahi(prediction:float) -> int:
    """ 
    ahi 지수를 계산하는 코드
    하이카디의 경우 : 전체 prediction 값 에서 true라고 얘기한 것의 개수 (예: segment 20개 apnea 5개이면, 25% (100 * (5/20))
    """
    ahi_idx = 100 * ((len([np.where(prediction != 0)][0])) / (len(prediction)))
    # class_ = 0 # normal
    # if 5 <= ahi_idx < 15: # mild 
    #     class_ = 1
    # elif 15 <= ahi_idx < 30: # moderate
    #     class_ = 2
    # elif ahi_idx >= 30: # severe 
    #     class_ = 3

    return ahi_idx

def sleep_efficiency(prediction:int, sleep_alarm:int=None, wake_alarm:int=None):

    """ 
    sleep efficiency를 계산하는 코드 (input: sleep stage 모델 추론 값) 
    time in bed : 침대에 머문 시간
    sleep latency : 처음 잠에 들기까지 걸리는 시간
    onset : 침대에 머문 시간 중, sleep 시작 시점
    offset : 최종적으로 깨기 전까지 시점
    sleep period : time in bed 중, onset부터 offset까지 
    total sleep time (tst) : sleep period 중, 잠에 든 시간
    sleep efficiency : total sleep time / time in bed
    time in bed : 침대에 머문 시간 
    """

    slp_idx = np.where(prediction != 0)[0]
    onset = slp_idx[0]
    offset = slp_idx[-1]
    sleep_period = prediction[onset:offset+1]
    tst = sleep_period[np.where(sleep_period != 0)]
    sleep_latency = prediction[:onset]
    tib_before_wake = prediction[offset+1:]

    slp_eff = 100 * ((len(tst)) / (len(sleep_period))) 
    slp_eff_2 = 100 * (len(tst)) / (len(sleep_period)+len(sleep_latency))
    slp_eff_3 = 100 * ((len(tst)) / len(prediction))


    return round(slp_eff, 2), round(slp_eff_2, 2), round(slp_eff_3, 2)




if __name__ == "__main__":
    stage_lab = glob.glob("/Volumes/Seagate/SHHS/shhs1_txt/**/*SLEEP-STAGE.txt")
    apnea_path = "/Volumes/Seagate/SHHS/shhs1_txt/label/"
    start_time = time.time()
    df = pd.read_csv("/Volumes/Seagate/SHHS/samplingrate_info_full_data_cvd_events.csv")
    cvd_events = df.columns[4:]
    slp_eff_df = pd.DataFrame()
    ahi_list = []
    for i in tqdm(range(len(stage_lab))[:100]):
        try:
            cvd_y = 0
            id = re.findall(r"shhs1-\d{6}", stage_lab[i])[0]
            # print("Loading  {} RRI ... ".format(id))
            sr_list = df.loc[df['id'] == int(re.sub('shhs1-', '', id)), 'sampling_rate'].tolist()
            fn_list = df.loc[df['id'] == int(re.sub('shhs1-', '', id)), 'file_name'].tolist()

            for cvd in cvd_events:
                e_list = (df.loc[df['id'] == int(re.sub("shhs1-", '', id)), cvd].tolist())
                if 1 in e_list:
                    print("CVD events patients ! {}".format(id))
                    cvd_y = 1
                    break

            if cvd_y == 0:
                y = []
                y2 = []
                sr = int(min(sr_list))
                # print("""{}'s Sampling Rate is {}... """.format(id, sr))
                d = np.loadtxt(stage_lab[i])
                d2 = np.loadtxt(os.path.join(apnea_path, id+"_SLEEP-APNEA.txt"))
                min_ = 330
                segment = sr * min_
                min_2 = 180
                segment2 = sr * min_2
                

                for s in range(0, len(d)+1, segment):
                    if len(d)+1 < segment:
                        break
                    temp_lab = d[s:s+segment]
                    temp_dict = sorted(Counter(temp_lab).items(), key =lambda x: x[1], reverse=True)
                    many_l = temp_dict[0][0]
                    y.append(many_l)
                for s in range(0, len(d)+1, segment2):
                    if len(d2)+1 < segment2:
                        break
                    temp_lab = np.array(d2[s:s+segment2])
                    if len(np.where(temp_lab != 0)[0]) >= sr * 30:
                        y2.append(1)
                    else:
                        y2.append(0)
                    
                    
                eff1, eff2, eff3 = sleep_efficiency(np.array(y))
                ahi_index = ahi(np.array(y2))
                ahi_list.append(ahi_index)
        except: 
            pass
        
    print(sum(ahi_list) / len(ahi_list))
        # id = re.findall(r"shhs1-\d{6}", stage_lab[i])[0]
        # apnea_data = os.path.join(apnea_path, id+"_SLEEP-APNEA.txt")
        # d2 = np.loadtxt(apnea_data)
        # onset, offset, sleep_period, slp_eff, slp_eff_2, slp_eff_3 = sleep_efficiency(d)
        # ahi_idx = ahi(d2)
        # print(ahi_idx)
        # plt.title("{} 's sleep efficiency ver1 is {}, ver2 is {}, ver3 is {} and AHI is {}".format(id, slp_eff, slp_eff_2, slp_eff_3, ahi_idx))
        # plt.plot(d, label="sleep stage")
        # plt.plot(np.arange(onset, offset+1), sleep_period, label="sleep period")
        # plt.scatter(onset, d[onset], label="onset", color="red")
        # plt.scatter(offset, d[offset], label="offset", color="red")
        # plt.legend()
        # plt.show()
