import csv
import math
import os
import sys
import mne
import numpy as np
import scipy
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QThreadPool
import folium
from WindowAbstractImage import ImageWindow
from WindowGraph import WindowGraph
from Worker import Worker
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import webbrowser
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        self.w2 = None
        self.w3 = None
        self.threadpool = QThreadPool()
        self.setWindowTitle("App")
        self.buttonGenerate=QPushButton("Generate Maps")
        self.buttonOpen = QPushButton("Open Maps")
        self.buttonGraph=QPushButton("View Statistics")
        self.buttonGenImage=QPushButton("Generate abstract image")
        self.buttonExit=QPushButton("Exit")
        self.buttonGradient="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #555555, stop: 1 #222222);"

        pagelayout = QVBoxLayout()
        button_layout = QVBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        self.buttonGenerate.pressed.connect(self.activate_tab_1)
        self.buttonGenerate.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonGenerate)

        self.buttonOpen.pressed.connect(self.activate_tab_5)
        self.buttonOpen.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonOpen)

        self.buttonGraph.pressed.connect(self.activate_tab_2)
        self.buttonGraph.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonGraph)

        self.buttonGenImage.pressed.connect(self.activate_tab_3)
        self.buttonGenImage.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonGenImage)

        self.buttonExit.pressed.connect(self.activate_tab_4)
        self.buttonExit.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonExit)



        button_layout.setSpacing(15)

        widget = QWidget()
        widget.setLayout(pagelayout)
        gradientBg = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #87CEFA, stop: 1 white);"
        widget.setStyleSheet("background: "+gradientBg+"color: #333333; font: bold 14px;")
        self.setCentralWidget(widget)


    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        self.buttonGenerate.setEnabled(True)
        self.buttonGenerate.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        print("THREAD COMPLETE!")


    def on_finished(self):
        self.w2.close()
        self.thread_finished = True


    def on_finised_abstract_image(self):
        self.thread_finished = True

    def thread_complete_abstract_image(self):
        print("THREAD COMPLETE!")

    def progress_fn_abstract_image(self, n):
        print("%d%% done" % n)

    def print_output_abstract_image(self, s):
        print(s)

    def closeEvent(self, event):
        # Execute function on close
        self.cleanup()
        event.accept()

    def cleanup(self):
        print("Cleaning up before closing.")
        # Perform any necessary cleanup before closing the app
        sys.exit(0)

    def selectFile(self, startPath):
        Tk().withdraw()
        default_path = startPath
        file_path_csv = askopenfilename(initialdir=default_path)
        return file_path_csv

    def activate_tab_5(self):
        fileName = self.selectFile("resources\\Maps")
        webbrowser.open(fileName)

    def activate_tab_1(self):
        color_magnitude={
            1:"#2fb2cc",
            2:"#2da5ad",
            3:"#218a42",
            4:"#8fc255",
            5:"#9ccc66",
             6:"#e6b243",
             7:"#a3263a",
             8:"#5c242d",
        }
        cordinateAll =(20.0286674,-155.4425049)
        allEarthquakes = folium.Map(
            tiles='Stamen Terrain',
            zoom_start=13,
            location=cordinateAll
        )
        fileName=self.selectFile("resources\\Csv_Data")

        with open(fileName, 'r') as csvfile:
            # Create a CSV reader
            reader = csv.reader(csvfile)
            skipHeader=True
            # Iterate over each row in the CSV file
            for row in reader:
                # Access data in each column of the row
                if skipHeader==True:
                    skipHeader=False
                    continue
                latitude = float(row[7])
                longitude = float(row[8])
                magnitude = math.ceil(float(row[2]))
                coordinate = (latitude, longitude)
                m = folium.Map(
                    tiles='Stamen Terrain',
                    zoom_start=13,
                    location=coordinate
                )

                # add circle in the middle of the map
                folium.Circle(
                    location=coordinate,
                    radius=1000,  # radius in meters
                    color='red',  # outline color
                    fill=True,  # fill the circle
                    fill_color=color_magnitude[magnitude],  # fill color
                    fill_opacity=0.6  # fill opacity
                ).add_to(m)

                folium.Circle(
                    location=coordinate,
                    radius=1000,  # radius in meters
                    color='red',  # outline color
                    fill=True,  # fill the circle
                    fill_color=color_magnitude[magnitude],  # fill color
                    fill_opacity=0.6  # fill opacity
                ).add_to(allEarthquakes)

                # save map to an HTML file
                map_filename = 'map_'+row[0]+'.html'
                m.save("resources"+"\\"+'Maps'+"\\"+map_filename)
            allEarthquakes.save("resources" + "\\"+'Maps'+"\\" + 'ALL_EARTHQUAKES_MAP_WORLD')

    def activate_tab_2(self):
        fileName=self.selectFile("resources\\Csv_Data")
        if self.w is None:
            self.w = WindowGraph(fileName)
            self.w.show()
            self.w=None


    def on_w3_closed(self):
        self.w3 = None

    def showWindow(self):
        self.buttonGenImage.setEnabled(True)
        self.buttonGenImage.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        self.buttonGenImage.setText("Generate abstract image")
        self.w3.displayWindow()

    def activate_tab_3(self):
        file_path_csv = self.selectFile('resources/headset data')
        print(file_path_csv)
        if file_path_csv!='':
            self.buttonGenImage.setEnabled(False)
            disableButtonGradient = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #000000, stop: 1 #222222);"
            self.buttonGenImage.setStyleSheet("background: " + disableButtonGradient + "color: white; font: bold 14px;")
            self.buttonGenImage.setText("Loading...")

            if self.w3 is None:
                self.w3 = ImageWindow(os.path.basename(file_path_csv))
                self.w3.showWindowSignal.connect(self.showWindow)
                self.w3.window_closed.connect(self.on_w3_closed)

            def start_generating_wrapper(progress_callback):
                self.w3.startGenerating(progress_callback)

            worker = Worker(start_generating_wrapper)
            worker.signals.result.connect(self.print_output_abstract_image)
            worker.signals.finished.connect(self.on_finised_abstract_image)
            worker.signals.progress.connect(self.progress_fn_abstract_image)

            self.threadpool.start(worker)

    def activate_tab_4(self):
        sys.exit(0)
