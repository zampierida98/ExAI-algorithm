"""
SCRIPT CHE TESTA L'ALGORITMO ID3 (DECISION TREE)
Codice da: https://www.kaggle.com/code/tareqjoy/easy-id3/notebook
"""

# IMPORT
import numpy as np
import pandas as pd
import Id3Classifier 
from sklearn.model_selection import train_test_split

# VARIABLES
DATASET_PATH = "../dataset/cell_samples.csv"
CLASS_COLUMN = "Class"
MISSING = "?"
POS_CLASS = 2
NEG_CLASS = 4

""" DATASET_PATH = "../dataset/Balloons/adult+stretch.data"
CLASS_COLUMN = "inflated"
MISSING = "?"
POS_CLASS = "T"
NEG_CLASS = "F" """


if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    df = df.replace({MISSING:np.NaN})
    
    # drop columns with only missing values
    df = df.dropna(axis=1, how='all')

    # drop rows with missing values
    #df = df.dropna()

    """ X = df.drop(columns=CLASS_COLUMN)
    y = df[CLASS_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y)
    print(len(X_train), len(X_test), len(y_train), len(y_test))
    print(y_train[:].mean(), y_test[:].mean())

    train_data = X_train.copy()
    train_data[CLASS_COLUMN] = y_train
    print(X_train.shape, y_train.shape, train_data.shape)

    test_data = X_test.copy()
    test_data[CLASS_COLUMN] = y_test
    print(X_test.shape, y_test.shape, test_data.shape) """

    # split
    train_data, test_data = train_test_split(df, test_size=0.3, stratify=df[CLASS_COLUMN])
    #print(train_data[CLASS_COLUMN].mean(), test_data[CLASS_COLUMN].mean())

    # fit
    tree = Id3Classifier.id3(train_data, CLASS_COLUMN)
    print(tree)

    # predict & evaluate
    metrics = Id3Classifier.evaluate(tree, test_data, CLASS_COLUMN, POS_CLASS, NEG_CLASS)
    print("precision:", metrics["precision"])
    print("recall:", metrics["recall"])
    print("accuracy:", metrics["accuracy"])
