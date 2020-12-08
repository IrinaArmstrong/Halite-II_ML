import os
import sys
import warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from typing import Tuple, List, NoReturn, Union, Any

# We don't want tensorflow to produce any warnings in the standard output, since the bot communicates
# with the game engine through stdout/stdin.
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '50' #99


import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Conv1D, GlobalAveragePooling1D, MaxPooling1D
from keras.layers import BatchNormalization
from keras.losses import CategoricalCrossentropy


class CNN_Net(object):
    FIRST_LAYER_FILTERS = 32
    FIRST_LAYER_KERNEL = 3
    SECOND_LAYER_FILTERS = 64
    SECOND_LAYER_KERNEL = 3

    def __init__(self, input_size: Tuple[int, int], output_size: int,
                 cached_model: bool, cached_model_path: str, seed=None):

        np.random.seed(seed)
        if cached_model:
            # returns an already compiled model
            self._model = load_model(cached_model_path)
        else:
            # returns an already compiled model
            self._model = self.create_model(input_size, output_size,
                                            loss=CategoricalCrossentropy(),
                                            optimizer="adam",
                                            metrics=['accuracy'], verbose=False)



    def create_model(self, input_size: Tuple[int, int], output_size: int,
                     loss: Union[str, Any], optimizer: str, metrics: List[str],
                    verbose: bool):

        model = Sequential()
        model.add(Conv1D(self.FIRST_LAYER_FILTERS, self.FIRST_LAYER_KERNEL,
                               activation='relu', input_shape=input_size))
        model.add(Conv1D(self.FIRST_LAYER_FILTERS, self.FIRST_LAYER_KERNEL,
                         activation='relu'))
        model.add(BatchNormalization())
        model.add(MaxPooling1D())
        model.add(Conv1D(self.SECOND_LAYER_FILTERS, self.SECOND_LAYER_KERNEL,
                               activation='relu'))
        model.add(Conv1D(self.SECOND_LAYER_FILTERS, self.SECOND_LAYER_KERNEL,
                         activation='relu'))
        model.add(BatchNormalization())
        model.add(GlobalAveragePooling1D())
        model.add(Dropout(0.5))
        model.add(Dense(output_size * 2, activation='sigmoid'))
        model.add(Dense(output_size * 2, activation='sigmoid'))
        model.add(Dense(output_size, activation='sigmoid'))
        if verbose:
            print("Model created:")
            print(model.summary())

        self._loss = loss
        self._metrics = metrics

        model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

        return model

    def train(self, input_train, target_train, validation_split: float,
              n_epochs: int, batch_size: int, verbose: int,
              model_version: str)-> NoReturn:
        print(f"Input features shape: {input_train.shape}")
        print(f"output targets shape: {target_train.shape}")

        # Fit data to model
        history = self._model.fit(input_train, target_train,
                                  batch_size=batch_size,
                                  epochs=n_epochs,
                                  verbose=verbose,
                                  validation_split=validation_split,
                                  shuffle=True)

        # Plot history
        print(f"History consist of: {history.history.keys()}")
        current_directory = os.path.dirname(os.path.abspath(__file__))
        hist_df = pd.DataFrame(history.history, columns=self._metrics + ["val_" + m for m in self._metrics] + ['loss', 'val_loss'])
        hist_df = hist_df.reset_index(col_fill='epoch')
        fig = hist_df.plot(x='index', y=['loss', 'val_loss']).get_figure()
        curve_path = os.path.join(current_directory, os.path.pardir, "models", "training_plot.png")
        fig.savefig(curve_path)

        # Save model
        self.save(model_save_fn="cnn_model_" + model_version + ".hd5")


    def predict(self, input_data):
        predictions = self._model.predict(input_data)
        return predictions


    def save(self, model_save_path="../models",
             model_save_fn="cnn_model.hd5"):
        self._model.save(os.path.join(model_save_path, model_save_fn))
