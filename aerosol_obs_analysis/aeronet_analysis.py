'''''

AERONET analysis tool for Level 2.0 Daily

class aeronet
methods:
  - __init__(time_range, aod_var_names, pickle_path, pickle_name,
             from_pickle, save_pickle, start_with_guide)
  - analysis_guide()

  - load_pickle           (pickle_name,pickle_path)       : self.df 
  - load_pickle_all       (data_name,pickle_name_default) : return df
  - extract_daily_from_raw(data_name)                     : return df
    - data_name: 'AOD' or 'INV'

  - skim_inv(df): return df_new ()
    - df: DataFrame of raw inv data

  - combine_df(): return df
    - Combine df_aod_all and df_inv_all

  - filter_time (df,time_range)   : return df_result
  - filter_site (df)              : return df_result, site_name
  - filter_rec  (df,min_rec)      : return df_result
  - cal_average (columns,min_rec) : return df_ave
  - select_sites  (lat,lon)       : return list_of_site_names

'''''
import numpy as np
import pandas as pd
import os
import datetime
from analysis_utils import *

# Constants
month_day = {1:31, 2:28, 3:31,  4:30,  5:31,  6:30,
             7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

size_bins = [0.05,0.065604, 0.086077, 0.112939, 0.148184,
             0.194429, 0.255105, 0.334716, 0.439173, 0.576227,
             0.756052, 0.991996, 1.301571, 1.707757, 2.240702,
             2.939966, 3.857452, 5.06126, 6.640745, 8.713145,
             11.432287, 15.0]

columns_def = ['AERONET_Site_Name','Day_of_Year','Site_Latitude(Degrees)','Site_Longitude(Degrees)']

# Variable names
aod_var_names = {'aod':'AOD_500nm', 'alfa':'440-870_Angstrom_Exponent'}

# For class aeronet
data_path   = './' #'../AERONET/'
pickle_path = 'workspace/AERONET/'
time_range = [datetime.date(2006,1,1),datetime.date(2006,12,31)] #YY,MM,DD [start, end]
time_range_str = '_'.join([x.strftime("%Y%m%d") for x in time_range])

aod_name = 'All_Sites_Times_Daily_Averages_AOD20.dat'
inv_name = 'INV_Level2_Daily_V3.tar.gz'
aod_data_path = 'AOD/AOD20/DAILY/'
inv_data_path = 'INV/LEV20/ALL/DAILY/'

#Pickles
pickle_default = 'temp.pkl'
# All records -> For primilary analysis
pickle_aod_all_name = 'AOD20_daily_all_sites.pkl'
pickle_inv_all_name = 'INV20_daily_all_sites.pkl'
pickle_size_all_name = 'INV20_daily_all_sites_size.pkl'

# Records filtered by year
## AOD
pickle_aod_name = 'AOD20_{}.pkl'.format(time_range_str)
pickle_aod_ave_name = 'AOD20_ave_{}.pkl'.format(time_range_str)

# INV
pickle_inv_name  = 'INV20_{}.pkl'.format(time_range_str)
pickle_inv_ave_name = 'INV20_size_ave_{}.pkl'.format(time_range_str)

# Combined
pickle_name = 'COM20_{}.pkl'.format(time_range_str)

# Columns
columns_to_keep=['AERONET_Site_Name', 'Date(dd:mm:yyyy)',
                  'Day_of_Year',
                  'Site_Latitude(Degrees)',
                  'Site_Longitude(Degrees)']

inv_col_to_aod_col = {'AERONET_Site':'AERONET_Site_Name',
                      'Latitude(Degrees)':'Site_Latitude(Degrees)',
                      'Longitude(Degrees)':'Site_Longitude(Degrees)'}

columns_reff = ['REff-C', 'REff-F', 'REff-T']

# Column names for AOD products
aod_names = {'aod':'AOD_500nm', 'alfa':'440-870_Angstrom_Exponent'}
# Columns names for INV products
wavelength = 440
inv_names = {}
col_names = {}
def set_inv_name(wavelength):
  wavelength = wavelength
  inv_names = {'aod_fine'  : 'AOD_Extinction-Fine[{}nm]'.format(wavelength),
              'aod_coarse': 'AOD_Extinction-Coarse[{}nm]'.format(wavelength),
              'aod_abs'   : 'Absorption_AOD[{}nm]'.format(wavelength)
              }
  col_names = {**aod_names,**inv_names}
  return col_names

col_names = set_inv_name(wavelength)

# For input
enter_yes = '\nPress enter for YES, other keys for NO: '
enter_def = '\nPress enter for default '

input_yes = lambda question: input('{} {}'.format(question,enter_yes)) in ['','YES','yes','Y','y']
input_def = lambda question,def_value: input('{} {}({}): '.format(question,enter_def,def_value)) or def_value

# For print
saved_as = lambda dname,fname: '\nSaved {} as {} \n************'.format(dname,fname)
###################
class aeronet():

  def __init__(self,time_range = time_range,
                    aod_var_names = aod_var_names,
                    pickle_path = pickle_path,
                    pickle_name = pickle_name,
                    col_names = col_names,
                    from_pickle = False, # AOD and size combined
                    save_pickle=False,
                    start_with_guide=False):

    self.time_range     = time_range

    # Pickle names
    self.pickle_path  = pickle_path
    self.pickle_name  = pickle_name
    self.col_names = col_names
    self.aod_vnames = aod_var_names

    if not os.path.exists(pickle_path):
      os.makedirs(pickle_path)    
      print(f'Work directory created: {pickle_path}')

    if from_pickle:
      print('Loading AERONET data from pickle: {}'.format(pickle_name))
      self.df = pd.read_pickle(self.pickle_path+self.pickle_name)
    elif start_with_guide:
      self.analysis_guide()
    else:
      print('AERONET data object created. Use .read_pickle() to load data from pickle, or .analysis_guide() to read raw data.')
      

  ## Guide to load and do data analysis
  def analysis_guide(self):

    print('\n##### Analysis from raw/half-processed data #####')

    ## AOD
    aod_from_pickle = input_yes('Load AOD data (all records) from pickle?')

    if aod_from_pickle: # Load from pickle
      try: 
        self.df_aod_all = self.load_pickle_all('AOD',pickle_aod_all_name)
      except:
        print('\nError in loading pickle. Check file name and path.')
        return
        
    else: # Load from dat
      self.df_aod_all = self.extract_daily_from_raw('AOD')

    ## Size from inversion product
    inv_from_pickle = input_yes('Load INV df (all records) from pickle?')

    if inv_from_pickle: # Load from pickle
      self.df_inv_all = self.load_pickle_all('INV',pickle_inv_all_name)
    else:
      self.df_inv_all = self.extract_daily_from_raw('INV')

    # Combine df
    combine = input_yes('Combine AOD and INV df?')
    if combine:
      self.df = self.combine_df()

    ## Filter time period
    extract = input_yes('Filter time range?')
    if extract:
      print(f'Time range: {self.time_range}')
      self.df = self.filter_time(self.df,self.time_range)
      time_range_str = '_'.join([x.strftime("%Y%m%d") for x in self.time_range]) 
    else:
      time_range_str = 'all_time'  

    ## Filter site
    extract = input_yes('Filter site?')
    if extract:
      self.df,site_name = self.filter_site(self.df)
      site_name = '_'+site_name if site_name else ''
    else:
      site_name = '' 

    save_pickle = input_yes('Save pickle?')
    if save_pickle:
      pickle_name = input_def('Pickle name to save?', 'COM20_{}{}.pkl'.format(time_range_str,site_name))      
      self.df.to_pickle(self.pickle_path+pickle_name)
      print(saved_as('COM', self.pickle_path+pickle_name))
    else:
      print('Data not saved to pickle')

    return

  ## From pickle
  def load_pickle(self, pickle_name, pickle_path=None):
    print('Loading AERONET data from pickle: {}'.format(pickle_name))
    pickle_path = pickle_path or self.pickle_path
    self.df = pd.read_pickle(pickle_path+self.pickle_name)

  def load_pickle_all(self,data_name,pickle_name):

    pickle_name = self.pickle_path+input_def('Pickle name?', pickle_name)
    print('Loading AERONET {} all site data from pickle: {}'.format(data_name, pickle_name))
    df = pd.read_pickle(pickle_name)

    print('Loaded AERONET {} all site data from pickle: {}'.format(data_name, pickle_name))
    print('************')

    return df

  ## From raw data
  def extract_daily_from_raw(self, data_name):

    print('\n#### Load AERONET {} all site data from raw data ####'.format(data_name))

    if data_name == 'AOD':
      file_path_default = aod_data_path
      pickle_name_default = pickle_aod_all_name
      df_name = 'df_aod_all'
    else:
      file_path_default = inv_data_path
      pickle_name_default = pickle_inv_all_name
      df_name = 'df_inv_all'

    # Ask for raw file info
    path     = input_def('Enter directory of raw files?', data_path)
    read_tar = input('Extract .tar? Type "YES" for yes: ')
    if read_tar in ['YES','yes']:
      tar_name = input('Name of .tar file? ')
      try: 
        extract_tar(path+tar_name,path=path)
      except:
        print(f'Tarfile not found. {path+tar_name}\nCheck the filename and directory')

    file_path   = input_def('Path for files?', path+file_path_default)

    print('Loading AERONET {} all site data from {}'.format(data_name,file_path))
    # Get all filenames from the directory
    files = os.listdir(file_path)
    end = files[0].index('.') - len(files[0])
    sitenames = [f[18:end] for f in files]

    # Read all files and merge into a datafile
    single_site= []

    for i in range(len(files)):
      f = files[i]
      draw_progress_bar((i+1)/len(files))
      single_site.append(pd.read_table(file_path+f,header=6,delimiter=','))
    df = pd.concat(single_site,ignore_index=True)

    skim = input_yes('\nSkim data?')
    if skim:
      if data_name == 'AOD':
        df = df[columns_to_keep + ['AOD_500nm','440-870_Angstrom_Exponent']]
        df = df.replace(-999.0,np.nan)
      else: # INV
        df = self.skim_inv(df)

    df['Date(dd:mm:yyyy)'] =df['Date(dd:mm:yyyy)'].apply(lambda x: datetime.datetime.strptime(x,'%d:%m:%Y'))

    print('\nFinished extracting {} data from raw data'.format(data_name))

    save_pickle = input_yes('Save pickle?')
    if save_pickle:
      pickle_name = input_def('Pickle name to save?', pickle_name_default)
      if not os.path.exists(self.pickle_path):
        os.makedirs(self.pickle_path)
      df.to_pickle(self.pickle_path+pickle_name)
      print(saved_as(df_name, self.pickle_path+pickle_name))

    return df

  ## INV daily data
  def skim_inv(self,df):
    df=df.rename(columns=inv_col_to_aod_col)
    # size_bins = sorted(['{:.6f}'.format(float(c)) for c in df.columns if '.' in c and 'N[' not in c])
    size_bins = ['{:.6f}'.format(c) for c in sorted([float(c) for c in df.columns if '.' in c and 'N[' not in c])]

    # Combine columns with similar wavelengths
    try: 
      wl_pairs = [['440nm','443nm'],['675nm','667nm'],['870nm','865nm']]

      keys_size      = ['Coarse','Fine','Total']
      keys_with_size = ['AOD_Extinction','Asymmetry_Factor']
      keys_no_size   = ['Absorption_AOD','Single_Scattering_Albedo']
      keys_all_size  = ['{}-{}'.format(k,s) for k in keys_with_size for s in keys_size]
      keys_all       = keys_all_size+keys_no_size

      pairs = [['{}[{}]'.format(k,wl[0]), '{}[{}]'.format(k,wl[1])]
              for k in keys_all for wl in wl_pairs]
      cols = ['{}[{}]'.format(k,w)
              for k in keys_all for wl in wl_pairs for w in wl]

      df = df[columns_to_keep + columns_reff + size_bins + cols]
      df = df.replace(-999.0,np.nan)

      for [v1, v2] in pairs:
        df[v1] = df[v1].combine_first(df[v2])
        df     = df.drop(columns=[v2])
      print('Volume distribution and AOD data is kept.')
    except:
      df = df[size_bins]
      df = df.replace(-999.0,np.nan)
      print('No AOD data. Only volume distribution is kept.')

    # Bins
    size_dict = {size_bins[i]:'Bin {}'.format(i+1) for i in range(len(size_bins))}
    df=df.rename(columns=size_dict)
    df = df.replace(-999.0,np.nan)

    # Convert size bin info into one columns
    df['dV/dlnr'] = df[list(size_dict.values())].values.tolist()

    return df

  ## Combine
  def combine_df(self):
    df = pd.merge(self.df_aod_all, self.df_inv_all, how='outer',
                  on=columns_to_keep)
    return df

  ## Filters
  def filter_time(self,df,time_range):
    df2 = df[(df['Date(dd:mm:yyyy)'] > time_range[0]) &
             (df['Date(dd:mm:yyyy)'] < time_range[1])]
    if len(df2) < 1:
      print(f'Not record in this time range: {time_range}') 
      return df
    else:
      print(f'Filtered records in this time range: {time_range}')
      print(f'Number of records: {len(df2)}')
      return df2

  def filter_site(self,df):
    site_name = input('Site name? ')
    df2 = []
    while site_name and len(df2)<1:
      df2 = df[df['AERONET_Site_Name'] == site_name]
      if len(df2) < 1: 
        print('No data at the specified site.')
        site_name = input('Site name? ') 
      
    
    if site_name == '':
      print('Data not filtered by site')
      return df, site_name
    else:
      print(f'Data filtered: {site_name}.')
      print(f'Number of records: {len(df2)}')
      return df2, site_name

  def filter_rec(self,df,min_rec=0,columns=['AOD_500nm']):
    nrec = (df[['AERONET_Site_Name']+columns]
              .dropna()
              .groupby('AERONET_Site_Name')
              .count())
    nrec = nrec[nrec[columns[0]] > min_rec]
    df2 = df[df['AERONET_Site_Name'].isin(list(nrec.index))][columns_def+columns]

    return df2

  ## Calculate averages
  def cal_average(self,columns=['AOD_500nm'],min_rec=0):

    if type(columns)==str and columns.upper() == 'SIZE':
      columns = [c  for c in self.df.columns if 'Bin' in c]
    
    df = self.df[columns_def+columns]
    df_ave = (df.dropna().groupby('AERONET_Site_Name').mean())
    df_ave['Day_of_Year'] = df.dropna().groupby('AERONET_Site_Name')['Day_of_Year'].apply(list)
    df_ave['Record_number'] = df_ave['Day_of_Year'].apply(lambda x: len(x))
    if min_rec>0:
      df_ave = df_ave[df_ave['Record_number']>= min_rec]

    return df_ave

  ## Select sites
  def select_sites(self,lat=[0,30],lon=[0,10]):

    df_trim = self.df[(self.df['Site_Latitude(Degrees)']>lat[0]) & \
                      (self.df['Site_Latitude(Degrees)']<lat[1]) & \
                      (self.df['Site_Longitude(Degrees)']>lon[0]) & \
                      (self.df['Site_Longitude(Degrees)']<lon[1])]

    return list(df_trim["AERONET_Site_Name"].unique()) # Return site names only
