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
def get_parser():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@') 
    parser.add_argument('--dataset_path', required=True)
    parser.add_argument('--sep', default=',')
    parser.add_argument('--output_var_name_verbose', action='store_true')
    parser.set_defaults(output_var_name_verbose=False)
    parser.add_argument('--class_column_name', required=True)
    parser.add_argument('--pos_class_value', required=True)
    parser.add_argument('--neg_class_value', required=True)
    parser.add_argument('--bool_debug_preprocessing', action='store_true')
    parser.set_defaults(bool_debug_preprocessing=False)
    parser.add_argument('--bool_debug', action='store_true')
    parser.set_defaults(bool_debug=False)
    parser.add_argument('--threshold', type=float, default=1)
    parser.add_argument('--output_path', required=True)
    parser.add_argument('--output_path_sup_rel', required=True)
    parser.add_argument('--null_value', default='?')
    # aggiungo l'argomento test_size per realizzare una pipeline automatizzata e generale
    parser.add_argument('--test_size', type=float, default=0.2)
    return parser

def save_on_file(rules, mark, output_path):
    with open(output_path, 'w') as fout:
        for k in rules:
            if mark == 'exemplified':
                fout.write(f'{tuple(k)}{rules[k]}\n'.replace("'", ""))
            else:
                fout.write(f'{tuple(k[0])}{k[1]}{rules[k]}\n'.replace("'", ""))

def save_on_file_superior_relation(superior_relation, output_path):
    with open(output_path, 'w') as fout:
        for (inf, sup) in superior_relation:
            fout.write(f'{tuple(inf)} < {tuple(sup)}\n'.replace("'", ""))

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
    
    # variables serve per la funzione interna 'get_rule_from_binary'
    import string
    variables = string.ascii_lowercase      # nomi delle variabili

    def get_rule_from_binary(bitstring, col_name):
        '''
        Calcolo: dal bitstring in ingresso e dal nome della colonna viene creato il set di letterali corrispondenti a tale stringa binaria
        Output: regola senza l'informazione di classe
        '''
        rule = set()

        for n in range(len(bitstring)):
            # nella pipeline siamo verbose.
            rule.add( ('-' if bitstring[n] == '0' else '') + variables[n] + '_' + col_name)
        return rule
    
    # risultato da ritornare. Conterrà le istanze trasformate come le regole del training set
    res = []


    # conversione a stringa per evitare problemi con pos_class_value,neg_class_value (passati come stringhe da parametro)
    for column in list(testset.columns):
        testset[column] = testset[column].astype(str)

    # variabile che conta quante istanze non riescono ad essere convertite
    n_instance_not_transformed = 0

    # per ogni istanza del test set
    for k in range(len(testset)):
        row = set()
        row_index = int(testset.iloc[[k]].index.values) # indice della riga
        
        # la shannon map potenzialemente non ha la corrispondenza per tutti i valori per tutte le istanze
        try:
            # la riga viene creata solo sulle colonne della shannon map perché sono quelle mantenute durante le fasi
            # del preprocessing da p1 a p4
            for column in shannon_map:
                _map = shannon_map[column]
                # _get_value ritorna dato l'indice e il nome della colonna il valore in quella 'cella' del DataFrame
                col_value = testset._get_value(row_index, column)

                # i null value non vengono considerati come durante la preprocessing. Non sono considerati valori (ovviamente)
                if col_value != null_value:
                    # row è un set quindi per aggiungere il set di letterali si usa 'set1 = set1.union(set2)'
                    row = row.union( get_rule_from_binary(_map[ str( testset._get_value(row_index, column) ) ], column) )

            # la shannon map non include la colonna 'classe' 
            raw_class = testset._get_value(row_index, class_column_name)

            res.append( (frozenset(row), '+' if raw_class == pos_class_value else '-') )

        except:
            # conto le istanze non trasformate
            n_instance_not_transformed += 1

    if n_instance_not_transformed > 0:
        print("\nNella shannon map è assente uno o più valori per la conversione delle istanze")
        print(f"Non sono state trasformate {n_instance_not_transformed} su un tot. di {len(testset)}.\n")

    return res

