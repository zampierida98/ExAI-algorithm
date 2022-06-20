'''
Preprocessing: algoritmo da xmls
'''
# IMPORT
import math
import pandas as pd
import numpy as np

# FUNCTIONS
def p0(dataset):
    '''
    Calcolo: per ogni colonna determino la frequenza di ogni valore
    Output:  bow di tipo 'dict' della forma 'colonna:{valore:freq.}'
    '''
    bow = {}
    for column in list(dataset.columns):
        bow[column] = dataset[column].value_counts().to_dict()
    return bow

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

def p4(dataset):
    '''
    Calcolo:When the dataset is not marked as exemplified, 
            compute the outliers on the distirbution of R/r based on ANOVA (mean-devst) and delete them
    
    Output: Same dataset with possibly less rows
    '''
    original_len = len(dataset) # lunghezza del dataset originario
    dataset = dataset.replace({np.NaN:''}) # rimpiazzo i NaN con vuoto

    # raggruppo il dataset per tutte le colonne così da avere i campioni di ogni riga univoca e calcolo quante righe
    # (di ogni gruppo di righe uguali) ci sono in ogni bucket con il metodo .size()
    df_grupped = dataset.groupby(dataset.columns.tolist(), as_index=False).size()
    
    # ANOVA
    mean = df_grupped['size'].mean()
    std = df_grupped['size'].mean()
    # tengo le righe che verificano ANOVA
    df_grupped = df_grupped.loc[mean-std>df_grupped['size'], list(dataset.columns)]

    # tengo solo le righe che hanno i valori che appartengono alle righe sopra trovate
    for column in list(dataset.columns):
        dataset = dataset[dataset[column].isin(list(df_grupped[column].values))]

    # se la original_len == len(dataset) allora non sono state fatte eliminate righe
    return dataset, original_len == len(dataset)

def p5(dataset):
    '''
    Calcolo: Shannon Map
    Output: A binary univariate dataset with NULL elements and a mark
    '''
    
    for column in list(dataset.columns):
        # genero la lista di valori di ogni colonna
        list_of_values = list(dataset[column].unique())
        # rimuovo il np.NaN se presente usando il metodo statico di pandas
        list_of_values = [x for x in list_of_values if pd.notnull(x)]
        # n numero di variabili
        n = math.ceil(math.log(len(list_of_values), 2 ) )
        
        # creo una mappa del tipo valore -- cifra binaria corrispondente
        _map = {}
        for i in range(len(list_of_values)):
            # zfill riempie aggiungendo in testa degli 0 fino a raggiungere la lunghezza n
            _map[list_of_values[i]] = format(i, "b").zfill(n)

        _map[np.NaN] = ''
        dataset[column] = dataset[column].replace(_map)
    
    # rimuovo i nan
    return dataset

def p6(dataset):
    '''
    Calcolo:When the dataset is marked as exemplified, for each row compute the corresponding set of literals, 
            and mark it with positive or negative label, when it derives the class/not class respectively
    Output: A set of literals with positive or negative mark, and the mark exemplified
    '''
    rules = dict()

    # per ogni riga del dataset
    for irow in range(len(dataset)):
        row = dataset.iloc[[irow]].values.tolist()[0]
        sgn = '-'
        if 'class' in row:
            sgn = '+'
            row.remove('class')
        else:
            row.remove('NON-class')
        
        # aggiungo la regola
        # non posso agginugere ad un insieme un tipo list poiché è mutable
        rules[tuple(row)] = sgn
    
    return rules


# def p6(dataset):
#     '''
#     Calcolo:When the dataset is marked as exemplified, for each row compute the corresponding set of literals, 
#             and mark it with positive or negative label, when it derives the class/not class respectively
#     Output: A set of literals with positive or negative mark, and the mark exemplified
#     '''
#     import string
#     variables = string.ascii_lowercase

#     # insieme di letterali positivi o negativi
#     result = []
    
#     # per ogni riga del dataset
#     for row in range(len(dataset)):
#         _str = '(' ; i = -1
        
#         # di ogni colonna della riga
#         for column in list(dataset.columns):
#             # incremento l'indice per le lettere
#             i += 1

#             # aggiungiamo l'informazione di classe in fondo
#             if column == 'CLASS':
#                 continue
            
#             bin_string = dataset.iloc[[row]][column].tolist()[0]
#             if pd.isnull(bin_string):
#                 continue
            
#             # analizzo la stringa binaria
#             for j in range(len(bin_string) ):
#                 if bin_string[j] == '1':
#                     _str += variables[j] + str(i)
#                 else:
#                     _str += '-' + variables[j] + str(i)
            
#             _str += ', '

#         _str = _str[:-2] # tolgo gli ultimi due caratteri ', '
#         _str += ')' + ('+' if dataset.iloc[[row]]['CLASS'].tolist()[0] == 'class' else '-')
#         result.append(_str)
#     return result



def p7(dataset):
    '''
    Calcolo:For every combination of literals appearing in the input dataset marked as positive (or negative) 
            count the occorrences of the same combination and add the computed number to the bag in correspondence 
            with the combination
    Output: A bag of rules with positive or negative mark and the mark proportional
    '''
    bow = dict()

    # per ogni riga del dataset
    for irow in range(len(dataset)):
        row = dataset.iloc[[irow]].values.tolist()[0]
        
        # creo una tupla dove so che l'ultimo elemento è + o -
        if 'class' in row:
            row.remove('class')
            row.append('+')
        else:
            row.remove('NON-class')
            row.append('-')
        
        # non posso agginugere ad un insieme un tipo list poiché è mutable
        bow[tuple(row)] = bow.get(tuple(row), 0) + 1
    
    return bow

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

    print("Passo 0")
    bow = p0(dataset)


    chanings = True
    while chanings:
        chanings = False

        print(">>", "Passo 1")
        dataset = p1(dataset)
        print(dataset)

        print(">>", "Passo 2")

        dataset = p2(dataset)
        print(dataset)

        print(">>", "Passo 3: ottengo info sul tipo di dataset (se possibile)")

        mark = p3(dataset)
        print('mark =', mark)

        print(">>", "Decisione 1")
        # ### D1 ### # When the dataset is marked as exemplified, go to step P5
        if mark == 'exemplified':
            print(">>", "Passo 5")
            dataset = p5(dataset)
        elif mark == None:
            # Shannon Map sul dataset None non deve applicarsi anzi. Se none l'algoritmo si ferma e
            # non produce output
            print("Mark = None. L'algoritmo si ferma e non produce output")
            exit()
        else:
            print(">>", "Passo 4")
            dataset, changing = p4(dataset)
            print(">>", "Decisione 2")
            # ### D2 ### # When step P4 has eliminated at least one row, go to P1, otherwise go to P5
            if changing:
                continue # riparte da P1

            print(">>", "Passo 5")
            # altrimenti passa a P5
            dataset = p5(dataset)
        
        print(dataset)
    
    # aggiungo la colonna classe (dovremmo toglierla all'inizio e poi riaggiungerla al dataset)
    class_column = 'CLASS'
    dataset['CLASS'] = np.random.choice(['class', 'NON-class'], len(dataset), p=[0.5, 0.5])
    

    if mark == 'exemplified':
        print(">>", "Passo 6")
        rules = p6(dataset)
        print(rules)

    if mark == 'proportional':
        print(">>", "Passo 7")
        rules = p7(dataset)
        print(rules)