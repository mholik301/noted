from abc import abstractclassmethod

class WhosEmpty():
    """
    DTO za prijenos stanja undo/redo stogova

    ---
    
    koristenje:

    info = WhosEmpty(undoEmpty=not self._undoStack, redoEmtpy=not self._redoStack)

    info.isUndoEmpty() # = True za _undoStack==[]

    ---

    elementarni primjer

    info2 = WhosEmpty(undoEmpty=True, redoEmtpy=False)

    info2.isUndoEmpty() #=True

    info2.isRedoEmpty() #=False
    """
    def __init__(self, undoEmpty: bool, redoEmtpy: bool):
        self._undoEmpty=undoEmpty
        self._redoEmpty=redoEmtpy

    def isUndoEmpty(self):
        return self._undoEmpty

    def isRedoEmpty(self):
        return self._redoEmpty


class UndoObserver:
    @abstractclassmethod
    def updateUndoLis(whoIsEmpty: WhosEmpty):
        """primarno da disablanje undo/redo gumba"""
        pass