def evaluation(test_adapted, rules, superior_relation, mark):
    '''
    Calcolo: dal testset trasformato vado a stimare la classe di appartenenza delle diverse instanze
    Output: lista contenente solo la classe delle singole instanze. Viene mantenuto lo stesso ordine delle
            istanze in 'test_adapted'
    '''
    # evaluation mantiene lo stesso ordine di test_adapted
    evaluation = []

    # per ogni istanza del test set. Il ground truth non è necessario
    for instance, _ in test_adapted:
        # tengo due variabili per la stima della classe di una istanza. Pos è per regole positive mentre neg per le negative
        pos_evaluation = []
        neg_evaluation = []

        # marco le regole utilizzate inserendole nelle due liste pos_evalutation e neg_evaluation
        for k in rules:
            inner_set = None
            if mark == 'exemplified':
                inner_set = se.get_the_inner_set(instance, k)
                if inner_set == k:
                    if rules[k] == '+':
                        pos_evaluation.append(k)
                    else:
                        neg_evaluation.append(k)
            else:
                inner_set = se.get_the_inner_set(instance, k[0])
                if inner_set == k[0]:
                    if k[1] == '+':
                        pos_evaluation.append(k[0])
                    else:
                        neg_evaluation.append(k[0])
        
        # EVALUATION PHASE
        if len(pos_evaluation) > 0 and len(neg_evaluation) == 0:
            evaluation.append('+')
        elif len(neg_evaluation) > 0 and len(pos_evaluation) == 0:
            evaluation.append('-')
        elif len(neg_evaluation) == 0 and len(pos_evaluation) == 0:
            evaluation.append('?') # Se non applico nessuna regola allora non conosco la classe
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
                # interrompo il ciclo esterno e etichetto come positiva l'istanza
                if count == len(neg_evaluation):
                    class_estimation = '+'
                    break # rompe il ciclo for esterno
            
            # ho class_estimation='?' se alla fase precedente non sono riusciuto a trovare la regola positiva
            # che batte tutte le negative e quindi class_estimation è rimasto invariato
            if class_estimation == '?':
                # ciclo sui positivi per trovarne uno che batte tutti i negativi
                for n in neg_evaluation:
                    count = 0
                    for p in pos_evaluation:
                        if (p, n) not in superior_relation:
                            break
                        count += 1
                    # se non ho mai interrotto il ciclo ovvero c'è una regola negativa che batte tutte le positive
                    # interrompo il ciclo esterno e etichetto come negativa l'istanza
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
    # matrice di confusione 3x2 P,N,? 
    conf_matrix = np.zeros((3,2)) # una riga per ognuno dei risultati di classificazione    

    # per ogni istanza del test set    
    for ind, (_, ground_truth) in enumerate(test_rules):
        prediction = evaluation[ind]
        conf_matrix[SIGN_map[prediction] ][SIGN_map[ground_truth]] += 1

    return conf_matrix

def metrics(matrix):
    '''
    Calcolo:data la confusion matrix vado a calcolare le diverse metriche. E' una 3x2 dove le righe corrispondono 
            alle predizione mentre le colonne i valori reali.
    
    Output: ACC, PREC, RECALL
    '''
    try:
        ACC = (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['-']][SIGN_map['-']]) / matrix.sum()
    except:
        pass

    try: # TP/ (TP+FP)  <--- VERI CORRETTI CONTRO TUTTI QUELLI CLASSIFICATI COME VERI
        PREC = matrix[SIGN_map['+']][SIGN_map['+']] / (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['+']][SIGN_map['-']])
    except:
        pass

    try: # TP/ (TP+FN)  <--- VERI CORRETTI CONTRO IL TOTALE DEI VERI
        REC = matrix[SIGN_map['+']][SIGN_map['+']] / (matrix[SIGN_map['+']][SIGN_map['+']] + matrix[SIGN_map['-']][SIGN_map['+']] + matrix[SIGN_map['?']][SIGN_map['+']])
    except:
        pass

    return ACC, PREC, REC


# CONSTANTS
SIGN_map = {'+': 0, '-':1, '?':2} # per le righe della matrice

