# Risultati

## Dataset exemplified
[Balloons Data Set](https://archive.ics.uci.edu/ml/datasets/Balloons): quattro dataset che rappresentano diverse condizioni di un esperimento.

Hanno tutti gli stessi attributi:
- `color`: yellow, purple
- `size`: large, small
- `act`: stretch, dip
- `age`: adult, child
- `inflated`: T, F (classe)

Output:
- Nel dataset `adult-stretch.data` la classe è `T` se `age=adult` e `act=stretch`.
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

- Nel dataset `adult+stretch.data` la classe è `T` se `age=adult` oppure `act=stretch`.
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

## Dataset non marcato
[HIV-1 protease cleavage Data Set](https://archive.ics.uci.edu/ml/datasets/HIV-1+protease+cleavage): elenco di ottameri (8 aminoacidi) e un flag di classe (-1 o 1 a seconda che la proteasi dell'HIV-1 si scinderà o meno in posizione centrale).

Output:
```
R=746, r=746, R/r=1.0, N=1, N^2=1

Mark = None. L'algoritmo si ferma e non produce output
```
Il risultato era atteso in quanto l'unico attributo presenta un numero di valori distinti pari al numero delle righe del dataset.

## Dataset proportional
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
L'applicazione dell'algoritmo ha permesso di passare da 19051 a 544 regole.
