import tkinter as tk
from tkinter import *
from tkinter.font import Font

from math import floor, ceil
from copy import copy

from Location import Location
from LocationRange import LocationRange
from UndoManagerImpl import UndoManagerImpl
from TextEditorModel import TextEditorModel
from ClipboardStack import ClipboardStack

from CursorObserver import CursorObserver
from TextObserver import TextObserver
from SelectionObserver import SelectionObserver
from ClearSelectionObserver import ClearSelectionObserver
from ClipboardObserver import ClipboardObserver
from UndoManager import UndoManager, UndoObserver, WhosEmpty

from bindKeys import bind as bindUtil
from AddMenubar import setupMenubar
from AddToolbar import setupToolbar

from Plugin import Plugin
from ModuleFactory import ModuleFactory as myfactory

from functools import partial



class Config(object):
    height=800
    width=800

    fontSize=24
    fontType='TkFixedFont'
    fontColor="black"

    globalXOffset=5 #to make space for cursor in front of 1st letter

    cursorSizeModifier=8 #smaller number->bigger reduction, default=8
    cursorWidth=3 #default=3

    underlineHeightModifier=6 #smaller number->higher/closer to text, default=6
    underlineWidth=3 #default=3




class TextEditor(tk.Frame, CursorObserver, SelectionObserver, TextObserver, ClearSelectionObserver, UndoObserver, ClipboardObserver):
#region basic
    def __init__(self, parent: Tk, model: TextEditorModel):
        tk.Frame.__init__(self, parent, height=Config.height, width=Config.width)
        
        self.label = tk.Label(self) #why?

        self._parent=parent
        self.tk_focusFollowsMouse()
        parent.title("MH's noted")

        

        self._canvas = Canvas(self, bg="white", height=Config.height, width=Config.width)
        self._canvas.pack(fill="both", expand=True)

        self._font = Font(font=Config.fontType)
        self._font["size"]=Config.fontSize

    
        self._menubar = setupMenubar(parent=parent, textEditor=self)

        refList=list()
        self.toolbarRef=setupToolbar(parent=parent, textEditor=self, refList=refList, canvas=self._canvas)

        self._copyButton=refList[0]
        self._cutButton=refList[1]
        self._pasteButton=refList[2]
        self._undoButton=refList[3]
        self._redoButton=refList[4]

        self.disableButton(self._redoButton)
        self.disableButton(self._undoButton)
        self.disableButton(self._pasteButton)
        self.disableButton(self._copyButton)
        self.disableButton(self._cutButton)



        self._model = model
        letterWidth, canvasWidth, letterHeight, canvasHeight = self.cavnasInfoQuery()
        self._model._setCanvasParams(letterWidth, canvasWidth, letterHeight, canvasHeight)

        self._clipboard = ClipboardStack()

        self._undoManager = UndoManagerImpl()
        self._undoEmpty = self._redoEmpty = True
        self._model._setUndoManager(self._undoManager)

        

        self._cursorObj = self._resetCursor()
        self._selectObjList = list()

        self.updateText()

        self._model.attachCursorObserver(self)
        self._model.attachSelectObserver(self)
        self._model.attachTextObserver(self)
        self._model.attachClearSelectObserver(self)
        self._undoManager.attachUndoObserver(self)
        self._clipboard.attachClipboardObserver(self)
        

        bindUtil(parent=parent, textEditor=self, canvas=self._canvas)


        
        self._statusBarVariable=tk.StringVar() 
        self._statusBarVariable.set("Click somewhere on the canvas")
        self._statusbar = tk.Label(parent, text=self._statusBarVariable.get(), bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self._statusbar.pack(side=tk.BOTTOM, fill=tk.X)


        self.loadPlugins()

        self.pack(fill="both", expand=True)


    
    def terminate(self):
        self.destroy()


    def getLetterHeight(self):
        return Font.metrics(self._font, 'linespace')

    def getLetterWidth(self):
        return Font.measure(self._font, "A")
    
    def getLineLenght(self, line):
        return Font.measure(self._font, line)

    def getMaxLineLen(self):
        return floor(self._canvas.winfo_reqwidth()/self.getLetterWidth())

#endregion


#region concrete commands
    #the invokers are in the tkinter.Window, setCommand() are the 'bind' commands in bindKeys


    def cavnasInfoQuery(self):
        letterWidth, canvasWidth = self.getLetterWidth(), self._canvas.winfo_reqwidth()
        letterHeight, canvasHeight = self.getLetterHeight(), self._canvas.winfo_reqheight()
        return letterWidth, canvasWidth, letterHeight, canvasHeight


    def testHandler(self, event=''):
        print(event.char, event.keysym, event.keycode)

    def voidHandler(self, event=''):
        pass


    def focus(self, event=''):
        widget = self._parent.focus_get()
        children = self._parent.winfo_children()
        print(widget, "has focus")



    def keyHandler(self, event=''):
        self._model.insert(event.char)


    def cursorUp(self, event=''):   #execute (nema Concrete command klase/objekta)
        self._model.cursorUp()      #action() (nema Receiver klase/objekta)

    def cursorDown(self, event=''):
        self._model.cursorDown()

    def cursorRight(self, event=''):
        self._model.cursorRight()

    def cursorLeft(self, event=''):
        self._model.cursorLeft()

    

    def selectionUp(self, event=''):
        self._model.selectionUp()

    def selectionDown(self, event=''):
        self._model.selectionDown()

    def selectionRight(self, event=''):
        self._model.selectionRight()

    def selectionLeft(self, event=''):
        self._model.selectionLeft()



    def xy(self, event=''):
        if event=='':
            #misclick?
            x, y = 0, 0
        else:
            x, y = event.x, event.y
        self._model.xy(x, y)

    def makeSelect(self, event=''):
        if event=='':
            #misclick?
            current_x, current_y = 0, 0
        else:
            current_x, current_y = event.x, event.y
        self._model.makeSelect(current_x, current_y)


    def deleteAfter(self, event=''):
        self._model.deleteAfter()

    def deleteBefore(self, event=''):
        self._model.deleteBefore()




    def copy(self, event=''):
        selectedText = self._model.getTextInSelection()
        self._clipboard.push(selectedText)

    def cut(self, event=''):
        self.copy(self, event)
        self._model.deleteRange(self._model.selection)

    def paste(self, event=''):
        savedText = self._clipboard.peek()
        if savedText:
            self._model.insert(savedText)

    def pasteOnce(self, event=''):
        self.paste()
        _ = self._clipboard.pop()



    def undo(self, event=''):
        if not self._undoEmpty:
            self._undoManager.undo()

    def redo(self, event=''):
        if not self._redoEmpty:
            self._undoManager.redo()




    
#endregion


#region listeners
    
    def updateCursorLocationLis(self, loc: Location):
        self.updateCursor()
        self.updateStatusBar()

    def updateTextLis(self, cursor: Location=None, rangeParam: LocationRange=None):
        self.updateText(cursor=cursor, rangeParam=rangeParam)
        self.updateStatusBar()


    def updateSelectLis(self, range: LocationRange):
        self.updateSelect(range)
        self.enableButton(self._copyButton)
        self.enableButton(self._cutButton)
        #self._menubar.entryconfig(1, state=DISABLED)

    def clearSelectLis(self):
        for selection in self._selectObjList:
            self._deleteElement(selection)
        self.disableButton(self._copyButton)
        self.disableButton(self._cutButton)


    def updateUndoLis(self, whoIsEmpty: WhosEmpty):
        self._undoEmpty = whoIsEmpty.isUndoEmpty()
        self._redoEmpty = whoIsEmpty.isRedoEmpty()

        if self._undoEmpty:
            self.disableButton(self._undoButton)
        else:
            self.enableButton(self._undoButton)

        if self._redoEmpty:
            self.disableButton(self._redoButton)
        else:
            self.enableButton(self._redoButton)

    def updateClipboardLis(self, isEmtpy: bool):
        if isEmtpy:
            self.disableButton(self._pasteButton)
        else:
            self.enableButton(self._pasteButton)

#endregion

     
#region elementary
    #functions have _ appended if they call _canvas.pack()
    #if a function doesnt have _, it shouldnt referece/modify canvas

    def _deleteElement(self, ref):
        self._canvas.delete(ref)
        self._canvas.pack()

    def _clearCanvas(self):
        self._canvas.delete('all')

    def _resetCursor(self):
        return self._drawCursor(1,1)


    def _drawLine(self, line):
        lineNum=self._model.cursor.y #this overrides the specified lineNum -> lineNum arg has no effect
        lineY = self.getLetterHeight()*(lineNum-1)
        lineX = Config.globalXOffset+(self._model.cursor.x-1)*self.getLetterWidth()
        ref = self._canvas.create_text(lineX,lineY,fill="black",font=self._font, text=line, anchor=NW)
        self._canvas.pack()
        #return ref

    def _eraseLine(self, lineNum):
        x1=Config.globalXOffset+self.getLetterWidth()*(1-1)
        x2=Config.globalXOffset+self.getLetterWidth()*self.getMaxLineLen()
        y1=y2=self.getLetterHeight()*(lineNum-0.50)
        coord = x1, y1, x2, y2
        self._canvas.create_line(coord, fill="white", width=self.getLetterHeight()*0.9)
        self._model.setCursor(0, lineNum)
        self.updateCursor()
        self._canvas.pack()

    def _refreshLine(self, line, lineNum, newCursor):
        newCursorX=None
        if newCursor!=None:
            newCursorX = newCursor.x
            newCursorY = newCursor.y
        self._eraseLine(lineNum)
        lineY = self.getLetterHeight()*(lineNum-1)
        lineX = Config.globalXOffset+(self._model.cursor.x-1)*self.getLetterWidth()
        self._canvas.create_text(lineX,lineY,fill="black",font=self._font, text=line, anchor=NW)
        if newCursor==None:
            self._model.setCursor(len(line)+1, lineNum)
        else:
            #self._model.setCursor(newCursorX, self._model.cursor.y)
            self._model.setCursor(newCursorX, newCursorY)
        self.updateCursor()
        self._canvas.pack()

    def _drawUnderline(self, startLetter, endLetter, lineNum):
        x1=Config.globalXOffset+self.getLetterWidth()*(startLetter-1)
        x2=Config.globalXOffset+self.getLetterWidth()*endLetter
        y1=y2=self.getLetterHeight()*lineNum-self.getLetterHeight()/Config.underlineHeightModifier
        coord = x1, y1, x2, y2
        ref = self._canvas.create_line(coord, fill="black", width=Config.underlineWidth)
        self._canvas.pack()
        return ref

    def _drawCursor(self, beforeLetter, lineNum):
        cursorTopReduce=-1*self.getLetterHeight()/Config.cursorSizeModifier 
        cursorBottomReduce=self.getLetterHeight()/Config.cursorSizeModifier
        x1=x2=Config.globalXOffset+self.getLetterWidth()*(beforeLetter-1)
        y1=self.getLetterHeight()*(lineNum-1)-cursorTopReduce
        y2=self.getLetterHeight()*(lineNum)-cursorBottomReduce
        coord = x1, y1, x2, y2
        ref = self._canvas.create_line(coord, fill="black", width=Config.cursorWidth)
        self._canvas.pack()
        return ref

    def _drawSelect(self, startLetter, endLetter, lineNum):
        self._eraseLine(lineNum)

        x1=Config.globalXOffset+self.getLetterWidth()*(startLetter-1)
        x2=Config.globalXOffset+self.getLetterWidth()*endLetter
        y1=y2=self.getLetterHeight()*(lineNum-0.55)
        coord = x1, y1, x2, y2
        ref = self._canvas.create_line(coord, fill="lightblue", width=self.getLetterHeight()*0.85)
        
        line=self._model.getLine(lineNum-1)
        self._model.setCursor(0, lineNum)
        self._drawLine(line)
        self._model.setCursor(endLetter+1, lineNum)
        self.updateCursor()

        return ref
        

#endregion


#region user functions
    def printLine(self, line, lineNum=None):
        self.update()
        if self._model.cursor.y + self.getLetterHeight() > self._canvas.winfo_reqheight():
            #TODO: expand canvas?, undo?, raise exception?
            #self.terminate()
            pass
        if lineNum == None:
            lineNum = self._model.cursor.y
        if self._model.cursor.x*self.getLetterWidth() + self.getLineLenght(line) > self._canvas.winfo_reqwidth():
            self.setCursorNextLine()   
        self._drawLine(line)
        self._model.moveCursor(len(line)+1, 0)
        self.updateCursor()

    def printLines(self, lines, lineNum=None):
        if self._model.cursor.x > 1:
            self.setCursorNextLine()
        for line in lines:
            self.update()
            if self._model.cursor.x*self.getLetterWidth() + self.getLineLenght(line) > self._canvas.winfo_reqwidth():
                #TODO: split line?
                #self.terminate()
                pass
            self.printLine(line, lineNum)
            self.setCursorNextLine()



    def updateCursor(self):
        beforeLetter=self._model.cursor.x
        lineNum=self._model.cursor.y
        self._deleteElement(self._cursorObj)
        self._cursorObj = self._drawCursor(beforeLetter, lineNum)
        
    def setCursorNextLine(self, event=''):
        beforeLetter = 1
        lineNum=self._model.cursor.y + 1
        self._model.setCursor(beforeLetter, lineNum)
        self.updateCursor()


    def cursorHome(self):
        self._model.cursorHome()

    def cursorEnd(self):
        self._model.cursorEnd()

    def deleteAll(self):
        self._model.deleteAll()


    def updateSelect(self, rangeArg: LocationRange):
        for selection in self._selectObjList:
            self._deleteElement(selection)
        self._selectObjList = []

        start = Location(rangeArg.p1.x,rangeArg.p1.y)
        end = Location(rangeArg.p2.x,rangeArg.p2.y)

        #print("start {} {}, end {} {}".format(start.x, start.y, end.x, end.y))
        #return

        if rangeArg.isDefault():
            return

        lineCount = end.y-start.y+1
        if lineCount==1:
            #unutar jedne linije, highlightamo [x1-x2]
            self._selectObjList.append(self._drawSelect(start.x, end.x, start.y))
        elif lineCount==2:
            #dvije linije, highlightamo [x1-end, 0-x2]
            self._selectObjList.append(self._drawSelect(start.x, self.getMaxLineLen(), start.y))
            self._selectObjList.append(self._drawSelect(0, end.x, end.y))
        else:
            #tri ili vise linija
            for i in range(0, (end.y - start.y)+1):
                if i == 0:
                    #highlightamo [x1-end] u prvoj liniji
                    self._selectObjList.append(self._drawSelect(start.x, self.getMaxLineLen(), start.y))
                elif i<(end.y - start.y):
                    #highlightamo [0-end] u "srednjim" linijama
                    self._selectObjList.append(self._drawSelect(0, self.getMaxLineLen(), start.y+i))
                else:
                    #highlightamo [0-x2] u zadnjoj liniji
                    self._selectObjList.append(self._drawSelect(0, end.x, end.y))

    def updateText(self, cursor: Location=None,rangeParam: LocationRange=None):
        if rangeParam == None or rangeParam.isDefault():
            affectedLines = self._model.allLines()
        else:
            diff = rangeParam.p1.y-rangeParam.p2.y
            if diff>0:
                affectedLines = self._model.linesRange(rangeParam.p1.y, rangeParam.p2.y)
            else:
                affectedLines = self._model.linesRange(cursor.y-1,cursor.y)
        for line, lineNum in affectedLines:
            self._refreshLine(line, lineNum, cursor)

        _, _, letterHeight, canvasHeight = self.cavnasInfoQuery()
        maxRowNum = floor(canvasHeight/letterHeight)
        
        actualCursorLoc=copy(cursor)
        for lineNum in range(len(self._model.lines)+1, maxRowNum):
            self._eraseLine(lineNum)
            

        if actualCursorLoc == None:
            actualCursorLoc = self._model.cursor
        self._model.setCursor(actualCursorLoc.x, actualCursorLoc.y)


#endregion


#region toolbar, menubar, statusbar
    def disableButton(self, button):
        button['state'] = DISABLED

    def enableButton(self, button):
        button['state'] = NORMAL


    def disableCommand(self, command):
        command['state'] = DISABLED

    def enableCommand(self, command):
        command['state'] = NORMAL


    def updateStatusBar(self):
        #self._statusBarVariable.set("Test") doesnt work
        location=self._model.cursor
        lineNum=len(self._model.lines)
        positionString = "Row: {}, Column: {}, Lines: {}".format(location.x, location.y, lineNum)
        
        self._statusbar.config(text=positionString)

#endregion


#region plugins

    def loadPlugins(self):
        import os

        rootFullPath = os.path.dirname(os.path.realpath(__file__)) + "\\"
        pluginFullPath = rootFullPath + 'plugins'

        plugins=[]
        for mymodule in os.listdir(pluginFullPath):
            moduleName, moduleExt = os.path.splitext(mymodule)
            if moduleExt=='.py':
                classRef=myfactory(moduleName)
                plugins.append(classRef)

        self._plugins = list()
        filemenu = Menu(self._menubar, tearoff=0)
        for plugin in plugins:
            action_with_arg = partial(plugin.execute, self._model, self._undoManager, self._clipboard)
            self.__setattr__(plugin.getName(), action_with_arg)
            filemenu.add_command(label=plugin.getName(), command= self.__getattribute__(plugin.getName()))
        self._menubar.add_cascade(label="Plugins", menu=filemenu)

#endregion