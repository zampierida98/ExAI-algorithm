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
    R=699, r=720000000, R/r=9.708333333333333e-07, N=9, Nln(N)=19.775021196025975
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
    Nel file di output le lettere rappresentano i vari bit dei numeri binari  che codificano i valori delle colonne (`a` è il più significativo), ed i numeri rappresentano le colonne stesse. La presenza del segno `-` davanti al letterale indica che il bit corrispondente vale 0. Ad esempio, `-c_0, -b_0, -a_0` indica il valore 5 per la colonna Clump.

Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F) utilizzando un test set con dimensione pari al 30% dell'intero dataset:
```
[[82.  0.]
 [ 0.  0.]
 [56. 67.]]

ACCURACY=0.4
PRECISION=1.0
RECALL=0,594202898550724
```

Di seguito proponiamo la consueta matrice di confusione con training set uguale al test set e pari all'intero dataset.
```
[[365.   0.]
 [  0.   0.]
 [ 92. 205.]]

ACCURACY=0,551359516616314
PRECISION=1.0
RECALL=0,79868708971553
```


## Risultati sul dataset `kr-vs-kp`
Il formato delle istanze di questo [dataset](https://archive.ics.uci.edu/ml/datasets/Chess+%28King-Rook+vs.+King-Pawn%29) è una sequenza di 36 attributi che formano una descrizione della scacchiera. L'ultimo attributo (il 37esimo) è la classe: White-can-win ("won"), White-cannot-win ("nowin").

Il passo `P3` ha marcato il dataset come exemplified dopo aver calcolato i valori necessari a prendere tale decisione.
```
R=3196, r=103079215104, R/r=3.1005280713240303e-08, N=36, Nln(N)=129.00668178441995
mark = exemplified
```

L'applicazione dell'algoritmo permette di passare da 3196 a 1771 regole.

Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F) utilizzando un test set con dimensione pari al 30% dell'intero dataset:
```
[[  0.   0.]
 [  0.   0.]
 [501. 458.]]

ACCURACY=0.0
PRECISION=0.0
RECALL=0.0
```

Inoltre, siccome questo dataset è fatto in maniera tale da contenere tutte le combinazioni degli attributi, esso è stato anche valutato utilizzando come test set il dataset stesso. Così facendo è possibile verificare in che modo la riduzione del numero di regole impatta su precisione e accuratezza.

Di seguito proponiamo la consueta matrice di confusione con training set uguale al test set e pari all'intero dataset.
```
[[1607.    0.]
 [   0. 1428.]
 [  62.   99.]]

ACCURACY=0.9496245306633292
PRECISION=1.0
RECALL=0.9628520071899341
```


## Risultati sul dataset `agaricus-lepiota`
Questo [dataset](https://archive.ics.uci.edu/ml/datasets/Mushroom) contiene descrizioni corrispondenti a 23 specie di funghi della famiglia Agaricus-Lepiota. Il dataset è formato da 22 attributi (tutti categorici) più l'informazione della classe: commestibile (edible=e) o velenoso (poisonous=p).


Il passo `P3` ha marcato il dataset come exemplified dopo aver calcolato i valori necessari a prendere tale decisione.
```
R=8124, r=54854914867200, R/r=1.4809976498309493e-10, N=21, Nln(N)=63.9349711922 
mark = exemplified
```

L'applicazione dell'algoritmo permette di passare da 8124 a 173 regole.

Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F) utilizzando un test set con dimensione pari al 30% dell'intero dataset:
```
[[  29.    0.]
 [   0.   19.]
 [1214. 1152.]]

ACCURACY=0,0198840099420049
PRECISION=1.0
RECALL=0,0233306516492357
```

Di seguito proponiamo la consueta matrice di confusione con training set uguale al test set e pari all'intero dataset.
```
[[4068.    0.]
 [   0. 3866.]
 [  12.    0.]]

ACCURACY=0.9984898061917946
PRECISION=1.0
RECALL=0.9970588235294118
```


## Risultati sul dataset `car`
Questo [dataset](https://archive.ics.uci.edu/ml/datasets/Car+Evaluation) contiene valutazioni di veicoli secondo 6 attributi (tutti categorici). L'ultimo attributo è la classe: acceptable (acc) o unacceptable (unacc), dove in acceptable sono state inserite anche le istanze classificate come good e very good (per la natura univariata dell'algoritmo in esame).

Il passo `P3` ha marcato il dataset come exemplified dopo aver calcolato i valori necessari a prendere tale decisione.
```
R=1728, r=1728, R/r=1.0, N=6, N^2=36
mark = exemplified
```

L'applicazione dell'algoritmo permette di passare da 1728 a 91 regole.

Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F) utilizzando un test set con dimensione pari al 30% dell'intero dataset:
```
[[ 24.   0.]
 [  3. 118.]
 [ 43.   5.]]

ACCURACY=0,735751295336787
PRECISION=1.0
RECALL=0,342857142857142
```

