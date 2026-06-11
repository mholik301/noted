from abc import abstractclassmethod
from EditAction import EditAction
from UndoObserver import UndoObserver, WhosEmpty


class UndoManager(EditAction, UndoObserver):

    @abstractclassmethod
    def push(self, c: EditAction):
        """
        pohrani undo/redo akciju i pocisti redo stack
        
        tj., svaka nova akcija resetira redo lanac, tj. mogu se redo-ati samo undo-ovi sve dok se ne
        napravi nova akcija
        """
        

    @abstractclassmethod
    def undo(self):
        """ponisti zadnju akciju i postavi ju na redo LIFO"""

    @abstractclassmethod
    def redo(self):
        """ponovi zadnju ponistenu akciju i postavi ju na undo LIFO"""


    @abstractclassmethod
    def attachUndoObserver(self, observer):
        pass

    @abstractclassmethod
    def detachUndoObserver(self, observer):
        pass

    @abstractclassmethod
    def updateUndoObservers(self, whoIsEmpty: WhosEmpty):
        pass


