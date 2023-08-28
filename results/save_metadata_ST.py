import os
import glob
from pathlib import Path
import json
import pandas as pd
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from tqdm import tqdm
import numpy as np
import statistics as stat
import re
from post_processing_detections.utilities.def_func import read_header, sorting_detections, get_season, histo_detect, get_tz, get_timestamps, t_rounder, extract_datetime


#%% Import csv deployments

deploy = pd.read_excel('L:/acoustock/Bioacoustique/DATASETS/APOCADO/PECHEURS_2022_PECHDAUPHIR_APOCADO/APOCADO - Suivi déploiements.xlsx', skiprows=[0])
deploy = deploy.loc[~((deploy['N° campagne'] == 1)), :] #deleting C1
deploy = deploy.loc[~((deploy['N° campagne'] == 4) & (deploy['N° déploiement'] == 9)), :] #deleting C4D9
deploy = deploy.loc[~((deploy['N° campagne'] == 7) & (deploy['N° déploiement'] == 1)), :] #deleting C7D1
deploy = deploy.reset_index(drop=True)


deploy['durations_deployments'] = [dt.datetime.combine(deploy['Date fin déploiement'][i], deploy['Heure fin déploiement'][i])\
                                    -dt.datetime.combine(deploy['Date début déploiement'][i], deploy['Heure début déploiement'][i]) for i in range(len(deploy))]

deploy['season'] = [get_season(i)[:-5] for i in deploy['Date début déploiement']]
deploy['season_year'] = [get_season(i)[-4:] for i in deploy['Date début déploiement']]

#%% First results from deployments csv

print('\n#### RESULTS DEPLOYMENTS ####')
#t_tot : duration_deployement divided by 2 if 2 ST are used in the deployment
t_tot = int(sum(deploy[deploy['nb ST/filet'] == 1]['durations_deployments'], dt.timedelta()).total_seconds()/3600) + 0.5*int(sum(deploy[deploy['nb ST/filet'] != 1]['durations_deployments'], dt.timedelta()).total_seconds()/3600)
print('-total duration: {:.0f} h'.format(t_tot))

print('\n# Observation effort per season #')
# [print('-{0}:'.format(season), int(sum(deploy[deploy['season']== season]['durations_deployments'], dt.timedelta()).total_seconds()/3600),'h') for season in ['spring', 'summer', 'autumn', 'winter']];
for y in sorted(list(set(deploy['season_year']))):    
    for s in list(dict.fromkeys(deploy[(deploy['season_year']==y)]['season'])):
        
        #t : duration_deployement divided by 2 if 2 ST are used in the deployment
        t = int(sum(deploy[(deploy['season_year'] == y) & (deploy['season'] == s) & (deploy['nb ST/filet'] == 1)]['durations_deployments'], dt.timedelta()).total_seconds()/3600)+ int(sum(deploy[(deploy['season_year'] == y) & (deploy['season'] == s) & (deploy['nb ST/filet'] != 1)]['durations_deployments'], dt.timedelta()).total_seconds()/3600)*0.5
        print('-{0}: {1:.0f}% - {2:.0f} h'.format(s+' '+y, 100*(t/t_tot), t))

print('\n# Duration per net #')
[print('-Filet {0}:'.format(filet), int(sum(deploy[(deploy['Filet']== filet) & (deploy['nb ST/filet'] == 1)]['durations_deployments'], dt.timedelta()).total_seconds()/3600)+ 0.5*int(sum(deploy[(deploy['Filet']== filet) & (deploy['nb ST/filet'] != 1)]['durations_deployments'], dt.timedelta()).total_seconds()/3600),'h') for filet in sorted(list(set(deploy['Filet'])))];

print('\n# Mean duration of a deployment per net type #')
[print('-Filet {0}:'.format(filet), round(np.mean(deploy[deploy['Filet']== filet]['durations_deployments']).total_seconds()/3600,1), 'h +/-', round(np.std(deploy[deploy['Filet']== filet]['durations_deployments']).total_seconds()/3600,1), 'h') for filet in sorted(list(set(deploy['Filet'])))];

