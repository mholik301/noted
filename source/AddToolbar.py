from tkinter import PhotoImage
from tkinter import Tk, Canvas, Frame, Button
from tkinter import LEFT, TOP, X, RAISED

#ref: https://stackoverflow.com/questions/4297949/image-on-a-button
#ref: https://zetcode.com/tkinter/menustoolbars/

#modelirano kao klasa jer ako slike nemaju anchor, garbage collector ih brise pa su gumbi prazni


class setupToolbar:
    def __init__(self, parent: Tk, textEditor, refList: list, canvas: Canvas):
        self._parent=parent
        self._canvas=canvas

        toolbar = Frame(parent, bd=1, relief=RAISED)
        toolbar.pack(side=TOP, fill=X)

        self._toolbar=toolbar


        self.copyImg = PhotoImage(file="./icons/copy.png")
        copyBtn = Button(toolbar, image=self.copyImg, command=textEditor.copy)
        copyBtn.pack(side=LEFT)

        self.cutImg = PhotoImage(file="./icons/cut.png")
        cutBtn = Button(toolbar, image=self.cutImg, command=textEditor.cut)
        cutBtn.pack(side=LEFT)

        self.pasteImg = PhotoImage(file="./icons/paste.png")
        pasteBtn = Button(toolbar, image=self.pasteImg, command=textEditor.paste)
        pasteBtn.pack(side=LEFT)

        self.undoImg = PhotoImage(file="./icons/undo.png")
        undoBtn = Button(toolbar, image=self.undoImg, command=textEditor.undo)
        undoBtn.pack(side=LEFT)

        self.redoImg = PhotoImage(file="./icons/redo.png")
        redoBtn = Button(toolbar, image=self.redoImg, command=textEditor.redo)
        redoBtn.pack(side=LEFT)

        refList.append(copyBtn)
        refList.append(cutBtn)
        refList.append(pasteBtn)
        refList.append(undoBtn)
        refList.append(redoBtn)


        #toolbar.bind("<Enter>", self.on_enter)
        #toolbar.bind("<Leave>", self.on_leave)


    def quit(self):
        self._parent.quit()

    def donothing(self):
        x = 0


    def on_enter(self, event=''):
        self._toolbar.focus_set()

    def on_leave(self, enter=''):
        self._canvas.focus_set()