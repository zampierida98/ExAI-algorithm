'''
Main
'''

# IMPORT
import preprocessing as pp
import shrink_exemplified as se
import shrink_proportional as sp
import argparse

# FUNCTIONS
def save_on_file(rules, mark, output_path):
    with open(output_path, 'w') as fout:
        for k in rules:
            if mark == 'exemplified':
                fout.write(f'{tuple(k)}{rules[k]}\n'.replace("'", ""))
            else:
                fout.write(f'{tuple(k[0])}{k[1]}{rules[k]}\n'.replace("'", ""))

def evaluation(testset, rules, superior_relation, shannon_map, class_column_name, pos_class_value, neg_class_value):
    '''
    Calcolo: utilizza le regole per determinare la classe delle istanze
    Output: la confusion matrix
    '''
    import string
    variables = string.ascii_lowercase      # nomi delle variabili
    columns_name = list(dataset.columns)

    conf_matrix = [[0, 0]]*3 # una riga per ognuno dei risultati di classificazione
    for irow in range(len(testset)):
        row = dataset.iloc[[irow]].values.tolist()[0]
        _map = shannon_map#[]
        _class = '-'
        if pos_class_value in row:
            _class = '+'
            row.remove(pos_class_value)
        else:
            row.remove(neg_class_value)
        

    return conf_matrix
    

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

    import pandas as pd
    from sklearn.model_selection import train_test_split
    dataset = pd.read_csv(args.dataset_path, sep=args.sep)
    #train, test = train_test_split(dataset, test_size = 0.1) # , stratify=dataset[list(dataset.columns)[1:]]

    # https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedShuffleSplit.html
    from sklearn.model_selection import StratifiedShuffleSplit

    X = dataset.drop(columns=args.class_column_name)
    y = dataset[args.class_column_name]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=0)
    for train_index, test_index in sss.split(X, y):
        print("split")
        X_train, X_test = X.loc[train_index], X.loc[test_index]
        y_train, y_test = y.loc[train_index], y.loc[test_index]
    print(len(X_train), len(X_test), len(y_train), len(y_test))

    train = X_train.copy()
    train[args.class_column_name] = y_train
    print(X_train.shape, y_train.shape, train.shape)

    test = X_test.copy()
    test[args.class_column_name] = y_test
    print(X_test.shape, y_test.shape, test.shape)


    rules, mark, shannon_map = pp.main_preprocessing(train,
                                        True,                   # output_verbose
                                        args.class_column_name,
                                        args.pos_class_value,
                                        args.neg_class_value,
                                        bool_debug=args.bool_debug_preprocessing,
                                        null_value=args.null_value)
    print("#"*59)

    print("#"*59)
    print(shannon_map)
    print("#"*59)

    if mark == 'exemplified':
        rules, superior_relation = se.main_shrink_exemplified(rules, args.bool_debug)
    elif mark == 'proportional':
        rules, superior_relation = sp.main_shrink_proportional(rules, args.bool_debug, args.threshold)
    else:
        # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
        exit()

    print("#"*59)

    #save_on_file(rules, mark, args.output_path)

    conf_matrix = evaluation(args.class_column_name, args.pos_class_value, args.neg_class_value)
    print(conf_matrix)

    print(f"Salvataggio completato in {args.output_path}")
