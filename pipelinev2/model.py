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

def save_model(rules,mark,superior_relation, shannon_map, output_path, output_path_sup_rel,output_path_clear_rules, bool_debug):
    '''
    Calcolo: Si preoccupa di salvare su file il modello. Richiama le funzione save_... soprastanti nel file
    Output: None
    '''
    print("#"*59)

    save_on_file(rules, mark, output_path)
    if bool_debug:
        print(superior_relation)
    save_on_file_superior_relation(superior_relation, output_path_sup_rel)

    print(f"Salvataggio completato in {output_path}")
    print(f"Salvataggio completato in {output_path_sup_rel}")

    if output_path_clear_rules:
        clear_rules_var, colnames = clear_rules(rules, shannon_map, mark)
        save_clear_rules(clear_rules_var, colnames, output_path_clear_rules)
        print(f"Salvataggio completato in {output_path_clear_rules}")
    
    print("#"*59)

def clear_rules(rules, shannon_map, mark):
    '''
    Calcolo: Le regole possono non avere tutti i letterali di ogni colonna (per via della fase di shrinking).
            Per cui l'obiettivo è individuare, partendo da un gruppo di letterali 'fisso' CONSIDERANDO UNA SOLA colonna, 
            tutte le combinazioni binarie che hanno quel gruppo di letterali. Dopodichè avviene la decodifica 
            cioè da stringa binaria si ottiene il valore della colonna. Infine, viene eseguito il prodotto cartesiano 
            generando tutte le regole "decodificate" concordi alla regola di soli letterali.

    Output: regole della teoria non monotone decifrate ovvero 
            al posto dei letterali ci sarà il valore della colonna corrispondente ai letterali
    '''
    # Trasformazione delle regole in chiaro
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
    res_rules = set()

    #reverse shannon map. Invece di avere per ogni colonna dizionari valore:stringabin adesso è stringabin:valore
    rev_shann_map = {col: {v:k for k,v in shannon_map[col].items()} for col in shannon_map}

    # mappa variabile posizione all'interno della stringa binaria
    map_var_pos = {v:i for i,v in enumerate(string.ascii_lowercase)}
    # caso di default di tutte le regole
    default_istance = {col:('x' * len(shannon_map[col][next(iter(shannon_map[col])) ]) ) for col in shannon_map}

    for k in rules:
        # faccio una copia del caso di default
        clear_rule = default_istance.copy()
        for var in (k if mark == 'exemplified' else k[0]):
            
            #variabile, colonna
            v,c = var.split("_", 1) # splitto solo al primo '_' in modo che se la colonna ha nel nome _ tengo l'intero nome
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
            # non tutte le stringhe binarie sono presenti. Se ho xxxx e ho solo 10 valori gli altri 6 non esistono.
            # Non saranno presenti nella mappa
            tmp = []
            for bitstring in incomplete_to_complete_bitstring(clear_rule[col]):
                # aggiungo il valore corrispondente alla codifica binaria solo se la stringa binaria esiste
                # la stringa binaria nella mappa
                try:
                    tmp.append(rev_shann_map[col][bitstring])
                except:
                    pass
            clear_rule[col] = tmp
        
        # uso il metodo statico di itertools product che esegue un prodotto cartesiano.
        #res_rules += list(itertools.product(* (list(clear_rule.values()) + [ [(rules[k] if mark == 'exemplified' else k[1])] ])))
        for r in list(itertools.product(* (list(clear_rule.values()) + [ [(rules[k] if mark == 'exemplified' else k[1])] ]))):
            res_rules.add(r)
    
    # ritorno le regole in chiaro con anche le chiavi
    return res_rules, list(clear_rule.keys()) + ['class']


def model(dataset, output_var_name_verbose, class_column_name, pos_class_value, neg_class_value, null_value, 
        threshold, output_path, output_path_sup_rel, output_path_clear_rules, bool_debug_preprocessing, bool_debug):
    '''
    Calcolo: Richiamo i metodi da altri moduli per costruire il modello. Preprocessing -> Shrinking
    Output: teoria NM, tipo di dataset, relazione di superiorità, shannon map (per la fase di validazione)
    '''

    rules, mark, shannon_map = pp.main_preprocessing(dataset,
                                        output_var_name_verbose,
                                        class_column_name,
                                        pos_class_value,
                                        neg_class_value,
                                        bool_debug=bool_debug_preprocessing,
                                        null_value=null_value)
    
    print("#"*59)
    if mark == 'exemplified':
        rules, superior_relation = se.main_shrink_exemplified(rules, bool_debug)
    elif mark == 'proportional':
        rules, superior_relation = sp.main_shrink_proportional(rules, bool_debug, threshold)
    else:
        # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
        None, None, None, None

    save_model(rules,mark,superior_relation, shannon_map, output_path, output_path_sup_rel,
                output_path_clear_rules, bool_debug)

    return rules, mark, superior_relation, shannon_map

# MAIN
if __name__ == "__main__":
    pass