print('\n# Duration per net length #')
[print('-{:.0f}'.format(L),'m :', int(sum(deploy[deploy['Longueur (m)']== L]['durations_deployments'], dt.timedelta()).total_seconds()/3600),'h') for L in sorted(list(set(deploy['Longueur (m)'])))];

#%% write PG_formatteddata files


list_raw = glob.glob(os.path.join('L:/acoustock/Bioacoustique/DATASETS/APOCADO/PECHEURS_2022_PECHDAUPHIR_APOCADO', '**/PG_rawdata**.csv'), recursive=True)\
            +glob.glob(os.path.join('L:/acoustock2/Bioacoustique/APOCADO2', '**/PG_rawdata**.csv'), recursive=True)



# for file in tqdm(list_raw):

#     tz = get_tz(file)
#     msg = pd.read_csv(file, usecols=['dataset'])['dataset'].tolist()[0]
#     path = os.path.join(Path(file).parents[2])
    
#     timestamps_file = get_timestamps(tz=tz, f_type='dir', ext= 'wav', choices='No', date_template='%y%m%d%H%M%S', msg=msg, path_dir = path)
    
#     df_detections, t_detections = sorting_detections(file, timebin_new=10)
#     timebin = int(t_detections['max_time'][0])
    
#     df_detections['start_datetime'].iloc[-1].strftime('%y%m%d')
    
#     PG2Ap_str = "/PG_formatteddata_" + df_detections['start_datetime'][0].strftime('%y%m%d') + '_' + df_detections['start_datetime'].iloc[-1].strftime('%y%m%d') +'_'+ str(t_detections['max_time'][0]) + 's'+ '_V2.csv'
    
#     df_detections.to_csv(os.path.dirname(file) + PG2Ap_str, index=False)  


#%% Write metadata files

list_csv = glob.glob(os.path.join('L:/acoustock/Bioacoustique/DATASETS/APOCADO/PECHEURS_2022_PECHDAUPHIR_APOCADO', '**/PG_formatteddata**V2.csv'), recursive=True)\
            +glob.glob(os.path.join('L:/acoustock2/Bioacoustique/APOCADO2', '**/PG_formatteddata**V2.csv'), recursive=True)

# for i in tqdm(list_csv):

#     df_detections, t_detections = sorting_detections(i)
#     fmax = int(list(set(t_detections['max_freq']))[0])
#     time_bin = int(list(set(t_detections['max_time']))[0])
#     labels = list(set(t_detections['labels'].explode()))
#     annotators = list(set(t_detections['annotators'].explode()))
#     [tz] = list(set([dt.tz for dt in df_detections['start_datetime']]))
    
#     [ID0] = list(set(df_detections['dataset']))
#     ID1 = re.search(r'C\d{1,2}D\d{1,2}', ID0).group() #campaign and deployment identifier
#     ID2 = re.search(r'ST\d+', ID0).group() #instrument identifier
#     ID_detections = ID1 + ' ' + ID2

#     rank = [i for i, ID in enumerate(deploy['ID']) if ID in ID_detections][0]
#     duration_deployment = int(deploy['durations_deployments'][rank].total_seconds())
#     dt_deployment_beg = pd.Timestamp(dt.datetime.combine(deploy['Date début déploiement'][rank], deploy['Heure début déploiement'][rank]), tz=tz)
#     dt_deployment_end = pd.Timestamp(dt.datetime.combine(deploy['Date fin déploiement'][rank], deploy['Heure fin déploiement'][rank]), tz=tz)
        
#     net_len = int(deploy['Longueur (m)'][rank])
#     n_instru = deploy['nb ST/filet'][rank] if type(deploy['nb ST/filet'][rank]) is int else int(deploy['nb ST/filet'][rank][0])
    
#     wav_files = glob.glob(os.path.join(Path(i).parents[2], "**/*.wav"), recursive=True)
#     wav_names = [os.path.basename(file) for file in wav_files]
#     [wav_folder] = list(set([os.path.dirname(file) for file in wav_files]))
    
