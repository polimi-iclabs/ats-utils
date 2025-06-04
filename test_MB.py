#%% import the module
import fnv
import fnv.reduce
import fnv.file   

# modules for math and plotting
import numpy as np
from matplotlib import pyplot as plt  

# modules for opening file
from tkinter import filedialog
import tkinter
import os

# import for timestamp handling
import datetime

def get_timestamp(frame_info):
    for f in frame_info:
        # simply print the name and value of each metadatum
        # print("{}: {}".format(f['name'], f['value']))
        
        # look for the timestamp in the frame. 
        # The time stamp is stored in a hard to read format and we can convert it to something more user friendly.
        if f['name'] == 'Time' :
            # get the timestamp string
            DateStr = f['value']
            
            # extract values from the timestamp string
            Microsecond = int(DateStr[-6:])
            Second = int(DateStr[-9:-7])
            Minute = int(DateStr[7:9])
            Hour = int(DateStr[4:6])
            DayOfYear = int(DateStr[0:3])
            
            # no year info is saved in the timestamp, so we grab it from PC clock
            Year = datetime.datetime.now().year
            
            # the month and day can be determined from the day of the year
            Month = datetime.datetime.strptime(str(DayOfYear), '%j').month
            Day = datetime.datetime.strptime(str(DayOfYear), '%j').day
            
            # combine all date info into a datetime object
            TimeStamp = datetime.datetime(tzinfo=datetime.timezone.utc, # timezone is UTC
                                          year=Year,
                                          month=Month,
                                          day=Day,
                                          hour=Hour,
                                          minute=Minute,
                                          second=Second,
                                          microsecond=Microsecond)
            
            return TimeStamp
        
