import os, sys

fill_mode = 'nearest'
batch_size = 24
data_path = "data"
model_path = "models"
number_of_classes=102



# Model training parameters
nb_train_samples = 6587
epochs = 100
nb_validation_samples = 1602

if __name__ == '__main__':
    import numpy as np
    import keras.backend as K

    # verify backend
    if not K.backend() == 'tensorflow':
        raise Exception('Backend inncorrecclty set to: '+ K.image_dim_ordering)

    # Verify CNN dimension ordering:
    if not K.image_dim_ordering() == 'tf':
        raise Exception('Dimension ordering incorrectly set to : '+K.image_dim_ordering())

    from keras.applications.resnet50 import ResNet50
    from keras.applications.resnet50 import decode_predictions
    model = ResNet50()
    image_size = (224,224)

    model.summary()

    from keras.layers import Dense
    model_output = model.layers[-1].output
    model_output = Dense(number_of_classes, activation='softmax')(model_output)


    #creating the final model
    from keras.models import Model
    model = Model(input = model.input, output = model_output)

    ## setup generator for loading images
    from keras.preprocessing.image import ImageDataGenerator