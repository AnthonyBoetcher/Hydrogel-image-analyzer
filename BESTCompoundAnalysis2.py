import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, filedialog, messagebox, Canvas, Frame, Scrollbar, Button, Label
import os

def select_images():
    file_paths = filedialog.askopenfilenames(
        title="Select Image Files",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
    )
    if not file_paths:
        messagebox.showinfo("No Selection", "No images selected.")
        return
    process_images(file_paths)

def select_folder():
    folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
    if not folder_path:
        messagebox.showinfo("No Selection", "No folder selected.")
        return
    
    file_paths = [
        os.path.join(folder_path, f) 
        for f in sorted(os.listdir(folder_path)) 
        if f.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'))
    ]
    if not file_paths:
        messagebox.showinfo("Empty Folder", "No image files found in the selected folder.")
        return
    process_images(file_paths)

def isolate_hydrogel(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No contours found.")
        return None, None
    
    largest_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
    isolated = cv2.bitwise_and(image, image, mask=mask)
    
    area = cv2.contourArea(largest_contour)
    perimeter = cv2.arcLength(largest_contour, True)
    return isolated, mask, area, perimeter

def calculate_radial_rgb_profile(isolated_rgb, mask, num_rings=10):
    h, w, _ = isolated_rgb.shape
    center = (int(w / 2), int(h / 2))
    radius = min(center) // 2

    radial_rgb_profile = {'Red': [], 'Green': [], 'Blue': []}
    for r in range(num_rings):
        ring_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(ring_mask, center, int(radius * (r + 1) / num_rings), 255, thickness=-1)
        cv2.circle(ring_mask, center, int(radius * r / num_rings), 0, thickness=-1)

        ring_mask = cv2.bitwise_and(ring_mask, mask)
        ring_red = np.mean(isolated_rgb[:, :, 0][ring_mask == 255])
        ring_green = np.mean(isolated_rgb[:, :, 1][ring_mask == 255])
        ring_blue = np.mean(isolated_rgb[:, :, 2][ring_mask == 255])

        radial_rgb_profile['Red'].append(ring_red)
        radial_rgb_profile['Green'].append(ring_green)
        radial_rgb_profile['Blue'].append(ring_blue)
    
    return radial_rgb_profile

def save_figures(fig):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    fig.savefig(os.path.join(downloads_folder, "hydrogel_analysis_results.png"), bbox_inches='tight')
    messagebox.showinfo("Saved", f"Results saved to {downloads_folder}/hydrogel_analysis_results.png")

def process_images(file_paths):
    avg_red, avg_green, avg_blue = [], [], []
    red_stddev, green_stddev, blue_stddev = [], [], []
    avg_hue, avg_saturation, avg_value = [], [], []
    edge_sharpness_values = []
    radial_profiles = {'Red': [], 'Green': [], 'Blue': []}
    areas, perimeters = [], []
    timepoints = []

    for idx, file_path in enumerate(file_paths, 1):
        image = cv2.imread(file_path)
        if image is None:
            print(f"Failed to load image {file_path}. Skipping.")
            continue

        isolated, mask, area, perimeter = isolate_hydrogel(image)
        if isolated is None:
            print(f"Failed to isolate hydrogel in image {file_path}. Skipping.")
            continue

        isolated_rgb = cv2.cvtColor(isolated, cv2.COLOR_BGR2RGB)
        mean_red = np.mean(isolated_rgb[:, :, 0][mask == 255])
        mean_green = np.mean(isolated_rgb[:, :, 1][mask == 255])
        mean_blue = np.mean(isolated_rgb[:, :, 2][mask == 255])

        # RGB standard deviation within hydrogel
        std_red = np.std(isolated_rgb[:, :, 0][mask == 255])
        std_green = np.std(isolated_rgb[:, :, 1][mask == 255])
        std_blue = np.std(isolated_rgb[:, :, 2][mask == 255])

        # HSV analysis
        isolated_hsv = cv2.cvtColor(isolated, cv2.COLOR_BGR2HSV)
        mean_hue = np.mean(isolated_hsv[:, :, 0][mask == 255])
        mean_saturation = np.mean(isolated_hsv[:, :, 1][mask == 255])
        mean_value = np.mean(isolated_hsv[:, :, 2][mask == 255])

        # Edge sharpness (using Sobel for edge strength)
        edges = cv2.Sobel(mask, cv2.CV_64F, 1, 1, ksize=5)
        edge_sharpness = np.mean(np.abs(edges))

        # Radial RGB Profile
        radial_rgb_profile = calculate_radial_rgb_profile(isolated_rgb, mask, num_rings=10)
        radial_profiles['Red'].append(radial_rgb_profile['Red'])
        radial_profiles['Green'].append(radial_rgb_profile['Green'])
        radial_profiles['Blue'].append(radial_rgb_profile['Blue'])

        avg_red.append(mean_red)
        avg_green.append(mean_green)
        avg_blue.append(mean_blue)
        red_stddev.append(std_red)
        green_stddev.append(std_green)
        blue_stddev.append(std_blue)
        avg_hue.append(mean_hue)
        avg_saturation.append(mean_saturation)
        avg_value.append(mean_value)
        edge_sharpness_values.append(edge_sharpness)
        areas.append(area)
        perimeters.append(perimeter)
        timepoints.append(idx)

    # Create a scrollable window to display the plots
    result_window = Tk()
    result_window.title("Hydrogel Analysis Results")
    result_window.geometry("800x600")

    canvas = Canvas(result_window)
    scroll_y = Scrollbar(result_window, orient="vertical", command=canvas.yview)
    scroll_x = Scrollbar(result_window, orient="horizontal", command=canvas.xview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    # Generate plots
    fig, axs = plt.subplots(5, 2, figsize=(12, 16), constrained_layout=True)
    plt.rcParams.update({'font.size': 8})

    # RGB Channels Over Time
    axs[0, 0].plot(timepoints, avg_red, 'r-', label='Red')
    axs[0, 0].plot(timepoints, avg_green, 'g-', label='Green')
    axs[0, 0].plot(timepoints, avg_blue, 'b-', label='Blue')
    axs[0, 0].set_title("RGB Channels Over Time")
    axs[0, 0].legend()
    axs[0, 0].grid()

    # HSV Channels Over Time
    axs[0, 1].plot(timepoints, avg_hue, 'm-', label='Hue')
    axs[0, 1].plot(timepoints, avg_saturation, 'c-', label='Saturation')
    axs[0, 1].plot(timepoints, avg_value, 'y-', label='Value')
    axs[0, 1].set_title("HSV Channels Over Time")
    axs[0, 1].legend()
    axs[0, 1].grid()

    # RGB Variance Over Time
    axs[1, 0].plot(timepoints, red_stddev, 'r--', label='Red StdDev')
    axs[1, 0].plot(timepoints, green_stddev, 'g--', label='Green StdDev')
    axs[1, 0].plot(timepoints, blue_stddev, 'b--', label='Blue StdDev')
    axs[1, 0].set_title("RGB Variance Over Time")
    axs[1, 0].legend()
    axs[1, 0].grid()

    # Contour Area Over Time
    axs[1, 1].plot(timepoints, areas, 'b-', label='Area')
    axs[1, 1].set_title("Contour Area Over Time")
    axs[1, 1].grid()

    # Edge Sharpness Over Time
    axs[2, 0].plot(timepoints, edge_sharpness_values, 'm-', label='Edge Sharpness')
    axs[2, 0].set_title("Edge Sharpness Over Time")
    axs[2, 0].grid()

    # Radial RGB Profile
    for i in range(10):
        axs[2, 1].plot(timepoints, [radial_profiles['Red'][j][i] for j in range(len(timepoints))],
                       color=(1 - i / 10, 0, 0), label=f'Ring {i + 1}')
    axs[2, 1].set_title("Radial Red Profile Over Time")
    axs[2, 1].grid()

    # Contour Perimeter Over Time
    axs[3, 0].plot(timepoints, perimeters, 'g-', label='Perimeter')
    axs[3, 0].set_title("Contour Perimeter Over Time")
    axs[3, 0].grid()

    # RGB Mean Values Over Time
    axs[3, 1].plot(timepoints, avg_red, 'r-', label='Mean Red')
    axs[3, 1].plot(timepoints, avg_green, 'g-', label='Mean Green')
    axs[3, 1].plot(timepoints, avg_blue, 'b-', label='Mean Blue')
    axs[3, 1].set_title("Mean RGB Values Over Time")
    axs[3, 1].legend()
    axs[3, 1].grid()

    # Save button
    save_button = Button(scrollable_frame, text="Save Results as PNG", command=lambda: save_figures(fig))
    save_button.pack(pady=10)

    # Display all plots
    fig_canvas = FigureCanvasTkAgg(fig, scrollable_frame)
    fig_canvas.get_tk_widget().pack(fill="both", expand=True)

    # Pack the scrollbars and canvas
    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")

    result_window.mainloop()

# Tkinter UI setup
root = Tk()
root.title("Hydrogel Swelling Analysis Tool (HSAT)")
root.geometry("400x200")

label = Label(root, text="Select images or a folder to analyze color and contour changes over time.", wraplength=300)
label.pack(pady=20)

button_images = Button(root, text="Select Images", command=select_images)
button_images.pack(pady=10)

root.mainloop()
