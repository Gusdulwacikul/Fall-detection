import csv
import socket
import time
import numpy as np
from scipy.signal import spectrogram
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import os

host = '192.168.43.85'  # Listen on all available interfaces
port = 8888             # UDP port number, should match the port used in the ESP8266 code
data_per_file = 250     # Number of data points per CSV file (2.5 seconds at 100 Hz)
sampling_rate = 100     # Sampling rate (Hz) of accelerometer data

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))

print('UDP server listening on {}:{}'.format(host, port))

file_count = 1  # Counter for the file names

# Initialize data list
data = []

# Infinite loop to continuously receive and process data
while True:
    # Receive data from ESP8266
    received_data, _ = sock.recvfrom(1024)  # Adjust buffer size as necessary
    
    # Process received data (assuming it's in CSV format)
    # You may need to parse the received data according to your ESP8266's output format
    received_data = received_data.decode().strip()  # Convert bytes to string and remove leading/trailing whitespace
    
    # Split the received data into a list of values
    received_values = received_data.split(',')  # Adjust delimiter as necessary

    data.append(received_values)
    # Print the current row to the terminal
    print(data[-1])  # Print the last row added

    # Write data to a CSV file every 'data_per_file' data points
    if len(data) % data_per_file == 0:
        filename = f'UDPESP8266_{file_count}.csv'
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(data)
        
        print('Data saved to', filename)
        
        # Get the most recently saved CSV file
        latest_file = max([f for f in os.listdir() if f.startswith('UDPESP8266_') and f.endswith('.csv')], key=os.path.getctime)

        # Read the latest CSV file
        data_df = pd.read_csv(latest_file, header=None)

        # Assuming the columns are in order: X, Y, Z
        x_data = data_df.iloc[:, 0]  # First column
        y_data = data_df.iloc[:, 1]  # Second column
        z_data = data_df.iloc[:, 2]  # Third column

        # Combine into a single array
        accel_data = np.vstack((x_data, y_data, z_data))
        # Compute time axis
        time_axis = np.arange(0, len(x_data) / sampling_rate, 1 / sampling_rate)
        # Compute frequency axis
        freq_axis = np.fft.fftfreq(len(x_data), 1 / sampling_rate)[:len(x_data) // 2]
        # Perform FFT on each axis
        fft_result = np.fft.fft(accel_data, axis=0)
        # Compute magnitude spectrum
        magnitude = np.abs(fft_result)
        # Plot and save spectrogram image with timestamp in the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.figure(figsize=(10, 5))
        plt.imshow(magnitude, aspect='auto', origin='lower', cmap='jet', extent=[0, len(x_data) / sampling_rate, 0, sampling_rate / 2])
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.title('Spectrogram of Accelerometer Data')
        plt.colorbar(label='Magnitude (dB)')
        plt.savefig(f'UDPESP8266_{file_count}_spectrogram_{timestamp}.png')
        plt.close()
        
        print('Spectrogram image saved')

        # Increment file counter
        file_count += 1

        # Clear data list for the next set of data
        data = []

    time.sleep(0.01)
