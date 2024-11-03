This Python application analyzes color changes in hydrogel images over time using various image processing techniques. It allows users to select images or a folder containing images and visualizes the results in multiple plots.

Requirements
To run this application, ensure you have the following installed:

Python 3.x
Required libraries:
OpenCV (opencv-python)
NumPy (numpy)
Matplotlib (matplotlib)
Tkinter (usually included with Python installations)
You can install the required libraries using pip:

bash
Copy code
pip install opencv-python numpy matplotlib
Usage Instructions
Run the Application: Execute the script. You can do this from a command line or terminal:

bash
Copy code
python hydrogel_analysis.py
Select Images or Folder:

Click the "Select Images" button to choose one or more image files (supported formats: JPG, JPEG, PNG, BMP, TIF, TIFF).
Alternatively, click the "Select Folder" button to choose a folder containing images. The program will process all supported image files in that folder.
Image Processing:

The application will analyze the selected images, isolating hydrogel regions and calculating color metrics (RGB and HSV) and edge sharpness.
Results Display:

After processing, a new window will appear displaying the analysis results in various plots:
RGB Channels Over Time
HSV Channels Over Time
RGB Variance Over Time
Contour Area Over Time
Edge Sharpness Over Time
Radial RGB Profile Over Time
Contour Perimeter Over Time
Mean RGB Values Over Time
Save Results: You can save the generated plots by clicking the "Save Results as PNG" button. The results will be saved in the Downloads folder.

Close the Application: Once you have finished viewing or saving results, you can close the results window to exit the application.

Notes
Ensure that images contain visible hydrogel regions for meaningful analysis.
The application uses Gaussian blur and contour detection methods, which may vary in effectiveness based on image quality and content.
