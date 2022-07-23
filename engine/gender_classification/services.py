import string
import io
import os
import pandas as pd
import numpy as np
import tensorflow as tf
from rest_framework import status


class Service:
    max_length_name = 39
    label_count = 2
    vocabulary = [' ', 'END', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                  's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    chars_index = {' ': 0, 'END': 1, 'a': 2, 'b': 3, 'c': 4, 'd': 5, 'e': 6, 'f': 7, 'g': 8, 'h': 9, 'i': 10, 'j': 11,
                   'k': 12, 'l': 13, 'm': 14, 'n': 15, 'o': 16, 'p': 17, 'q': 18, 'r': 19, 's': 20, 't': 21, 'u': 22,
                   'v': 23, 'w': 24, 'x': 25, 'y': 26, 'z': 27}
    removing_chars = list(string.punctuation + '0123456789' + '\t' + '\n')

    def data_processing(self, df):
        df = df.dropna()
        for i in range(df.shape[0]):
            df.iloc[i, 0] = ''.join(i for i in df.iloc[i, 0] if not i in self.removing_chars)
            df.iloc[i, 0] = str(df.iloc[i, 0]).lower()
        x = list(df.iloc[:, 0])
        x_vectorized = self.prepare_x(x)
        return x_vectorized

    # Builds an empty line with a 1 at the index of character
    def set_flag(self, i):
        temp = np.zeros(len(self.vocabulary))
        temp[i] = 1
        return list(temp)

    # Truncate names and create the matrix
    def prepare_x(self, x):
        new_list = []
        trunc_train_name = [str(i)[0:self.max_length_name] for i in x]
        for i in trunc_train_name:
            temp = [self.set_flag(self.chars_index[j]) for j in str(i)]
            for k in range(0, self.max_length_name - len(str(i))):
                temp.append(self.set_flag(self.chars_index["END"]))
            new_list.append(temp)
        return new_list

    def classification(self, data, data_type):
        df = None
        if data_type == 'single':
            df = pd.read_fwf(io.StringIO(data), header=None, widths=[200], names=['CUSTOMER_NAME'])
        elif data_type == 'bulk':
            df = pd.read_csv(data.path)
        directory_path = str(os.getcwd())
        directory_path = directory_path.replace("\\", '/')
        if os.path.isdir(directory_path):
            list_dirs_files = os.listdir(directory_path)
            dir_status = 0
            for element in list_dirs_files:
                if element == 'resources':
                    dir_status = 1
            if dir_status == 1:
                model_directory_path = directory_path + "/resources"
                list_models = os.listdir(model_directory_path)
                model_status = 0
                for element in list_models:
                    if element == 'Model.h5':
                        model_status = 1
                if model_status == 1:
                    model = tf.keras.models.load_model(model_directory_path + "/Model.h5")
                    x_vectorized = self.data_processing(df)
                    raw_predictions = model.predict(x_vectorized)
                    probability = []
                    for row in raw_predictions:
                        probability.append(','.join(str(i) for i in row))
                    prediction = ['Male' if np.argmax(row) == 0 else 'Female' for row in raw_predictions]
                    if data_type == 'single':
                        return self.custom_response(
                            data_type=data_type,
                            status_code=status.HTTP_200_OK,
                            message='Prediction Successful !!',
                            prediction_status=True,
                            prediction=prediction,
                            probability=probability,
                            dataframe=None
                        )
                    elif data_type == 'bulk':
                        return self.custom_response(
                            data_type=data_type,
                            status_code=status.HTTP_200_OK,
                            message='Prediction Successful !!',
                            prediction_status=True,
                            prediction=prediction,
                            probability=probability,
                            dataframe=df
                        )
                else:
                    return self.custom_response(
                        data_type=data_type,
                        status_code=status.HTTP_404_NOT_FOUND,
                        message='Predicting Model Not Found !!',
                        prediction_status=False,
                        prediction=None,
                        probability=None,
                        dataframe=None
                    )
            else:
                return self.custom_response(
                    data_type=data_type,
                    status_code=status.HTTP_404_NOT_FOUND,
                    message='Models Directory Not Found !!',
                    prediction_status=False,
                    prediction=None,
                    probability=None,
                    dataframe=None
                )
        else:
            return self.custom_response(
                data_type=data_type,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                message='Path Is Not A Directory !!',
                prediction_status=False,
                prediction=None,
                probability=None,
                dataframe=None
            )

    @staticmethod
    def custom_response(data_type, status_code, message, prediction_status, prediction, probability, dataframe):
        if prediction_status:
            if data_type == 'single':
                return {
                    'status_code': status_code,
                    'message': message,
                    'prediction': prediction,
                    'probability': probability
                }
            elif data_type == 'bulk':
                return {
                    'status_code': status_code,
                    'message': message,
                    'prediction': prediction,
                    'probability': probability,
                    'dataframe': dataframe
                }
        else:
            return {
                'status_code': status_code,
                'message': message
            }