#     arg1 = [extract_datetime(dt_from_filename, tz=tz) for dt_from_filename in df_detections['filename']]
#     arg2 = [extract_datetime(wav_name, tz=tz) for wav_name in wav_names]
#     test_wav = [j in arg1 for j in arg2]
    
#     wav_names, wav_files = zip(*[(wav_names[i], wav_files[i]) for i in range(len(wav_names)) if test_wav[i]]) #only the wav files corresponding to the detections are kept
#     durations = [read_header(file)[-1] for file in wav_files]
    
#     threshold = 0.75
#     total_detections = len(df_detections)
#     threshold_detect = round(total_detections * threshold)
#     bins = pd.date_range(start=dt_deployment_beg, end=dt_deployment_end, freq='1min')
#     hist, _ = np.histogram([dt.timestamp() for dt in df_detections['start_datetime']], bins=[b.timestamp() for b in bins])
#     cumul_count = np.cumsum(hist)
#     bin_index = int(np.argmax(cumul_count >= threshold_detect))
#     dt_thr = bins[bin_index] #datetime of the threshold
#     min_elapsed = bin_index #elapsed time in minutes to achieve threshold_detect, freq bins is 1min
#     perc_elapsed = round((dt_thr-bins[0])/(bins[-1]-bins[0]),2) # % of elapsed time to achieve threshold_detect
    

#     metadata =  {'deploy_ID' : ID_detections,
#                   'wav_folder': wav_folder, 
#                   'detection_file': i, 
#                   'beg_deployment': dt_deployment_beg.strftime('%Y-%m-%dT%H:%M:%S%z'), 
#                   'end_deployment': dt_deployment_end.strftime('%Y-%m-%dT%H:%M:%S%z'), 
#                   'duration_deployment (s)': duration_deployment, 
#                   'fmax': fmax, 
#                   'annotators': annotators, 
#                   'labels': labels, 
#                   'detections number': total_detections, 
                 
#                   'threshold75': threshold, 
#                   'threshold75_detections': threshold_detect, 
#                   'threshold75 elapsed time (min)': min_elapsed,
#                   'threshold75 % elapsed': perc_elapsed,
                 
#                   'timebin': time_bin, 
#                   'net_length (m)': net_len, 
#                   'n_instru': n_instru, 
#                   'wav_path': list(wav_files), 
#                   'durations': durations}
    
#     out_file = open(os.path.join(Path(i).parents[0], 'metadata.json'), 'w+')
#     json.dump(metadata, out_file, indent=4)
#     out_file.close()




#%% Load all metadata files

list_json = glob.glob(os.path.join('L:/acoustock/Bioacoustique/DATASETS/APOCADO/PECHEURS_2022_PECHDAUPHIR_APOCADO', "**/metadata.json"), recursive=True)\
            +glob.glob(os.path.join('L:/acoustock2/Bioacoustique/APOCADO2', '**/metadata.json'), recursive=True)               

data=[]
for i in tqdm(range(len(list_json))):
    r_file = open(list_json[i], 'r')
    data.append(json.load(r_file))
    r_file.close()
data = pd.DataFrame.from_dict(data)
data['df_detections'] = [sorting_detections(i)[0] for i in tqdm(data['detection_file'])]

for i in range(len(data)):
    data['df_detections'][i]['start_deploy'] = pd.to_datetime(data['beg_deployment'][i])
    data['df_detections'][i]['end_deploy'] = pd.to_datetime(data['end_deployment'][i])

