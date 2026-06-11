from Location import Location
from abc import abstractclassmethod

class CursorObserver:
    @abstractclassmethod
    def updateCursorLocationLis(loc: Location):
        pass