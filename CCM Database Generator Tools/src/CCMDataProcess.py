import os
import numpy as np
import pandas as pd
import geopandas as gpd
from tkinter import filedialog, Tk
from shapely.geometry import Point
import matplotlib.pyplot as plt
import xlrd


def UnionWiseReduceGeopandas(Data, Polys, func, varName):
    joined = gpd.sjoin(Data, Polys, op='within', how='left')
    joinedClean = joined[~joined.DDIEM_ID.isna()]
    GroupRes = joinedClean.groupby('DDIEM_ID')['z'].agg(func)
    CountRes = joinedClean.groupby('DDIEM_ID')['z'].count()
    GroupRes.name = varName
    res = pd.merge(Polys, GroupRes.to_frame(), on='DDIEM_ID', how='left')
    res.loc[res[varName].isnull(),varName] = 0
    return (res, CountRes)

def StructureDamageCondition(df, DamageMatrix, DmClass):
    if (df['Water Depth'] > 6) or (df['Wind Speed'] > 250):
        cls = 6
    else:
        cls = DamageMatrix.loc[DamageMatrix.loc[:,0] >= df['Water Depth'], DamageMatrix.loc[0,:] >= df['Wind Speed']].iloc[0,0]
    return DmClass[DmClass.StructureDamageID == cls].StructureDamageClass.iloc[0]

def PolderDamageCondition(df, PldDamageMatrix):
    if df['Thrust Force'] > 81.4:
        res = 'HP'
    elif df.RegionID in PldDamageMatrix.columns:
        res = PldDamageMatrix[PldDamageMatrix['Thrust Force'] > df['Thrust Force']].loc[:,PldDamageMatrix.columns == df.RegionID].iloc[-1,0]
    else:
        res = 'No polder in the area'
      
    return res
	
root = Tk()
root.withdraw()
DirN = filedialog.askdirectory()
	
OutputDir = DirN
files = list(os.walk(DirN + '/WD/'))[0][2]

PolyWithoutRiver = gpd.read_file("DECCMA_Upazilla_without_River_for_JICA_CCM/DECCMA_Upazilla_without_River_for_JICA_CCM_WGS_1984.shp")
PolyFull = gpd.read_file("DECCMA_Upazilla_Final/DECCMA_Upazilla_Final_WGS_1984.shp")

PolderDamageMtx = pd.read_excel("PolderInfo.xlsx",sheet_name='PolderDataMatrix')
PolderInfo = pd.read_excel("PolderInfo.xlsx",sheet_name='PolderInfo')

StrDamageMtx = pd.read_excel("StructureDamageData.xlsx",sheet_name="DamageMatrix",header=None)
StrDamageClass = pd.read_excel("StructureDamageData.xlsx",sheet_name="Metadata")


