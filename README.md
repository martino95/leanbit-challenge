# leanbit-challenge

requisiti:
è necessario installare il pacchetto holidays (ad es. con pip: 'pip install holidays')
il codice dovrebbe funzionare sia con python2 che con python3

per testare il codice:

livelli 1,2,3: semplicemente lanciare 'python main.py' da riga di comando. L'output richiesto viene prodotto direttamente.

livello 4: lanciare 'python tractus.py' da riga di comando. Lo script chiederà quali operazioni svolgere. È possibile ottenere gli output richiesti ai livelli precedenti (ho aggiunto alla cartella level4 il file data_lv2.json: copia del file data.json in level2 e level1, per replicarne i risultati); oppure un calendario in cui ogni giorno è indicato il progetto assegnato a ciascun sviluppatore. Il calendario può essere stampato come file .json oppure come tabella in html. 

Il calendario è creato con un algoritmo greedy piuttosto semplice, che ogni giorno assegna i progetti in base a una valutazione di priorità basata su quanti giorni mancano alla deadline e quanti giorni di effort occorre ancora allocare per ciascun progetto. 
