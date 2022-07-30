'''
XAI_pipeline rappresenta l'esecuzione del modello completa cioè include:
- split del dataset
- creazione del modello sul trainset
- evaluation del test set
'''

# IMPORT
import pandas as pd
import argparse
from sklearn.model_selection import StratifiedShuffleSplit

import evaluation
import model


# FUNCTIONS
def get_parser():
    '''
    Calcolo: definisco il parser
    Output: parser
    '''
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@') 
    parser.add_argument('--dataset_path', required=True)
    parser.add_argument('--sep', default=',')
    parser.add_argument('--output_var_name_verbose', action='store_true')
    # output_verbose obbligatorio nella pipeline
    parser.set_defaults(output_var_name_verbose=True)
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
    parser.add_argument('--test_size', type=float, default=0.3)
    # opzione per salvare le regole in formato più chiaro
    parser.add_argument('--output_path_clear_rules', default=None)

    return parser

def split_procedure(dataset, test_size=0.3):
    '''
    Calcolo: esegue lo split del dataset
    Output: ritorna il train e il test set
    '''
    # divisione dati e ground truth
    X = dataset.drop(columns=args.class_column_name)
    y = dataset[args.class_column_name]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=0)

    # esegue un solo ciclo in cui viene estratto il train e test set
    for train_index, test_index in sss.split(X, y):
        X_train, X_test = X.loc[train_index], X.loc[test_index]
        y_train, y_test = y.loc[train_index], y.loc[test_index]

    # TRAIN e TEST
    X_train[args.class_column_name] = y_train
    X_test[args.class_column_name] = y_test

    return X_train, X_test

def dimensionality(rules, mark):
    '''
    Calcolo: la dimensione della teoria non monotona. N di teoremi * lunghezza del teorema più grande
    Output: dimensioni del modello
    '''
    _max = 0 # _max contiene la lunghezza del teorema più grande
    # for su ogni regola
    for k in rules:
        if mark == 'exemplified':
            _max = max(_max, len(k))
        else:
            _max = max(_max, len(k[0])) # se proportional k è una coppia della forma (regola, '+'/'-')
    return len(rules), _max # vengono ritornate le due coordinate per calcolare la dimensione del modello

# MAIN
if __name__ == "__main__":
    # ################
    # PIPELINE
    # ################
    
    # argomenti estratti tramite il parser
    args = get_parser().parse_args()
    # Creazione del dataset come pandas.DataFrame
    dataset = pd.read_csv(args.dataset_path, sep=args.sep)
    
    # ################
    # SPLITTING
    # ################

    print("Splitting del dataset")
    train, test = split_procedure(dataset, test_size=args.test_size)
    print("Splitting completato")

    # ################
    # MODEL CREATION
    # ################
    rules, mark, superior_relation, shannon_map = model.model(train, args.output_var_name_verbose, args.class_column_name, 
                                args.pos_class_value, args.neg_class_value, args.null_value, 
                                args.threshold, args.output_path, args.output_path_sup_rel, 
                                args.output_path_clear_rules, args.bool_debug_preprocessing, args.bool_debug)

    # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
    if mark == None:
        exit()
    
    # ################
    # DIMENSIONS
    # ################
    length, width = dimensionality(rules, mark)
    print(f"Dimensionalità del modello: lunghezza={length}, larghezza={width}, dim={length*width}")


    # ################
    # EVALUATION PHASE
    # ################
    print("FASE DI VALUTAZIONE")

    # trasformo il test set usando lo stesso formato per il train set. Poiché potrei avere più volte la stessa 
    # instanza, test_adapted è una lista di coppie della forma: (test_rule, '+'/'-')
    test_adapted = evaluation.adapt_test_set(test, shannon_map, args.class_column_name, args.pos_class_value, args.null_value)

    # faccio le previsioni col modello ritornando una lista di previsioni. La lista mantiene lo stesso ordine delle
    # instanze in ingresso.
    pred = evaluation.evaluation(test_adapted, rules, superior_relation, mark)

    # genero la confusion matrix
    conf_matrix = evaluation.confusion_matrix(test_adapted, pred)
    print("Confusion matrix generata")

    # calcolo le metriche
    ACC, PREC, REC = evaluation.metrics(conf_matrix)

    print("\nRisultati", "#"*49)
    print("Confusion matrix")
    print(conf_matrix)
    print(f"ACCURACY={ACC}, PRECISION={PREC}, RECALL={REC}")
