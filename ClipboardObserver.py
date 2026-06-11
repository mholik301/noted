from abc import abstractclassmethod

class ClipboardObserver:
    @abstractclassmethod
    def updateClipboardLis(isEmpty: bool):
        pass