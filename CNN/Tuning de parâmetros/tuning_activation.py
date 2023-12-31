# -*- coding: utf-8 -*-
"""Tuning_regressao3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wvLQbDluufYGfszBcQ7TNXy447HUWBbY

# Hiperparâmetros: funções de ativação e matriz de pesos

Nesse código o objetivo é encontrar as melhores funções de ativação em ambas camadas e encontrar a melhor forma de se iniciar os pesos de ambas camadas. Para isso testaremos as seguintes funções de ativação: Linear, Sigmóide, Tangente hiperbólica, ReLU, SoftPlus, ELU, SELU.
"""

# importações que deve er para criação da rede
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
#Importações para auxiliar
import numpy as np
import pandas as pd
# importações para tuning
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import GridSearchCV
from keras.layers.normalization.batch_normalization import BatchNormalization


#bibliotecas para baixar imagens
import os
from PIL import Image

trainDf = pd.read_excel("/content/drive/MyDrive/TCC/Experimento1.xlsx")
#print(trainDf)
#colTrain = ["LeftPoca","WidthPoca","Curto"]
y_train = trainDf[["percentageWidthPoca","Imagem"]].values

images = []
labels = []

image_dir = '/content/drive/MyDrive/TCC/Experimento1'


for image_file in os.listdir(image_dir):
    #print(image_file)
    image_path = os.path.join(image_dir, image_file)
    image = Image.open(image_path)
    image = image.resize((230, 230))  # Redimensionar para o tamanho desejado
    image = np.array(image)  # Converter a imagem em um array numpy

    # Adicionar a imagem e o rótulo correspondente às listas
    images.append(image)
    labels.append(image_file)

y_train = np.array(y_train)
y_trainOrdenado = sorted(y_train, key=lambda x: x[1])
y_trainOrdenado = np.array(y_trainOrdenado)
y_trainOrdenado2 = pd.DataFrame(y_trainOrdenado)
y_trainOrdenado3 = y_trainOrdenado2.drop(1,axis=1)
y_train = np.array(y_trainOrdenado3)
y_train = y_train *100
y_train = y_train.astype('float32')

X_train = np.array(images)
X_train = X_train.reshape(X_train.shape[0], 230, 230, 1)
X_train = X_train / 255.0
X_train32 = X_train.astype('float32')

def create_model(conv_activation, dense_activation, conv_kernel_initializer, dense_kernel_initializer):
    model = Sequential()

    model.add(Conv2D(16, (3, 3), activation=conv_activation, input_shape=(230, 230, 1), kernel_initializer=conv_kernel_initializer))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(32, (3, 3), activation=conv_activation, kernel_initializer=conv_kernel_initializer))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3), activation=conv_activation, kernel_initializer=conv_kernel_initializer))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(128, (3, 3), activation=conv_activation, kernel_initializer=conv_kernel_initializer))
    model.add(MaxPooling2D((2, 2)))

    model.add(Flatten())

    model.add(Dense(units = 500, activation=dense_activation, kernel_initializer=dense_kernel_initializer))
    model.add(Dropout(0.15))



    model.add(Dense(1, activation='linear'))

    model.compile(optimizer='Adamax', loss='mean_squared_error')
    return model

param_grid = {
    'batch_size':[20],
    'conv_activation':
        ['relu',
        'softplus',
        'elu',
        'selu',
        'tanh',
        'sigmoid'], 
    'dense_activation':
        ['relu',
        'selu',
        'elu',
        'tanh',
        'linear'],
    'conv_kernel_initializer':
        ['glorot_uniform',
        'random_uniform',
        'glorot_normal',
        'he_normal',
        'he_uniform'], 
    'dense_kernel_initializer':
        ['glorot_uniform',
        'random_uniform',
        'glorot_normal',
        'he_normal',
        'he_uniform'],
    'epochs': [3]
}

regressor = KerasRegressor(build_fn=create_model)
grid = GridSearchCV(estimator=regressor, param_grid=param_grid,scoring='neg_mean_squared_error',cv=5)

grid.fit(X_train32,y_train)
melhores_parametros = grid.best_params_
# mostra o valor do melhor resultado
melhor_precisao = grid.best_score_

resultados = grid.cv_results_
for indice_combinacao, score_mean, score_std, params in zip(resultados['rank_test_score'], resultados['mean_test_score'], resultados['std_test_score'], resultados['params']):
    print(f"Combinação {indice_combinacao}: Desempenho médio = {score_mean:.4f}, Desvio padrão = {score_std:.4f}, Hiperparâmetros = {params}")

print(melhor_precisao)
print(melhores_parametros)