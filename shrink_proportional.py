'''
Shriking dataset proporzionale
'''
# IMPORT
import math
import pandas as pd
import numpy as np

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


def mre3(r1, r2):
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

def mre4(r1, r2, occ_r1, occ_r2, threshold):
    '''
    Calcolo: Due condizioni:
    1 - the premises of r1 are the same of the premises of r2, 
        and rule r1 occurrences is higher than r2 occurrences
    2 - the ratio of the number of occurrences of r1 and r2 is lower that a given threshold 
        (note: the ratio can't be lower than 1, so the minimum threshold is 1)

    Output: ritorna le regole da eliminare
    '''
    C1 = r1 == r2
    C1_1 = C1 and occ_r1 > occ_r2
    C2_1 = occ_r1 / occ_r2 < threshold

    C1_2 = C1 and occ_r2 > occ_r1
    C2_2 = occ_r2 / occ_r1 < threshold
    
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



def mre5(r1,r2, occ_r1, occ_r2, threshold):
    '''
    Calcolo: overlap delle premesse di r1 ed r2. In più verifico se r1/r2 > threshold allora output
    Output: ritorna la regola che è superiore all'altra, se nessuna allora None
    '''
    if len(r1 - r2) > 0 and len(r2 - r1) > 0: # overlap (SE SERVE L'INCLUSIONE SI AGGIUNGE >=)
        if occ_r1 / occ_r2 > threshold:
            return r1
        elif occ_r2 / occ_r1 > threshold:
            return r2
    return None
        

def main_shrink_proportional(rules, bool_debug=False, threshold=1):    
    print(f"> Procedura di shrinking proportional avviata\n")

    changings = True
    i = 1               # conto quante iterazioni vengono fatte

    # è un dizionario. Se r2 è sup di r1 allora sarà {r1: r2}
    superior_relation = {}

    while changings:
        print(f"> ciclo #{i}")

        changings = False

        explored = []   # chiavi già completamente esplorate
        to_remove = []  # regole da eliminare per la metaregola 1
        to_add = {}     # nuove regole da aggiungere per la metaregola 3
        keys = rules.keys()

        print(f"> Inzio procedura di controllo delle regole a coppie")

        # chiavi sono (set-variabili, segno)
        for k in keys:
            for k2 in keys:
                if k2 in explored or k2==k:
                    continue
                
                # regole concordi
                if k[1] == k2[1]:
                    # MRE1
                    mre1_res = get_the_inner_set(k[0], k2[0]) # ritorna l'insieme contenuto nell'altro
                    if mre1_res != None:
                        to_remove.append((mre1_res, k[1]))
                        
                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRE1 rimuove {mre1_res}')
                    
                    # MRE3
                    mre3_res = mre3(k[0], k2[0])
                    if mre3_res != None:
                        # se già fosse presente 
                        #to_add[(mre3_res, k[1])] = to_add.get( (mre3_res, k[1]), 0) + 1
                        to_add[(mre3_res, k[1])] = 0

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRE3 aggiunge {mre3_res}, {rules[k]}')
                    
                else:
                    # MRE2
                    mre2_res = get_the_inner_set(k[0], k2[0]) # ritorna l'insieme contenuto nell'altro
                    if mre2_res != None:
                        superior_relation[mre2_res] = k[0] if mre2_res == k2[0] else k2[0]

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRE2 indica che {mre2_res} è inferiore')
                    
                    # MRE4
                    mre4_res = mre4(k[0], k2[0], rules[k], rules[k2], threshold)
                    if mre4_res != []:
                        # concat di liste
                        to_remove += [(x, k[1]) for x in mre4_res]

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRE4 rimuove che {mre4_res}')
                    
                    # MRE5
                    mre5_res = mre5(k[0], k2[0], rules[k], rules[k2], threshold) # ritorna il superiore
                    if mre5_res != None:
                        superior_relation[k[0] if mre5_res == k2[0] else k2[0]] = mre5_res

                        if bool_debug:
                            print(f'r1={k[0]}\nr2={k2[0]}\nMRE5 indica che {mre5_res} è superiore')

            explored.append(k)
        
        print(f"> Fine procedura di controllo delle regole a coppie")

        # UPDATE
        # ######
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

    print(f"> Procedura di shrinking proportional completata")
    return rules


# COSTANTS
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