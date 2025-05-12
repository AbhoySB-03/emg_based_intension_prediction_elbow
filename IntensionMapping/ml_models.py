from mlutils import *
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from sklearn.linear_model import LinearRegression

class CNNClassifier:
    def __init__(self, input_shape, save_file=None):
        self.model=models.Sequential()
        self.model.add(layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape))
        self.model.add(layers.MaxPooling2D((1,3)))
        self.model.add(layers.Conv2D(64, (1,10), activation='relu'))
        self.model.add(layers.AveragePooling2D((1,10)))
        self.model.add(layers.Conv2D(128, (1,10), activation='relu'))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(64, activation='relu'))
        self.model.add(layers.Dense(4, activation='softmax'))
        self.model.summary()
        self.ckpt_path=save_file
        self.cb_ckpt=None
        if save_file!=None:
            self.cb_ckpt=callbacks.ModelCheckpoint(filepath=save_file, save_weights_only=True, verbose=1)

        self.model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

        self.history=None

    def train(self, train_data, train_label, epochs=10, test_data=None, test_label=None):
        cb=[self.cb_ckpt] if self.cb_ckpt!=None else None
        if test_data==None or test_label==None:
            self.history=self.model.fit(train_data,train_label, epochs=epochs)
        else:
            self.history=self.model.fit(train_data, train_label, epochs=epochs, validation_data=(test_data, test_label), callbacks=cb) 

        
    def predict(self, test_data):
        if self.cb_ckpt!=None:
            self.model.load_weights(self.ckpt_path)

        if len(test_data.shape)<=3:
            test_data=tf.convert_to_tensor([test_data])

        pred=self.model.predict(test_data)
        return pred


class PolyRegression:
    def __init__(self, powers=[1]):
        self.powers=powers
        self.model=LinearRegression()

    def fit(self, X, y):
        init=False
        for p in self.powers:
            if not init:
                X=X**p
                init=True
            else:
                X=np.c_[X,X**p]

        self.model.fit(X,y)

    def predict(self, X):
        init=False
        for p in self.powers:
            if not init:
                X=X**p
                init=True
            else:
                X=np.c_[X,X**p]

        return self.model.predict(X)
