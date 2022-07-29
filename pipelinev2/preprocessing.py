'''
Preprocessing: algoritmo da xmls
'''
# IMPORT
import math
import pandas as pd
import numpy as np

# FUNCTIONS

def p0(dataset, bool_debug=False):
    '''
    Calcolo: per ogni colonna determino la frequenza di ogni valore
    Output:  bow di tipo 'dict' della forma 'colonna:{valore:freq.}'
    '''
    bow = {}
    for column in list(dataset.columns):
        bow[column] = dataset[column].value_counts()
    if bool_debug:
        print(bow)
    return bow

def p1(dataset, bool_debug=False):
    '''
    Calcolo: Se in una colonna un valore è outlier (sotto media-devst) sostituiscilo con NULL
    Outpit: Same dataset, with some column marked by NULL in places
    '''
    abs_freq = p0(dataset, bool_debug=bool_debug) # frequenze assolute per ogni colonna

    for column in list(dataset.columns):
        mean = abs_freq[column].mean()
        std = abs_freq[column].std()
        if bool_debug:
            print(f">>> colonna={column} -- media:{mean}, std:{std}")
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


def p3(dataset, bool_debug=False):
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

    if bool_debug:
        print(f">>> R={R}, r={r}, R/r={R/r}, N={N}, Nln(N)={N*np.log(N)}")

    if R/r < N:
        mark = 'exemplified'
    elif R/r > N*np.log(N):     #N**2:
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

def p5(dataset, bool_debug=False):
    '''
    Calcolo: Shannon Map
    Output: A binary univariate dataset with NULL elements and a mark
    '''
    shannon_map = {}

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
        shannon_map[column] = _map

        if bool_debug:
            print(f">>> Shannon map per {column}:", _map)
    
    # rimuovo i nan
    return dataset, shannon_map

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
        row = dataset.iloc[[irow]].values.tolist()[0] # l'ordine è lo stesso di columns_name 
        sgn = '-'
        # l'ultimo elemento è la classe. Controllo se pos_class_value == row[-1]
        if pos_class_value == row[-1]:
            sgn = '+'
        row = row[:-1] # tolgo l'ultimo elemento che è la classe
        
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
        row = dataset.iloc[[irow]].values.tolist()[0] # l'ordine è lo stesso di columns_name 
        sgn = '-'
        # l'ultimo elemento è la classe. Controllo se pos_class_value == row[-1]
        if pos_class_value == row[-1]:
            sgn = '+'
        row = row[:-1] # tolgo l'ultimo elemento che è la classe

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


def main_preprocessing(dataset, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=False, null_value='?'):
    print(">> Creazione delle regole iniziata\n")

    if bool_debug:
        print("Originale")
        print(dataset)
    
    # conversione a stringa per evitare problemi con pos_class_value,neg_class_value (passati come stringhe da parametro)
    for column in list(dataset.columns):
        dataset[column] = dataset[column].astype(str)

    # salvo e rimuovo la colonna 'class_column_name' per riaggiungerla quando tornerà comoda    
    class_column = dataset[class_column_name]
    dataset = dataset.drop([class_column_name], axis=1)

    # rimpiazzo i null value con NaN
    dataset = dataset.replace({null_value:np.NaN})

    # variabili di ciclo (changings) e tipo del dataset (mark)
    changings = True
    mark = None
    while changings:
        changings = False

        print(">>", "Passo 1")
        dataset = p1(dataset, bool_debug=bool_debug)
        if bool_debug:
            print(dataset)

        print(">>", "Passo 2")

        dataset = p2(dataset)
        if bool_debug:
            print(dataset)

        print(">>", "Passo 3: ottengo info sul tipo di dataset (se possibile)")

        mark = p3(dataset, bool_debug=bool_debug)
        print('mark =', mark)

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
        return None, None, None

    dataset, shannon_map = p5(dataset, bool_debug=bool_debug)
    if bool_debug:
        print(dataset)

    # riaggiungo la colonna di classe
    # inserisco la classe come ultima colonna del DataFrame
    dataset.insert(len(dataset.columns), class_column_name, class_column) # dataset[class_column_name] = class_column
    
    rules = None
    if mark == 'exemplified':
        print(">>", "Passo 6")
        rules = p6(dataset, output_var_name_verbose, pos_class_value, neg_class_value)
    
    #if mark == 'proportional':
    else:
        print(">>", "Passo 7")
        rules = p7(dataset, output_var_name_verbose, pos_class_value,neg_class_value)

    if bool_debug:
        print(rules)
    
    print("\n>> Creazione delle regole completata")
    
    return rules, mark, shannon_map


# CONSTANT
# VARIABLES
dataset_path = './dataset/dataset.csv'
output_var_name_verbose = False
class_column_name = 'CLASS'
pos_class_value = 'class'
neg_class_value = 'NON-class'
bool_debug = False
null_value = '?'

# MAIN
if __name__ == "__main__":
    main_preprocessing(dataset_path, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=bool_debug, null_value=null_value)