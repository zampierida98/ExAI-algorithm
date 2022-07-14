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
        bow[column] = dataset[column].value_counts()
    return bow

def p1(dataset):
    '''
    Calcolo: Se in una colonna un valore è outlier (sotto media-devst) sostituiscilo con NULL
    Outpit: Same dataset, with some column marked by NULL in places
    '''
    abs_freq = p0(dataset) # frequenze assolute per ogni colonna

    for column in list(dataset.columns):
        mean = abs_freq[column].mean()
        std = abs_freq[column].std()
        tmp = abs_freq[column][abs_freq[column] < mean-std].to_dict()
        dataset.loc[dataset[column].isin(tmp.keys()), column] = np.NaN
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
    std = df_grupped['size'].std()

    # tengo le righe che verificano ANOVA
    df_grupped = df_grupped.loc[mean-std<=df_grupped['size'], list(dataset.columns)]

    # tengo solo le righe che hanno i valori che appartengono alle righe sopra trovate
    for column in list(dataset.columns):
        dataset = dataset[dataset[column].isin(list(df_grupped[column].values))]

    # se la original_len == len(dataset) allora non sono state fatte eliminate righe
    return dataset, original_len != len(dataset)

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

def p6(dataset, var_name_verbose, pos_class_value,neg_class_value):
    '''
    Calcolo:When the dataset is marked as exemplified, for each row compute the corresponding set of literals, 
            and mark it with positive or negative label, when it derives the class/not class respectively
    Output: A set of literals with positive or negative mark, and the mark exemplified
    '''
    import string

    rules = dict()
    columns_name = list(dataset.columns)    # nomi delle colonne del dataset
    variables = string.ascii_lowercase      # nomi delle variabili

    # per ogni riga del dataset
    for irow in range(len(dataset)):
        row = dataset.iloc[[irow]].values.tolist()[0]
        sgn = '-'
        if pos_class_value in row:
            sgn = '+'
            row.remove(pos_class_value)
        else:
            row.remove(neg_class_value)
        
        # trasformo le stringhe di bit in variabili

        rule = set()
        i = 0
        for bitstring in row:
            # per i NaN che ora sono stringa epsilon non viene eseguito questo ciclo
            for n in range(len(bitstring)):
                if var_name_verbose:
                    rule.add( ('-' if bitstring[n] == '0' else '') + variables[n] + '_' + columns_name[i])
                else:
                    rule.add( ('-' if bitstring[n] == '0' else '') + variables[n] + '_' + str(i))
            i += 1

        # aggiungo la regola
        rules[frozenset(rule)] = sgn
    
    return rules

def p7(dataset, var_name_verbose, pos_class_value,neg_class_value):
    '''
    Calcolo:For every combination of literals appearing in the input dataset marked as positive (or negative) 
            count the occorrences of the same combination and add the computed number to the bag in correspondence 
            with the combination
    Output: A bag of rules with positive or negative mark and the mark proportional
    '''
    import string

    bow = dict()
    columns_name = list(dataset.columns)    # nomi delle colonne del dataset
    variables = string.ascii_lowercase      # nomi delle variabili

    # per ogni riga del dataset
    for irow in range(len(dataset)):
        row = dataset.iloc[[irow]].values.tolist()[0]
        sgn = '-'
        # creo una tupla dove so che l'ultimo elemento è + o -
        if pos_class_value in row:
            row.remove(pos_class_value)
            sgn = '+'
        else:
            row.remove(neg_class_value)

        # trasformo le stringhe di bit in variabili
        rule = []
        i = 0
        for bitstring in row:
            # per i NaN che ora sono stringa epsilon non viene eseguito questo ciclo
            for n in range(len(bitstring)):
                if var_name_verbose:
                    rule.append( ('-' if bitstring[n] == '0' else '') + variables[n] + '_' + columns_name[i])
                else:
                    rule.append( ('-' if bitstring[n] == '0' else '') + variables[n] + '_' + str(i))
            i += 1
        
        # chiavi immutable
        bow[(frozenset(rule), sgn)] = bow.get( (frozenset(rule), sgn), 0) + 1
    
    return bow


