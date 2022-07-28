'''
Shrinking dataset proporzionale
'''
# IMPORT
import preprocessing as pp

# FUNCTIONS
def get_the_inner_set(r1, r2):
    '''
    Calcolo:the premises of r1 are all premises of r2, 
            but some premise of r2 is not a premise of r1

    Output: la regola contenuta nell'altra, None se non vale il contenimento
    '''
    if len(r1 - r2) > 0 and len(r2 - r1) == 0:
        return r2
    elif len(r2 - r1) > 0 and len(r1 - r2) == 0:
        return r1
    else:
        return None

def mrp3(r1, r2):
    '''
    Calcolo:have antecedents that are all the same but one each, 
            and r1's sole different antecedent is the opposite literal of r2's sole different antecedent
    Output: ritorna l'insieme degli antenati comuni se soddisfa la condizione, altrimenti None
    '''
    diff1 = r1 - r2
    diff2 = r2 - r1
    if len(diff1) == len(diff2) and len(diff1) == 1:
        e1 = next(iter(diff1))
        e2 = next(iter(diff2))
        # sono stringhe come 'd1', '-d_1'
        if e1 in e2 or e2 in e1:
            return r1.intersection(r2)
    return None

def mrp4(r1, r2, occ_r1, occ_r2, threshold):
    '''
    Calcolo: Due condizioni:
    1 - the premises of r1 are the same of the premises of r2, 
        and rule r1 occurrences is higher than r2 occurrences
    2 - the ratio of the number of occurrences of r1 and r2 is lower that a given threshold 
        (note: the ratio can't be lower than 1, so the minimum threshold is 1)

    Output: ritorna le regole da eliminare
    '''
    try:
        r1_over_r2 = occ_r1 / occ_r2
    except:
        r1_over_r2 = 0
    try:
        r2_over_r1 = occ_r2 / occ_r1
    except:
        r2_over_r1 = 0
    

    C1 = r1 == r2
    C1_1 = C1 and occ_r1 > occ_r2
    C2_1 = r1_over_r2 > threshold

    C1_2 = C1 and occ_r2 > occ_r1
    C2_2 = r2_over_r1 > threshold
    
    # CASO R1 - R2
    if C1_1 and C2_1: # entrambe vere
        return [r2]
    elif C1_1 and not C2_1:
        return [r1, r2]

    # CASO R2 - R1
    elif C1_2 and C2_2: # entrambe vere
        return [r1]
    elif C1_2 and not C2_2:
        return [r1, r2]
    else:
        return []

def mrp5(r1,r2, occ_r1, occ_r2, threshold):
    '''
    Calcolo: overlap delle premesse di r1 ed r2. In più verifico se r1/r2 > threshold allora output
    Output: ritorna la regola che è superiore all'altra, se nessuna allora None
    '''
    try:
        r1_over_r2 = occ_r1 / occ_r2
    except:
        r1_over_r2 = 0
    try:
        r2_over_r1 = occ_r2 / occ_r1
    except:
        r2_over_r1 = 0

    if len(r1.intersection(r2)) >= 0:
        if r1_over_r2 > threshold:
            return r1
        elif r2_over_r1 > threshold:
            return r2
    return None

