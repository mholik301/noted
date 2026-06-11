from LocationRange import LocationRange
from Location import Location
from abc import abstractclassmethod

class TextObserver:
    @abstractclassmethod
    def updateTextLis(cursorLocation: Location, range: LocationRange):
        pass