def main_preprocessing(dataset_path, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=False, sep=','):
    dataset = pd.read_csv(dataset_path, sep=sep)

    print(">> Creazione delle regole iniziata\n")

    ####################### DA TOGLIERE ######################
    ####################### DA TOGLIERE ######################
    ####################### DA TOGLIERE ######################
    ####################### DA TOGLIERE ######################
    # dataset = dataset.drop(columns=['timestamp', 'sleep_log_entry_id']) #da togliere poi

    # # aggiungo una colonna fittizzia che al passo p2 dovrebbe venir eliminata
    # dataset['elim'] = np.NaN

    # # aggiungo la colonna classe perchè questo dataset di test non ce l'ha
    # dataset[class_column_name] = np.random.choice(['class', 'NON-class'], len(dataset), p=[0.5, 0.5])

    if bool_debug:
        print("Originale")
        print(dataset)

    ####################### FINE ######################
    ####################### FINE ######################
    ####################### FINE ######################
    ####################### FINE ######################

    # salvo e rimuovo la colonna 'class_column_name' per riaggiungerla quando tornerà comoda
    class_column = dataset[class_column_name]
    dataset = dataset.drop([class_column_name], axis=1)


    changings = True
    mark = None
    while changings:
        changings = False

        print(">>", "Passo 1")
        dataset = p1(dataset)
        if bool_debug:
            print(dataset)

        print(">>", "Passo 2")

        dataset = p2(dataset)
        if bool_debug:
            print(dataset)

        print(">>", "Passo 3: ottengo info sul tipo di dataset (se possibile)")

        mark = p3(dataset)
        print('mark =', mark)

        # DA TOGLIERE la riga sotto PERCHE' SERVE SOLO PER I TEST
        # mark = 'proportional'
        # #######################################################

        print(">>", "Decisione 1")
        # ### D1 ### # When the dataset is marked as exemplified, go to step P5
        if mark == 'exemplified':
            # sapendo che changings = False dall'inizio il continue equivale ad un break
            continue
        else:
            print(">>", "Passo 4")
            dataset, changings = p4(dataset)
            print(">>", "Decisione 2")
            # ### D2 ### # When step P4 has eliminated at least one row, go to P1, otherwise go to P5
            print("Changings =", changings)
        
        if bool_debug:
            print(dataset)
    
    print(">>", "Passo 5")
    if mark == None:
        # Shannon Map sul dataset None non deve applicarsi anzi. Se none l'algoritmo si ferma e
        # non produce output
        print("Mark = None. L'algoritmo si ferma e non produce output")
        return None, None

    dataset = p5(dataset)
    if bool_debug:
        print(dataset)

    # riaggiungo la colonna di classe
    dataset[class_column_name] = class_column
    
    rules = None
    if mark == 'exemplified':
        print(">>", "Passo 6")
        rules = p6(dataset, output_var_name_verbose,  pos_class_value,neg_class_value)
    
    #if mark == 'proportional':
    else:
        print(">>", "Passo 7")
        rules = p7(dataset, output_var_name_verbose, pos_class_value,neg_class_value)

    ####### DA TOGLIERE POI ###########
    #rules = p7(dataset, output_var_name_verbose, pos_class_value,neg_class_value)
    ###################################
    
    if bool_debug:
        print(rules)
    
    print("\n>> Creazione delle regole completata")
    
    return rules, mark

# CONSTANT
# VARIABLES
dataset_path = './dataset/dataset.csv'
output_var_name_verbose = False
class_column_name = 'CLASS'
pos_class_value = 'class'
neg_class_value = 'NON-class'
bool_debug = False

# MAIN

if __name__ == "__main__":
    main_preprocessing(dataset_path, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=bool_debug)