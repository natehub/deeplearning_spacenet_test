import os, sys


# Set some options:
fill_mode = 'nearest'
batch_size = 24
data_path = r'F:\\digitalglobe_imagery\\buildings_true\\'
model_path = r'D:\\Git_hub\\deeplearning_spacenet_test\\model\\'
number_of_classes = 102

# Model training parameters:
nb_train_samples = 2895
epochs = 100
nb_validation_samples = 1311

if __name__ == '__main__':
    import numpy as np
    import keras.backend as K
    print("we started")
    ## Verify our backend:
    if not K.backend() == 'tensorflow':
        raise Exception('Backend inncorrently set to : ' + K.backend() )

    ## Verify CNN dimension ordering:
    if not K.image_dim_ordering() == 'tf':
        raise Exception('Dimension ordering inncorrently set to : ' + K.image_dim_ordering() )

    ## Load model:
    from keras.applications.resnet50 import ResNet50
    from keras.applications.resnet50 import decode_predictions
    model = ResNet50()
    image_size = (224, 224)

    ## Some butchering to make the model work for us:
    #  Strip the last layer:
    model.layers.pop()

    # Add a new one:
    from keras.layers import Dense
    model_output = model.layers[-1].output
    model_output = Dense(number_of_classes, activation="softmax")(model_output)

    # creating the final model
    from keras.models import Model
    model = Model(input = model.input, output = model_output)

    #model.summary(); sys.exit()

    ## Setup generator for loading images:
    from keras.preprocessing.image import ImageDataGenerator

    ## Prepocess input:
    def preprocess_input(x):
        x = x[:, :, ::-1]
        x[:, :, 0] -= 255./2.
        x[:, :, 1] -= 255./2.
        x[:, :, 2] -= 255./2.
        return x

    train_gen = ImageDataGenerator(
            preprocessing_function=preprocess_input,
            fill_mode = fill_mode,
            )

    train_generator = train_gen.flow_from_directory(
            os.path.join(data_path,'train'),
            target_size=image_size,
            batch_size=batch_size,
            class_mode='categorical'
            )

    valid_gen = ImageDataGenerator(
            preprocessing_function=preprocess_input,
            fill_mode = fill_mode,
            )

    validation_generator = valid_gen.flow_from_directory(
            os.path.join(data_path,'valid'),
            target_size=image_size,
            batch_size=batch_size,
            class_mode='categorical'
            )

    # Verify classes:
    for i in train_generator.class_indices.keys():
        if train_generator.class_indices[i] != validation_generator.class_indices[i]:
            print ('Mismatch for class index', i)
            print ('  Train class:', train_generator.class_indices[i])
            print ('  Valid class:', validation_generator.class_indices[i])
            raise Exception()

    # Save classes:
    import json
    #json.dump( train_generator.class_indices,
        #open( os.path.join(model_path,'classes.json'), 'wb'))

    from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping

    # Save model:
    open(os.path.join(model_path,'model.json'), 'w').write(model.to_json())

    # Save model weights:
    checkpoint = ModelCheckpoint(os.path.join(model_path,"bestweights_acc.h5"),
            monitor='val_acc', verbose=1, save_best_only=True,
            save_weights_only=False, mode='auto', period=1)

    # Stop model after validation quits improving:
    ## Choose an optimizer:
    #   - 10 is set as learning rate, to make things fail quickly in the event
    #     the schedule callback isn't working.
    from keras import optimizers
    #optimizer = optimizers.SGD(lr=10.0, momentum=0.9,
    #        nesterov=True, clipnorm=1., clipvalue=1.5)

    optimizer = optimizers.RMSprop(lr=10.0, clipnorm=1., clipvalue=1.5)

    #optimizer = optimizers.Nadam(lr=10.0, clipnorm=1., clipvalue=1.5)

    ## Choose a learning rate scheule:
    learning_rate = 0.01
    scheule = 'linear'

    def scheduler(epoch):
        if scheule == 'constant':
            lr = learning_rate
        elif scheule == 'linear':
            lr = (1. - float(epoch/epochs))*learning_rate
        elif scheule == 'inverse':
            scale = 1.2
            lr = learning_rate/(float(epoch/scale) + 1.)
        else:
            raise Exception('Unrecognized schedule:',scheule)
        return lr

    learning_rate_schedule = LearningRateScheduler(scheduler)

    ## Compile the model
    model.compile(loss = "categorical_crossentropy",
            optimizer = optimizer,
            metrics=["accuracy"])

    ## Fit the model:
    history = model.fit_generator(
            train_generator,
            samples_per_epoch = nb_train_samples,
            nb_epoch = epochs,
            validation_data = validation_generator,
            nb_val_samples = nb_validation_samples,
            max_q_size=100, verbose=1,
            #callbacks = [checkpoint, early, learning_rate_schedule])
            callbacks = [checkpoint, learning_rate_schedule])

    # Save model training history
    import cPickle as pickle
    pickle.dump( history.history, open( os.path.join(model_path,'history.pkl'), 'wb'))

    # Plot train/test curves
    import matplotlib as mpl;mpl.use('Agg')
    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    X = range(epochs)
    Y = history.history

    p1, = ax1.plot(X,Y['loss'],'k',label='Train Loss')
    p2, = ax1.plot(X,Y['val_loss'],'--k',label='Valid Loss')

    p3, = ax2.plot(X,Y['acc'],'r',label='Train Acc')
    p4, = ax2.plot(X,Y['val_acc'],'--r',label='Valid Acc')

    ax1.set_xlabel('Epoch Number')

    ax1.set_ylabel('Categorical Crossentropy Loss',color='k')
    ax2.set_ylabel('Accuracy',color='r')
    ax2.tick_params(axis='y', colors='r')

    lines = [p1, p2, p3, p4]
    plt.legend(lines, [l.get_label() for l in lines])
    plt.savefig(os.path.join(model_path,'train_validation_curve.jpg'))
