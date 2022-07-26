# Modalità di utilizzo

Per eseguire l'algoritmo usare il seguente comando:
```
python main.py @<path_to_config_file>
```

Il file di configurazione deve contenere i seguenti argomenti:
- `dataset_path`, percorso in cui si trova il dataset (in formato `csv`).
- `sep`, separatore delle colonne (di default è `,`).
- `output_var_name_verbose`, se presente indica all'algoritmo di usare il nome completo delle colonne nell'output.
- `class_column_name`, nome della colonna che indica la classe all'interno del dataset (univariato).
- `pos_class_value`, valore corrispondente alla classe positiva.
- `neg_class_value`, valore corrispondente alla classe negativa (non-classe).
- `bool_debug_preprocessing`, se presente indica all'algoritmo di stampare in console ulteriori informazioni durante la fase di preprocessing.
- `bool_debug`, se presente indica all'algoritmo di stampare in console ulteriori informazioni durante la fase di shrinking.
- `threshold`, valore della soglia (di default è 1) utilizzata nelle regole `MRP4` e `MRP5` (shrinking per dataset proportional).
- `output_path`, percorso in cui si desidera salvare l'output dell'algoritmo.
- `output_path_sup_rel`, percorso in cui si desiderano salvare le coppie di superiorità prodotte dall'algoritmo.
- `output_path_clear_rules`, se presente indica il percorso in cui salvare la riscrittura delle regole secondo la Shannon Map.
- `null_value`, valore nullo utilizzato all'interno del dataset (di default è `?`).

# Scopo
Dato in input un dataset, si vuole ricavare una teoria logica (le cui conseguenze sono classe o non-classe) basata su *regole non monotone* (ossia indipendenti l'una dall'altra).

Dopo l'operazione di shrinking (contrazione), si otterrà la teoria più piccola possibile ed essa rappresenterà quindi la *spiegazione* del dataset.

Vedere la cartella `docs` per lo pseudo-codice dell'algoritmo e per la spiegazione di alcuni risultati.
