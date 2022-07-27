'''
Main
'''

# IMPORT
import pandas as pd
import argparse
import model

# FUNCTIONS
def get_parser():
    '''
    Calcolo: definisco il parser
    Output: parser
    '''
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
    parser.add_argument('--output_path_clear_rules', default=None)

    return parser

# MAIN
if __name__ == "__main__":
    # argomenti estratti tramite il parser
    args = get_parser().parse_args()

    # creazione del dataset
    dataset = pd.read_csv(args.dataset_path, sep=args.sep)
    
    # applicazione del modello
    rules, mark, superior_relation, shannon_map = model.model(dataset, args.output_var_name_verbose, args.class_column_name, 
                                args.pos_class_value, args.neg_class_value, args.null_value, 
                                args.threshold, args.output_path, args.output_path_sup_rel, 
                                args.output_path_clear_rules, args.bool_debug_preprocessing, args.bool_debug)
