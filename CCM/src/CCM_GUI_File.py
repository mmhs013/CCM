"""
Cyclone Classifier Model (CCM)

Author: Md. Manjurul Husain Shourov
last edited: 17/11/2018
"""

import sys
import os
from PyQt5 import uic, QtWidgets, QtGui
from CCM_Core import CCM
from pandas import read_csv

class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('CCM_GUI_New.ui', self)
        self.setWindowTitle('Cyclone Classifier Model')
        self.show()

        self.RootDir = os.getcwd()

        self.ImView.setScaledContents(True)
        self.ImView.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.TableWidget.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.TableWidget.horizontalHeader().setStretchLastSection(True)

        self.ApplyPButton.clicked.connect(lambda: self.Action(self.HighRButton.isChecked()))
        self.ClearPButton.clicked.connect(self.Action)

    def Action(self, RButton):
        sender = self.sender()

        if sender.text() == 'Apply':
            if (self.LatLineEdit.text() != '') and (self.LongLineEdit.text() != '') and (self.WSLineEdit.text() != ''):
                lat = float(self.LatLineEdit.text())
                lon = float(self.LongLineEdit.text())
                wind = float(self.WSLineEdit.text())

                if RButton:
                    tide = 'H'
                else:
                    tide = 'L'

                CycloneID = CCM(lat, lon, wind, tide, os.path.join(self.RootDir,'CyconeDataBase/CycloneInfo'))
                print(CycloneID)

                CycloneDBPath = self.RootDir + '/CyconeDataBase/CycloneInfo/' + CycloneID + '.csv'
                CycloneMapPath = self.RootDir + '/CyconeDataBase/HazardMap/' + CycloneID + '.jpg'

                # Map Preparation
                self.PixMap = QtGui.QPixmap(CycloneMapPath)
                self.ImView.setPixmap(self.PixMap)
                self.ImView.adjustSize()

                # Table Preparation
                PolderClasses = {'HP':'Possibility of substantial damage to polders',
                                 'MP':'Possiblity of some damage to polders',
                                 'LP':'Possiblity of no damage to polders'}

                StructureClasses = {'Pacca- No, Semi Pacca- No, Kacha- No':'All types of houses are likely to remain safe',
                                    'Pacca- No, Semi Pacca- No, Kacha- Partial':'Kacha houses are likely to be partially damaged. Semi-paka and paka houses are likely to reamin safe.',
                                    'Pacca- No, Semi Pacca- No, Kacha- Full':'Kacha houses are likely to be fully damaged. Semi-paka and paka houses are likely to reamin safe.',
                                    'Pacca- No, Semi Pacca- Partial, Kacha- Full':'Kacha houses are likely to be fully damaged. Semi-paka houses are likely to be partially damaged. Paka houses are likely to reamin safe.',
                                    'Pacca- Partial, Semi Pacca- Full, Kacha- Full':'Kacha houses are likely to be fully damaged. Semi-paka houses are likely to be fully damaged. Paka houses are likely to be partially damaged.',
                                    'Pacca- Full, Semi Pacca- Full, Kacha- Full':'All types of houses are likely to be fully damaged.'}

                ColumnName = {'DIVNAME':'Division',
                              'DISTNAME':'District',
                              'Water Depth':'Surge Height (m)',
                              'Wind Speed':'Wind Speed (km/hr)'}

                CycloneData = read_csv(CycloneDBPath)
                CycloneData.drop(['DDIEM_ID', 'Thrust Force', 'Count'],axis=1,inplace=True)
                CycloneData['Polder Damage Condition'].replace(PolderClasses,inplace=True)
                CycloneData['Structure Damage Condition'].replace(StructureClasses, inplace=True)
                CycloneData['Water Depth'] = CycloneData['Water Depth'].round(1)
                CycloneData['Wind Speed'] = CycloneData['Wind Speed'].astype(int)
                CycloneData.rename(ColumnName, axis=1, inplace=True)

                self.TableWidget.setRowCount(0)
                self.TableWidget.setColumnCount(CycloneData.shape[1])
                self.TableWidget.setHorizontalHeaderLabels(CycloneData.columns.tolist())

                for r in range(CycloneData.shape[0]):
                    self.TableWidget.insertRow(r)
                    for c in range(CycloneData.shape[1]):
                        self.TableWidget.setItem(r, c, QtWidgets.QTableWidgetItem(str(CycloneData.iloc[r, c])))

        else:
            self.LatLineEdit.clear()
            self.LongLineEdit.clear()
            self.WSLineEdit.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())