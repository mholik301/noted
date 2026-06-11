import tkinter as tk
from tkinter import *

def bind(parent: Tk, textEditor, canvas: Canvas):

    #generic
    parent.bind("<Key>", textEditor.keyHandler)
    parent.bind("<Return>", textEditor.keyHandler) #<Return> == ENTER

    #every bind after this will override the above ^^ binds

    #cursor
    parent.bind("<Up>", textEditor.cursorUp)
    parent.bind("<Down>", textEditor.cursorDown)
    parent.bind("<Right>", textEditor.cursorRight)
    parent.bind("<Left>", textEditor.cursorLeft)

    #select
    #parent.bind("<Shift-L><Right>", textEditor.selectionRight)
    #parent.bind("<Shift-L><Left>", textEditor.selectionLeft)
    #parent.bind("<Shift-L><Up>", textEditor.selectionUp)
    #parent.bind("<Shift-L><Down>", textEditor.selectionDown)
    #kombinacije ^^ ne rade na zalost


    #control
    parent.bind("<Escape>", lambda x: textEditor.terminate())


    #click location
    canvas.bind("<Button-1>", textEditor.xy)
    #parent.bind("<B1-Motion>", textEditor.makeSelect)
    canvas.bind("<ButtonRelease-1>", textEditor.makeSelect)


    #edit
    parent.bind("<BackSpace>", textEditor.deleteBefore)
    parent.bind("<Delete>", textEditor.deleteAfter)


    #masking special keys
    parent.bind("<Control_L>", textEditor.voidHandler)
    parent.bind("<Shift_L>", textEditor.voidHandler)
    parent.bind("<Control_R>", textEditor.voidHandler)
    parent.bind("<Shift_R>", textEditor.voidHandler)

    #clipboard
    parent.bind("<Control-c>", textEditor.copy) #copy
    parent.bind("<Control-x>", textEditor.cut) #cut
    parent.bind("<Control-v>", textEditor.paste) #paste #alt: <Control_L><v>
    parent.bind("<Control_L><Shift_L><V>", textEditor.pasteOnce) #one time paste


    #undo/redo
    parent.bind("<Control-z>", textEditor.undo)
    parent.bind("<Control-y>", textEditor.redo)

    #focus check
    parent.bind("<Alt-Up>", textEditor.focus)



