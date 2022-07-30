'''
Shrinking dataset esemplificativo
'''
# IMPORT
import preprocessing as pp

# FUNCTIONS
def get_the_inner_set(r1, r2):
    '''
    Calcolo: determina, dati due insiemi r1 ed r2 quale fra i due è contenuto nell'altro
    Output: la regola contenuta nell'altra, None se non vale il contenimento
    '''
    diff1 = r1 - r2
    diff2 = r2 - r1
    if len(diff1) > 0 and len(diff2) == 0:
        return r2
    elif len(diff2) > 0 and len(diff1) == 0:
        return r1
    else:
        return None

def mre3(r1, r2):
    '''
    Calcolo: date due regole r1 ed r2, esegue l'intersezione delle due solamente se r1 ed r2 sono
            insiemi diversi per un solo letterale di differenza.
    Output: ritorna l'insieme degli antenati comuni se soddisfa la condizione, altrimenti None
    '''
    diff1 = r1 - r2
    diff2 = r2 - r1
    if len(diff1) == len(diff2) and len(diff1) == 1:
        e1 = next(iter(diff1)) # recupera l'unico elemento dell'insieme diff1
        e2 = next(iter(diff2)) # recupera l'unico elemento dell'insieme diff2
        # sono stringhe come 'd1', '-d_1'
        if e1 in e2 or e2 in e1:
            return r1.intersection(r2)
    return None

def main_shrink_exemplified(rules, bool_debug=False):
    print(f"> Procedura di shrinking exemplified avviata\n")

    changings = True
    i = 1               # conto quante iterazioni vengono fatte

    # Se r2 è sup di r1 allora ci sarà una coppia (r1, r2)
    superior_relation = set()

    while changings:
        print(f"> ciclo #{i}")

        changings = False

        explored = set()    # chiavi già completamente esplorate (il tipo set permette di effettuare l'operazione 'in' in O(1))
        to_remove = []      # regole da eliminare per la metaregola 1
        to_add = {}         # nuove regole da aggiungere per la metaregola 3
        keys = rules.keys()

        print(f"> Inzio procedura di controllo delle regole a coppie")
        for k in keys:
            for k2 in keys:
                if k2 in explored or k2==k:
                    continue
                
                # regole concordi
                if rules[k] == rules[k2]:
                    # MRE1
                    inner_set = get_the_inner_set(k, k2) # ritorna l'insieme contenuto nell'altro
                    if inner_set != None:
                        # devo eliminare l'insieme più grande. Se k2 è il più piccolo elimino k altrimenti k2
                        to_remove.append(k if inner_set == k2 else k2)
                        
                        if bool_debug:
                            print(f'r1={k}\nr2={k2}\nMRE1 rimuove {k if inner_set == k2 else k2}')
                        
                        # non controllo la condizione MRE3 poiché inutile. So che o k è strettamente contenuto in k2
                        # altrimenti k2 è strettamente contenuto in k quindi è impossibile che entrambi abbiano un letterale
                        # uno l'opposto dell'altro
                        continue
                    
                    # MRE3
                    # mre3_res è l'intersezione delle due regole sse hanno esattamente un letterale uno l'opposto dell'altro
                    mre3_res = mre3(k, k2)
                    if mre3_res != None:
                        to_add[mre3_res] = rules[k] # rules[k] stesso segno

                        if bool_debug:
                            print(f'r1={k}\nr2={k2}\nMRE3 aggiunge {mre3_res}, {rules[k]}')
                    
                else:
                    # MRE2
                    inner_set = get_the_inner_set(k, k2) # ritorna l'insieme contenuto nell'altro
                    if inner_set != None:
                        superior_relation.add((inner_set, k if inner_set == k2 else k2))

                        if bool_debug:
                            print(f'r1={k}\nr2={k2}\nMRE2 indica che {inner_set} è inferiore')
            
            #print("> ciclo dentro il for", k)
            explored.add(k)
        
        print(f"> Fine procedura di controllo delle regole a coppie")

        # UPDATE
        # ######
        
        # ripeto il ciclo se ci sono degli aggiornamenti
        if len(to_remove) > 0 or len(to_add) > 0:
            changings = True
        
        # procedura di rimozione degli elementi
        for k in to_remove:
            # la regola potrebbe già essere stata rimossa. Più regole ne possono eliminare una
            if k in rules:
                rules.pop(k)

        print(f"> Update: rimozione regole 'dominate'")
        
        # procedura di aggiunta delle nuove regole
        rules.update(to_add)
        print(f"> Update: aggiunta nuove regole\n")


        i += 1 # incremento l'indice che indica quanto impiega per arrivare alla fine

    print(f"> Procedura di shrinking exemplified completata")
    return rules, superior_relation


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
    rules, mark = pp.main_preprocessing(dataset_path, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=bool_debug)
    main_shrink_exemplified(rules, bool_debug)
