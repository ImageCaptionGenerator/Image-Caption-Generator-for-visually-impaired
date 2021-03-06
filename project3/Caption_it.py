#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
from gtts import gTTS
import os
import matplotlib.pyplot as plt
import keras
import json
import pickle
from keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from keras.preprocessing import image
from keras.models import Model, load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from keras.layers import Input, Dense, Dropout, Embedding, LSTM
from keras.layers import add

model = load_model("model_9.h5")
model.make_predict_function()

model_temp = ResNet50(weights="imagenet",input_shape=(224,224,3))


#Create a new model, by removing the last layer (output layer of 1000 classes) from resnet50
model_resnet = Model(model_temp.input,model_temp.layers[-2].output)
model_resnet.make_predict_function()

with open("./storage/word_to_idx.pkl", "rb") as w2i:
    word_to_idx = pickle.load(w2i)
    
with open("./storage/idx_to_word.pkl", "rb") as i2w:
    idx_to_word = pickle.load(i2w)

max_len=35

import tensorflow as tf
def preprocess_img(img):
    img = tf.keras.utils.load_img(img,target_size=(224,224))
    img = tf.keras.utils.img_to_array(img)
    img = np.expand_dims(img,axis=0)
    # Normalisation
    img = preprocess_input(img)
    return img


def encode_image(img):
    img = preprocess_img(img)
    feature_vector = model_resnet.predict(img)
    feature_vector = feature_vector.reshape(1, feature_vector.shape[1])
    #print(feature_vector.shape)
    return feature_vector


def predict_caption(photo):
    in_text = "startseq"

    for i in range(max_len):
        sequence = [word_to_idx[w] for w in in_text.split() if w in word_to_idx]
        sequence = pad_sequences([sequence],maxlen=max_len,padding='post')
        
        ypred = model.predict([photo,sequence])
        ypred = ypred.argmax() #WOrd with max prob always - Greedy Sampling
        word = idx_to_word[ypred]
        in_text += (' ' + word)
        
        if word == "endseq":
            break
    
    final_caption = in_text.split()[1:-1]
    final_caption = ' '.join(final_caption)
    return final_caption

def caption_this_image(image):
    enc = encode_image(image)
    caption = predict_caption(enc)
    tts = gTTS(text=caption,lang='en')
    tts.save("C://Users//yaksh//Downloads//project3//test.mp3")
    return caption