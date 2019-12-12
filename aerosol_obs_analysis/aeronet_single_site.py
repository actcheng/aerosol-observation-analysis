import datetime

class aeronet_single_site():

  def __init__(self,aeronet,site):

    df = aeronet.df[aeronet.df['AERONET_Site_Name']==site]

    self.name = site
    self.lon = df['Site_Longitude(Degrees)'].unique()[0]
    self.lat = df['Site_Latitude(Degrees)'].unique()[0]

    self.data= df
    return

  def monthly_average(self,vname):
    data = self.data[['Date(dd:mm:yyyy)',vname]].dropna()

    data['date_month'] = data['Date(dd:mm:yyyy)'].apply(lambda x: datetime.datetime(x.year,x.month,1))
    ave = data.groupby(by='date_month').mean()

    return ave
