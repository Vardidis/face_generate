import os

import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, MaxPooling2D, Dropout
from sklearn.model_selection import train_test_split

DATA_BASE_DIR = 'data/'
RATING_CSV = os.path.join(DATA_BASE_DIR, 'rating.csv')
RATINGS_BIN_FILE = os.path.join(DATA_BASE_DIR, 'ratings.bin')

def kernel_size():
    return (9, 9)

def build(x_train, x_test, y_train, y_test):
    model = Sequential([
        Conv2D(32, kernel_size(), padding='same', input_shape=x_train.shape[1:], activation='relu'),
        Conv2D(32, kernel_size(), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Conv2D(64, kernel_size(), padding='same', activation='relu'),
        Conv2D(64, kernel_size(), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=10, batch_size=16)

    loss, accuracy = model.evaluate(x_test, y_test)
    print('Test loss:', loss)
    print('Test accuracy:', accuracy)

def parse_csv():
    df = pd.read_csv(RATING_CSV)
    x = df.drop('like', axis=1)
    y = df['like']

    print(x)
    # we have to import the images pixels somehow
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
    print(f'Splitted dataset into: train={len(x_train)}, test={len(x_test)} images.')

    return x_train, x_test, y_train, y_test