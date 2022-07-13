'''
Main
'''

# IMPORT
import preprocessing as pp
import shrink_exemplified as se
import shrink_proportional as sp

# FUNCTIONS
def save_on_file(rules, mark, output_path):
    with open(output_path, 'w') as fout:
        for k in rules:
            if mark == 'exemplified':
                fout.write(f'{tuple(k)}{rules[k]}\n'.replace("'", ""))
            else:
                fout.write(f'{tuple(k[0])}{k[1]}{rules[k]}\n'.replace("'", ""))

# CONSTANTS
# VARIABLES
dataset_path = './dataset/dataset.csv'
output_var_name_verbose = False
class_column_name = 'CLASS'
pos_class_value = 'class'
neg_class_value = 'NON-class'
bool_debug_preprocessing = False # bool_D solo per il preprocessing
bool_debug = True
threshold = 1
output_path = 'results.txt'

# MAIN
if __name__ == "__main__":
    rules, mark = pp.main_preprocessing(dataset_path, output_var_name_verbose, class_column_name, pos_class_value,neg_class_value, bool_debug=bool_debug_preprocessing)
    print("#"*59)
    # DA TOGLIERE la riga sotto PERCHE' SERVE SOLO PER I TEST
    # mark = 'proportional'
    # #######################################################

    if mark == 'exemplified':
        rules, superior_relation = se.main_shrink_exemplified(rules, bool_debug)
    elif mark == 'proportional':
        rules, superior_relation = sp.main_shrink_proportional(rules, bool_debug, threshold)
    else:
        # se il mark è None, per la fase di preprocessing, l'algoritmo deve terminare
        exit()
    
    print("#"*59)

    save_on_file(rules, mark, output_path)
    print(f"Salvataggio completato in {output_path}")