deploy['detection_num'] = [len(data.loc[data['deploy_ID']==ID, 'df_detections'].reset_index(drop=True)[0]) for ID in deploy['ID']]
deploy['deploy_num_win'] = [deploy['durations_deployments'][i].total_seconds()/10 for i in range(len(deploy))] #num of 10s win
deploy['detection_rate'] = [ ((len(data[data['deploy_ID']==ID].reset_index(drop=True)['df_detections'][0]) * data[data['deploy_ID']==ID].reset_index(drop=True)['timebin'][0])/deploy['durations_deployments'][i].total_seconds())*100 for i, ID in enumerate(deploy['ID'])]
deploy['dt_begin'] = [dt.datetime.strftime(dt.datetime.combine(deploy['Date début déploiement'][i], deploy['Heure début déploiement'][i]), '%d/%m/%Y %H:%M:%S') for i in range(len(deploy))]
deploy['dt_end'] = [dt.datetime.strftime(dt.datetime.combine(deploy['Date fin déploiement'][i], deploy['Heure fin déploiement'][i]), '%d/%m/%Y %H:%M:%S') for i in range(len(deploy))]
deploy['season'] = [get_season(deploy['Date début déploiement'][i]) for i in range(len(deploy))]

print('\n#### Hourly positive detection rate (whistles)####')
print('-Total: {:.1f}%'.format(np.mean(deploy['detection_rate'])))

print('\n# Observation effort per season #')
for s in list(dict.fromkeys(deploy['season'])):
    print('{0} : {1:.0f}%'.format(s, np.mean(deploy[deploy['season']== s]['detection_rate'])))


test = data['threshold75 % elapsed']
np.mean(test)
fig,ax = plt.subplots(figsize=(20,9))
ax.hist(test, bins=25, density=True)
plt.xlabel('Threshold 75% elapsed')
plt.ylabel('Density')
plt.title('% of time elapsed to achieve 75% of the detections')
plt.grid(True)
plt.show()

#%% Distribution du nombre d'heures enregistrées selon la longueur de filière

x = [str(elem) for elem in sorted(list(set(deploy['Longueur (m)'])))]
# y = [int(sum(deploy[deploy['Longueur (m)']== L]['durations_deployments'], dt.timedelta()).total_seconds()/3600) for L in sorted(list(set(deploy['Longueur (m)'])))]
y = [int(sum(deploy[(deploy['Longueur (m)']== L) & (deploy['nb ST/filet'] != 1)]['durations_deployments'], dt.timedelta()).total_seconds()*0.5/3600)+ int(sum(deploy[(deploy['Longueur (m)']== L) & (deploy['nb ST/filet'] == 1)]['durations_deployments'], dt.timedelta()).total_seconds()/3600) for L in sorted(list(set(deploy['Longueur (m)'])))]

fig,ax = plt.subplots(figsize=(16,6), facecolor='#36454F')
ax.bar(x,y); #histo
ax.set_facecolor('#36454F')
ax.tick_params(axis='both', colors='w')
ax.spines['bottom'].set_color('w')
ax.spines['left'].set_color('w')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.grid(visible=False)
plt.suptitle('', color='w')
ax.set_ylabel('Heures d\'enregistrement', fontsize = 16, color='w')
ax.set_xlabel('Longueur filière [m]', fontsize = 16, color='w')


#%% Cumulated histo 

df_detections = data['df_detections'][50]
threshold = 0.75

[ID0] = list(set(df_detections['dataset']))
ID1 = re.search(r'C\d{1,2}D\d{1,2}', ID0).group() #campaign and deployment identifier
ID2 = re.search(r'ST\d+', ID0).group() #instrument identifier
ID_test = ID1 + ' ' + ID2

data_histo= df_detections['start_datetime'] #detections datetimes
tb= df_detections['end_time'][0] #timebin
deploy_dt = [df_detections['start_deploy'][0], df_detections['end_deploy'][0]] #beginning and end of deployment

res_min = 1
delta, start_vec, end_vec = dt.timedelta(seconds=60*res_min),  deploy_dt[0], deploy_dt[1]
bins = pd.date_range(start=deploy_dt[0], end=deploy_dt[1], freq='1min')
n_annot_max = (res_min*60)/tb #max nb of annoted time_bin max per res_min slice

total_detections = len(data_histo)
threshold_detect = round(total_detections * threshold)

hist, _ = np.histogram([dt.timestamp() for dt in data_histo], bins=[b.timestamp() for b in bins])
cumul_count = np.cumsum(hist)
bin_index = int(np.argmax(cumul_count >= threshold_detect))
dt_thr = bins[bin_index] #datetime of the threshold
min_elapsed = bin_index #elapsed time in minutes to achieve threshold_detect, freq bins is 1min
perc_elapsed = round((dt_thr-bins[0])/(bins[-1]-bins[0]),2) # % of elapsed time to achieve threshold_detect

