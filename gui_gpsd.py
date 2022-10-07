import sys
from PyQt5 import uic, QtWebEngineWidgets, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem,QHeaderView, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThread , pyqtSignal, QDateTime , QObject, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
import json
from time import sleep
from datetime import datetime


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
                try:
                    dict_datos_gps = datos_gps.json()
                    #print(dict_datos_gps) 
                    recepcion = []
                    recepcion.append(dict_datos_gps)
                    self.refresh.emit(recepcion,server)
                    sleep(1)
                except (json.decoder.JSONDecodeError):
                    continue
            else:
                server = False
                self.refresh.emit(recepcion,server)
                sleep(1)
                
  

## CLASE PARA CREAR Y EJECUTAR INTERFAZ GRAFICA (GUI)
class gui_gps(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi("data_gui.ui",self)
        ## NOMBRE VENTANA ##
        self.setWindowTitle('GEOLOCALIZADOR GPS -- by Michel Alvarez --')
        ## IMAGEN FONDO ##
        pixmap1 = QPixmap('fondo.jpg')
        self.img_fondo.setPixmap(pixmap1)

        ## IMAGEN LETRAS ##
        pixmap2 = QPixmap('Letras_geolocalizador_GPS.png')
        self.img_letras.setPixmap(pixmap2)

        ## IMAGEN K1MICHEL ##
        pixmap3 = QPixmap('logo_obs.png')
        self.img_k1michel.setPixmap(pixmap3)

        ## THREAD ## 
        self.backend = BackendThread() 
        self.backend.refresh.connect(self.mostrar_datos)
        self.thread = QThread()
        self.backend.moveToThread(self.thread)
        self.thread.started.connect(self.backend.run)
        self.thread.start()
        
        ## BARRA PROGRESO ##
        self.barra_progreso.setValue(0)
        
        ## NAVEGADOR ##
        self.navegador.loadProgress.connect(self.webLoading)

        ## VARIABLES ##
        self.lat_anterior = int
        self.lon_anterior = int

    def mostrar_datos(self,recepcion,server):
        
        if server:
            
            if recepcion[0] != None: 
                n_satelites = recepcion[0]['n_satelites']
                fecha = recepcion[0]['fecha']
                hora = recepcion[0]['hora']
                velocidad_h = str(recepcion[0]['velocidad_h'])
                velocidad_v = str(recepcion[0]['velocidad_v'])
                lat = recepcion[0]['latitud']
                lon = recepcion[0]['longitud']
                altitud = str(recepcion[0]['altitud'])
                self.url_gps = recepcion[0]['url']
                url = QUrl(self.url_gps)
                if (round(lat,1) != self.lat_anterior) or (round(lon,1) != self.lon_anterior):
                    self.navegador.page().load(url)
                    print('GPS MOVIL')
                    self.in_movimiento.setText('Dinamico')
                else:
                    print('GPS INMOVIL')
                    self.in_movimiento.setText('Estatico')

                self.in_satelites.setText(n_satelites)
                self.in_fecha.setText(fecha)
                self.in_hora.setText(hora)
                self.in_vel_h.setText(velocidad_h)
                self.in_vel_v.setText(velocidad_v)
                self.in_latitud.setText(str(lat))
                self.in_longitud.setText(str(lon))
                self.in_altitud.setText(altitud)
            
                self.lat_anterior = round(lat,1)
                self.lon_anterior = round(lon,1)


        else:
            print('Ningun dato recibido')

    def webLoading(self, event):
        self.barra_progreso.setValue(event)

def run_gui():
    app = QApplication(sys.argv)
    GUI = gui_gps()
    GUI.show()
    sys.exit(app.exec_()) 

if __name__ == '__main__':
    run_gui()

