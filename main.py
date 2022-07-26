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

def save_on_file_superior_relation(superior_relation, output_path):
    with open(output_path, 'w') as fout:
        for (inf, sup) in superior_relation:
            fout.write(f'{tuple(inf)} < {tuple(sup)}\n'.replace("'", ""))

def clear_rules(rules, shannon_map, mark):
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

# MAIN
if __name__ == "__main__":
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
    parser.add_argument('--output_path_clear_rules', default=None)
    parser.add_argument('--null_value', default='?')
    args = parser.parse_args()

    rules, mark, shannon_map = pp.main_preprocessing(args.dataset_path,
                                        args.output_var_name_verbose,
                                        args.class_column_name,
                                        args.pos_class_value,
                                        args.neg_class_value,
                                        bool_debug=args.bool_debug_preprocessing,
                                        sep=args.sep,
                                        null_value=args.null_value)
    print("#"*59)

    if mark == 'exemplified':
        rules, superior_relation = se.main_shrink_exemplified(rules, args.bool_debug)
    elif mark == 'proportional':
        rules, superior_relation = sp.main_shrink_proportional(rules, args.bool_debug, args.threshold)
    else:
        # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
        exit()

    print("#"*59)

    save_on_file(rules, mark, args.output_path)
    if args.bool_debug:
        print(superior_relation)
    save_on_file_superior_relation(superior_relation, args.output_path_sup_rel)

    print(f"Salvataggio completato in {args.output_path}")
    print(f"Salvataggio completato in {args.output_path_sup_rel}")

    if args.output_path_clear_rules:
        clear_rules, colnames = clear_rules(rules, shannon_map, mark)
        save_clear_rules(clear_rules, colnames, args.output_path_clear_rules)
        print(f"Salvataggio completato in {args.output_path_clear_rules}")
