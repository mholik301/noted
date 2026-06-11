from tkinter import Tk, Menu

def donothing():
   x = 0

#ref:https://pythonspot.com/tk-menubar/
#ref: https://www.tutorialspoint.com/python/tk_menu.htm
   

def setupMenubar(parent: Tk, textEditor):

   menubar = Menu(parent)

   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="Open", command=donothing)
   filemenu.add_command(label="Save", command=donothing)
   filemenu.add_separator()
   filemenu.add_command(label="Exit", command=parent.quit)
   menubar.add_cascade(label="File", menu=filemenu)

   helpmenu = Menu(menubar, tearoff=0)
   helpmenu.add_command(label="Undo", command=textEditor.undo)
   helpmenu.add_command(label="Redo", command=textEditor.redo)
   helpmenu.add_command(label="Cut", command=textEditor.cut)
   helpmenu.add_command(label="Copy", command=textEditor.copy)
   helpmenu.add_command(label="Paste", command=textEditor.paste)
   helpmenu.add_command(label="Paste and Take", command=textEditor.pasteOnce)
   helpmenu.add_command(label="Delete selection", command=textEditor.deleteBefore)
   helpmenu.add_command(label="Clear document", command=textEditor.deleteAll)
   menubar.add_cascade(label="Edit", menu=helpmenu)

   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="Cursor to start", command=textEditor.cursorHome)
   filemenu.add_command(label="Cursor to end", command=textEditor.cursorEnd)
   menubar.add_cascade(label="Move", menu=filemenu)

   parent.config(menu=menubar)
   return menubar