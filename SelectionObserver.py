from LocationRange import LocationRange
from abc import abstractclassmethod

class SelectionObserver:
    @abstractclassmethod
    def updateSelectLis(range: LocationRange):
        pass