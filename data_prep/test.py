import os, sys
from optparse import OptionParser

batch_size = 24
fill_mode = 'nearest'
model_path = '.\model'
imagess = r'C:\Users\Monster\Desktop\deeplearning_spacenet_test\yo9.jpg'
if __name__ == '__main__':
    import numpy as np
    import keras.backend as K
    from keras.preprocessing import image

    ## Verify our backend:
    if not K.backend() == 'tensorflow':
        raise Exception('Backend inncorrently set to : ' + K.backend() )

    ## Verify CNN dimension ordering:
    if not K.image_dim_ordering() == 'tf':
        raise Exception('Dimension ordering inncorrently set to : ' + K.image_dim_ordering() )


    if not model_path:
        raise Exception('Model directory required.')
    else:
        model_path = os.path.normpath(model_path)
        if not os.path.isdir(model_path):
            raise Exception('Model directory not found...\n  ' + model_path)


    ## Load model:
    model_json = os.path.join(model_path,'model.json')
    model_weights = os.path.join(model_path,"bestweights_acc.h5")

    if not os.path.isfile(model_json):
        raise Exception('Could not find:',model_json)
    if not os.path.isfile(model_weights):
        raise Exception('Could not find:',model_weights)

    from keras.models import model_from_json
    from keras.models import Model

    model = model_from_json(open(model_json).read())
    model.load_weights(model_weights)

    # Pull image size from the model:
    image_size = (model.get_layer('input_1').input_shape[1],
                  model.get_layer('input_1').input_shape[2])

    #print (model.summary())

    #model = Model(input=model.input, output=model.get_layer('flatten_1').output)

    def preprocess_input(x):
        x = x[:, :, ::-1]
        x[:, :, 0] -= 255./2.
        x[:, :, 1] -= 255./2.
        x[:, :, 2] -= 255./2.
        return x

    L = []
    address = []
    jpg_images = r"G:\training_sets\Paris\grayscale\jpg"
    for fileTIF in os.listdir(jpg_images):
        if fileTIF.endswith(".jpg") or fileTIF.endswith(".jpeg"):
            imageload = jpg_images+"\\"+fileTIF
            img = image.load_img(imageload, target_size=image_size)
            X = preprocess_input(image.img_to_array(img))
            X = np.expand_dims(X, axis=0)

            feat_vect = model.predict(X)
            print(str(fileTIF))
            L.append(feat_vect[0])
            address.append(imageload)
            print(feat_vect[0])
            print(feat_vect[0][0])
            print(feat_vect[0][1])
            #img = None
    np.savetxt("parisfile_name.csv",  np.column_stack((L, address)), delimiter=",", fmt='%s', header="head")