def main_shrink_proportional(rules, bool_debug=False, threshold=1):    
    print(f"> Procedura di shrinking proportional avviata\n")

    changings = True
    i = 1               # conto quante iterazioni vengono fatte

    # Se r2 è sup di r1 allora ci sarà (r1, r2)
    superior_relation = set()

    while changings:
        print(f"> ciclo #{i}")

        changings = False

        explored = set()    # chiavi già completamente esplorate (il tipo set permette di effettuare l'operazione 'in' in O(1))
        to_remove = []      # regole da eliminare per la metaregola 1
        to_add = {}         # nuove regole da aggiungere per la metaregola 3
        multiplicity_after_remove = {}
        keys = rules.keys()

        print(f"> Inzio procedura di controllo delle regole a coppie")

        # chiavi sono (set-variabili, segno)
        for k in keys:
            for k2 in keys:
                if k2 in explored or k2==k:
                    continue
                
                # regole concordi
                if k[1] == k2[1]:
                    # MRP1
                    inner_set = get_the_inner_set(k[0], k2[0]) # ritorna l'insieme contenuto nell'altro
                    if inner_set != None:
                        # devo eliminare l'insieme più grande. Se k2 è il più piccolo elimino k altrimenti k2
                        to_remove.append((k[0] if inner_set == k2[0] else k2[0], k[1]))
                        
                        # aggiungo la molteplicità della regole eliminata alla regola che sopravvive.
                        multiplicity_after_remove[((inner_set, k[1]))] = (multiplicity_after_remove.get((inner_set, k[1]), 0) + 
                                                                            rules[(k[0] if inner_set == k2[0] else k2[0], k[1])] 
                                                                        )

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRP1 rimuove {k[0] if inner_set == k2[0] else k2[0]}')
                        
                        # non controllo la condizione MRP3 poiché inutile. So che o k è strettamente contenuto in k2
                        # altrimenti k2 è strettamente contenuto in k quindi è impossibile che entrambi abbiano un letterale
                        # uno l'opposto dell'altro
                        continue
                    
                    # MRP3
                    mrp3_res = mrp3(k[0], k2[0])
                    if mrp3_res != None:

                        # se già fosse presente 
                        #to_add[(mrp3_res, k[1])] = to_add.get( (mrp3_res, k[1]), 0) + 1
                        to_add[(mrp3_res, k[1])] = 0

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRP3 aggiunge {(mrp3_res, k[1])}, {0}')
                    
                else:
                    # MRP2
                    inner_set = get_the_inner_set(k[0], k2[0]) # ritorna l'insieme contenuto nell'altro
                    if inner_set != None:
                        superior_relation.add((inner_set, k[0] if inner_set == k2[0] else k2[0]))

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRP2 indica che {inner_set} è inferiore')
                    
                    # MRP4
                    mrp4_res = mrp4(k[0], k2[0], rules[k], rules[k2], threshold)
                    if mrp4_res != []:
                        # concat di liste
                        # Essendo discordi k[0] e k[1] allora quando aggiungo le coppie alla lista 'to_remove'
                        # aggiungo il segno corrispondente alla regola da aggiungere
                        to_remove += [(x, k[1] if x == k[0] else k2[1]) for x in mrp4_res]

                        if len(mrp4_res) == 1:
                            # chiave della regola che soppravive
                            k_live = (k2 if mrp4_res[0] == k[0] else k)
                            # chiave della regola da eliminare
                            k_dead = (k if mrp4_res[0] == k[0] else k2)

                            multiplicity_after_remove[k_live] = (multiplicity_after_remove.get(k_live, 0) + 
                                                                            rules[k_dead] )

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRP4 rimuove {mrp4_res}')
                    
                    # MRP5
                    mrp5_res = mrp5(k[0], k2[0], rules[k], rules[k2], threshold) # ritorna il superiore
                    if mrp5_res != None:
                        superior_relation.add((k[0] if mrp5_res == k2[0] else k2[0], mrp5_res))

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRP5 indica che {mrp5_res} è superiore')

            explored.add(k)
        
        print(f"> Fine procedura di controllo delle regole a coppie")

        # UPDATE
        # ######
        if len(to_remove) > 0 or len(to_add) > 0:
            changings = True
        
        # questo aggiornamento viene messo prima della rimozione perché ci possono essere casi come questo:
        # r1 elimina r2 ed r2 elimina r3. Se faccio prima la eliminazione allora dentro rules non avro' né
        # r2 né r3 e quindi l'aggiornamento delle molteplicità darà errore perché non trova r2.

        # aggiornamento molteplicità delle regole
        for k in multiplicity_after_remove:
            rules[k] += multiplicity_after_remove[k]
            '''
            try:
                rules[k] += multiplicity_after_remove[k]
            except:
                continue
            '''
        print("> Update: aggiornamento molteplicità delle regole")
        
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

    print(f"> Procedura di shrinking proportional completata")
    return rules, superior_relation


# CONSTANT
# VARIABLES
dataset_path = './dataset/dataset.csv'
output_var_name_verbose = False
class_column_name = 'CLASS'
pos_class_value = 'class'
neg_class_value = 'NON-class'
bool_debug = False
threshold = 1

# MAIN
if __name__ == "__main__":
    rules, mark = pp.main_preprocessing(dataset_path, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=bool_debug)
    main_shrink_proportional(rules, bool_debug, threshold)
