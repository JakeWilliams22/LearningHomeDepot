from __future__ import print_function
from helperFunctions import *

import numpy as np
import tensorflow as tf
import random;

def getFeatureResultFormat(productTriples):
    features = []; #[two days ago views][one day ago views]
    classifications = [] # [third day views];

    for triple in productTriples:
        if(len(triple) == 3):        
            twoAgo = float(triple[0][1])
            oneAgo = float(triple[1][1]);        
            features.append([twoAgo, oneAgo]);
#            classifications.append(float(triple[2][1]));
            arr = [0 for x in range(1,15000)];
            arr[int(triple[2][1])] = 1;
            classifications.append(arr);

    return features, classifications;

def splitTestTrain(features, classes, breakPercent):
    if len(features) != len(classes):
        print("BIG PROBLEM, YUUGE");
        return;
    
    randIndexes = random.sample(range(0, len(features)), len(features))
    
    Xtr=[];
    Xte=[]
    Ytr=[]
    Yte = [];

    for index in randIndexes:
        if(len(Xtr) <= int(len(features) * .8)):
            Xtr.append(features[index]);
            Ytr.append(classes[index]);
        else:
            Xte.append(features[index])
            Yte.append(classes[index])

    return [Xtr,Ytr],[Xte,Yte];

def runWithOneNeighbor():
    trips = loadData('./TimeSeriesPredictionTrain.csv');
    features, classes = getFeatureResultFormat(trips)
    train, test = splitTestTrain(features, classes, .8);
    Xtr, Ytr = train;
    Xte, Yte = test;

    print(Xte);

    Xtr = np.asarray(Xtr);
    print(Xtr);
    Xte = np.asarray(Xte);    
    print(Xte);
    Ytr = np.asarray(Ytr);
    print(Ytr);
    Yte = np.asarray(Yte);
    print(Yte);

    # tf Graph Input
    xtr = tf.placeholder("float", [None, 2])
    xte = tf.placeholder("float", [2])

    # Nearest Neighbor calculation using L1 Distance
    # Calculate L1 Distance
    distance = tf.reduce_sum(tf.abs(tf.add(xtr, tf.negative(xte))), reduction_indices=1)
    # Prediction: Get min distance index (Nearest neighbor)
    pred = tf.arg_min(distance, 0)

    accuracy = 0.

    # Initializing the variables
    init = tf.global_variables_initializer()

    # Launch the graph
    with tf.Session() as sess:
        sess.run(init)

        # loop over test data
        for i in range(len(Xte)):
            # Get nearest neighbor
            nn_index = sess.run(pred, feed_dict={xtr: Xtr, xte: Xte[i, :]})
            # Get nearest neighbor class label and compare it to its true label
            ##print("Test", i, "Prediction:", np.argmax(Ytr[nn_index]), \
            ##   "True Class:", np.argmax(Yte[i]))
            print("Test", i, "Prediction:", Ytr[nn_index], \
               "True Class:", Yte[i])

            # Calculate accuracy
            if Ytr[nn_index] == (Yte[i]):#Do this as a percent?
                accuracy += 1./len(Xte)
        print("Done!")
        print("Accuracy:", accuracy)



#runWithOneNeighbor();

def runWithKNeighbors(K):
    trips = loadData('./TimeSeriesPredictionTrain.csv');
    features, classes = getFeatureResultFormat(trips)
    train, test = splitTestTrain(features, classes, .8);
    Xtr, Ytr = train;
    Xte, Yte = test;


    Xtr = np.asarray(Xtr);
    print(Xtr);
    Xte = np.asarray(Xte);    
    print(Xte);
    Ytr = np.asarray(Ytr);
    print(Ytr);
    Yte = np.asarray(Yte);
    print(Yte);

    # tf Graph Input
    xtr = tf.placeholder("float", [None, 2])
    ytr = tf.placeholder("float", Ytr.shape)
    xte = tf.placeholder("float", [2])


    # Euclidean Distance
    distance = tf.negative(tf.sqrt(tf.reduce_sum(tf.square(tf.subtract(xtr, xte)), reduction_indices=1)))
    # Prediction: Get min distance neighbors
    values, indices = tf.nn.top_k(distance, k=K, sorted=False)

    nearest_neighbors = []
    for i in range(K):
        nearest_neighbors.append(tf.argmax(ytr[indices[i]], 0))

    neighbors_tensor = tf.stack(nearest_neighbors)
    y, idx, count = tf.unique_with_counts(neighbors_tensor)
    pred = tf.slice(y, begin=[tf.argmax(count, 0)], size=tf.constant([1], dtype=tf.int64))[0]

    accuracy = 0.

    # Initializing the variables
    init = tf.initialize_all_variables()

    # Launch the graph
    with tf.Session() as sess:
        sess.run(init)

        # loop over test data
        for i in range(len(Xte)):
            # Get nearest neighbor
            nn_index = sess.run(pred, feed_dict={xtr: Xtr, ytr: Ytr, xte: Xte[i, :]})
            # Get nearest neighbor class label and compare it to its true label
            print("Test", i, "Prediction:", nn_index,
                 "True Class:", np.argmax(Yte[i]))
            #Calculate accuracy
            if nn_index == np.argmax(Yte[i]):
                accuracy += 1. / len(Xte)
        print("Done!")
        print("Accuracy:", accuracy)



runWithKNeighbors(4);
























