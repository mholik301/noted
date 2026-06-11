from Plugin import Plugin, TextEditorModel, UndoManager, ClipboardStack
import tkinter

class Foo(Plugin):

    def __init__(self):
        return self

    def getName():
        ime="Foo"
        return ime

    def getDescription():
        ime="Ispisuje Foo"
        return ime

    def execute(model: TextEditorModel, undoManager: UndoManager, clipboardStack: ClipboardStack):
        lineNum=len(model.lines)

        characterCount=0
        wordCount=0

        for line in model.allLines():
            wordList=line[0].split(' ')
            characterCount += len(line[0])
            wordCount += len(wordList)

        
        #make window widget
        root = tkinter.Tk()

        root.title("Foo")

        result = "Bar"

        #make frame
        frame1 = tkinter.Label(root, text=result, bg = '#AAAAAA', width=30, height=10)

        #render frame in window
        frame1.pack()
        root.mainloop()

        