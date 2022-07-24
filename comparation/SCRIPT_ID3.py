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

DATASET_PATH = "../dataset/kr-vs-kp.data"
CLASS_COLUMN = "class"
POS_CLASS = "won"
NEG_CLASS = "nowin"

DATASET_PATH = "../dataset/agaricus-lepiota.data"
CLASS_COLUMN = "class"
POS_CLASS = "p"
NEG_CLASS = "e"

DATASET_PATH = "../dataset/Balloons/yellow-small+adult-stretch.data"
CLASS_COLUMN = "inflated"
POS_CLASS = "T"
NEG_CLASS = "F"

DATASET_PATH = "../dataset/car.data"
CLASS_COLUMN = "class"
POS_CLASS = "acc"
NEG_CLASS = "unacc"

""" # RecursionError: maximum recursion depth exceeded while calling a Python object
DATASET_PATH = "../dataset/sepsis_survival_dataset/s41598-020-73558-3_sepsis_survival_study_cohort.csv"
CLASS_COLUMN = "hospital_outcome_1alive_0dead"
POS_CLASS = 1
NEG_CLASS = 0 """


if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    df = df.replace({MISSING:np.NaN})
    
    # drop columns with only missing values
    df = df.dropna(axis=1, how='all')

    # drop rows with missing values
    #df = df.dropna()

    # split
    train_data, test_data = train_test_split(df, test_size=0.3, stratify=df[CLASS_COLUMN])

    # fit
    tree = Id3Classifier.id3(train_data, CLASS_COLUMN)
    print(tree)

    # predict & evaluate
    metrics = Id3Classifier.evaluate(tree, test_data, CLASS_COLUMN, POS_CLASS, NEG_CLASS)
    print("precision:", metrics["precision"])
    print("recall:", metrics["recall"])
    print("accuracy:", metrics["accuracy"])
