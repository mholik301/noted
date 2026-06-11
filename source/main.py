
from TextEditor import TextEditor
from TextEditorModel import TextEditorModel

from tkinter import *

initalText = '''Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua.'''


top = Tk()

model = TextEditorModel(initalText)
editor = TextEditor(top, model)


top.mainloop()
    