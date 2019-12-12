import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors
import numpy as np
import pandas as pd
# import seaborn as sns

# sns.set()
# sns.set_style("ticks")

month_dict = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 
              'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10,'NOV':11, 'DEC':12}

size_bins = [0.05,0.065604, 0.086077, 0.112939, 0.148184,
             0.194429, 0.255105, 0.334716, 0.439173, 0.576227,
             0.756052, 0.991996, 1.301571, 1.707757, 2.240702,
             2.939966, 3.857452, 5.06126, 6.640745, 8.713145,
             11.432287, 15.0]

bin_names = ['Bin {}'.format(i+1) for i in range(len(size_bins))]
agg_dict = {'Site_Latitude(Degrees)':'mean',
            'Site_Longitude(Degrees)':'mean',
            'AOD_500nm':['mean','count'],
            '440-870_Angstrom_Exponent':['mean','count']
           }

agg_dict2 = {'dV/dlnr':'count'}
for bin_name in bin_names:
    agg_dict2[bin_name] = 'mean'

colors={'Sulfate':'orange','BC':'grey','OC':'hotpink','Salt':'royalblue','Dust':'brown'}

class plot_single_site_size():

    def __init__(self,aeronet):
        self.aeronet = aeronet
        self.aeronet_size_agg =  (aeronet.df
                            .groupby(['AERONET_Site_Name'])
                            .agg({**agg_dict,**agg_dict2})
                            .dropna(subset=[('AOD_500nm','mean'),('440-870_Angstrom_Exponent','mean')])
                            .sort_values(by=[('dV/dlnr','count')],ascending=False))

    def plot_dvdlnr(self,site,
                    savedir=None,
                    save_suffix='',
                    legend=True):

        # AERONET
        try: 
            data_aeronet = [self.aeronet_size_agg.loc[site,bin_name] for bin_name in bin_names]
        except (KeyError):
            print('Site does not contain size data in this period')
            return

        fig, ax = plt.subplots()
        plt.semilogx(size_bins,data_aeronet,'-',linewidth=2,color='k',label='AERONET')
    
        plt.xlabel('Radius [${\mu m}$]',fontsize=14)
        plt.ylabel('dV(r)/dln(r) [${\mu m}$]',fontsize=14)
        plt.title('{} (rec={})'.format(site,int(self.aeronet_size_agg.loc[site,'dV/dlnr'])),fontsize=14)

        if legend: plt.legend()
        plt.tick_params(labelsize=14)
        plt.tight_layout()
        
        if savedir:
            filename= '{}{}_size_dv{}.png'.format(savedir,site.lower(),save_suffix)
            plt.savefig(filename,facecolor='white')
            print('Figure saved at '+filename)
        plt.show()
        return

    # Plot size distribution: Time series
    def get_dV_data(self,site,time_range=None):
        data = self.aeronet.df[self.aeronet.df['AERONET_Site_Name']==site]

        if time_range:
            data = data[data['Date(dd:mm:yyyy)']>time_range[0]]
            data = data[data['Date(dd:mm:yyyy)']<time_range[1]]
        data = data.set_index('Date(dd:mm:yyyy)')

        if time_range and data.iloc[0].name != time_range[0]:
            data.loc[time_range[0]] = np.nan
        if time_range and data.iloc[-1].name != time_range[1]:
            data.loc[time_range[1]] = np.nan

        # data = data.resample('D').mean()

        dV_data = data[bin_names].T

        return dV_data

    def dV2dN(self,dV_data):
        dN_data = pd.DataFrame()
        for i in range(len(bin_names)):
            bin_name=bin_names[i]
            volume = 4/3*np.pi*size_bins[i]**3
            dN_data[bin_name] = dV_data.T[bin_name].apply(lambda x: x/volume)

        return dN_data.T

    def plot_dV_time(self,site,time_range=None,
                        vmin=2e-2, vmax=1e1):

        dV_data = self.get_dV_data(site=site,time_range=time_range)

        # Plot
        date_list=list(dV_data.columns)
        days_fmt = mdates.DateFormatter('%m/%d')

        fig, ax = plt.subplots(figsize=(16,4))
        pcm = ax.pcolormesh(date_list,size_bins,dV_data,
                            cmap='Reds',
                            norm=matplotlib.colors.LogNorm(vmin=vmin,
                                            vmax=vmax))
        fig.colorbar(pcm, ax=ax, extend='both')

        ax.tick_params(labelsize=14)

        ax.xaxis.set_major_formatter(days_fmt)
        ax.set_xlabel('Date',fontsize=15)
        if time_range: ax.set_xlim(time_range)
        ax.set_yscale('log')
        ax.set_ylabel('Radius (${\mu}m$)',fontsize=15)
        ax.set_title('dV/dlnr',fontsize=16)
        return

    def plot_dN_time(self,site='Solar_Village',time_range=None,all_dates=True,
                    vmin=2e-2, vmax=1e2):

        dV_data = self.get_dV_data(site=site,time_range=time_range)
        dN_data = self.dV2dN(dV_data)

        # Plot
        date_list=list(dN_data.columns)
        days_fmt = mdates.DateFormatter('%m/%d')

        fig, ax = plt.subplots(figsize=(16,4))
        pcm = ax.pcolormesh(date_list,size_bins,dN_data,
                            cmap='Reds',
                        norm=matplotlib.colors.LogNorm(vmin=vmin,
                                            vmax=vmax))

        fig.colorbar(pcm, ax=ax, extend='both')

        ax.tick_params(labelsize=14)
        ax.xaxis.set_major_formatter(days_fmt)
        ax.set_xlabel('Date',fontsize=15)
        if time_range: ax.set_xlim(time_range)
        ax.set_yscale('log')
        ax.set_ylabel('Radius (${\mu}m$)',fontsize=15)
        ax.set_title('dN/dlnr',fontsize=16)
        return 
    