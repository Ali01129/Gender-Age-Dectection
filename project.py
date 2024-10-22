# -*- coding: utf-8 -*-
"""project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rqwfBFZxeikEHdJUVtlNMOSguOoGmsCN
"""

!kaggle datasets download -d jangedoo/utkface-new

!unzip -qq "utkface-new"

#import dataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import load_img
from sklearn.model_selection import train_test_split
from tensorflow.keras.initializers import random_uniform, glorot_uniform, constant, identity
from tensorflow.keras.layers import Dropout, Input, Add, Dense, Activation, BatchNormalization, Flatten, Conv2D, MaxPooling2D, GlobalMaxPooling2D
from tensorflow.keras.models import Model, load_model

#getting images
path = Path("UTKFace/")
filenames = list(map(lambda x: x.name, path.glob('*.jpg')))
print(len(filenames))
#data processing
np.random.seed(10)
np.random.shuffle(filenames)

age_labels, gender_labels, image_path = [], [], []

for filename in filenames:
    image_path.append(filename)
    temp = filename.split('_')
    age_labels.append(temp[0])
    gender_labels.append(temp[1])
#extra
df = pd.DataFrame()
df['image'], df['age'], df['gender'] = image_path, age_labels, gender_labels
gender_dict = {0:"Male",1:"Female"}
df = df.astype({'age':'float32', 'gender': 'int32'})

# test train split
train, test = train_test_split(df, test_size=0.2, random_state=42)
print("training dataset =",len(train))
print("training dataset =",len(test))

#converting Image to numpy array (extracting feature)
x_train = []
for file in train.image:
    img = load_img("UTKFace/"+file, grayscale=True)
    img = img.resize((128,128), Image.ANTIALIAS)
    img = np.array(img)
    x_train.append(img)

x_train = np.array(x_train)

x_train = x_train.reshape(len(x_train), 128,128,1)
#normalizing data
x_train = x_train/255
y_gender = np.array(train.gender)
y_age = np.array(train.age)
input_size = (128,128,1)

inputs = Input((input_size))
# convolutional layers
conv_1 = Conv2D(32, kernel_size=(3, 3), activation='relu') (inputs)
maxp_1 = MaxPooling2D(pool_size=(2, 2)) (conv_1)
conv_2 = Conv2D(64, kernel_size=(3, 3), activation='relu') (maxp_1)
maxp_2 = MaxPooling2D(pool_size=(2, 2)) (conv_2)
conv_3 = Conv2D(128, kernel_size=(3, 3), activation='relu') (maxp_2)
maxp_3 = MaxPooling2D(pool_size=(2, 2)) (conv_3)
conv_4 = Conv2D(256, kernel_size=(3, 3), activation='relu') (maxp_3)
maxp_4 = MaxPooling2D(pool_size=(2, 2)) (conv_4)

flatten = Flatten() (maxp_4)

# fully connected layers
dense_1 = Dense(256, activation='relu') (flatten)
dense_2 = Dense(256, activation='relu') (flatten)

dropout_1 = Dropout(0.4) (dense_1)
dropout_2 = Dropout(0.4) (dense_2)

output_1 = Dense(1, activation='sigmoid', name='gender_out') (dropout_1)
output_2 = Dense(1, activation='relu', name='age_out') (dropout_2)

model = Model(inputs=[inputs], outputs=[output_1, output_2])

model.compile(loss=['binary_crossentropy', 'mae'], optimizer='adam', metrics=['accuracy', 'mae'])

# train model
history = model.fit(x=x_train, y=[y_gender, y_age], batch_size=32, epochs=30, validation_split=0.2)

#save model
from tensorflow.keras.models import load_model
model.save('/content/drive/MyDrive/saved model/my_model.hdf5')

#load model
model_path = '/content/drive/MyDrive/saved model/my_model.hdf5'
model = keras.models.load_model(model_path)
model.summary()

#test
x_test = []
for file in test.image:
    img = load_img("UTKFace/"+file, grayscale=True)
    img = img.resize((128,128), Image.ANTIALIAS)
    img = np.array(img)
    x_test.append(img)

x_test = np.array(x_test)

x_test = x_test.reshape(len(x_test), 128,128,1)

x_test = x_test/255
y_gender = np.array(test.gender)
y_age = np.array(test.age)
input_size = (128,128,1)

index=37
print("Original: Gender = ", gender_dict[y_gender[index]]," Age = ", y_age[index])

pred = model.predict(x_test[index].reshape(1, 128, 128, 1))
pred_gender = gender_dict[round(pred[0][0][0])]
pred_age = round(pred[1][0][0])

print("Prediction: Gender = ", pred_gender," Age = ", pred_age)
plt.imshow(x_test[index].reshape(128,128), cmap='gray')

#custom image

custom_image_path = "./ali.png";
# Load the image and preprocess it
img = load_img(custom_image_path, grayscale=True)
img = img.resize((128, 128), Image.ANTIALIAS)
img_array = np.array(img)  # Convert to array

# Normalize and reshape to match model input shape
img_array = img_array / 255
img_array = img_array.reshape(1, 128, 128, 1)

# Make predictions
pred = model.predict(img_array)

# Interpret the predictions
pred_gender = gender_dict[round(pred[0][0][0])]
pred_age = round(pred[1][0][0])
pred_age = max(0, min(100, pred_age))

# Display the results
print("Prediction: Gender = ", pred_gender, " Age = ", pred_age)
plt.imshow(img_array.reshape(128, 128), cmap='gray')
plt.title(f"Predicted: Gender = {pred_gender}, Age = {pred_age}")
plt.show()

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Predict on test set
y_pred_gender, y_pred_age = model.predict(x_test)

# Calculate regression metrics
mae_age = mean_absolute_error(y_age, y_pred_age)
rmse_age = np.sqrt(mean_squared_error(y_age, y_pred_age))
r2_age = r2_score(y_age, y_pred_age)

print("Regression Metrics:")
print("MAE:", mae_age)
print("RMSE:", rmse_age)
print("R^2 Score:", r2_age)

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Round predictions to obtain binary gender labels
y_pred_gender_binary = np.round(y_pred_gender).astype(int)

# Calculate classification metrics
accuracy = accuracy_score(y_gender, y_pred_gender_binary)
precision = precision_score(y_gender, y_pred_gender_binary)
recall = recall_score(y_gender, y_pred_gender_binary)
f1 = f1_score(y_gender, y_pred_gender_binary)
conf_matrix = confusion_matrix(y_gender, y_pred_gender_binary)

print("\nClassification Metrics:")
print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)
print("Confusion Matrix:")
print(conf_matrix)