import socket
import time
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

UDP_IP = "192.168.100.6"  # kamu isi sesuai IP yang ada di program arduino
UDP_PORT = 8888            # kamu isi sesuai port yang ada di program arduino
BUFFER_SIZE = 64

# UDP socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 0)  # Disable receive buffer
sock.bind((UDP_IP, UDP_PORT))

# Variables for saving 500 data points per CSV file
DATA_LIMIT = 500  # Number of data points to collect before saving
data_list = []
file_counter = 1  # Initialize file counter

while True:
    data_counter = 0
    
    # Collect 500 data points
    while data_counter < DATA_LIMIT:
        data, addr = sock.recvfrom(BUFFER_SIZE)  # Receive data
        data_str = data.decode('utf-8')  # Decode received bytes to string
        x_str, y_str, z_str = data_str.split(',')  # Assuming data is comma-separated
        x = float(x_str)
        y = float(y_str)
        z = float(z_str)
        
        resultant_vector = np.sqrt(x**2 + y**2 + z**2)  # Keep the values in G
        resultant_vector = round(resultant_vector, 2)  # Round to 2 decimal places
        print(f"Resultant vector magnitude: {resultant_vector} G")
        # Append resultant vector to the list
        data_list.append([resultant_vector])
        
        # Increment data counter
        data_counter += 1
        
        # Delay to match Arduino data transmission rate
        time.sleep(0.001)  # Adjust if necessary to match Arduino's actual transmission rate
    
    # Save data to CSV file after collecting 500 data points
    csv_filename = f"resultant_vector_{file_counter}.csv"
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
    
    # Create a time array for the x-axis of the resultant vector plot
    time_array = np.linspace(1, 5, DATA_LIMIT)
    
    # Plot spectrogram
    plt.figure(figsize=(5, 2.5))
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), cmap='jet', vmin=-80, vmax=-20)
    plt.axis('off')  # Turn off both x and y axis ticks and labels
    spectrogram_filename = f"spectrogram{file_counter}.png"
    plt.savefig(spectrogram_filename, dpi=130, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    print(f"Saved spectrogram as {spectrogram_filename}")
    
    # Clear data list for the next batch
    data_list = []
    
    # Increment file counter for the next file
    file_counter += 1