bin_height = cumul_count[bin_index] / total_detections

min_elapsed = bin_index*res_min #elapsed time in minutes to achieve threshold_detect 
perc_elapsed = (dt_thr-bins[0])/(bins[-1]-bins[0]) # % of elapsed time to achieve threshold_detect

fig,ax = plt.subplots(figsize=(20,9))
ax.hist(data_histo, bins, cumulative=True) #histo
# vline = ax.axvline(x=dt_thr, ymax = bin_height*0.92 ,color='r', linestyle='-', label='75% of Detections')
vline = ax.axvline(x=dt_thr, ymax = 1 ,color='r', linestyle='-', label='75% of Detections')
# hline = ax.axhline(y=threshold_detect, xmax = (dt_thr-bins[0])/(bins[-1]-bins[0]), color='r', linestyle='-', label='75% of Detections')
hline = ax.axhline(y=threshold_detect, xmax = 1, color='r', linestyle='-', label='75% of Detections')
ax.set_ylabel("Detection rate [%] ("+str(res_min)+"min)", fontsize = 20)
ax.grid(color='k', linestyle='-', linewidth=0.2, axis='both')
ax.text(bins[bin_index+10], 50, '{0} min - {1:.0f}%'.format(min_elapsed, 100*perc_elapsed), color='r', ha='left', fontsize=16, fontweight='bold')
ax.text(bins[0], threshold*total_detections*1.02 + 2, '{0} detections'.format(threshold_detect), color='r', ha='left', fontsize=16, fontweight='bold')
tz_data = deploy_dt[0].tz
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz_data))  
fig.suptitle('Cumulated detections - {0}\n{1} - {2}'.format(ID_test, deploy_dt[0].strftime('%d/%m/%y'), deploy_dt[1].strftime('%d/%m/%y')), fontsize = 24, y=0.98)

#%% test pentes detection_rate
test = data['df_detections'][40]

data_histo= test['start_datetime']
tb= test['end_time'][0]
deploy_dt = [test['start_deploy'][0], test['end_deploy'][0]]


# bins,vec = histo_detect(data_histo, deploy_dt, res_min=60, time_bin=tb, plot=True)

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import math
res_min = 10
delta, start_vec, end_vec = dt.timedelta(seconds=60*res_min),  deploy_dt[0], deploy_dt[1]
bins = [start_vec + i * delta for i in range(int((end_vec - start_vec) / delta) + 1)]
bins2 = [bins[i:i + math.ceil(len(bins)/4)] for i in range(0, len(bins), math.ceil(len(bins)/4))]
n_annot_max = (res_min*60)/tb #max nb of annoted time_bin max per res_min slice
tz_data = deploy_dt[0].tz

fig,ax = plt.subplots(figsize=(20,9))
ax.hist(data_histo, bins, cumulative=False); #histo
ax.set_ylabel("Detection rate [%] ("+str(res_min)+"min)", fontsize = 20)
ax.axvline(x = bins2[-1][-1], color = 'r')
[ax.axvline(x = bins2[i][0], color = 'g') for i in range(len(bins2))]
ax.grid(color='k', linestyle='-', linewidth=0.2, axis='both')





#%% export csv for QGIS
# deploy_out = deploy.drop(columns=['Date début campagne', 'Date fin campagne', 'Heure début campagne', 'Heure fin campagne', 'check heures', 'Conditions météo', 'Conditions météo.1', 'Présence cétacés', 'Présence cétacés.1', 'Commentaire', 'Unnamed: 25', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29'])
deploy_out = deploy.drop(columns=['lat D','lat DM','lat DD','long D','long DM','long DD','Date début campagne', 'Date fin campagne', 'Heure début campagne', 'Heure fin campagne', 'check heures', 'Conditions météo', 'Conditions météo.1', 'Présence cétacés', 'Présence cétacés.1', 'Commentaire'])

