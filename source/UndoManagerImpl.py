from UndoManager import UndoManager, UndoObserver, EditAction, WhosEmpty
from collections import deque


ActionStack = deque[EditAction]
UndoObservers = deque[UndoObserver]

#https://www.geeksforgeeks.org/deque-in-python/
#.pop(), .append()
# append, appendleft, remove, popleft nisu u duhu stoga
#postoje i naredbe za automatsko ubacivanje vise elem, u raznim redosljedima i sl.



#note za 2.8: mislim da je "Neka razred UndoManager bude Subjekt (OO Promatrač) za informacije 
# o statusu stogova" krivo. Nema mi smisla da UndoManager koji sadrzi stogove bude njihov promatrac
#s druge strane, da bude publisher o tome je li undo/redoStack prazan ili ne vec ima smisla


#note2: definicijom preko UndoManager sucelja, niti TextEditor niti TextEditorModel nisu ovisni o
#MyUndoManageru, niti je on ovisan o njima. Zbog toga je potrebno u instance EditAction pohraniti i
#potrebne reference

class UndoManagerImpl(UndoManager):
    def __init__(self):
        self._undoStack = ActionStack()
        self._redoStack = ActionStack()

        self._undoObservers = UndoObservers()



    def push(self, c: EditAction):
        self._redoStack = ActionStack()
        self._undoStack.append(c)

        self.updateUndoObservers(WhosEmpty(undoEmpty=not self._undoStack, redoEmtpy=not self._redoStack))
        


    def undo(self):
        action = self._undoStack.pop()
        assert isinstance(action, EditAction)
        self._redoStack.append(action)
        action.execute_undo()

        #"not self._undoStack" = True ako je undoStack prazan
        self.updateUndoObservers(WhosEmpty(undoEmpty=not self._undoStack, redoEmtpy=not self._redoStack))


    def redo(self):
        action = self._redoStack.pop()
        assert isinstance(action, EditAction)
        self._undoStack.append(action)
        action.execute_do()

        #"not self._undoStack" = True ako je undoStack prazan
        self.updateUndoObservers(WhosEmpty(undoEmpty=not self._undoStack, redoEmtpy=not self._redoStack))




    


    def attachUndoObserver(self, observer):
        self._undoObservers.append(observer)

    def detachUndoObserver(self, observer):
        self._undoObservers.remove(observer)

    def updateUndoObservers(self, whoIsEmpty: WhosEmpty):
        for undoObserver in self._undoObservers:
            undoObserver.updateUndoLis(whoIsEmpty)


