'''
Pipeline main
'''

# IMPORT
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
import preprocessing as pp
import shrink_exemplified as se
import shrink_proportional as sp
import argparse

# FUNCTIONS
def split_procedure(dataset, test_size=0.1):
    '''
    Calcolo: esegue lo split del dataset
    Output: ritorna il train e il test set
    '''
    X = dataset.drop(columns=args.class_column_name)
    y = dataset[args.class_column_name]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=0)

    for train_index, test_index in sss.split(X, y):
        X_train, X_test = X.loc[train_index], X.loc[test_index]
        y_train, y_test = y.loc[train_index], y.loc[test_index]

    # TRAIN
    X_train[args.class_column_name] = y_train

    # TEST
    X_test[args.class_column_name] = y_test

    return X_train, X_test

def adapt_test_set(testset, shannon_map, class_column_name, pos_class_value, null_value):
    '''
    Calcolo: dato il testset si va a generare una lista di coppie dove il primo elemento è il classico frozenset che rappresenta
            l'istanza mentre il secondo è la sua classe.
    Output: lista di coppie della forma (frozenset(letterali dell'istanza), classe)
    '''
    def get_rule_from_binary(bitstring, col_name):
        '''
        Calcolo: dal bitstring in ingresso e dal nome della colonna viene creato il set di letterali corrispondenti a tale stringa binaria
        Output: regola senza l'informazione di classe
        '''
        import string
        variables = string.ascii_lowercase      # nomi delle variabili
        rule = set()

        for n in range(len(bitstring)):
            rule.add( ('-' if bitstring[n] == '0' else '') + variables[n] + '_' + col_name)    
        return rule
    
    res = []
    # adatto il test alla procedura del train

    # conversione a stringa per evitare problemi con pos_class_value,neg_class_value (passati come stringhe da parametro)
    for column in list(testset.columns):
        testset[column] = testset[column].astype(str)

    # variabile che conta quante istanze non riescono ad essere convertite
    n_instance_not_transformed = 0

    # per ogni istanza del test set
    for k in range(len(testset)):
        row = set()
        row_index = int(testset.iloc[[k]].index.values) # indice della riga
        
        # la shannon map potenzialemente non ha la corrispondenza per tutti i valori di tutte le istanze
        try:
            # la riga viene creata solo sulle colonne della shannon map perché sono quelle mantenute durante le fasi
            # del preprocessing da p1 a p4  
            for column in shannon_map:
                _map = shannon_map[column]
                col_value = testset._get_value(row_index, column)

                if col_value != null_value:
                    row = row.union( get_rule_from_binary(_map[ str( testset._get_value(row_index, column) ) ], column) )

            raw_class = testset._get_value(row_index, class_column_name)

            res.append( (frozenset(row), '+' if raw_class == pos_class_value else '-') )

        except:
            n_instance_not_transformed += 1

    if n_instance_not_transformed > 0:
        print("\nNella shannon map è assente uno o più valori per la conversione delle istanze")
        print(f"Non sono state trasformate {n_instance_not_transformed} su un tot. di {len(testset)}.\n")

    return res

def evaluation(test_adapted, rules, superior_relation, mark):
    # evaluation mantiene lo stesso ordine di test_adapted
    evaluation = []

    # per ogni istanza del test set    
    for instance, _ in test_adapted:
        # tengo due variabili per la stima della classe di una istanza. Pos è per regole positive mentre neg per le negative
        pos_evaluation = {}
        neg_evaluation = {}
        for k in rules:
            inner_set = None
            if mark == 'exemplified':
                inner_set = se.get_the_inner_set(instance, k)
                if inner_set == k:
                    if rules[k] == '+':
                        pos_evaluation[k] = 1
                    else:
                        neg_evaluation[k] = 1
            else:
                inner_set = se.get_the_inner_set(instance, k[0])
                if rules[k[0]] == '+':
                    pos_evaluation[k[0]] = 1
                else:
                    neg_evaluation[k[0]] = 1
        
        if len(pos_evaluation) > 0 and len(neg_evaluation) == 0:
            evaluation.append('+')
        elif len(neg_evaluation) > 0 and len(pos_evaluation) == 0:
            evaluation.append('-')
        elif len(neg_evaluation) == 0 and len(pos_evaluation) == 0:
            evaluation.append('?')
        else:
            class_estimation = '?'
            # ciclo sui positivi per trovarne uno che batte tutti i negativi
            for p in pos_evaluation:
                count = 0
                for n in neg_evaluation:
                    if (n, p) not in superior_relation:
                        break
                    count += 1
                # se non ho mai interrotto il ciclo ovvero c'è una regola positiva che batte tutte le negative
                # interrompo e etichetto come positiva l'istanza
                if count == len(neg_evaluation):
                    class_estimation = '+'
                    break # rompe il ciclo for esterno
            
            # se non ho determinato classe positiva allora cerco tra i negativi
            if class_estimation == '?':
                # ciclo sui positivi per trovarne uno che batte tutti i negativi
                for n in neg_evaluation:
                    count = 0
                    for p in pos_evaluation:
                        if (p, n) not in superior_relation:
                            break
                        count += 1
                    # se non ho mai interrotto il ciclo ovvero c'è una regola negativa che batte tutte le positive
                    # interrompo e etichetto come negativa l'istanza
                    if count == len(pos_evaluation):
                        class_estimation = '-'
                        break # rompe il ciclo for esterno
            
            evaluation.append(class_estimation)
    return evaluation

