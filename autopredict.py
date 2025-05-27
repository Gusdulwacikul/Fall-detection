import socket
import time
import csv
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

UDP_IP = "192.168.43.85"  # Listen on all available interfaces
UDP_PORT = 8888
BUFFER_SIZE = 64

# UDP socket setup with no receive buffer
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)  # Disable receive buffer
sock.bind((UDP_IP, UDP_PORT))

# Variables for saving data points to CSV file
data_list = []
DATA_LIMIT = 500  # Number of data points to collect before saving

# Load the trained model
model_path = 'ModelCNN.keras'  # Replace with your actual model path
if not os.path.exists(model_path):
    print(f"Error: Model file '{model_path}' not found.")
    exit()
model = load_model(model_path)

# Function to preprocess an image
def preprocess_image(img_path, target_size=(503, 250)):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize pixel values
    return img, img_array

while True:
    data_counter = 0
    
    # Collect data
    while data_counter < DATA_LIMIT:
        data, addr = sock.recvfrom(BUFFER_SIZE)  # Receive data
        data_str = data.decode('utf-8')  # Decode received bytes to string
        x_str, y_str, z_str = data_str.split(',')  # Assuming data is comma-separated
        x = float(x_str)
        y = float(y_str)
        z = float(z_str)
        
        resultant_vector = np.sqrt(x**2 + y**2 + z**2)
        resultant_vector = round(resultant_vector, 2)  # Round to 2 decimal places
        print(f"Resultant vector magnitude: {resultant_vector}")
        # Append resultant vector to the list
        data_list.append([resultant_vector])
        
        # Increment data counter
        data_counter += 1
        
        # Delay to match Arduino data transmission rate
        time.sleep(0.001)  # Adjust if necessary to match Arduino's actual transmission rate
    
    # Save data to CSV file
    csv_filename = "resultant_vector.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)
    
    print(f"Saved data as {csv_filename}")
    
    # Read the CSV file
    data = pd.read_csv(csv_filename, header=None)
    accel_data = data.iloc[:, 0].values  # Assuming the data is in the first column
    
    # Parameters for spectrogram
    sampling_freq = 100  # Sampling frequency in Hz
    nperseg = 30  # Increase nperseg for zero-padding
    noverlap = 25  # Adjust overlap as needed
    
    # Compute spectrogram
    frequencies, times, Sxx = spectrogram(accel_data, fs=sampling_freq, window='hann', nperseg=nperseg, noverlap=noverlap)
    
    # Plot spectrogram without axis labels and ticks
    plt.figure(figsize=(5, 2.5))
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), cmap='jet', vmin=-80, vmax=-20)
    plt.axis('off')  # Turn off both x and y axis ticks and labels
    
    # Save the plot with tight bounding box and no padding
    spectrogram_filename = "spectrogram.png"
    plt.savefig(spectrogram_filename, dpi=130, bbox_inches='tight', pad_inches=0)
    plt.close()  # Close the plot to free memory
    
    print(f"Saved spectrogram as {spectrogram_filename}")
    
    # Preprocess the spectrogram image for prediction
    img, img_array = preprocess_image(spectrogram_filename)

    # Make predictions
    predictions = model.predict(img_array)

    # Map predicted class index to class name
    class_names = ['berjalan', 'diam', 'jatuh']  # Replace with your actual class names
    predicted_class_idx = np.argmax(predictions)
    predicted_class_name = class_names[predicted_class_idx]
    predicted_probability = np.max(predictions)

    # Plot the image with predicted class and probability
    plt.figure(figsize=(8, 5))
    plt.imshow(img, aspect='auto')
    plt.axis('off')
    plt.title(f'Predicted class: {predicted_class_name}\nProbability: {predicted_probability:.4f}', fontsize=14)
    plt.show()

    # Clear data list for the next batch
    data_list = []
