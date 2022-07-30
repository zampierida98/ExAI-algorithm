# Algoritmo per regole

## INPUT
Dataset (categorico e univariato, ossia con una sola classe) avente la forma di un insieme di regole *if-then-else* indipendenti l'una dall'altra (approccio non monotono); le regole avranno la forma *feature/colonne/valori --> classe*.

## PRE-PROCESSING
* **P0**: tabella di input --> bag of words, per ogni colonna si calcolano le frequenze assolute di ciascun valore.
* **P1**: outlier elimination, ANOVA ordine 1 (eliminazione dei valori con frequenza minore di *media - std*).
* **P2**: feature selection, eliminazione delle colonne in cui c'è un solo valore oppure un valore e NULL.
* **P3**: stato del dataset, calcolo *R / r* (#righe / #combinazioni possibili nel dataset; es.: 5 * 4 * 3 se ci sono 3 colonne con 5, 4 e 3 valori rispettivamente) non contando le combinazioni con il NULL, l'output è *esempi* (non dobbiamo calcolare le frequenze) o *proporzioni*.
* **D1**: se stato del dataset = *esempi*, salta a **P5**.
* **P4**: ANOVA sulla distribuzione di *R / r* (per ogni combinazione vado a vedere quante volte occorre quella combinazione indipendentemente dal fatto che porti alla classe o alla non-classe; es.: se ho 3 colonne che contengono valori binari *x,y,z* guardo quante volte occorre ogni loro combinazione, quella che occorre meno è inutile), eliminazione di righe e combinazioni.
* **D2**: se **P4** ha eliminato almeno una riga, ritorna a **P1**.
* **P5**: Shannon Map (2 algoritmi diversi a seconda dello stato del dataset, se è *none* l'algoritmo si ferma e non produce output), se in una colonna ci sono *N* valori escluso NULL il primo intero più grande di *log N* è sufficiente per mappare tutti i valori (ogni colonna viene mappata in un certo numero di variabili booleane, se c'è NULL non scriverò il letterale).
* **P6**: se stato del dataset = *esempi*, calcolo il set di letterali marcandoli positivo/negativo se derivano o meno la classe e li aggiungo all'insieme delle regole della teoria (es.: se un set di letterali compare 12 volte lo aggiungerò una volta sola).
* **P7**: se stato del dataset = *proporzioni*, calcolo per ogni combinazione di letterali (positiva o negativa) quante volte essa si presenta e costruisco la corrispondente bag of words.

## SHRINKING (per dataset exemplified)
* **MRE1**: se le due regole sono concordi (portano entrambe alla classe o alla non-classe) e gli antecedenti della prima sono un sottoinsieme degli antecedenti della seconda con alcuni antecedenti della seconda che non lo sono della prima (es.: *a,b+* e *a,b,c+*), allora cancello la seconda regola perché inutile.
* **MRE2**: se le due regole sono discordi (una porta alla classe e l'altra alla non-classe) e gli antecedenti della prima sono un sottoinsieme degli antecedenti della seconda con alcuni antecedenti della seconda che non lo sono della prima, allora dico che la regola con più letterali (la seconda) batte l'altra cioè aggiungo una coppia di superiorità.
* **MRE3**: se le due regole sono concordi e gli antecedenti sono tutti uguali tranne uno che è l'opposto del suo corrispondente (es.: *a,b,c* e *a,b,-c*), allora aggiungo una nuova regola formata dagli antecedenti in comune (es.: *a,b*) senza cancellare le due regole.

## SHRINKING (per dataset proportional)
* **MRP1**: se le due regole sono concordi e gli antecedenti della prima sono un sottoinsieme degli antecedenti della seconda con alcuni antecedenti della seconda che non lo sono della prima, allora cancello la seconda regola (in realtà devo solo marcarla segnando se ho confrontato quella regola con tutte le regole esistenti e solo in quel caso cancellarla veramente); il numero di volte in cui essa si presenta sarà la somma delle frequenze della prima e della seconda regola.
* **MRP2**: se le due regole sono discordi e gli antecedenti della prima sono un sottoinsieme degli antecedenti della seconda con alcuni antecedenti della seconda che non lo sono della prima, allora dico che la regola con più letterali (la seconda) batte l'altra cioè aggiungo una coppia di superiorità.
* **MRP3**: se le due regole sono concordi e gli antecedenti sono tutti uguali tranne uno che è l'opposto del suo corrispondente, allora aggiungo una nuova regola formata dagli antecedenti in comune e con frequenza pari a 0 (se è nuova) oppure aumentata di 1 (se era già presente).
* **MRP4**
    * *C1*: se le due regole sono discordi e gli antecedenti della prima sono un sottoinsieme degli antecedenti della seconda con le occorrenze della prima che sono maggiori delle occorrenze della seconda.
    * *C2*: se il rapporto tra le occorrenze della prima e della seconda regola è più basso di una threshold (almeno pari a 1).
    * Se *C1 and C2*, allora cancello la seconda regola in quanto la prima prevale sulla seconda (in realtà devo solo marcarla segnando se ho confrontato quella regola con tutte le regole esistenti e solo in quel caso cancellarla veramente); il numero delle occorrenze sarà aggiornato con la somma delle frequenze della prima e della seconda regola.
    * Se *C1 and not C2*, allora cancello sia la prima che la seconda regola in quanto sono troppo vicine (in realtà devo solo marcarle segnando se ho confrontato quelle regole con tutte le regole esistenti e solo in quel caso cancellarle veramente); i numeri delle occorrenze saranno aggiornati con la somma delle frequenze della prima e della seconda regola.
* **MRP5**: se le due regole sono discordi e gli antecedenti della prima sono sovrapposti agli antecedenti della seconda (es. *a,b,c* e *a,b,c,d*) e se il rapporto tra le occorrenze della prima e della seconda regola è più alto di una threshold (anche la stessa di **MRP4**), allora dico che la prima regola è superiore alla seconda.

## OUTPUT
File di testo col seguente formato:
* Per dataset exemplified, *(a,b,-c,-d)+*.
* Per dataset proportional, *(a,-c,-d)+53*.