# MAIN
if __name__ == "__main__":
    # argomenti estratti tramite il parser
    parser = get_parser()
    args = get_parser().parse_args()

    # Creazione del dataset
    dataset = pd.read_csv(args.dataset_path, sep=args.sep)
    
    # Splitting. Ottengo il train e il test set
    print("Splitting del dataset")
    train, test = split_procedure(dataset, test_size=args.test_size)
    print("Splitting completato")

    # Preprocessing
    rules, mark, shannon_map = pp.main_preprocessing(train,
                                        True,                   # output_verbose obbligatorio nella pipeline
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
        exit() # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare

    print("#"*59)

    # Fase di salvataggio delle regole per un futuro riutilizzo
    save_on_file(rules, mark, args.output_path)
    save_on_file_superior_relation(superior_relation, args.output_path_sup_rel)

    print(f"Salvataggio completato in {args.output_path}")
    print(f"Salvataggio completato in {args.output_path_sup_rel}")
    print("#"*59)

    # Fase di valutazione
    print("FASE DI VALUTAZIONE")

    # trasformo il test set usando lo stesso formato per il train set. Poiché potrei avere più volte la stessa 
    # instanza, test_adapted è una lista di coppie della forma: (test_rule, real_test_class)
    test_adapted = adapt_test_set(test, shannon_map, args.class_column_name, args.pos_class_value, args.null_value)

    # faccio le previsioni col modello ritornando una lista di previsioni. La lista mantiene lo stesso ordine delle
    # instanze in ingresso.
    evaluation = evaluation(test_adapted, rules, superior_relation, mark)

    # genero la confusion matrix
    conf_matrix = confusion_matrix(test_adapted, evaluation)
    print("Confusion matrix generata")

    # calcolo le metriche
    ACC, PREC, REC = metrics(conf_matrix)

    print("\nRisultati", "#"*49)
    print("Confusion matrix")
    print(conf_matrix)
    print(f"ACCURACY={ACC}, PRECISION={PREC}, RECALL={REC}")

    ####################### ####################### ####################### ####################### #######################
    ####################### ####################### ####################### ####################### #######################
    ####################### ####################### ####################### ####################### #######################
    # Trasformazione delle regole in chiaro
    


    def clear_rules(rules,shannon_map, mark):
        import string
        import itertools

        def incomplete_to_complete_bitstring(incomplete_bitstring):
            '''
            E' una funzione che converte stringhe di questo tipo '0x0' generando tutte le possibili
            combinazioni sostituendo x con 0 e 1
            '''
            res = []

            for i, b in enumerate(incomplete_bitstring):
                if b == 'x':
                    tmp0 = list(incomplete_bitstring)
                    tmp1 = list(incomplete_bitstring)
                    tmp0[i] = '0'
                    tmp1[i] = '1'
                    res += incomplete_to_complete_bitstring("".join(tmp0))
                    res += incomplete_to_complete_bitstring("".join(tmp1))

                    break # si deve fermare al primo x

            # manteniamo solo le stringhe completamente istanziate 
            if incomplete_bitstring.find('x') < 0:
                res.append(incomplete_bitstring)

            return res

        # variabile da ritornare
        res_rules = []

        #reverse shannon map. Invece di avere per ogni colonna dizionari valore:stringabin adesso è stringabin:valore
        rev_shann_map = {col: {v:k for k,v in shannon_map[col].items()} for col in shannon_map}

        # mappa variabile posizione all'interno della stringa binaria
        map_var_pos = {v:i for i,v in enumerate(string.ascii_lowercase)}
        # mappa colonna posizione all'interno della regola in chiaro
        map_colname_pos = {col: ind for ind, col in enumerate(shannon_map.keys())}
        # caso di default di tutte le regole
        default_istance = {col:('x' * len(shannon_map[col][next(iter(shannon_map[col])) ]) ) for col in shannon_map}

        for k in rules:
            # faccio una copia del caso di default
            clear_rule = default_istance.copy()
            for var in (k if mark == 'exemplified' else k[0]):
                
                v = var.split("_")[0] # variabile
                c = var.split("_")[1] # colonna
                b = '1'

                # se ho variabili di questo tipo '-c' allora cambio b a 0 e imposto v ad 'c'
                if len(v) == 2: v = v[1]; b = '0'

                # cambio la stringa in clear_rule e la salvo in tmp
                tmp = list(clear_rule[c])
                tmp[map_var_pos[v]] = b
                clear_rule[c] = "".join(tmp)

            # rimpiazzo le stringhe binarie incomplete con i valori nella shannon map.
            # Genero tutte le possibili combinazioni dalla stringa binaria incompleta e poi
            # converto le stringhe binarie con la mappa associata alla colonna
            for col in clear_rule:
                tmp_map = rev_shann_map[col]
                clear_rule[col] = [tmp_map[bitstring] for bitstring in incomplete_to_complete_bitstring(clear_rule[col])]
            
            # uso il metodo statico di itertools product che esegue un prodotto cartesiano.
            res_rules += list(itertools.product(* (list(clear_rule.values()) + [ [(rules[k] if mark == 'exemplified' else k[1])] ])))
        
        # ritorno le regole in chiaro con anche le chiavi
        return res_rules, list(clear_rule.keys()) + ['class']
    
    def save_clear_rules(clear_rules, colnames, output_path):
        with open(output_path, 'w') as fout:
            for ennupla in clear_rules:
                line = '('
                for i, v in enumerate(ennupla):
                    # sappiamo che è il valore di classe è l'ultimo per come è stato formattata la lista in 'clear_rules'
                    if i == len(colnames) - 1:
                        line = f'{line[0:-2]}){v}'# v è classe
                    else:
                        line += f'{colnames[i]}={v}, '
                fout.write(line + '\n')

    clear_rules, colnames = clear_rules(rules, shannon_map, mark)
    save_clear_rules(clear_rules, colnames, "filepath.txt")
    print("Salvate le regole in chiaro")