for i in range(len(deploy['nb ST/filet'])):
    if '1' in str(deploy['nb ST/filet'][i]): deploy_out['nb ST/filet'][i]=1
    if '2' in str(deploy['nb ST/filet'][i]): deploy_out['nb ST/filet'][i]=2
    
deploy_out.to_csv('L:/acoustock/Bioacoustique/DATASETS/APOCADO/Data QGIS/APOCADO - Suivi déploiements 13042023.csv', index=False, encoding='latin1')

#%% Nombre moyen de detection à chaque heure de la journée / saison

hour_list = ['{:02d}:00'.format(i) for i in range(24)]; hour_list.append('0:00')
seasons = list(set(deploy['season']))
effort_obs = [int(sum(deploy[deploy['season']==season]['durations_deployments'], dt.timedelta()).total_seconds()/3600) for season in seasons]

all_detections = pd.concat(df_detections).reset_index(drop=True)
all_detections['date'] = [dt.datetime.strftime(i.date(), '%d/%m/%Y') for i in all_detections['start_datetime']]
all_detections['season'] = [get_season(i) for i in all_detections['start_datetime']]

result = {}
for season in tqdm(seasons):
    detection_byseason = all_detections[all_detections['season'] == season] #sub-dataframe 1 : tri par saison
    
    detection_dates = sorted(list(set(detection_byseason['date']))) #liste des dates / saison

    for date in detection_dates:
        detection_bydate = detection_byseason[detection_byseason['date'] == date] #sub-dataframe 2 : tri par saison & par date
        list_datasets = sorted(list(set(detection_bydate['dataset']))) #liste des datesets / saison / date
        
        for dataset in list_datasets:
            df = detection_bydate[detection_bydate['dataset'] == dataset].set_index('start_datetime')
            test = [len(df.between_time(hour_list[j], hour_list[j+1], inclusive='left')) for j in (range(len(hour_list)-1))]
            
            deploy_beg, deploy_end = int(df['start_deploy'][0].timestamp()), int(df['end_deploy'][0].timestamp())
            
            list_present_h = [dt.datetime.fromtimestamp(i) for i in list(range(deploy_beg, deploy_end, 3600))]
            list_present_h2 = [dt.datetime.strftime(list_present_h[i], '%d/%m/%Y %H') for i in range(len(list_present_h))]

            list_deploy_d = sorted(list(set([dt.datetime.strftime(dt.datetime.fromtimestamp(i), '%d/%m/%Y') for i in list(range(deploy_beg, deploy_end, 3600))])))
            list_deploy_d2 = [d for i, d in enumerate(list_deploy_d) if d in date][0]
            
            list_present_h3 = []
            for item in list_present_h2:
                if item.startswith(list_deploy_d2):
                    list_present_h3.append(item)

            list_deploy = [df['date'][0] + ' ' + n for n in [f'{i:02}' for i in range(0,24)]]

            for i, h in enumerate(list_deploy):
                if h not in list_present_h3:
                    test[i] = np.nan
                    
            if season in result:
                result[season].append(test)
            else:
                result[season] = [test]
    
    data = result[season]
    df_data = pd.DataFrame()
    df_data = ((df_data.from_dict(data, orient = 'columns').T/360)*100).median(1, skipna=True)
    
    plt.bar(height=df_data, x=hour_list[:-1], width=1)
    plt.ylim(0,100)
    plt.xlim(hour_list[0],hour_list[-2])
    plt.xticks(rotation=60)    
    plt.title('Mean detection rate per hour of the day in '+ season)
    plt.show()

#%%
data = pd.DataFrame([100*(np.nanmedian(result[season], axis=0)/360) for season in result.keys()], index=list(result.keys()) ).T.set_index([hour_list[:-1]])
data.plot(kind='bar', grid=0)
plt.style.use('default')
plt.ylim(0,40)
plt.xticks(rotation=90)   
plt.ylabel('positive detection rate, %', fontsize = 10)
plt.title('Delphinids acoustics presence', fontsize = 12, y=1);

plt.show()

