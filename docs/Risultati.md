# Rappresentazione della conoscenza (A.A. 2021-2022)

**Autori:**

*VR464051 - Michele Dalla Chiara*

*VR458470 - Davide Zampieri*


## Risultati sul dataset `cell_sample`
Questo dataset presenta i seguenti attributi (da [Original Wisconsin Breast Cancer Database](https://archive.ics.uci.edu/ml/datasets/Breast+Cancer+Wisconsin+%28Original%29)):
- Clump Thickness: 1 - 10
- Uniformity of Cell Size: 1 - 10
- Uniformity of Cell Shape: 1 - 10
- Marginal Adhesion: 1 - 10
- Single Epithelial Cell Size: 1 - 10
- Bare Nuclei: 1 - 10
- Bland Chromatin: 1 - 10
- Normal Nucleoli: 1 - 10
- Mitoses: 1 - 10
- Class: 2 (benign), 4 (malignant)

Applicazione dell'algoritmo:
- Il passo `P2` ha eliminato la colonna in cui era presente il solo valore nullo.
- Il passo `P3` ha marcato il dataset come exemplified dopo aver calcolato i valori necessari a prendere tale decisione.
    ```
    R=699, r=1000000000, R/r=6.99e-07, N=9, N^2=81
    mark = exemplified
    ```
- Il passo `P5` ha calcolato la Shannon Map secondo cui ogni colonna viene mappata in un certo numero di variabili booleane.
    ```
    >>> Shannon map per Clump: {'5': '000', '3': '001', '6': '010', '4': '011', '8': '100', '1': '101', '2': '110', '10': '111', nan: ''}
    >>> Shannon map per UnifSize: {'1': '0000', '4': '0001', '8': '0010', '10': '0011', '2': '0100', '3': '0101', '7': '0110', '5': '0111', '6': '1000', '9': '1001', nan: ''}
    >>> Shannon map per UnifShape: {'1': '0000', '4': '0001', '8': '0010', '10': '0011', '2': '0100', '3': '0101', '5': '0110', '6': '0111', '7': '1000', '9': '1001', nan: ''}
    >>> Shannon map per MargAdh: {'1': '0000', '5': '0001', '3': '0010', '8': '0011', '10': '0100', '4': '0101', '6': '0110', '2': '0111', '9': '1000', '7': '1001', nan: ''}
    >>> Shannon map per SingEpiSize: {'2': '0000', '7': '0001', '3': '0010', '1': '0011', '6': '0100', '4': '0101', '5': '0110', '8': '0111', '10': '1000', '9': '1001', nan: ''}
    >>> Shannon map per BareNuc: {'1': '0000', '10': '0001', '2': '0010', '4': '0011', '3': '0100', '9': '0101', '7': '0110', '5': '0111', '8': '1000', '6': '1001', nan: ''}
    >>> Shannon map per BlandChrom: {'3': '0000', '9': '0001', '1': '0010', '2': '0011', '4': '0100', '5': '0101', '7': '0110', '8': '0111', '6': '1000', '10': '1001', nan: ''}
    >>> Shannon map per NormNucl: {'1': '0000', '2': '0001', '7': '0010', '4': '0011', '5': '0100', '3': '0101', '10': '0110', '6': '0111', '9': '1000', '8': '1001', nan: ''}
    >>> Shannon map per Mit: {'1': '0000', '5': '0001', '4': '0010', '2': '0011', '3': '0100', '7': '0101', '10': '0110', '8': '0111', '6': '1000', nan: ''}
    ```
- Il passo `P6` ha creato 699 regole le quali, dopo lo shrinking, si sono ridotte a 431.
    ```
    (d_5, -d_8, d_3, -c_4, -b_6, -c_1, d_4, -a_1, -a_6, -c_7, -c_5, -a_8, -c_2, -c_0, -b_7, -b_0, -a_7, -a_4, -b_1, -c_6, -c_3, -a_0, -b_2, -b_5, d_2, -d_6, -a_2, -b_3, -a_3, d_1, -b_4, -b_8, -c_8, -a_5, d_7)+

    (d_5, -d_8, -b_6, -a_1, c_1, b_0, -a_6, -a_8, -c_0, -b_7, -a_7, -a_4, -d_3, -b_1, -d_4, -c_6, -c_3, -a_0, -d_1, -b_2, c_7, -b_5, -d_6, -a_2, -d_2, -b_3, -a_3, -b_4, -b_8, c_2, -c_8, -d_7, c_4, -a_5, c_5)+

    (d_5, -d_8, d_3, -c_4, -b_6, d_4, -a_1, c_1, -a_6, -c_5, -a_8, -c_0, -b_7, -b_0, -a_7, -a_4, -b_1, -c_6, -b_2, c_7, -b_5, d_2, c_3, -a_2, d_6, -b_3, a_0, -a_3, d_1, -b_4, -b_8, c_2, -c_8, -d_7, -a_5)-

    (-d_8, -c_4, -c_1, -a_1, -a_6, -c_5, -a_8, -c_2, -c_0, -b_7, -b_0, -a_7, -a_4, -d_3, -d_4, b_1, b_2, -c_6, -a_0, c_7, -d_5, d_2, b_6, -d_6, c_3, -a_2, -b_3, -a_3, d_1, -b_4, -b_8, b_5, -c_8, -a_5, d_7)-

    ...
    ```
    Nel file di output le lettere rappresentano i vari bit dei numeri binari su cui sono mappati i valori delle colonne (`a` è il più significativo), ed i numeri rappresentano le colonne stesse. La presenza del segno `-` davanti al letterale indica che il bit corrispondente vale 0. Ad esempio, `-c_0, -b_0, -a_0` indica il valore 5 per la colonna Clump.

Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F):
```
[[82.  0.]
 [ 0.  0.]
 [56. 67.]]
```


## Risultati sul dataset `kr-vs-kp`
Il formato delle istanze di questo [dataset](https://archive.ics.uci.edu/ml/datasets/Chess+%28King-Rook+vs.+King-Pawn%29) è una sequenza di 36 attributi che formano una descrizione della scacchiera. L'ultimo attributo (il 37esimo) è la classe: White-can-win ("won"), White-cannot-win ("nowin").

Il dataset è di tipo exemplified e l'applicazione dell'algoritmo permette di passare da 3196 a 1758 regole (più 8 coppie di superiorità).


## Risultati sul dataset `agaricus-lepiota`
Questo [dataset](https://archive.ics.uci.edu/ml/datasets/Mushroom) contiene descrizioni corrispondenti a 23 specie di funghi della famiglia Agaricus-Lepiota. Il dataset è formato da 22 attributi (tutti categorici) più l'informazione della classe: commestibile (edible=e) o velenoso (poisonous=p).


## Risultati sul dataset `car`
Questo [dataset](https://archive.ics.uci.edu/ml/datasets/Car+Evaluation) contiene valutazioni di veicoli secondo 6 attributi (tutti categorici). L'ultimo attributo è la classe: acceptable (acc) o unacceptable (unacc), dove in acceptable sono state inserite anche le istanze classificate come good e very good (per la natura univariata dell'algoritmo in esame).

Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F):
```
[[ 24.   0.]
 [  3. 118.]
 [ 43.   5.]]
```


## Altri risultati
Sono stati selezionati ulteriori 3 dataset per verificare il comportamento dell'algoritmo nei diversi casi previsti (exemplified, proporitonal, nessuno dei due).

### Dataset exemplified
[Balloons Data Set](https://archive.ics.uci.edu/ml/datasets/Balloons): quattro dataset che rappresentano diverse condizioni di un esperimento.

Hanno tutti gli stessi attributi:
- `color`: yellow, purple
- `size`: large, small
- `act`: stretch, dip
- `age`: adult, child
- `inflated`: T, F (classe)

Output:
- Nel dataset `adult+stretch.data` la classe è `T` se `age=adult` e `act=stretch`.
    ```
    Shannon map per color: {'YELLOW': '0', 'PURPLE': '1', nan: ''}
    Shannon map per size: {'SMALL': '0', 'LARGE': '1', nan: ''}
    Shannon map per act: {'STRETCH': '0', 'DIP': '1', nan: ''}
    Shannon map per age: {'ADULT': '0', 'CHILD': '1', nan: ''}

    (-a_age, -a_act)+
    (a_age,)-
    (a_act,)-
    ```
    Si può vedere che l'algoritmo ritorna come regola per la classe positiva `(-a_age, -a_act)` ossia: primo bit di `age` pari a 0 e primo bit di `act` pari a 0.

- Nel dataset `adult-stretch.data` la classe è `T` se `age=adult` oppure `act=stretch`.
    ```
    Shannon map per color: {'YELLOW': '0', 'PURPLE': '1', nan: ''}
    Shannon map per size: {'SMALL': '0', 'LARGE': '1', nan: ''}
    Shannon map per act: {'STRETCH': '0', 'DIP': '1', nan: ''}
    Shannon map per age: {'ADULT': '0', 'CHILD': '1', nan: ''}

    (a_act, a_age)-
    (-a_act,)+
    (-a_age,)+
    ```
    Si può vedere che l'algoritmo ritorna come regole per la classe positiva `(-a_age)` e `(-a_act)` rispettivamente: primo bit di `age` pari a 0 e primo bit di `act` pari a 0.

- Nel dataset `yellow-small.data` la classe è `T` se `color=yellow` e `size=small`.
    ```
    Shannon map per color: {'YELLOW': '0', 'PURPLE': '1', nan: ''}
    Shannon map per size: {'SMALL': '0', 'LARGE': '1', nan: ''}
    Shannon map per act: {'STRETCH': '0', 'DIP': '1', nan: ''}
    Shannon map per age: {'ADULT': '0', 'CHILD': '1', nan: ''}

    (-a_color, -a_size)+
    (a_size,)-
    (a_color,)-
    ```
    Si può vedere che l'algoritmo ritorna come regola per la classe positiva `(-a_color, -a_size)` ossia: primo bit di `color` pari a 0 e primo bit di `size` pari a 0.

- Nel dataset `yellow-small+adult-stretch.data` la classe è `T` se `age=adult` e `act=stretch` oppure se `color=yellow` e `size=small`.
    ```
    Shannon map per color: {'YELLOW': '0', 'PURPLE': '1', nan: ''}
    Shannon map per size: {'SMALL': '0', 'LARGE': '1', nan: ''}
    Shannon map per act: {'STRETCH': '0', 'DIP': '1', nan: ''}
    Shannon map per age: {'ADULT': '0', 'CHILD': '1', nan: ''}

    (-a_size, -a_color)+
    (-a_act, -a_age)+
    (a_size, a_age)-
    (a_size, a_act)-
    (a_color, a_age)-
    (a_color, a_act)-
    ```
    Si può vedere che l'algoritmo ritorna giustamente come regole per la classe positiva `(-a_size, -a_color)` e `(-a_act, -a_age)`.

### Dataset non marcato
[HIV-1 protease cleavage Data Set](https://archive.ics.uci.edu/ml/datasets/HIV-1+protease+cleavage): elenco di ottameri (8 aminoacidi) e un flag di classe (-1 o 1 a seconda che la proteasi dell'HIV-1 si scinderà o meno in posizione centrale).

Output:
```
R=746, r=746, R/r=1.0, N=1, N^2=1

Mark = None. L'algoritmo si ferma e non produce output
```
Il risultato era atteso in quanto l'unico attributo presenta un numero di valori distinti pari al numero delle righe del dataset.

### Dataset proportional
[Sepsis survival minimal clinical records Data Set](https://archive.ics.uci.edu/ml/datasets/Sepsis+survival+minimal+clinical+records): raccolta di dataset contenenti record sanitari (con informazioni minime) di ricoveri di pazienti con sepsi.

Ogni dataset presenta 4 informazioni cliniche:
- `age_years`: valore intero
- `sex_0male_1female`: valore binario
- `episode_number`: valore intero
- `hospital_outcome_1alive_0dead`: valore binario (classe)

Output:
```
R=19051, r=1010, R/r=18.862376237623764, N=3, N^2=9
mark = proportional
```
L'applicazione dell'algoritmo permette di passare da 19051 a 544 regole.
