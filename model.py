'''
Modulo contenente le funzioni riguardanti il modello compreso
'''

# IMPORT
import preprocessing as pp
import shrink_exemplified as se
import shrink_proportional as sp

# FUNCTIONS
def save_on_file(rules, mark, output_path):
    '''
    Calcolo: Salva su file le regole della teoria non monotona nel formato predefinito
    Output: None
    '''
    with open(output_path, 'w') as fout:
        for k in rules:
            if mark == 'exemplified':
                fout.write(f'{tuple(k)}{rules[k]}\n'.replace("'", ""))
            else:
                fout.write(f'{tuple(k[0])}{k[1]}{rules[k]}\n'.replace("'", ""))

def save_on_file_superior_relation(superior_relation, output_path):
    '''
    Calcolo: Salva su file la relazione di superiorità. Formato: (regola1) < (regola2)
    Output: None
    '''
    with open(output_path, 'w') as fout:
        for (inf, sup) in superior_relation:
            fout.write(f'{tuple(inf)} < {tuple(sup)}\n'.replace("'", ""))

def save_clear_rules(clear_rules, colnames, output_path):
    '''
    Calcolo: Salva su file le regole "decifrate" della teoria non monotona con un formato equivalente
            a quello della teoria iniziale
    Output: None
    '''
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

def save_model(rules,mark,superior_relation, shannon_map, output_path, output_path_sup_rel, output_var_name_verbose, output_path_clear_rules, bool_debug):
    '''
    Calcolo: Si preoccupa di salvare su file il modello. Richiama le funzione save_... soprastanti nel file corrente
    Output: None
    '''
    print("#"*59)

    save_on_file(rules, mark, output_path)
    if bool_debug:
        print(superior_relation)
    save_on_file_superior_relation(superior_relation, output_path_sup_rel)

    print(f"Salvataggio completato in {output_path}")
    print(f"Salvataggio completato in {output_path_sup_rel}")

    # se args.output_var_name_verbose è specificato nel file di configurazione allora
    # salvo nel percorso indicato da output_var_name_verbose le clear_rules altrimenti
    # se output_var_name_verbose non è presente nel file di configurazione allora il parser
    # inizializza args.output_var_name_verbose = False.
    if output_var_name_verbose and output_path_clear_rules != None:
        clear_rules_var, colnames = clear_rules(rules, shannon_map, mark)
        save_clear_rules(clear_rules_var, colnames, output_path_clear_rules)
        print(f"Salvataggio completato in {output_path_clear_rules}")
    
    print("#"*59)

