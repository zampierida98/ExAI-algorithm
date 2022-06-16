'''
Preprocessing: algoritmo da xmls
'''
# IMPORT
import pandas as pd
import numpy as np

# FUNCTIONS
def p1(dataset):
    '''
    Calcolo: Se in una colonna un valore è outlier (sotto media-devst) sostituiscilo con NULL
    Outpit: Same dataset, with some column marked by NULL in places
    '''
    for column in list(dataset.columns):
        mean = dataset[column].mean()
        std = dataset[column].std()
        dataset.loc[mean-std>dataset[column], column] = np.NaN
    return dataset

def p2(dataset):
    '''
    Calcolo: Se in una colonna ci sono solo due valori di cui uno NULL oppure un solo valore, scarta la colonna
    Output: Same dataset with possibly less columns
    '''
    col_to_del = []
    for column in list(dataset.columns):
        # <= perché se avessi una colonna di soli NaN non avrei valori e quindi il metodo ritornerebbe 0
        if dataset[column].nunique(dropna=True) <= 1:
            col_to_del.append(column)

    return dataset.drop(columns=col_to_del)

def p3(dataset):
    '''
    Calcolo:  Compute the number R/r where R is the number of rows and r is the number of combinations in the dataset
            - If R/r is less than N (number of columns), mark the dataset as exemplified
            - If R/r is greater than N^2, mark the dataset as proportional
    
    Output: Same dataset with  possibly a mark
    '''
    mark = None
    R = len(dataset)
    r = 1 # combinazioni di valori. Combinazione nel senso di calcolo combinatorio
    N = len(list(dataset.columns))

    for column in list(dataset.columns):
        r *= dataset[column].nunique(dropna=True)

    if R/r < N:
        mark = 'exemplified'
    elif R/r > N**2:
        mark = 'proportional'
    return mark

def p5(dataset):
    '''
    Calcolo: Shannon Map
    Output: A binary univariate dataset with NULL elements and a mark
    '''
    return dataset

def p4(dataset):
    '''
    Calcolo:When the dataset is not marked as exemplified, 
            compute the outliers on the distirbution of R/r based on ANOVA (mean-devst) and delete them
    
    Output: Same dataset with possibly less rows
    '''
    at_least_one_deleted = False
    return dataset, at_least_one_deleted

# CONSTANT
# VARIABLES
dataset_path = './dataset/dataset.csv'
# MAIN

if __name__ == "__main__":
    dataset = pd.read_csv(dataset_path)
    dataset = dataset.drop(columns=['timestamp', 'sleep_log_entry_id']) #da togliere poi
    

    # aggiungo una colonna fittizzia che al passo p2 dovrebbe venir eliminata
    dataset['elim'] = np.NaN

    print("Originale")
    print(dataset)

    chanings = True
    while chanings:
        chanings = False

        print("Passo uno")
        dataset = p1(dataset)
        print(dataset)

        print("Passo due")

        dataset = p2(dataset)
        print(dataset)

        print("Passo tre: ottengo info sul tipo di dataset (se possibile)")

        mark = p3(dataset)
        print(mark)

        print("Decisione 1")
        # ### D1 ### #
        if mark == 'exemplified':
            dataset = p5(dataset)
        else:
            dataset, chanings = p4(dataset)