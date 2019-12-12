'''''

Plotting tool for AERONET data and model results

Functions:
- plot_var_map_interactive
- plot_single_site

'''''

import numpy as np
import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt


import plotly as py
import plotly.graph_objs as go

import datetime

# Output directory
save_path = 'workspace/plot_output'

# For plotting
style = {('monthly','ae'):'x-',('daily','ae'):'-',
         ('monthly','ssd'):'s-',('daily','ssd'):'-'}
case_label = {'ae':'Original SPRINTARS', 'ssd':'Revised SPRINTARS'}

# For size distribution
size_bins = [0.05,0.065604, 0.086077, 0.112939, 0.148184,
             0.194429, 0.255105, 0.334716, 0.439173, 0.576227,
             0.756052, 0.991996, 1.301571, 1.707757, 2.240702,
             2.939966, 3.857452, 5.06126, 6.640745, 8.713145,
             11.432287, 15.0]

bin_names = ['Bin {}'.format(i+1) for i in range(len(size_bins))]

colors = {}
boundaries = {}
cmaps = {}
norms = {}

colors['cmap1'] = ['#A000C8','#8200DC','#1E3CFF','#00C8C8','#00D28C',
                  '#00DC00','#A0E632','#E6DC32','#F08228','#FA3C3C','#F00082']
boundaries['cmap1'] = [0,0.05,0.07,0.1,0.2,0.3,0.5,0.7,1,2]

colors['cmap2'] = ['#A000C8','#8200DC','#1E3CFF','#00A0FF','#00C8C8','#00D28C',
                  '#00DC00','#A0E632','#E6DC32','#E6AF2D','#F08228','#FA3C3C','#F00082']
boundaries['cmap2'] = [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6]

for key in colors.keys():
  cmaps[key] = matplotlib.colors .ListedColormap(colors[key][1:-1])
  cmaps[key].set_under(colors[key][0])
  cmaps[key].set_over(colors[key][-1])

############################
class plot_aeronet():

  def __init__(self,aeronet, # The only necessary input
                save_path=save_path,
                case_label=case_label,style=style):

    self.aeronet      = aeronet

    self.case_label   = case_label
    self.save_path    = save_path
    self.style        = style

    return

### Plotting: AERONET  ###

  def plot_var_map_interactive(self, var='aod',min_rec=0,dtick=0.1):


    py.offline.init_notebook_mode(connected=True)

    try:
      var_name = self.aeronet.col_names[var]
    except:
      var_name = var

    df_ave = self.aeronet.cal_average(columns=[var_name],min_rec=min_rec)

    lons = df_ave['Site_Longitude(Degrees)'].apply(lambda x: x+360 if x<0 else x)
    lats = df_ave['Site_Latitude(Degrees)']

    data = [go.Scattergeo(
        lat = lats,
        lon = lons,
        text = df_ave.index.values + ' ('+[str(d) for d in df_ave[var_name].values] +')',
        marker = dict(
            color = df_ave[var_name],
            colorscale = 'Rainbow',
            opacity = 0.7,
            line = dict(width=0.5),
            size = 7,
            colorbar = dict(
                thickness = 30,
                titleside = "right",
                outlinecolor = "rgba(68, 68, 68, 0)",
                ticks = "outside",
                ticklen = 2,
                dtick = dtick
            )
        )
    )]

    layout = go.Layout(
        autosize=False,
        width=600,
        height=300,
        margin=go.layout.Margin(
            l=0,
            r=0,
            b=0,
            t=40,
            pad=4
        ),
        geo = dict(
            lonaxis = dict(
                showgrid = True,
                gridwidth = 1,
                dtick = 30
            ),
            lataxis = dict (
                showgrid = True,
                gridwidth = 1,
                dtick = 30
            )
        ),
        title =var_name
    )

    fig = go.Figure(data=data, layout=layout)
    py.offline.iplot(fig)
    return