def clear_rules(rules, shannon_map, mark):
    '''
    Calcolo: Le regole possono non avere tutti i letterali di ogni colonna (per via della fase di shrinking).
            Per cui l'obiettivo è trovare, partendo da un gruppo di letterali potenzialmente incompleti
            tutte le combinazioni binarie compatibili con quel gruppo di letterali. Ad esempio se una colonna
            è codificata con a,b,c,d,e e per una certa istanza le variabili sono solo a,c,d,e allora quello
            che dobbiamo fare sarà creare tutte le stringhe binarie di lunghezza 5 (# letterali della colonna)
            dove a,c,d,e rimangono uguali mentre per gli altri letterali possiamo avere 0 o 1.
            
            Dopodichè avviene la decodifica cioè da stringa binaria si ottiene il valore della colonna per
            mezzo della shannon_map. 
            
            Infine, viene eseguito il prodotto cartesiano 
            generando tutte le regole "decodificate" concordi alla regola di soli letterali.

    Output: regole della teoria non monotone decifrate ovvero 
            al posto dei letterali ci sarà il valore della colonna corrispondente ai letterali
    '''
    import string
    import itertools

    def incomplete_to_complete_bitstring(incomplete_bitstring):
        '''
        E' una funzione ricorsiva che converte stringhe di questo tipo '0x1x0' generando tutte le possibili
        combinazioni sostituendo x con 0 e 1
        '''
        res = [] #variabile di ritorno

        # ciclo sui caratteri della stringa per trovare il primo x. Poi il ciclo si ferma,
        # perché sarà al passo ricorsivo che viene trovato il successivo x.
        for i, b in enumerate(incomplete_bitstring):
            if b == 'x':
                # le stringhe sono immutable così le trasformo in lista per cambiarne il valore in una certa pos.
                tmp0 = list(incomplete_bitstring)
                tmp1 = list(incomplete_bitstring)
                tmp0[i] = '0'
                tmp1[i] = '1'
                # passi ricorsivi, uno per 0 e uno per 1
                res += incomplete_to_complete_bitstring("".join(tmp0))
                res += incomplete_to_complete_bitstring("".join(tmp1))

                break # si deve fermare al primo x

        # salviamo solo le stringhe completamente istanziate 
        if incomplete_bitstring.find('x') < 0:
            res.append(incomplete_bitstring)

        return res

    # variabile da ritornare
    res_rules = set()

    #reverse shannon map. Invece di avere per ogni colonna dizionari valore:stringabin adesso è stringabin:valore
    rev_shann_map = {col: {v:k for k,v in shannon_map[col].items()} for col in shannon_map}

    # mappa variabile-posizione. Associo ad una variabile la posizione dentro la stringa binaria
    map_var_pos = {v:i for i,v in enumerate(string.ascii_lowercase)}
    
    # istanzo una variabile uguale per tutte le regole.
    default_istance = {col:('x' * len(shannon_map[col][next(iter(shannon_map[col])) ]) ) for col in shannon_map}

    for k in rules:
        # faccio una copia del caso di default
        clear_rule = default_istance.copy()

        # per ogni variabile nella regola
        for var in (k if mark == 'exemplified' else k[0]):
            
            # recupero dal letterale la variabile e la colonna
            v,c = var.split("_", 1) # splitto solo al primo '_' in modo che se la colonna ha nel nome _ tengo l'intero nome
            b = '1'

            # se ho variabili di questo tipo '-c' allora cambio la variabile b in 0 e imposto v ad 'c'
            if len(v) == 2: v = v[1]; b = '0'

            # popolo la stringa clear_rule[c] salvando in posizione map_var_pos[v] il valore di b
            tmp = list(clear_rule[c])
            tmp[map_var_pos[v]] = b
            # da lista ricreo la stringa col metodo join
            clear_rule[c] = "".join(tmp)

        # rimpiazzo le stringhe binarie incomplete con i valori nella shannon map.
        # Genero tutte le possibili combinazioni dalla stringa binaria incompleta e poi
        # converto le stringhe binarie con la reverse shannon map associata alla colonna
        for col in clear_rule:
            # non tutte le stringhe binarie sono presenti nella rev_shann_map. Se ho xxxx e ho solo 10 valori 
            # gli altri 6 non esistono. Non saranno presenti nella mappa
            tmp = []
            for bitstring in incomplete_to_complete_bitstring(clear_rule[col]):
                # aggiungo il valore corrispondente alla codifica binaria solo se la stringa binaria esiste
                # nella rev_shann_map
                try:
                    tmp.append(rev_shann_map[col][bitstring])
                except:
                    pass
            clear_rule[col] = tmp
        
        # uso il metodo statico product di itertools che esegue un prodotto cartesiano.
        for r in list(itertools.product(* (list(clear_rule.values()) + [ [(rules[k] if mark == 'exemplified' else k[1])] ]))):
            res_rules.add(r)
    
    # ritorno le regole in chiaro con anche i nomi delle colonne (compresa la class)
    return res_rules, list(clear_rule.keys()) + ['class']


def model(dataset, output_var_name_verbose, class_column_name, pos_class_value, neg_class_value, null_value, 
        threshold, output_path, output_path_sup_rel, output_path_clear_rules, bool_debug_preprocessing, bool_debug):
    '''
    Calcolo: Richiamo i metodi da altri moduli per costruire il modello. Preprocessing -> Shrinking
    Input: DataFrame che rappresenta il dataset (letto in formato csv)
    Output: teoria NM, tipo di dataset, relazione di superiorità, shannon map (per la fase di validazione)

    Parametri:
    - `output_var_name_verbose`, indica all'algoritmo di usare il nome completo delle colonne nell'output.
    - `class_column_name`, nome della colonna che indica la classe all'interno del dataset.
    - `pos_class_value`, valore corrispondente alla classe positiva.
    - `neg_class_value`, valore corrispondente alla classe negativa.
    - `null_value`, valore nullo utilizzato all'interno del dataset.
    - `threshold`, valore della soglia da utilizzare nello shrinking per dataset proportional.
    - `output_path`, percorso in cui salvare l'output.
    - `output_path_sup_rel`, percorso in cui salvare le coppie di superiorità.
    - `output_path_clear_rules`, percorso in cui salvare la riscrittura delle regole secondo la Shannon Map.
    - `bool_debug_preprocessing`, se True indica all'algoritmo di stampare in console ulteriori informazioni durante la fase di preprocessing.
    - `bool_debug`, se True indica all'algoritmo di stampare in console ulteriori informazioni durante la fase di shrinking.
    '''

    rules, mark, shannon_map = pp.main_preprocessing(dataset,
                                        output_var_name_verbose,
                                        class_column_name,
                                        pos_class_value,
                                        neg_class_value,
                                        bool_debug=bool_debug_preprocessing,
                                        null_value=null_value)
    
    print("#"*59)
    superior_relation = set()
    if mark == 'exemplified':
        rules, superior_relation = se.main_shrink_exemplified(rules, bool_debug)
    elif mark == 'proportional':
        rules, superior_relation = sp.main_shrink_proportional(rules, bool_debug, threshold)
    else:
        # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
        return None, None, None, None

    # salviamo il modello: regole, relazione di superiorità ed eventualmente le regole decodificate
    save_model(rules,mark, superior_relation, shannon_map, output_path, output_path_sup_rel,
                output_var_name_verbose, output_path_clear_rules, bool_debug)

    return rules, mark, superior_relation, shannon_map

# MAIN
if __name__ == "__main__":
    pass
