import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dense, Dropout
import numpy as np

def lstm_non_tuned(X_train):
    # Define the custom WeightedMSE class
    class WeightedMSE(tf.keras.losses.Loss):
        """ 
        Calculate a weighted MSE. This loss gives you control to weight the 
        pixels that are > 0 differently than the pixels that are 0 in y_true. This
        class is subclassed from tf.keras.lossess.Loss to hopefully enable 
        'stateful'-ness.
     
        weights[0] is the weight for non-zero pixels
        weights[1] is the weight for zero pixels.
        """
        def __init__(self, weights=[1.0, 1.0], name="custom_mse", **kwargs):
            super(WeightedMSE, self).__init__(name=name, **kwargs)
            # store weights
            self.w1 = weights[0]
            self.w2 = weights[1]

        def call(self, y_true, y_pred):
            # build weight_matrix 
            ones_array = tf.ones_like(y_true)
            weights_for_nonzero = tf.math.multiply(ones_array, self.w1)
            weights_for_zero = tf.math.multiply(ones_array, self.w2)
            weight_matrix = tf.where(tf.greater(y_true, 0), weights_for_nonzero, weights_for_zero)
            loss = tf.math.reduce_mean(tf.math.multiply(weight_matrix, tf.math.square(tf.math.subtract(y_pred, y_true))))
            return loss

    # Define the model
    model_WSE_G = Sequential()

    # Define the input shape in the first layer of the neural network
    input_shape = (X_train.shape[1], X_train.shape[2])

    # Add a Conv1D layer with 32 filters and a kernel size of 3
    model_WSE_G.add(Conv1D(filters=32, kernel_size=3, padding='same', input_shape=input_shape))

    # Add a Dropout layer
    model_WSE_G.add(Dropout(0.1))

    # Add the first LSTM layer with 128 units
    model_WSE_G.add(LSTM(units=64, return_sequences=True))

    # Add a Dropout layer
    model_WSE_G.add(Dropout(0.1))

    # Add the second LSTM layer with 256 units
    model_WSE_G.add(LSTM(units=256, return_sequences=True))

    # Add a Dropout layer
    model_WSE_G.add(Dropout(0.1))

    # Add a Dense (fully connected) layer with 4 units (for 4 stats)
    #model_WSE_G.add(Dense(units=128, activation='tanh'))

    # Add a Flatten layer
    #model_WSE_G.add(Flatten())

    # Add the final Dense layer with a linear activation function

    #output_length = 185
    model_WSE_G.add(Dense(units=1, activation='linear'))

    # Compile the model with the custom weighted MSE loss
    custom_loss = WeightedMSE(weights=[1.0, 0])
    #model_WSE_G.compile(optimizer='adam', loss=custom_loss)

    # Print the model summary
    #model_WSE_G.summary()
    return model_WSE_G, custom_loss