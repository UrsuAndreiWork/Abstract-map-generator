from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
import torch
from PIL import Image
from diffusers import DiffusionPipeline
import secrets
import string
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import platform
import time
import random

from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from scipy.integrate import simps

class ImageWindow(QMainWindow):
    window_closed = pyqtSignal()
    showWindowSignal = pyqtSignal()
    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)

    def open_folder(self):
        folder_path = os.path.join("resources", "abstract image")

        if platform.system() == 'Windows':
            os.startfile(folder_path)
        elif platform.system() == 'Linux':
            os.system(f'xdg-open "{folder_path}"')
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open "{folder_path}"')
        else:
            print("Unsupported operating system")


    def displayWindow(self):
        image1_path = os.path.join("resources", "abstract image", "plot_{}.jpg".format(self.UUID))
        image2_path = os.path.join("resources", "abstract image",
                                   "Generated_image_of_{}_{}.png".format(self.CSV_Path, self.UUID))
        image1 = QPixmap(image1_path)
        image2 = QPixmap(image2_path)

        # Create QLabel objects and set the loaded images as their pixmap
        label1 = QLabel()
        label1.setPixmap(image1)

        label2 = QLabel()
        label2.setPixmap(image2)

        # Create QLabel for the emotion and set it as a child of label1
        #emotion_label = QLabel("Emotion: "+self.get_emotion(), label1)
        #emotion_label.setStyleSheet(
        #    "QLabel {font: bold 24px; color: white; background-color: rgba(0, 0, 0, 0.6); padding: 2px;}")
        #emotion_label.move(10, 10)  # Adjust position as needed

        code_label = QLabel("The code of the image: " + self.UUID)

        label_width = code_label.fontMetrics().boundingRect("The code of the image: " + self.UUID).width() + 200
        label_height = code_label.fontMetrics().boundingRect("The code of the image: " + self.UUID).height() + 20
        code_label.setFixedSize(label_width, label_height)

        code_label.setStyleSheet(
            "QLabel {font: bold 24px; color: black; border: 1px solid black; padding: 2px; background-color:white;}")

        # Create the button
        button = QPushButton("Open in directory")
        buttonGradient = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #555555, stop: 1 #222222);"

        button_width = button.fontMetrics().boundingRect("Open in directory").width() + 140
        button_height = button.fontMetrics().boundingRect("Open in directory").height() + 20
        button.setFixedSize(button_width, button_height)
        button.clicked.connect(self.open_folder)

        button.setStyleSheet("background: " + buttonGradient + "; color: white; font: bold 24px;")

        # Create QHBoxLayouts for QLabel/Button
        hbox1 = QHBoxLayout()
        hbox1.addWidget(code_label)
        hbox1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(button)
        hbox2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create QVBoxLayouts for QLabel/Button pairs
        left_layout = QVBoxLayout()
        left_layout.addWidget(label1)
        left_layout.addLayout(hbox1)  # Add hbox1 to left_layout
        left_layout.addStretch()

        right_layout = QVBoxLayout()
        right_layout.addWidget(label2)
        right_layout.addLayout(hbox2)  # Add hbox2 to right_layout
        right_layout.addStretch()

        # Create a QHBoxLayout to arrange QVBoxLayouts side by side
        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        # Set the layout to the central widget of the main window
        central_widget = QWidget()
        backgroundGradient = "qlineargradient(spread:pad, x1:0, y1:0, x2:0.891, y2:0.454, stop:0.23 rgba(19, 131, 103, 255), stop:0.87 rgba(29, 102, 147, 255), stop:0.95 rgba(45, 136, 163, 255), stop:1 rgba(20, 140, 127, 255));"
        central_widget.setStyleSheet("background: " + backgroundGradient + ";")

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Abstract Image")
        self.show()


    def startGenerating(self, progress_callback):
        progress_callback.emit(100 / 4)
        self.createPlot()
        self.generateAbstractImage()
        self.showWindowSignal.emit()

    def __init__(self,CSV_Path):
        super().__init__()
        self.CSV_Path=CSV_Path
        self.UUID=self.generate_five_char_uuid()

    def getUUID(self):
        return self.UUID
    def getCSVname(self):
        return self.nameCSVfile_no_ext

    def resizePicture(self,directory, filename):
        image = Image.open(os.path.join(directory, filename))
        new_image = image.resize((512, 512))
        new_image.save(directory+"\\"+filename)

    def generate_five_char_uuid(self):
        alphanumeric_chars = string.ascii_letters + string.digits
        random_uuid = ''.join(secrets.choice(alphanumeric_chars) for _ in range(5))
        return random_uuid

    def get_random_word(self):
        words = ['wet map','pirate map','golden map','lava map','cursed map','holy map','candy map','cotton map','old map']
        random.seed(time.time())  # use current time as random seed
        return random.choice(words)


    def generateAbstractImage(self):
        self.resizePicture("resources\\abstract image","plot"+"_"+self.UUID+".jpg")
        # Load the input image and mask using PIL

        inp_img_path = os.path.join("resources", "abstract image", "plot_" + self.UUID + ".jpg")
        mask_path = os.path.join("resources", "abstract image", "plot_" + self.UUID + ".jpg")

        inp_img = Image.open(inp_img_path)
        mask = Image.open(mask_path)

        # Convert the input image to RGBA
        inner_image = inp_img.convert("RGBA")

        # Initialize the pretrained diffusion pipeline
        pipe = DiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting",
            custom_pipeline="img2img_inpainting",
            torch_dtype=torch.float16
        )

        # Move the pipeline to GPU
        pipe = pipe.to("cuda")

        # Enable attention slicing to save GPU memory
        pipe.enable_attention_slicing()

        # Set prompts for the pipeline

        the_word=self.get_random_word()
        print(the_word)


        prompt = the_word
        negative_prompt = "human"

        # Run the pipeline with the given prompts and input images
        result = pipe(
            prompt=prompt,
            image=inp_img,
            inner_image=inner_image,
            mask_image=mask,
            negative_prompt=negative_prompt,
            num_inference_steps=25,
            guidance_scale=10
        ).images

        output_filename = os.path.join("resources", "abstract image", "Generated_image_of_" + self.CSV_Path +"_"+self.UUID+".png")
        result[0].save(output_filename)
    def createPlot(self):
        df = pd.read_csv("resources\\" + "Csv_data" + "\\" + self.CSV_Path)

        # Create a figure and a set of subplots
        fig, ax = plt.subplots(figsize=(10, 6))

        # Set the background color to light blue
        ax.set_facecolor('lightblue')

        # Load the image
        img = Image.open("resources" + "\\" + "harta_fiz.jpg")

        # Get the extent of your data
        x_min, x_max = df["location.longitude"].min(), df["location.longitude"].max()
        y_min, y_max = df["location.latitude"].min(), df["location.latitude"].max()

        # Add image to the plot as background
        ax.imshow(img, extent=[x_min, x_max, y_min, y_max])

        # Scatter plot
        ax.scatter(df["location.longitude"], df["location.latitude"], zorder=1)

        # Remove xlabel, ylabel, and title
        ax.set_xticks([])  # Remove x-axis ticks
        ax.set_yticks([])  # Remove y-axis ticks

        # Remove the black border
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Adjust padding and margins
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        fig.savefig('resources\\abstract image\\plot' + '_' + self.UUID + '.jpg', format='jpg', dpi=300,
                    facecolor='lightblue')

        plt.close()