def read_ats_files(path, coords=None):
    # open the file
    im = fnv.file.ImagerFile(path)              # open the file

    # correct metadata
    # set desired units
    if im.has_unit(fnv.Unit.TEMPERATURE_FACTORY):
        # set units to temperature, if available
        im.unit = fnv.Unit.TEMPERATURE_FACTORY
        im.temp_type = fnv.TempType.KELVIN         # set temperature unit
        # print('Temperature calibration found')
    else:
        # if file has no temperature calibration, use counts instead
        im.unit = fnv.Unit.COUNTS
        # print('No temperature calibration found')

    #% object parameters
    ObjParam=im.object_parameters
    ObjParam.emissivity = 1
    # ObjParam.atmospheric_transmission = 1
    im.object_parameters = ObjParam

    #% SUPERFRAMING
    # What follows is just an example!
    # Image data stored in a numpy 3D array (like a voxel) and TimeStamp stored in a numpy 1D array.
    # TimeStamp equal to the number of seconds and microseconds elapsed since January 1 of the current year.
    myArray_sf=np.zeros((im.num_frames//2+1, im.height, im.width))
    TimeStamp = []
    time_rel = np.zeros((im.num_frames//2+1)) 

    im.get_superframe(0) 
    if im.preset == 0:
        start_idx = 0
    else:
        start_idx = 1

    for ii in range(start_idx,im.num_frames,2): 
        print("reading frame %d of %d" % (ii+1, im.num_frames), end='\r')
        im.get_superframe(ii)
        myArray_sf[ii//2]=np.array(im.final, copy=False).reshape((im.height, im.width))
        TimeStamp.append(get_timestamp(im.frame_info))
        time_rel[ii//2] = TimeStamp[ii//2].timestamp() - TimeStamp[0].timestamp()

    # #%%
    # plt.imshow(myArray_sf[10000], cmap='hot')
    # plt.show()

    #%
    if coords is not None:
        # extract the temperature at the coordinates
        temp = np.zeros((coords.shape[0], myArray_sf.shape[0]))

        for j in range(coords.shape[0]):
            # take the average of 3x3 pixels around the coordinates
            temp[j,:myArray_sf.shape[0]] = np.mean(myArray_sf[:, coords[j, 1]-1:coords[j, 1]+2, coords[j, 0]-1:coords[j, 0]+2], axis=(1, 2))

            # plot the temperature
            plt.plot(time_rel[:-1], temp[i,j,:len(time_rel)-1], label='%d' % (j))
            
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.xlabel('Time (s)')
        plt.ylabel('Temperature (K)')
        plt.title(path)
        plt.show()
    else:
        temp = None
    
    return myArray_sf, TimeStamp, temp


#%
coords = np.array([[201, 167],
                   [201, 131],
                   [201, 96],
                   [202, 60],

                   [156, 165],
                   [157, 129],
                   [158, 95],
                   [157, 60],

                   [111, 163],
                   [113, 128],
                   [114, 92],
                   [115, 58],

                   [67, 163],
                   [69, 127],
                   [70, 92],
                   [72, 57]])

#%%
folderpath = 'G:/file_ats_rego/'
# get all the ats files in the folder
files = [f for f in os.listdir(folderpath) if f.endswith('.ats')]
files.sort()  # sort the files by name
print(files)
# sort the files by name

temp = np.zeros((len(files),coords.shape[0],30000))
peaks = np.zeros((len(files),coords.shape[0]), dtype=int)

# i = -1
for i in range(len(files)):
    path = os.path.join(folderpath, files[i])
    print(path)                         # print file name

    im = fnv.file.ImagerFile(path)              # open the file

    #% correct metadata
    # set desired units
    if im.has_unit(fnv.Unit.TEMPERATURE_FACTORY):
        # set units to temperature, if available
        im.unit = fnv.Unit.TEMPERATURE_FACTORY
        im.temp_type = fnv.TempType.KELVIN         # set temperature unit
        # print('Temperature calibration found')
    else:
        # if file has no temperature calibration, use counts instead
        im.unit = fnv.Unit.COUNTS
        # print('No temperature calibration found')

    #% object parameters
    ObjParam=im.object_parameters
    ObjParam.emissivity = 1
    # ObjParam.atmospheric_transmission = 1
    im.object_parameters = ObjParam

    #% SUPERFRAMING
    # What follows is just an example!
    # Image data stored in a numpy 3D array (like a voxel) and TimeStamp stored in a numpy 1D array.
    # TimeStamp equal to the number of seconds and microseconds elapsed since January 1 of the current year.
    myArray_sf=np.zeros((im.num_frames//2+1, im.height, im.width))
    TimeStamp = []
    time_rel = np.zeros((im.num_frames//2+1)) 

    im.get_superframe(0) 
    if im.preset == 0:
        start_idx = 0
    else:
        start_idx = 1

    for ii in range(start_idx,im.num_frames,2): 
        print("reading frame %d of %d" % (ii+1, im.num_frames), end='\r')
        im.get_superframe(ii)
        myArray_sf[ii//2]=np.array(im.final, copy=False).reshape((im.height, im.width))
        TimeStamp.append(get_timestamp(im.frame_info))
        time_rel[ii//2] = TimeStamp[ii//2].timestamp() - TimeStamp[0].timestamp()

    # #%%
    # plt.imshow(myArray_sf[10000], cmap='hot')
    # plt.show()

    #%
    plt.figure(figsize=(10, 6), dpi=300)       # open new figure
    for j in range(coords.shape[0]):
        # take the average of 3x3 pixels around the coordinates
        temp[i,j,:myArray_sf.shape[0]] = np.mean(myArray_sf[:, coords[j, 1]-1:coords[j, 1]+2, coords[j, 0]-1:coords[j, 0]+2], axis=(1, 2))
        # plot the temperature
        plt.plot(time_rel[:-1], temp[i,j,:len(time_rel)-1], label=str(j+1))
    # get the peaks
    peaks[i,:] = np.argmax(temp[i], axis=1).astype(int)

    # plot the peaks
    for j in range(coords.shape[0]):
        # check if the peak is corresponding to a temperature greater than 600 K
        if temp[i,j,peaks[i,j]] < 600:
            peaks[i,j] = -1 # set the peak to -1 if it is not greater than 600 K
            print('Peak is not greater than 600 K for sample %d of %s' % (j+1, files[i]))
            continue

        # plot the temperature
        # plt.plot(time_rel[:-1], temp[i,j,:len(time_rel)-1], label=str(j+1))
        # plot the peak
        plt.axvline(x=time_rel[peaks[i,j]], color='r', linestyle='--')

    peaks[i,:] = peaks[i,:] - peaks[i,0]  # subtract the first peak from all peaks
    # put the legend outside the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (K)')
    plt.title(path)
    plt.savefig(path[:-4] + '.png', dpi=300, bbox_inches='tight')
    plt.close()
    # plt.show()

#%%
# extract layer number frm files
layer = []
for f in files:
    # extract the layer number from the file name
    layer.append(int(f.split(' ')[1].split('.')[0]))
# convert to numpy array
layer = np.array(layer)
print(layer)
#%%
# plot the relative position of the peaks
plt.figure(figsize=(10, 3), dpi=300)       # open new figure
for i in range(coords.shape[0]):
    # plot the peaks
    plt.scatter(layer, peaks[:,i], label='%d' % (i+1))
# add legend outside the plot
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.xlabel('Layer nr.')
plt.ylabel('Peak position (frame)')
plt.title('Relative position of the peaks')
plt.savefig('G:/file_ats_rego/peaks.png', dpi=300, bbox_inches='tight')
plt.show()

#%%
import pandas as pd
df = pd.read_csv('rego75.csv', sep=',')

#%%
idxs = [11,12,14,15,17,18,20]
# idxs = [11,12,13,14,15,16,17,18,19,20]

tat = np.zeros((len(files),coords.shape[0]))
plt.figure(figsize=(5, 5), dpi=300)       # open new figure
for idx in idxs: 
    for j in range(coords.shape[0]):
        tat[idx,j] = np.sum(temp[idx,j,:] > 500)
# convert tat to actual time
time_delta = TimeStamp[1] - TimeStamp[0]
# convert timedelta to seconds
seconds = time_delta.total_seconds()
tat = tat * seconds
# make a dataframe with tat and corresponding layer number and VED value
df_tat = pd.DataFrame({'Layer': [], 'SampleID': [], 'VED': [], 'Tat': []})
for i in range(len(files)):
    for j in range(coords.shape[0]):
        df_tat = pd.concat([df_tat, pd.DataFrame({'Layer': [layer[i]], 'SampleID': j, 'VED': [df['VED'][j]], 'Tat': [tat[i,j]]})], ignore_index=True)
#%
# make a scatterplot
plt.figure(figsize=(6, 5), dpi=300)       # open new figure
# plot the tat for each sample in each layer using the VED column in df as color
sm = plt.scatter(df_tat['Layer'], df_tat['Tat'], c=df_tat['VED'], cmap='viridis', s=70, alpha=0.8)
# sample_id = 1
# plt.scatter(df_tat['Layer'][df_tat['SampleID'] == sample_id-1], df_tat['Tat'][df_tat['SampleID'] == sample_id-1], c='w', marker='x', s=50, alpha=0.8, label='Sample %d' % (sample_id))
# add colorbar
cbar = plt.colorbar(sm)
cbar.set_label('VED')

plt.xlabel('Layer nr.')
plt.ylabel('Time (s)')
plt.title('Time above 500 K')
plt.xlim(16.5, 27)
plt.ylim(3, 13)
plt.savefig('G:/file_ats_rego/tat_ved.png', dpi=300, bbox_inches='tight')
plt.show()
#%%
# create a new dataframe with only the tat values that are greater than 0
df_tat_filt = df_tat[df_tat['Tat'] > 0]
df_tat_filt.to_csv('G:/file_ats_rego/tat_filt.csv', index=False)
#%%
for j in range(coords.shape[0]):
    
    # plt.scatter(layer, tat[:,j], label='%d' % (j+1))
    # plot the tat for each sample in each layer using the VED column in df as color
    # j is the index of the sample in the corresponding 
    
    
# add labels to each point
    for i in range(len(files)):
        plt.annotate(str(j+1), (layer[i], tat[i,j]), fontsize=8, alpha=0.5)
# add legend outside the plot
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.xlabel('Layer nr.')
plt.ylabel('Time (s)')
plt.title('Time above 500 K')
plt.xlim(16.5, 27)
plt.ylim(2, 13)
plt.savefig('G:/file_ats_rego/tat.png', dpi=300, bbox_inches='tight')
plt.show()

#%%
T = np.linspace(300, 1200, 100)
k_eff = 3.18e-11 * T**3 + 9.22e-4
plt.plot(T, k_eff, label='k_eff')
plt.xlabel('Temperature (K)')
plt.ylabel('k_eff (W/mK)')
plt.title('Effective thermal conductivity')

