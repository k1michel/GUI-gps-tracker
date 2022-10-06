import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem,QHeaderView, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThread , pyqtSignal, QDateTime , QObject
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

import requests
import json
from time import sleep
from datetime import datetime
import subprocess
from threading import Thread
import pandas as pd
 
## CLASE PARA ACCION DEL THREAD ##
class BackendThread(QObject):
    refresh = pyqtSignal(list,bool)
    ip_gps= 'http://192.168.1.4:8000/'
    server: bool
    recepcion: list
    
    def run(self):
        while True:
            try:
                datos_gps = requests.get(f'{self.ip_gps}url',timeout=4)
                print(datos_gps)
                server = True
            except (requests.exceptions.ConnectionError):
                print('GPS INACTIVO...Conectando...')
                server = False
                recepcion = []
                self.refresh.emit(recepcion,server)
                continue
                
            if server==True:
                server = True
                dict_datos_gps = datos_gps.json()
                print(dict_datos_gps) 
                recepcion = []
                recepcion.append(dict_datos_gps)
                self.refresh.emit(recepcion,server)
                sleep(1)
            else:
                info_server = ' '
                server = False
                self.refresh.emit(recepcion,server)
                sleep(1)
                
   

## CLASE PARA CREAR Y EJECUTAR INTERFAZ GRAFICA (GUI)
class gui_gps(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi("data_gui.ui",self)
        
        ## THREAD ## 
        self.backend = BackendThread() 
        self.backend.refresh.connect(self.mostrar_datos)
        self.thread = QThread()
        self.backend.moveToThread(self.thread)
        self.thread.started.connect(self.backend.run)
        self.thread.start()

        ## NOMBRE VENTANA ##
        self.setWindowTitle('GEOLOCALIZACION MI GPS')
        self.web_view = QWebEngineView()
        self.web_view.loadProgress.connect(self.webLoading)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        root = QVBoxLayout()
        root.addLayout(self.nav_bar)
        root.addWidget(self.web_view)
        root.addWidget(self.progress)

        self.setLayout(root)
        
    
    def mostrar_datos(self,recepcion,server):
        lat = recepcion[0]['latitud']
        lon = recepcion[0]['longitud']
        url_gps = recepcion[0]['url']
        info = str(f'Latitud= {lat}\nLongitud= {lon}\nURL= {url_gps}')
        if server:
            self.texto_info.setText(info)
            print(f'Recibidos los datos: {info}')
        else:
            print('Ningun dato recibido')
    
    def webLoading(self, event):
        self.progress.setValue(event)
    

def run_gui():
    app = QApplication(sys.argv)
    GUI = gui_gps()
    GUI.show()
    sys.exit(app.exec_()) 

if __name__ == '__main__':
    run_gui()