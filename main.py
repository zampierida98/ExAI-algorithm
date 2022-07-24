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

def save_on_file_superior_relation(superioor_relation, output_path):
    with open(output_path, 'w') as fout:
        for (inf, sup) in superioor_relation:
            fout.write(f'{tuple(inf)} < {tuple(sup)}\n'.replace("'", ""))

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
    parser.add_argument('--null_value', default='?')
    args = parser.parse_args()

    rules, mark = pp.main_preprocessing(args.dataset_path,
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
    print(superior_relation)
    save_on_file_superior_relation(superior_relation, args.output_path_sup_rel)

    print(f"Salvataggio completato in {args.output_path}")
    print(f"Salvataggio completato in {args.output_path_sup_rel}")
