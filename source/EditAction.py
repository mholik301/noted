from abc import abstractclassmethod

class EditAction():
    #implementacija mora dati i __init__ koji pohrani podatke o akciji kako bi znao pozvati korektni undo

    @abstractclassmethod
    def execute_do(self):
        pass

    @abstractclassmethod
    def execute_undo(self):
        pass