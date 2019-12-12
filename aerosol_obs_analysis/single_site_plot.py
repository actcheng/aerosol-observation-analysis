import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from pandas.plotting import register_matplotlib_converters
 
register_matplotlib_converters()
# Output directory
save_path = 'workspace/MSJ_plot/single_site/'

start_year, start_month = 2006, 1
# For plotting
case_label = {'ae_simple':'Orig-SPRINTARS', 'bin_20':'Bin-SPRINTARS'}

var_conv = {'title': {'aod': 'AOD','alfa':'Angstrom Exponent'}}

line_colors = {'aeronet': 'tab:blue'}

class plot_single_site():

  def __init__(self,aeronet,save_path=save_path):
    self.aeronet      = aeronet
    self.case_label   = case_label
    self.save_path    = save_path

  def plot_sites(self,sites=['Ascension_Island'],
                        var=['aod'],
                        plot_2var=False,
                        plot_time=False,
                        smooth_window=None,
                        show=True,
                        legend=False,
                        save=None):

    from aeronet_single_site import aeronet_single_site
    for site_name in sites:
      site = aeronet_single_site(self.aeronet,site_name)

      if plot_time:        
        self.plot_time_series_monthly(site_name,var,site,save=save,legend=legend)

      if plot_2var:
        self.plot_2var(site_name,var,site,
                      save=save,legend=legend)

  def plot_time_series_monthly(self,site_name,var,aeronet_data,legend=True,save=False):
    
    for vname in var:
      fig, ax = plt.subplots()
      ## Plot AERONET
      vname_aeronet = self.aeronet.col_names[vname]
      ave = aeronet_data.monthly_average(vname_aeronet)
      if len(ave) == 0: 
        print(f'{site_name} ({vname}) is not plotted')
        continue
      plt.plot(ave,'o-',label='AERONET observation') 
      plt.plot(datetime.datetime(2006,12,5),np.mean(ave),'D',markersize=5,color=line_colors['aeronet'])   
      
      if legend:
        plt.legend()
      plt.xlim([datetime.datetime(2005,12,15),datetime.datetime(2006,12,15)])
      ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
      ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%b"))
      plt.xlabel('Date')
      plt.ylabel(var_conv['title'][vname])
      plt.title('{}'.format(site_name))
      if save:
        fname = self.save_path+'{}_{}.png'.format(site_name.lower(),vname) 
        plt.savefig(fname)
        print('Save fig as {}'.format(fname))

  def plot_2var(self,site_name,var,aeronet_data,legend=True,save=False):
    fig, ax = plt.subplots()
    # AERONET
    vname_aeronet1 = self.aeronet.col_names[var[0]]
    vname_aeronet2 = self.aeronet.col_names[var[1]]

    ave1 = aeronet_data.monthly_average(vname_aeronet1)    
    ave2 = aeronet_data.monthly_average(vname_aeronet2)
    aeronet_combined = ave1.join(ave2,how='inner')

    if len(aeronet_combined) == 0: 
      print(f'{site_name} ({var}) is not plotted')
      return
    plt.scatter(aeronet_combined[vname_aeronet1],aeronet_combined[vname_aeronet2],s=60,marker='D',label='AERONET')
    
    plt.xlabel(var_conv['title'][var[0]])
    plt.ylabel(var_conv['title'][var[1]])
    plt.title('{}'.format(site_name)) 
    if legend: plt.legend()
    if save:
      fname = self.save_path+'{}_{}_{}.png'.format(site_name.lower(),var[0],var[1]) 
      plt.savefig(fname,facecolor='white')
      print('Save fig as {}'.format(fname))