def confusion_matrix(test_rules, evaluation):
    '''
    Calcolo: utilizza il testset adattato per determinare la classe delle istanze
    Output: la confusion matrix
    '''
    
    # FASE DI GENERAZIONE DELLA CONFUSION MATRIX
    print("Generazione della confusion matrix")

    # matrice di confusione 3x2 P,N,? 
    conf_matrix = np.zeros((3,2)) # una riga per ognuno dei risultati di classificazione    

    # per ogni istanza del test set    
    for ind, (instance, ground_truth) in enumerate(test_rules):
        prediction = evaluation[ind]
        conf_matrix[SIGN_map[prediction] ][SIGN_map[ground_truth]] += 1

    print("Confusion matrix generata")
    return conf_matrix

def metrics(matrix):
    '''
    Calcolo: calcola le 3 metriche 
    Output: ACC, PREC, RECALL
    '''
    try:
        ACC = ( (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['-']][SIGN_map['-']]) / 

                (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['+']][SIGN_map['-']] + 
                matrix[SIGN_map['-']][SIGN_map['+']] + matrix[SIGN_map['-']][SIGN_map['-']] + 
                matrix[SIGN_map['?']][SIGN_map['+']] + matrix[SIGN_map['?']][SIGN_map['-']])
            )
    except:
        pass

    try:
        PREC = matrix[SIGN_map['+']][SIGN_map['+']] / (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['+']][SIGN_map['-']] + matrix[SIGN_map['?']][SIGN_map['-']])
    except:
        pass

    try:
        REC = matrix[SIGN_map['+']][SIGN_map['+']] / (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['-']][SIGN_map['+']] + matrix[SIGN_map['?']][SIGN_map['+']])
    except:
        pass

    return ACC, PREC, REC


# CONSTANTS
SIGN_map = {'+': 0, '-':1, '?':2} # per le righe della matrice

# VARIABLES
test_size = 0.05

# MAIN
if __name__ == "__main__":
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@') 
    parser.add_argument('--dataset_path', required=True)
    parser.add_argument('--sep', default=',')
    parser.add_argument('--class_column_name', required=True)
    parser.add_argument('--pos_class_value', required=True)
    parser.add_argument('--neg_class_value', required=True)
    parser.add_argument('--bool_debug_preprocessing', action='store_true')
    parser.set_defaults(bool_debug_preprocessing=False)
    parser.add_argument('--bool_debug', action='store_true')
    parser.set_defaults(bool_debug=False)
    parser.add_argument('--threshold', type=float, default=1)
    parser.add_argument('--output_path', required=True)
    parser.add_argument('--null_value', default='?')
    args = parser.parse_args()

    # Creazione del dataset
    dataset = pd.read_csv(args.dataset_path, sep=args.sep)
    
    # Splitting. Ottengo il train e il test set
    print("Splitting del dataset")
    train, test = split_procedure(dataset, test_size=test_size)
    print("Splitting completato")

    # Preprocessing
    rules, mark, shannon_map = pp.main_preprocessing(train,
                                        True,                   # output_verbose
                                        args.class_column_name,
                                        args.pos_class_value,
                                        args.neg_class_value,
                                        bool_debug=args.bool_debug_preprocessing,
                                        null_value=args.null_value)
    print("#"*59)

    # Shrinking esemplificativo o proporzionale
    if mark == 'exemplified':
        rules, superior_relation = se.main_shrink_exemplified(rules, args.bool_debug)
    elif mark == 'proportional':
        rules, superior_relation = sp.main_shrink_proportional(rules, args.bool_debug, args.threshold)
    else:
        # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
        exit()

    print("#"*59)

    # Fase di valutazione
    print("FASE DI VALUTAZIONE")

    # trasformo il test set usando lo stesso formato per il train set. Dizionario dove le chiavi sono le istanze 
    # e i valori la classe dell'instanza
    test_adapted = adapt_test_set(test, shannon_map, args.class_column_name, args.pos_class_value, args.null_value)
    # faccio le previsioni col modello ritornando un dizionario con chiave l'istanza trasformata e come valore la classe
    # predetta
    evaluation = evaluation(test_adapted, rules, superior_relation, mark)

    # genero la confusion matrix
    conf_matrix = confusion_matrix(test_adapted, evaluation)
    
    # calcolo le metriche
    ACC, PREC, REC = metrics(conf_matrix)

    print("Risultati ###############")
    print("Confusion matrix")
    print(conf_matrix)
    print(f"ACCURACY={ACC}, PRECISION={PREC}, RECALL={REC}")
