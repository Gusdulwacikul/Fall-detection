import os
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Directory and dataset parameters
base_dir = 'C:/CNN/dataset'  # Adjust this according to your dataset location
train_dir = os.path.join(base_dir, 'train')

# Data generator with augmentation and preprocessing for training
train_datagen = ImageDataGenerator(
    rescale=1./255,          # Rescale pixel values to [0, 1]
    shear_range=0.2,         # Shear augmentation
    zoom_range=0.2,          # Zoom augmentation
    horizontal_flip=True    # Horizontal flip augmentation
)

# Flow training images in batches using train_datagen generator
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(503, 250),  # Resize images to (503, 250)
    batch_size=32,           # Batch size
    class_mode='categorical' # Class mode for multi-class classification
)

# Define the model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(503, 250, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(3, activation='softmax')  # Output layer for 3 classes
])

# Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Print model summary
model.summary()

# Train the model
print("Training started...")
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // 32,  # Number of batches per epoch
    epochs=20,               # Number of epochs
    verbose=1                # Print progress during training
)

print("Training completed.")

# Save the trained model
model.save('ModelCNN.keras')
print("Model saved successfully.")