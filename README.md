# leanbit-challenge

per testare il codice:

livelli 1,2,3: semplicemente lanciare 'python main.py' da riga di comando. L'output viene prodotto direttamente.

livello 4: lanciare 'python tractus.py' da riga di comando. Lo script chiederà quali operazioni svolgere. È possibile ottenere gli output richiesti ai livelli precedenti, oppure un calendario in cui ogni giorno è indicato il progetto assegnato a ciascun sviluppatore. Il calendario può essere stampato come file .json oppure come tabella in html. 

Il calendario è creato con un algoritmo greedy per nulla raffinato, che ogni giorno assegna i progetti in base a una valutazione di priorità basata su quanti giorni mancano alla deadline e quanti giorni di effort occorre ancora allocare per ciascun progetto. 
