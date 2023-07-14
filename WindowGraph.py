from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QGridLayout, QWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from PIL import Image

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class WindowGraph(QMainWindow):
    def __init__(self, fileName):
        super().__init__()
        self.resize(1250, 700)
        self.fileName = fileName
        self.setWindowTitle('Plots of magnitude')

        self.plot_time_magnitude = PlotWidget()
        self.plot_significance = PlotWidget()
        self.plot_location = PlotWidget()

        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(self.plot_time_magnitude, 0, 0)  # Add first widget at location (0,0)
        central_layout.addWidget(self.plot_significance, 0, 1)  # Add second widget at location (0,1)
        central_layout.addWidget(self.plot_location, 1, 0)  # Add second widget at location (0,1)
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)

        self.plot_magnitude_data()
        self.plot_magnitude_significance()
        self.plot_location_data()
        self.show()

    def plot_magnitude_significance(self):
        # Read CSV file using pandas
        df = pd.read_csv(self.fileName)

        self.plot_significance.ax.set_title("Average magnitude based on significance")
        self.plot_significance.ax.scatter(df["impact.magnitude"], df['impact.significance'])
        self.plot_significance.ax.set_xlabel('Magnitude')
        self.plot_significance.ax.set_ylabel('Significance')
        self.plot_significance.ax.grid(True)
        self.plot_significance.figure.tight_layout()
        self.plot_significance.canvas.draw()  # Draw the plot


    def plot_magnitude_data(self):
        # Read CSV file using pandas
        df = pd.read_csv(self.fileName, parse_dates=['time.full'])

        # Calculate time in different units
        seconds = df['time.full'].dt.second
        minutes = df['time.full'].dt.minute
        hours = df['time.full'].dt.hour
        days = df['time.full'].dt.dayofyear
        years = df['time.full'].dt.year

        # Convert time to a decimal representation for easy plotting
        time_values = seconds / 60.0 + minutes / 60.0 + hours + days * 24

        self.plot_time_magnitude.ax.set_title("Average magnitude based on time")
        self.plot_time_magnitude.ax.semilogy(time_values, df['impact.magnitude'])
        self.plot_time_magnitude.ax.set_xlabel('Time')
        self.plot_time_magnitude.ax.set_ylabel('Magnitude')
        self.plot_time_magnitude.ax.grid(True)
        self.plot_time_magnitude.figure.tight_layout()
        self.plot_time_magnitude.canvas.draw()  # Draw the plot

    def plot_location_data(self):
        # Read CSV file using pandas
        df = pd.read_csv(self.fileName)
        img = Image.open("resources/harta_fiz.jpg")
        self.plot_location.ax.imshow(img, extent=[-180, 180, -90, 90])
        # Plot latitude and longitude as a scatter plot
        self.plot_location.ax.scatter(df["location.longitude"], df["location.latitude"])
        self.plot_location.ax.set_title("Scatter plot of Locations")
        self.plot_location.ax.set_xlabel('Longitude')
        self.plot_location.ax.set_ylabel('Latitude')
        self.plot_location.ax.grid(True)
        self.plot_location.figure.tight_layout()
        self.plot_location.canvas.draw()
