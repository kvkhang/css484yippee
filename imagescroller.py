import tkinter as tk
from tkinter import Scrollbar, Canvas, Frame
from PIL import Image, ImageTk  # Pillow for handling image formats
from pathlib import Path
import glob
import random
import os

WIDTH = 384
HEIGHT = 256
rows, cols = 100, 25
intensity_histogram = [[0 for _ in range(cols)] for _ in range(rows)]
color_histogram = [[0 for _ in range(64)] for _ in range(rows)]
current_selected_img = ("", -1)


def randomize(arr):
    random.shuffle(arr)  # Shuffle the array in place
    display_images()


# Function to show the selected image in a larger view
def show_selected_image(tk_image, image_path, n):
    global current_selected_img

    # Open the original image
    img = Image.open(image_path)
    current_selected_img = (image_path, n)

    # Get the original dimensions of the image
    original_width, original_height = img.size

    # Double the size of the image
    new_width = original_width * 2
    new_height = original_height * 2

    # Resize the image while maintaining its original aspect ratio
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to a Tkinter-compatible image
    large_image = ImageTk.PhotoImage(img)

    # Update the displayed image
    selected_image_label.config(image=large_image)
    selected_image_label.image = (
        large_image  # Keep a reference to avoid garbage collection
    )


# Function to display images as buttons
def display_images():
    # Clear all widgets in the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Loop through photo_images to display the images as buttons
    for i, (tk_image, image_path, n) in enumerate(photo_images):
        # Create a frame to hold both the button and the label
        frame = tk.Frame(scrollable_frame)

        # Create the button
        button = tk.Button(
            frame,
            image=tk_image,
            command=lambda img=tk_image, path=image_path, num=n: show_selected_image(
                img, path, num
            ),
        )
        button.pack()

        # Create a label to show the image name (basename)
        image_name = image_path.name  # Get the name of the file
        label = tk.Label(frame, text=image_name)
        label.pack()

        # Arrange the frame in a grid, 10 per row
        frame.grid(row=i // 10, column=i % 10, padx=5, pady=5)


# Function to sort by Intensity
# Function to sort by Intensity (distance calculation)
def sort_by_distance(photo_arr, histogram):
    global current_selected_img  # Access the global variable
    if current_selected_img[1] == -1:
        print("No image selected")
        return  # Exit if no image is selected
    distances = []

    selected_histogram = histogram[
        current_selected_img[1]
    ]  # Selected image's histogram

    for x in range(len(histogram)):
        calculated_distance = 0
        for y in range(len(histogram[x])):
            calculated_distance += abs(
                float((selected_histogram[y] - histogram[x][y]) / (WIDTH * HEIGHT))
            )
        distances.append(calculated_distance)

    # Sorting photo_arr based on the calculated distances
    sorted_photo_arr = [
        photo for _, photo in sorted(zip(distances, photo_arr), key=lambda x: x[0])
    ]

    # Update the global photo_images with the sorted array
    photo_images[:] = sorted_photo_arr  # Update in place

    # Display images in sorted order
    display_images()

    photo_images[:] = sorted(photo_arr, key=lambda x: x[2])


# Create the main window
window = tk.Tk()
window.title("100 Images Viewer")

# Set window size and background color for a cleaner UI
window.geometry("800x600")
window.configure(bg="#f0f0f0")

# Create a frame for the selected image and buttons, aligned on the right
top_frame = tk.Frame(window, bg="#e6e6e6", borderwidth=2, relief="solid")
top_frame.pack(side="right", fill="y", padx=10, pady=10)  # Fill vertically

# Create a label to display the selected image with padding
selected_image_label = tk.Label(
    top_frame, text="No Image Selected", bg="white", borderwidth=2, relief="solid"
)
selected_image_label.pack(
    side="top", padx=10, pady=10, fill="both", expand=True
)  # Fill the space on the top

# Create a frame for buttons below the image display
button_frame = tk.Frame(top_frame, bg="#e6e6e6")
button_frame.pack(side="bottom", fill="both", expand=True)

# Sort by Intensity button
intensity_button = tk.Button(
    button_frame,
    text="Sort by Intensity",
    width=20,
    height=2,
    bg="#d3d3d3",  # Light gray for neutral actions
    fg="#000000",  # Black text for clarity
    command=lambda: sort_by_distance(photo_images, intensity_histogram),
)
intensity_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

# Sort by Color Code button
colorcode_button = tk.Button(
    button_frame,
    text="Sort by Color Code",
    width=20,
    height=2,
    bg="#87ceeb",  # Light blue to differentiate this button
    fg="#000000",
    command=lambda: sort_by_distance(photo_images, color_histogram),
)
colorcode_button.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Configure grid weights for responsive buttons
button_frame.grid_rowconfigure(0, weight=1)  # Ensure the rows can expand
button_frame.grid_rowconfigure(1, weight=1)
button_frame.grid_columnconfigure(0, weight=1)

# Create a scrollable canvas for image thumbnails on the left
canvas = Canvas(window, bg="#ffffff")
scrollbar = Scrollbar(window, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#f9f9f9")

# Add scrollable functionality
scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Add the scrollable frame to the canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar in the main window
canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scrollbar.pack(side="right", fill="y")

# Variables to keep track of drag position
start_x = 0
start_y = 0


# Functions to enable scrolling by dragging the mouse
def on_drag_start(event):
    global start_x, start_y
    start_x = event.x
    start_y = event.y


def on_drag_motion(event):
    # Calculate the difference in movement
    delta_x = start_x - event.x
    delta_y = start_y - event.y
    canvas.xview_scroll(int(delta_x), "units")  # Scroll horizontally
    canvas.yview_scroll(int(delta_y), "units")  # Scroll vertically


# Bind mouse events to the canvas for dragging
canvas.bind("<ButtonPress-1>", on_drag_start)
canvas.bind("<B1-Motion>", on_drag_motion)


folder_name = "images"  # Replace with your folder name

# Create a Path object
current_directory = Path.cwd()
folder_path = current_directory / folder_name

image_folder = folder_path

# Use a wildcard to match .jpg images
image_paths = list(image_folder.glob("*.jpg"))

# Limit to 100 images if there are more
image_paths = image_paths[:100]

# Keep a reference to the PhotoImage objects to avoid garbage collection
photo_images = []

# Define the maximum dimensions for the grid cells
max_width, max_height = 90, 90

# Define the target dimensions for the grid cells (150x150)
target_size = 90
counter = 0
for image_path in image_paths:
    img = Image.open(image_path)  # Open the image file
    # Image Processing
    width, height = img.size
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            rgbvals = pixels[x, y]
            intensity = (int)(
                rgbvals[0] * 0.299 + rgbvals[1] * 0.587 + rgbvals[2] * 0.114
            )
            histobin = (int)(intensity / 10)
            if histobin == 25:
                histobin -= 1
            intensity_histogram[counter][histobin] += 1
            colorcode = 0
            if rgbvals[0] >= 192:
                colorcode += 48
            elif rgbvals[0] >= 128:
                colorcode += 32
            elif rgbvals[0] >= 64:
                colorcode += 16
            if rgbvals[1] >= 192:
                colorcode += 12
            elif rgbvals[1] >= 128:
                colorcode += 8
            elif rgbvals[1] >= 64:
                colorcode += 4
            if rgbvals[2] >= 192:
                colorcode += 3
            elif rgbvals[2] >= 128:
                colorcode += 2
            elif rgbvals[2] >= 64:
                colorcode += 1
            color_histogram[counter][colorcode] += 1

    # Get the original dimensions of the image
    width, height = img.size

    # Determine the dimensions to crop a square
    if width > height:
        # Crop width to make it a square
        left = (width - height) // 2
        right = left + height
        top, bottom = 0, height
    else:
        # Crop height to make it a square
        top = (height - width) // 2
        bottom = top + width
        left, right = 0, width

    # Crop the image to a square
    img = img.crop((left, top, right, bottom))

    # Resize the square image to fit the grid cell
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    tk_image = ImageTk.PhotoImage(img)  # Convert image to PhotoImage
    photo_images.append(
        (tk_image, image_path, counter)
    )  # Keep a reference and the file path
    counter += 1

# Display images initially
photo_images.sort(key=lambda x: x[2])
display_images()
# Start the Tkinter event loop
window.mainloop()
