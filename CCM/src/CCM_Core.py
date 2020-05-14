"""
Cyclone Classifier Model (CCM)

Author: Md. Manjurul Husain Shourov
last edited: 13/11/2018
"""

from os import walk
from pandas import DataFrame
from math import radians, cos, sin, asin, sqrt

# dbDirectory = "F:/RAWork/CCM/CCMProject/CyconeDataBase/CycloneInfo/"


def distance(CycloneDBCoordinates, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1 = CycloneDBCoordinates
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    km = 2 * asin(sqrt(a)) * 6367
    return km

def Metadata_Genarator(CycloneDB):
    DataB = DataFrame()
    file = list(walk(CycloneDB))[0][2]

    for f in file:
        if (f[-4:] == '.csv') and (f != 'Metadata.csv'):
            oldN = str(int(f[:-5], 16)) + f[-5]
            DataB = DataB.append(DataFrame([f[:-4], oldN, int(oldN[:5]) / 1000, int(oldN[5:10]) / 1000, int(oldN[10:13]), oldN[13]]).T)

    DataB.columns = ['Cyclone ID', 'Old ID', 'Latitude', 'Longitude', 'Wind Speed', 'Tide']

    return DataB.reset_index()

	
def CCM(lat, lon, wind, tide, DBDir):

    Data = Metadata_Genarator(DBDir)

    Data['Distance'] = Data.loc[:, ['Longitude', 'Latitude']].apply(distance, args=(lon, lat), axis=1)
    Data['WindDistance'] = abs(Data['Wind Speed'] - wind)

    DataTide = Data[Data['Tide'] == tide]
    DataMinDis = DataTide[DataTide['Distance'] == DataTide['Distance'].min()]
    FData = DataMinDis[DataMinDis['WindDistance'] == DataMinDis['WindDistance'].min()]

    return FData.loc[FData.index[0],'Cyclone ID']