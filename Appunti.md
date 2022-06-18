# INPUT
Dataset (categorico e univariato, ossia con una sola classe) avente la forma di un insieme di regole *if-then-else* indipendenti l'una dall'altra (approccio non monotono); le regole avranno la forma *feature/colonne/valori --> classe*.

# PRE-PROCESSING
* **P0**: tabella di input --> bag of words, per ogni colonna calcoliamo le frequenze di ciascun valore (per ogni colonna si costruisce una tabella con *valore:frequenza*).
* **P1**: outlier elimination, ANOVA ordine 1 (eliminazione dei valori con frequenza minore di *media - std*).
* **P2**: feature selection, eliminazione delle colonne in cui c'è un solo valore oppure un valore e NULL.
* **P3**: stato del dataset, calcolo *R / r* (#righe / #combinazioni possibili nel dataset; es.: 5 * 4 * 3 se ci sono 3 colonne con 5, 4 e 3 valori rispettivamente) non contando le combinazioni con il NULL, l'output è *esempi* (non dobbiamo calcolare le frequenze) o *proporzioni*.
* **D1**: se stato del dataset = *esempi*, salta a **P5**.
* **P4**: ANOVA sulla distribuzione di *R / r* (per ogni combinazione vado a vedere quante volte occorre quella combinazione indipendentemente dal fatto che porti alla classe o alla non-classe; es.: se ho 3 colonne che contengono valori binari *x,y,z* guardo quante volte occorre ogni loro combinazione, quella che occorre meno è inutile), eliminazione di righe e combinazioni.
* **D2**: se **P4** ha eliminato almeno una riga, ritorna a **P1**.
* **P5**: Shannon Map (2 algoritmi diversi a seconda dello stato del dataset, se è *none* l'algoritmo si ferma e non produce output), se in una colonna ci sono *N* valori escluso NULL il primo intero più grande di *log N* è sufficiente per mappare tutti i valori (ogni colonna viene mappata in un certo numero di variabili booleane, se c'è NULL non scriverò il letterale).
* **P6**: se stato del dataset = *esempi*, calcolo il set di letterali marcandoli positivo/negativo se derivano o meno la classe e li aggiungo all'insieme delle regole della teoria (es.: se un set di letterali compare 12 volte lo aggiungerò una volta sola).
* **P7**: se stato del dataset = *proporzioni*, calcolo per ogni combinazione di letterali (positiva o negativa) quante volte essa si presenta e costruisco la corrispondente bag of words.
