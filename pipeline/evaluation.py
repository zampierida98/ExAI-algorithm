'''
Modulo per la valutazione del modello
'''

# IMPORT
import numpy as np
import shrink_exemplified as se


# FUNCTIONS

def adapt_test_set(testset, shannon_map, class_column_name, pos_class_value, null_value):
    '''
    Calcolo: dato il testset si va a generare una lista di coppie dove il primo elemento è il classico frozenset 
            che rappresenta l'istanza, mentre il secondo è la classe.
    Output: lista di coppie della forma (frozenset(letterali dell'istanza), classe)
    '''
    
    # variables serve per la funzione interna 'get_rule_from_binary'
    import string
    variables = string.ascii_lowercase      # nomi delle variabili

    def get_rule_from_binary(bitstring, col_name):
        '''
        Calcolo: dal bitstring in ingresso e dal nome della colonna viene creato il set di letterali corrispondenti 
                a tale parametri in ingresso
        Output: regola senza l'informazione di classe
        '''
        rule = set()
        
        # per ogni carattere della stringa binaria
        for n in range(len(bitstring)):
            # nella pipeline siamo verbose e quindi sicuri che col_name rappresenta il nome della colonna
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
        row_index = int(testset.iloc[[k]].index.values) # indice del DataFrame dell'istanza alla riga k
        
        # la shannon map potenzialemente non ha la corrispondenza per tutti i valori per tutte le istanze
        try:

            # Si usano solo le colonne della shannon map perché sono alcune potrebbero essere scomparse per 
            # via del passo 2 del preprocessing
            for column in shannon_map:
                _map = shannon_map[column]

                # _get_value ritorna, dato l'indice e il nome della colonna, il valore in quella 'cella' del DataFrame
                col_value = testset._get_value(row_index, column)

                # i null value non vengono considerati come durante la preprocessing. Non sono considerati valori (ovviamente)
                if col_value != null_value:
                    # row è un set quindi per aggiungere un set di letterali (generato da get_rule_from_binary) 
                    # si usa 'set1 = set1.union(set2)'
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
    for rule, _ in test_adapted:
        # pos_evaluation contiene le regole di rules (il nostro modello: le regole non monotone) di segno '+' 
        # che si attivano rispetto alla regola rule (istanza del test set). Neg_evaluation è lo stesso di pos_evaluation
        # solo per le regole di rules segno '-'
        pos_evaluation = []
        neg_evaluation = []

        # marco le regole utilizzate inserendole in una delle due liste pos_evalutation e neg_evaluation
        for k in rules:
            # perché una regola del modello NMR sia attiva è necessario che la regola sia un sottoinsieme
            # dell'istanza del testset trasformata (per trasformata si intende convertita in set di letterali)
            inner_set = None
            if mark == 'exemplified':
                inner_set = se.get_the_inner_set(rule, k)
                if inner_set == k:
                    if rules[k] == '+':
                        pos_evaluation.append(k)
                    else:
                        neg_evaluation.append(k)
            else:
                inner_set = se.get_the_inner_set(rule, k[0])
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
        
        else: # caso in cui pos_evaluation e neg_evaluation hanno delle regole che sono state attivate
            class_estimation = '?'

            # ciclo sui positivi per trovarne uno che batte tutti i negativi
            for p in pos_evaluation:
                count = 0 # questa variabile conta il numero di regole negative dominate/battute
                for n in neg_evaluation:
                    if (n, p) not in superior_relation:
                        break
                    count += 1
                # se non ho mai interrotto il ciclo ovvero c'è una regola positiva che batte tutte le negative
                # interrompo il ciclo esterno ed etichetto come positiva l'istanza
                if count == len(neg_evaluation):
                    class_estimation = '+'
                    break # rompe il ciclo for esterno
            
            # ho class_estimation='?' se alla fase precedente non sono riusciuto a trovare la regola positiva
            # che batte tutte le negative e quindi class_estimation è rimasto invariato
            if class_estimation == '?':
                # ciclo sui negativi per trovarne uno che batte tutti i positivi
                for n in neg_evaluation:
                    count = 0 # questa variabile conta il numero di regole positive dominate/battute
                    for p in pos_evaluation:
                        if (p, n) not in superior_relation:
                            break
                        count += 1
                    # se non ho mai interrotto il ciclo ovvero c'è una regola negativa che batte tutte le positive
                    # interrompo il ciclo esterno ed etichetto come negativa l'istanza
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

    SIGN_map = {'+': 0, '-':1, '?':2} # diz che mappa i segni +,-,? all'indice della riga/colonna della confusion matrix

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
    
    SIGN_map = {'+': 0, '-':1, '?':2} # diz che mappa i segni +,-,? all'indice della riga/colonna della confusion matrix

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

# MAIN
if __name__ == "__main__":
    pass