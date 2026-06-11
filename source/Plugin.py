from abc import abstractclassmethod
import tkinter as tk
from tkinter import *

from TextEditorModel import TextEditorModel
from UndoManager import UndoManager
from ClipboardStack import ClipboardStack

class Plugin:
    @abstractclassmethod
    def getName():
        """ime plugina (za izbornicku stavku)"""
        pass

    @abstractclassmethod
    def getDescription():
        """kratki opis"""
        pass

    @abstractclassmethod
    def execute(model: TextEditorModel, undoManager: UndoManager, clipboardStack: ClipboardStack):
        """kratki opis"""
        #TextEditorModel model, UndoManager undoManager, ClipboardStack clipboardStack
        pass
