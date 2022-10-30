# -*- coding: utf-8 -*-
"""Gender_Classification_LSTM_Model_Tester.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y43tLITRI00dGtKcnABb5PdOfdrt5nC1
"""

from google.colab import drive
drive.mount('/content/drive')

# Python Pckages
import random
import string
import pandas as pd
import numpy as np
from tabulate import tabulate

# ML Packages
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

# ML Classifiers
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier

# Deep ML Packages
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Dense, Activation, Dropout, LSTM, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.regularizers import l2
from tensorflow.keras.utils import plot_model
import tensorflow as tf
from tensorflow import keras

# ML Metrics
from sklearn.metrics import accuracy_score

removing_characters = list(string.punctuation+'0123456789'+'\t'+'\n')
def data_preprocessing(df):
    # Removing NaN Data
    df = df.dropna()
    # Seperating Male Indices and Female Indices
    male_df = []
    female_df = []
    for i in range(df.shape[0]):
        if df.iloc[i, 1] == 'male':
            male_df.append(i)
        elif df.iloc[i, 1] == 'female':
            female_df.append(i)
        df.iloc[i, 0] = str(df.iloc[i, 0]).lower()
        # Removing Special Characters and Digits
        temp = ''
        for char in df.iloc[i, 0]:
            if char not in removing_characters:
                temp += char
        df.iloc[i, 0] = temp
    
    # Creating New Dataset where Number of Male == Number of Female
    sampled_indices = list(random.sample(male_df, len(female_df))) + female_df
    sampled_df = df.iloc[sampled_indices, :]

    for i in range(sampled_df.shape[0]):
        if sampled_df.iloc[i, 1] == "male":
            sampled_df.iloc[i, 1] = "M"
        else:
            sampled_df.iloc[i, 1] = "F"

    sampled_df = sampled_df.sample(frac=1)

    return sampled_df

# Extracting Maximum Length of All The Names
def max_length_extractor_names(names):
    max_length = 0
    for name in names:
        if max_length < len(name):
            max_length = len(name)
    return max_length

# Builds an empty line with a 1 at the index of character
def set_flag(i):
    temp = np.zeros(len(vocabulary));
    temp[i] = 1
    return list(temp)

# Truncate names and create the matrix
def prepare_X(X):
    new_list = []
    trunc_train_name = [str(i)[0:maxlen] for i in X]

    for i in trunc_train_name:
        tmp = [set_flag(char_index[j]) for j in str(i)]
        for k in range(0,maxlen - len(str(i))):
            tmp.append(set_flag(char_index["END"]))
        new_list.append(tmp)

    return new_list

# Label Encoding of y
def prepare_y(y):
    new_list = []
    for i in y:
        if i == 'M':
            new_list.append([1,0])
        else:
            new_list.append([0,1])
    return new_list

vocabulary = [' ', 'END', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
char_index = {' ': 0, 'END': 1, 'a': 2, 'b': 3, 'c': 4, 'd': 5, 'e': 6, 'f': 7, 'g': 8, 'h': 9, 'i': 10, 'j': 11, 'k': 12, 'l': 13, 'm': 14, 'n': 15, 'o': 16, 'p': 17, 'q': 18, 'r': 19, 's': 20, 't': 21, 'u': 22, 'v': 23, 'w': 24, 'x': 25, 'y': 26, 'z': 27}
maxlen = 39
labels = 2

# Loading Saved Model
model = tf.keras.models.load_model("Model.h5")

# Load test data
test_df = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/Datasets/Test_Dataset.csv")
test_df.head()

print(test_df.shape)

with tf.device('/gpu:0'):
    for i in range(test_df.shape[0]):
        temp = ''
        for char in test_df.iloc[i, 0]:
            if char not in removing_characters:
                temp += char
        test_df.iloc[i, 0] = temp
        test_df.iloc[i, 0], test_df.iloc[i, 1] = str(test_df.iloc[i, 0]).lower(), str(test_df.iloc[i, 1]).lower()
        if test_df.iloc[i, 1] == 'male':
            test_df.iloc[i, 1] = 'M'
        else:
            test_df.iloc[i, 1] = 'F'
        test_df.head()

with tf.device("/gpu:0"):
    final_accuracy = []
    final_predictions = []
    final_test_y = []
    final_test_X = []
    hop = 500000
    start = 0
    end = hop
    while end <= test_df.shape[0]:
        test_X, test_y = list(test_df.iloc[start:end, 0]), list(test_df.iloc[start:end, 1])
        test_X_pred = prepare_X(test_X)
        test_predictions = model.predict(test_X_pred)
        final_test_predictions = ['M' if np.argmax(prediction) == 0 else 'F' for prediction in test_predictions]
        final_test_X.append(test_X)
        final_test_y.append(test_y)
        final_predictions.append(final_test_predictions)
        accuracy = accuracy_score(test_y, final_test_predictions)
        final_accuracy.append(accuracy)
        start += hop
        end += hop
        print(f"Accuracy : {round(accuracy * 100, 2)}%")

rX = []
rY = []
rP = []
for i in range(len(final_test_X)):
    for j in range(len(final_test_X[i])):
        rX.append(final_test_X[i][j])
        rY.append(final_test_y[i][j])
        rP.append(final_predictions[i][j])

print(f"Accuracy : {round(np.mean(final_accuracy) * 100, 2)}%")

result = pd.DataFrame(list(zip(rX, rY, rP)), columns=['Name', 'Original Gender', 'Predicted Gender'])
result.to_csv('/content/drive/MyDrive/Colab Notebooks/Results/Test_Result.csv', index=False)
