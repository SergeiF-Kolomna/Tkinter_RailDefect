import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import TK_normalization_image as tni
from tkinter import ttk


class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")

        self.f_top = tk.Frame(root)
        self.f_bottom = tk.LabelFrame(root, text='settings')

        self.f_top.pack()
        self.f_bottom.pack()

        # Variables
        self.image_path = None
        self.selection_coordinates = None
        self.dark_spots_coordinates = None

        # Interface
        self.load_button = tk.Button(self.f_top, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10, side = "left")
        #self.load_button.pack(pady=10, anchor="nw")

        # Insert TrackBars
        self.horizontalScaleH = ttk.Scale(self.f_top, orient=tk.HORIZONTAL, length=200, from_=0.0, to=100.0, value=30)
        self.horizontalScaleH.pack(pady=10, padx=10, side = "top")
        self.horizontalScaleS = ttk.Scale(self.f_top, orient=tk.HORIZONTAL, length=200, from_=0.0, to=100.0, value=30)
        self.horizontalScaleS.pack(pady=10, padx=10, side = "top")
        self.horizontalScaleV = ttk.Scale(self.f_top, orient=tk.HORIZONTAL, length=200, from_=0.0, to=100.0, value=30)
        self.horizontalScaleV.pack(pady=10, padx=10, side = "top")

        self.main_canvas = tk.Canvas(self.f_top)
        self.main_canvas.pack(expand=tk.YES, fill=tk.BOTH, side = "right")
        self.main_canvas.bind("<ButtonPress-1>", self.on_press)
        self.main_canvas.bind("<B1-Motion>", self.on_drag)
        self.main_canvas.bind("<ButtonRelease-1>", self.on_release)

        self.selection_label = tk.Label(root, text="Selection image:")
        self.selection_label.pack()

        self.selection_display = tk.Label(root, text="")
        self.selection_display.pack()

        self.selected_canvas = tk.Canvas(root, width=100, height=100)  # Needed size
        self.selected_canvas.pack()

        self.find_dark_spots_button = tk.Button(root, text="Find Dark Spots", command=self.find_dark_spots)
        self.find_dark_spots_button.pack(pady=10, side = "left")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            self.image_path = file_path
            self.display_image()

    def display_image(self):
        #global mini_image
        image = Image.open(self.image_path)
        self.mini_image = tni.main_resize(image, 700)
        self.image_tk = ImageTk.PhotoImage(self.mini_image)
        self.main_canvas.config(width=self.image_tk.width(), height=self.image_tk.height())
        self.main_canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)

    def on_press(self, event):
        self.start_x = self.main_canvas.canvasx(event.x)
        self.start_y = self.main_canvas.canvasy(event.y)

    def on_drag(self, event):
        cur_x = self.main_canvas.canvasx(event.x)
        cur_y = self.main_canvas.canvasy(event.y)
        self.main_canvas.delete("selection_rectangle")
        self.main_canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline="red", tags="selection_rectangle")

    def on_release(self, event):
        end_x = self.main_canvas.canvasx(event.x)
        end_y = self.main_canvas.canvasy(event.y)
        self.selection_coordinates = (self.start_x, self.start_y, end_x, end_y)
        self.display_selection()

    def display_selection(self):

        if self.selection_coordinates:
            self.selection_display.config(text=f"Selection Coordinates: {self.selection_coordinates}")

            # Extract the selected region from the original image
            selected_image = self.mini_image.crop(self.selection_coordinates)
            selected_image_tk = ImageTk.PhotoImage(selected_image)

            # Display the selected region in the second canvas
            self.selected_canvas.config(width=selected_image_tk.width(), height=selected_image_tk.height())
            self.selected_canvas.create_image(0, 0, anchor=tk.NW, image=selected_image_tk)
            self.selected_canvas.image = selected_image_tk  # Keep a reference to avoid garbage collection issues

    def find_dark_spots(self):
        if self.image_path and self.selection_coordinates:
            # Read the whole image
            full_image = cv2.imread(self.image_path)

            # Convert the selected region to monochrome
            selected_region = full_image[int(self.selection_coordinates[1]):int(self.selection_coordinates[3]),
                             int(self.selection_coordinates[0]):int(self.selection_coordinates[2])]
            gray_selected_region = cv2.cvtColor(selected_region, cv2.COLOR_BGR2GRAY)

            # Apply threshold to finded dark spots
            _, thresholded = cv2.threshold(gray_selected_region, 50, 255, cv2.THRESH_BINARY_INV)

            # Find contours of dark spots
            contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Extract coordinates of dark spots
            dark_spots_coordinates = [cv2.boundingRect(contour) for contour in contours]

            # Update the attribute and display it
            self.dark_spots_coordinates = dark_spots_coordinates
            self.display_dark_spots()

    def display_dark_spots(self):
        if self.dark_spots_coordinates:
            # Draw red rectangles around dark spots in the selected region
            for (x, y, w, h) in self.dark_spots_coordinates:
                x += self.selection_coordinates[0]  # Adjust x-coordinate based on the selection
                y += self.selection_coordinates[1]  # Adjust y-coordinate based on the selection
                self.main_canvas.create_rectangle(x, y, x + w, y + h, outline="red", width=4)

            print("Dark Spots Coordinates:", self.dark_spots_coordinates)

    def onScale(self, val):
        v = int(float(val))
        self.var.set(v)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
