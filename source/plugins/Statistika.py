from Plugin import Plugin, TextEditorModel, UndoManager, ClipboardStack
import tkinter

class Statistika(Plugin):

    def __init__(self):
        return self

    def getName():
        ime="Statistics"
        return ime

    def getDescription():
        ime="This tools prints the number of lines, words and characters in the document"
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

        root.title("Statistics")

        result = "Lines: {}\nWords: {}\nCharacters: {}\n".format(lineNum, wordCount, characterCount)

        #make frame
        frame1 = tkinter.Label(root, text=result, bg = '#AAAAAA', width=30, height=10)

        #render frame in window
        frame1.pack()
        root.mainloop()

        