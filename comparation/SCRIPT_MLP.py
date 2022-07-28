"""
SCRIPT CHE TESTA MLP (Multi Layer Perceptron)
Codice da: https://machinelearninggeek.com/multi-layer-perceptron-neural-network-using-python/
"""

# IMPORT
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import precision_score, recall_score, accuracy_score

# VARIABLES
MISSING = "?"

DATASET_PATH = "../dataset/cell_samples.csv"
CLASS_COLUMN = "Class"
POS_CLASS = 2
NEG_CLASS = 4

DATASET_PATH = "../dataset/sepsis_survival_dataset/s41598-020-73558-3_sepsis_survival_study_cohort.csv"
CLASS_COLUMN = "hospital_outcome_1alive_0dead"
POS_CLASS = 1
NEG_CLASS = 0

POS_CLASS = 0  # dopo il Label Encoding
NEG_CLASS = 1  # dopo il Label Encoding

DATASET_PATH = "../dataset/kr-vs-kp.data"
CLASS_COLUMN = "class"

DATASET_PATH = "../dataset/agaricus-lepiota.data"
CLASS_COLUMN = "class"

DATASET_PATH = "../dataset/car.data"
CLASS_COLUMN = "class"


if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    df = df.replace({MISSING:np.NaN})
    
    # drop columns with only missing values
    df = df.dropna(axis=1, how='all')

    # drop rows with missing values
    df = df.dropna()

    # Creating label encoder
    le = preprocessing.LabelEncoder()

    # Converting string labels into numbers
    for column in list(df.columns):
        if df[column].dtype == "object":
            df[column] = le.fit_transform(df[column])

    # Split the dataset
    X = df.drop(columns=CLASS_COLUMN)
    y = df[CLASS_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y)

    # Create model object
    clf = MLPClassifier(hidden_layer_sizes=(6,5),
                        random_state=5,
                        verbose=False,
                        learning_rate_init=0.01)

    # Fit data onto the model
    clf.fit(X_train, y_train)

    # dimensione = somma fanout totale dei nodi * numero nodi
    # https://scikit-learn.org/stable/modules/neural_networks_supervised.html
    #print(clf.coefs_, len(clf.coefs_), clf.n_layers_, clf.n_outputs_)  # pesi, layer con frecce in ingresso, input+hiddens+output, output
    fanout = 0
    nodes = 0
    #zero = []
    for i in range(len(clf.coefs_)):
        #print(clf.coefs_[i].shape)
        #for j in clf.coefs_[i]:
            #zero.append(0 in j or 0.0 in j)

        if i != 0:
            fanout += (clf.coefs_[i].shape[0] * clf.coefs_[i].shape[1])
        nodes += clf.coefs_[i].shape[1]
        #print(fanout, nodes)
    #print(True in zero)
    print("dimension:", fanout * nodes)

    # Make prediction on test dataset
    ypred = clf.predict(X_test)

    # Evaluate the Model
    print("precision:", precision_score(y_test, ypred, pos_label=POS_CLASS))
    print("recall:", recall_score(y_test, ypred, pos_label=POS_CLASS))
    print("accuracy:", accuracy_score(y_test, ypred))
