# Generate Data File

from netCDF4 import Dataset
import numpy as np

#nc_f = './forecast.nc'  # Your filename
nc_spread = Dataset("./mslp_spread.nc", 'r')  # Dataset is the class behavior to open the file
nc_msl = Dataset("./mslp_mean.nc")

spreadBins = np.array([200.,1000,1800,3000]) #spread levels
spreadInds = np.digitize(nc_spread['msl'][19,:,:],spreadBins)
meanBins = np.array([960,970,980,990,1000,1010,1020,1030])*100
meanInds = np.digitize(nc_msl['msl'][19,:,:],meanBins)
tmpInds = spreadInds*10+meanInds
vsupBins = np.array([0,2,3,4,5,6,7,8,10,12,15,17,20,25,30])
vsupInds = np.digitize(tmpInds,vsupBins)

import netCDF4 as nc4

f = nc4.Dataset('vsup.nc','w', format='NETCDF4') #'w' stands for write
f.createDimension('longitude', len(nc_spread['longitude'][:]))
f.createDimension('latitude', len(nc_spread['latitude'][:]))
longitude = f.createVariable('longitude', 'f4', 'longitude')
latitude = f.createVariable('latitude', 'f4', 'latitude')
vsup = f.createVariable('Vsup', 'i4', ('latitude', 'longitude'))
longitude[:] = nc_spread['longitude'][:]
latitude[:] = nc_spread['latitude'][:]
vsup[:,:] = vsupInds[:,:]
longitude.units = 'degrees_east'
latitude.units = 'degrees_north'
vsup.units = "1"
f.close()