for fileN in files:
    print(fileN)
    FileName = hex(int(fileN[:-5]))[2:] + fileN[-5] + '.csv'
    
    try:
        DataWD = pd.read_csv(DirN + "/WD/" + fileN, header=None, names=['x','y','z'], sep='\s+', skiprows=3)
        DataWD = DataWD[DataWD.loc[:,'z'] > 0]
        DataWD['Point'] = [Point(xyz) for xyz in zip(DataWD.iloc[:,0], DataWD.iloc[:,1])]
        DataWD = gpd.GeoDataFrame(DataWD, geometry=DataWD.Point, crs = PolyFull.crs)

        DataWS = pd.read_csv(DirN + "/WS/" + fileN[:-4] + '.xyz', header=None, names=['x','y','p','q'], sep='\s+', skiprows=4)
        DataWS['z'] = np.sqrt(DataWS.p ** 2 + DataWS.q ** 2) * 3.6
        DataWS = DataWS.loc[:,['x','y','z']]
        DataWS['Point'] = [Point(xyz) for xyz in zip(DataWS.iloc[:,0], DataWS.iloc[:,1])]
        DataWS = gpd.GeoDataFrame(DataWS, geometry=DataWS.Point, crs = PolyFull.crs)

        DataTF = pd.read_csv(DirN + "/TF/" + fileN[:-4] + '.csv', sep=',')
        DataTF.columns = ['x','y','z']
        DataTF = DataTF[DataTF.loc[:,'z'] > 0]
        DataTF['Point'] = [Point(xyz) for xyz in zip(DataTF.iloc[:,0], DataTF.iloc[:,1])]
        DataTF = gpd.GeoDataFrame(DataTF, geometry=DataTF.Point, crs = PolyFull.crs)

        (ResWD, Count) = UnionWiseReduceGeopandas(DataWD, PolyWithoutRiver, 'mean', 'Water Depth')
        (ResWS, c) = UnionWiseReduceGeopandas(DataWS, PolyFull, 'max', 'Wind Speed')
        (ResTF, c) = UnionWiseReduceGeopandas(DataTF, PolyFull, 'max', 'Thrust Force')                         

        FRes = ResWD.merge(ResWS.loc[:,['DDIEM_ID','Wind Speed']], on='DDIEM_ID'
                          ).merge(ResTF.loc[:,['DDIEM_ID','Thrust Force']], on='DDIEM_ID')

        temp = pd.merge(FRes, PolderInfo.loc[:,['DDIEM_ID','RegionID']], on =['DDIEM_ID'])
        FRes['Polder Damage Condition'] = temp.apply(PolderDamageCondition, args = (PolderDamageMtx,), axis = 1)
        FRes['Structure Damage Condition'] = FRes.apply(StructureDamageCondition, args=(StrDamageMtx, StrDamageClass), axis=1)

        Count.name = 'Count'
        FRes = pd.merge(FRes, Count.to_frame(), on='DDIEM_ID', how='left')
        FRes.drop(['OBJECTID','geometry'],axis=1).to_csv(OutputDir + '/' + FileName, index=False)

    except:
        print('Error in file : ' + fileN + '\n')


DataB = pd.DataFrame()
file = list(os.walk(OutputDir))[0][2]

for f in file:
    if f != 'Metadata.csv':
        oldN = str(int(f[:-5],16)) + f[-5]
        DataB = DataB.append(pd.DataFrame([f[:-4], oldN, int(oldN[:5])/1000, int(oldN[5:10])/1000, int(oldN[10:13]), oldN[13]]).T)

DataB.columns = ['Cyclone ID', 'Old ID', 'Latitude', 'Longitude', 'Wind Speed', 'Tide']
DataB.to_csv(OutputDir + '/Metadata.csv', index=False)

print('\nExporting Image...')
var = 'Water Depth'
maxV = 3

for f in file:
    if (f[-4:] == '.csv') and (f != 'Metadata.csv'):
#         f = '1fa0e143cdeH.csv'
        oldN = str(int(f[:-5],16)) + f[-5]
        pp = gpd.GeoSeries([Point(int(oldN[5:10])/1000, int(oldN[:5])/1000)])
        data = pd.read_csv(DirN + '/' + f)
#         data.rename(columns={'DDIEM ID':'DDIEM_ID'})
        res = pd.merge(PolyFull, data.loc[:,['DDIEM_ID',var]], on='DDIEM_ID', how='left')
        fig, ax = plt.subplots(1, figsize=(16,12))
        if res[var].max() <= maxV :
            res.plot(column=var, legend=True, cmap='OrRd', edgecolor='gray', ax=ax, vmax=maxV)
        else:
            print(f)
            res.plot(column=var, legend=True, cmap='OrRd', edgecolor='gray', ax=ax, vmax=res[var].max())
                     
        ax.set_title(f[:-4] + '_' + var, fontsize=25)
        pp.plot(ax=ax, marker=u'$\u2191$',color='b', markersize=500)
        plt.tight_layout()
        plt.savefig(DirN + '/' + f[:-4]  +'.png')
        plt.close()

print('Complete!')