Di seguito proponiamo la consueta matrice di confusione con training set uguale al test set e pari all'intero dataset.
```
[[ 518.    0.]
 [   0. 1210.]
 [   0.    0.]]

ACCURACY=1.0
PRECISION=1.0
RECALL=1.0
```


## Dataset proportional
[Sepsis survival minimal clinical records Data Set](https://archive.ics.uci.edu/ml/datasets/Sepsis+survival+minimal+clinical+records): raccolta di dataset contenenti record sanitari (con informazioni minime) di ricoveri di pazienti con sepsi.

Ogni dataset presenta 4 informazioni cliniche:
- `age_years`: valore intero
- `sex_0male_1female`: valore binario
- `episode_number`: valore intero
- `hospital_outcome_1alive_0dead`: valore binario (classe)

Il passo `P3` ha marcato il dataset come exemplified dopo aver calcolato i valori necessari a prendere tale decisione.
```
R=19051, r=1010, R/r=18.862376237623764, N=3, Nln(N)=3.295836866004329
mark = proportional
```

L'applicazione dell'algoritmo permette di passare da 19051 a 646 regole (il numero di coppie di superiorità varia a seconda della threshold utilizzata).


Valutazione dell'algorimo attraverso la matrice di confusione (righe=P,N,?; colonne=T,F) utilizzando un test set con dimensione pari al 30% dell'intero dataset:
```
[[ 437.   52.]
 [  85.   13.]
 [4112. 1017.]]
 
ACCURACY=0,0787263820853743
PRECISION=0,893660531697341
RECALL=0,0943029779887786
```

Di seguito proponiamo la consueta matrice di confusione con training set uguale al test set e pari all'intero dataset.
```
[[ 1290.    1.]
 [   82.   34.]
 [14073. 3571.]]

ACCURACY=0,0694976641646107
PRECISION=0,999225406661502
RECALL=0,0835221754613143
```

Per cercare di migliorare i risultati è stata apportata una modifica a `MRP3` tale per cui quando si aggiunge una nuova regola essa prende frequenza pari a 0 (se è nuova) oppure aumenta di 1 la sua frequenza (se era già presente). Con questo tipo di modifica i risultati migliorano (a fronte di un numero maggiore di coppie di superiorità):
```
[[15272. 3540.] 
 [  166.   57.] 
 [    7.    9.]]

ACCURACY=0.8046296782321138
PRECISION=0.8118222411226876
RECALL=0.9887989640660408
```



## Altri risultati
Sono stati selezionati ulteriori dataset per verificare il comportamento dell'algoritmo nei diversi casi previsti (exemplified, proporitonal, nessuno dei due).

### Dataset exemplified
[Balloons Data Set](https://archive.ics.uci.edu/ml/datasets/Balloons): quattro dataset che rappresentano diverse condizioni di un esperimento.

Hanno tutti gli stessi attributi:
- `color`: yellow, purple
- `size`: large, small
- `act`: stretch, dip
- `age`: adult, child
- `inflated`: T, F (classe)

Output:
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
    Si può vedere che l'algoritmo ritorna come regole per la classe positiva `(-a_size, -a_color)` e `(-a_act, -a_age)` rispettivamente:
    - Primo bit di `color` pari a 0 e primo bit di `size` pari a 0.
    - Primo bit di `age` pari a 0 e primo bit di `act` pari a 0.

- Per gli altri tre dataset è possibile fare ragionamenti analoghi. In particolare, tutti i dataset sono stati fatti in maniera tale che si possa estrarre questo tipo di regole come spiegazione; essi contengono infatti tutte le combinazioni degli attributi.

### Dataset non marcato
[HIV-1 protease cleavage Data Set](https://archive.ics.uci.edu/ml/datasets/HIV-1+protease+cleavage): elenco di ottameri (8 aminoacidi) e un flag di classe (-1 o 1 a seconda che la proteasi dell'HIV-1 si scinderà o meno in posizione centrale).

Output:
```
R=746, r=746, R/r=1.0, N=1, N^2=1

Mark = None. L'algoritmo si ferma e non produce output
```
Il risultato era atteso in quanto l'unico attributo presenta un numero di valori distinti pari al numero delle righe del dataset.