import glob
import pandas as pd
import re 
import os
import numpy as np



def main():
    min_ = 330
    file_path = "/Users/aimmo-aip-0168/Desktop/shhs/csv_ver2/330s"
    file_list = glob.glob(os.path.join(file_path, "*.csv"))
    df = pd.DataFrame()
    for i in range(len(file_list)):
        if re.search("hicardi", file_list[i]):
            hicardi = pd.read_csv(file_list[i])
        else:
            a = pd.read_csv(file_list[i])
            df = pd.concat([df, a])
    # features =['HRV_MeanNN', 'HRV_SDNN', 'HRV_SDANN1', 'HRV_SDNNI1', 'HRV_RMSSD',
    # 'HRV_SDSD', 'HRV_CVNN', 'HRV_CVSD', 'HRV_MedianNN', 'HRV_MadNN',
    # 'HRV_MCVNN', 'HRV_IQRNN', 'HRV_SDRMSSD', 'HRV_Prc20NN', 'HRV_Prc80NN',
    # 'HRV_pNN50', 'HRV_pNN20', 'HRV_MinNN', 'HRV_MaxNN', 'HRV_HTI',
    # 'HRV_TINN', 'HRV_SD1', 'HRV_SD2', 'HRV_SD1SD2', 'HRV_S', 'HRV_CSI',
    # 'HRV_CVI', 'HRV_CSI_Modified', 'HRV_PIP', 'HRV_IALS', 'HRV_PSS',
    # 'HRV_PAS', 'HRV_GI', 'HRV_SI', 'HRV_AI', 'HRV_PI', 'HRV_C1d', 'HRV_C1a',
    # 'HRV_SD1d', 'HRV_SD1a', 'HRV_C2d', 'HRV_C2a', 'HRV_SD2d', 'HRV_SD2a',
    # 'HRV_Cd', 'HRV_Ca', 'HRV_SDNNd', 'HRV_SDNNa', 'HRV_DFA_alpha1',
    # 'HRV_MFDFA_alpha1_Width', 'HRV_MFDFA_alpha1_Peak',
    # 'HRV_MFDFA_alpha1_Mean', 'HRV_MFDFA_alpha1_Max',
    # 'HRV_MFDFA_alpha1_Delta', 'HRV_MFDFA_alpha1_Asymmetry',
    # 'HRV_MFDFA_alpha1_Fluctuation', 'HRV_MFDFA_alpha1_Increment',
    # 'HRV_DFA_alpha2', 'HRV_MFDFA_alpha2_Width', 'HRV_MFDFA_alpha2_Peak',
    # 'HRV_MFDFA_alpha2_Mean', 'HRV_MFDFA_alpha2_Max',
    # 'HRV_MFDFA_alpha2_Delta', 'HRV_MFDFA_alpha2_Asymmetry',
    # 'HRV_MFDFA_alpha2_Fluctuation', 'HRV_MFDFA_alpha2_Increment',
    # 'HRV_ApEn','HRV_ShanEn', 'HRV_FuzzyEn', 'HRV_MSEn',
    # 'HRV_CMSEn', 'HRV_RCMSEn', 'HRV_CD', 'HRV_HFD', 'HRV_KFD', 'HRV_LZC',
    # 'HRV_ULF', 'HRV_VLF', 'HRV_LF', 'HRV_HF', 'HRV_VHF', 'HRV_TP',
    # 'HRV_LFHF', 'HRV_LFn', 'HRV_HFn', 'HRV_LnHF', 'stage', 'apnea'] 

    for i in df.columns:
        if df[i].isnull().sum() > len(df)*0.9:
            print(i)
            # if i in features:
            #     features.remove(i)


    features = df.columns
    ## train / valid dataset nan 값 제거
    train = df.replace([np.inf, -np.inf]).dropna()
    valid = hicardi.replace([np.inf, -np.inf]).dropna()
    train_data = train[features].dropna(axis=0, how='any')
    valid_data = valid[features].dropna(axis=0, how="any")
    train_y = train_data['stage'].apply(lambda x:1 if x != 0 else 0) 
    valid_y = valid_data['stage'].apply(lambda x:1 if x != 5 else 0)
    train_apnea = train_data['apnea'].apply(lambda x:1 if x != 0 else 0)
    valid_apnea = valid_data['apnea'].apply(lambda x:1 if x != 0 else 0)
    train_x = train_data.drop(columns=['stage', 'apnea', "SampEn"]) # record id는 추후 데이터 분석시 넣어야 하므로 제외하지 않음. 
    valid_x = valid_data.drop(columns=['stage', 'apnea', "SampEn"]) 
    print(train_y.value_counts())
    print(valid_y.value_counts())
    print(train_apnea.value_counts())
    print(valid_apnea.value_counts())
    print("train x shape is {}, train y.shape is {}, train apnea shape is {}".format(train_x.shape, train_y.shape, train_apnea.shape))
    print("valid x shape is {}, valid y.shape is {}, valid apnea shape is {}".format(valid_x.shape, valid_y.shape, valid_apnea.shape))

    train_y.to_csv(os.path.join(file_path, "train_y_{}s.csv".format(min_)), index=False)
    valid_y.to_csv(os.path.join(file_path, "valid_y_{}s.csv".format(min_)), index=False)
    train_x.to_csv(os.path.join(file_path, "train_x_{}s.csv").format(min_), index=False)
    valid_x.to_csv(os.path.join(file_path, "valid_x_{}s.csv".format(min_)), index=False)
    train_apnea.to_csv(os.path.join(file_path, "train_apnea_{}s.csv".format(min_)), index=False)
    valid_apnea.to_csv(os.path.join(file_path, "valid_apnea_{}s.csv".format(min_)), index=False)
    

    print("......... SAVED train dataset & valid dataset ......... ")




if __name__ == "__main__":  
    main()

    
    



