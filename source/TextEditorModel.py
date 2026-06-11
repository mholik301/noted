from tkinter.constants import E
from EditAction import EditAction
from Location import Location
from LocationRange import LocationRange

from CursorObserver import CursorObserver
from TextObserver import TextObserver
from SelectionObserver import SelectionObserver
from ClearSelectionObserver import ClearSelectionObserver

from enum import Enum
from math import ceil, floor
from copy import copy

from UndoManager import UndoManager

CursorObservers = list[CursorObserver]
TextObservers = list[TextObserver]
SelectObservers = list[SelectionObserver]
ClearSelectObservers = list[ClearSelectionObserver]

class Dir(Enum):
    left = 1
    right = 2
    up = 3
    down = 4

"""
TextEditorModel treba sadržavati sljedeće podatkovne članove:

lines ... lista redaka teksta
selectionRange ... koordinate (redak,stupac) početka i kraja označenog dijela teksta
cursorLocation ... koordinate trenutnog položaja kursora, odnosno znaka ispred kojeg se nalazi kursor
"""


class TextEditorModel:
#region basic
    def __init__(self, initialText: str):
        self._lines = initialText.split('\n')
        self._selectionRange = LocationRange()
        self._cursorLocation = Location()

        self._cursorObservers = CursorObservers()
        self._textObservers = TextObservers()
        self._selectObservers = SelectObservers()
        self._clearSelectObservers = ClearSelectObservers()

        self.last_x = 0
        self.last_y = 0
        self.delSelectFlag = 0


    def _get_lines(self):
        #return iter(self._lines)
        return self._lines
    def _set_lines(self, lines: str):
        self._lines = lines
        self.updateTextObservers()
    lines = property(_get_lines, _set_lines)

    def _get_selection(self):
        return self._selectionRange
    def _set_selection(self, selection: LocationRange):
        self._selectionRange = selection
        self.updateSelectionObservers()
    selection = property(_get_selection, _set_selection)

    def _get_cursorLoc(self):
        return self._cursorLocation
    def _set_cursorLoc(self, location: Location):
        self._cursorLocation = location
        self.updateCursorObservers()
    cursor = property(_get_cursorLoc, _set_cursorLoc)


    def _setCanvasParams(self, letterWidth, canvasWidth, letterHeight, canvasHeight):
        self._letterWidth = letterWidth
        self._canvasWidth = canvasWidth
        self._letterHeight = letterHeight
        self._canvasHeight = canvasHeight
        self._maxRowNum = floor(canvasHeight/letterHeight)
        self._maxLetterNum = floor(canvasWidth/letterWidth)

    def _setUndoManager(self, undoManager: UndoManager):
        self._undoManager=undoManager
#endregion
    

#region 2.3 iterators
    def getLine(self, lineNum):
        return self._lines[lineNum]


    def allLines(self) -> tuple[str, int]:
        """vrati tuple(line, lineNum) za sve linije u modelu"""
        i = 0
        try:
            while True:
                yield (self.lines[i], i+1)
                i += 1
        except:
            pass

    def linesRange(self, index1: int, index2: int) -> tuple[str, int]:
        """vrati tuple(line, lineNum) za linije u modelu s indexom [index1, index2>"""
        i = index1
        try:
            while i < index2:
                yield (self.lines[i], i+1)
                i += 1
        except:
            pass
#endregion


#region 2.4 cursor
    def attachCursorObserver(self, observer):
        self._cursorObservers.append(observer)

    def detachCursorObserver(self, observer):
        self._cursorObservers.remove(observer)

    def updateCursorObservers(self):
        for cursorObserver in self._cursorObservers:
            cursorObserver.updateCursorLocationLis(self.cursor)

    def moveCursor(self, xDif: int, yDif: int):
        currentPos = self.cursor
        currentPos.x += xDif
        if currentPos.x < 1:
            return
            #currentPos.x = 1
        if yDif == -1: #moving up:
            if currentPos.x > len(self.lines[currentPos.y-2])+1:
                currentPos.x = len(self.lines[currentPos.y-2])+1
        currentPos.y += yDif
        if currentPos.y < 1:
            return
            #currentPos.y = 1
        if currentPos.y > len(self.lines):
            currentPos.y = len(self.lines)
        if yDif == 1: #moving down:
            if currentPos.x > len(self.lines[currentPos.y-1])+1:
                currentPos.x = len(self.lines[currentPos.y-1])+1
        if currentPos.x + xDif > len(self.lines[currentPos.y-1])+2:
            return self.moveCursorToBeginingOfNextLine()
        
        self.updateCursorObservers()

    def setCursor(self, x: int, y: int):
        succ=True

        if y > len(self.lines):
            y = len(self.lines)
            succ=False
        if y < 1:
            y = 1
        self.cursor.y = y
        
        try:
            if x > len(self.lines[y-1])+1:
                x = len(self.lines[y-1])+1
                succ=False
        except:
            x = 1
        if x < 1:
            x = 1
        self.cursor.x = x
        
        self.updateCursorObservers()
        return succ

    def resetCursor(self):
        self.setCursor(1,1)


    def moveCursorToEndOfPrevLine(self):
        currentPos = self.cursor
        newY=currentPos.y-1
        if newY == 0:
            return False
        self.setCursor(len(self.lines[newY-1])+1, newY)
        self.updateClearSelectionObservers()
        self.updateCursorObservers()
        return False

    def moveCursorToBeginingOfNextLine(self):
        currentPos = self.cursor
        newY=currentPos.y+1
        newX=0
        if newY > len(self.lines):
            newX=currentPos.x
            newY= len(self.lines)
            return False
        self.setCursor(newX, newY)
        self.updateClearSelectionObservers()
        self.updateCursorObservers()
        return True

    
    def cursorUp(self) -> bool:
        currentPos = self.cursor
        if currentPos.y < 2:
            return False
        else:
            self.moveCursor(0,-1)
            return True

    def cursorDown(self) -> bool:
        currentPos = self.cursor
        if currentPos.y*self._letterHeight > self._canvasHeight-self._letterHeight:
            return False
        else:
            self.moveCursor(0,1)
            return True

    def cursorRight(self) -> bool:
        currentPos = self.cursor
        if currentPos.x + 1 > len(self.lines[currentPos.y-1])+1:
            return self.moveCursorToBeginingOfNextLine()
        if (currentPos.x*self._letterWidth > self._canvasWidth-self._letterWidth):
            return False
        else:
            self.moveCursor(1,0)
            return True

    def cursorLeft(self) -> bool:
        currentPos = self.cursor
        if currentPos.x < 2:
            return self.moveCursorToEndOfPrevLine()
        else:
            self.moveCursor(-1,0)
            return True

    def cursorHome(self) -> bool:
        currentPos = self.cursor
        self.setCursor(1, currentPos.y)
        return True

    def cursorEnd(self) -> bool:
        currentPos = self.cursor
        end=len(self.lines[currentPos.y-1])+1
        self.setCursor(end, currentPos.y)
        return True
#endregion


#region 2.5 select
    def attachSelectObserver(self, observer):
        self._selectObservers.append(observer)

    def detachSelectionObserver(self, observer):
        self._selectObservers.remove(observer)

    def updateSelectionObservers(self):
        for selectObserver in self._selectObservers:
            selectObserver.updateSelectLis(self.selection)


    def attachClearSelectObserver(self, observer):
        self._clearSelectObservers.append(observer)

    def detachClearSelectionObserver(self, observer):
        self._clearSelectObservers.remove(observer)

    def updateClearSelectionObservers(self):
        for clearSelectObserver in self._clearSelectObservers:
            clearSelectObserver.clearSelectLis()

    #napravljeno ovako atomarno (korak po korak) kako bi se selection dinamicki azurirao
    def _moveSelect(self, dir: Dir):
        if dir==Dir.left:
            if self.selection.p1.x < 2:
                return False
            else:
                self.selection.p1.x -= 1
                return True
        elif dir==Dir.right:
            self.selection.p2.x += 1
            return True
        elif dir==Dir.up:
            if self.selection.p1.y < 2:
                return False
            else:
                self.selection.p1.y -= 1
                return True
        elif dir==Dir.down:
            self.selection.p2.y += 1
            return True
        self.updateSelectionObservers()

    
    def getSelectionRange(self):
        return self.selection

    def setSelectionRange(self, range: LocationRange):
        self.setSelect(range)
        self.updateSelectionObservers()

    def resetSelectionRange(self):
        self.setSelect(LocationRange())
        self.delSelectFlag = 0
        self.updateClearSelectionObservers()
        


    def setSelect(self, range: LocationRange):
        for coord in range:
            if coord < 1:
                coord=1
        maxY = len(self._lines)
        if range.p2.y > maxY:
            range.p2.y = maxY
        maxX1 = len(self.lines[range.p1.y-1])
        maxX2 = len(self.lines[range.p2.y-1])
        if range.p1.x > maxX1:
            range.p1.x = maxX1
        if range.p2.x > maxX2:
            range.p2.x = maxX2
        self.selection=range
        self.delSelectFlag = 1
        self.updateSelectionObservers()


    def selectionUp(self) -> bool:
        self._moveSelect(Dir.up)
        return True

    def selectionDown(self) -> bool:
        currentPos = self.selection.p2
        if currentPos.y*self._letterHeight > self._canvasHeight-self._letterHeight:
            return False
        else:
            self._moveSelect(Dir.down)
            return True

    def selectionRight(self) -> bool:
        currentPos = self.selection.p2
        if currentPos.x*self._letterWidth > self._canvasWidth-self._letterWidth:
            return False
        else:
            self._moveSelect(Dir.right)
            return True

    def selectionLeft(self) -> bool:
        self._moveSelect(Dir.left)
        return True




    def resetXY(self):
        self.last_x = 0
        self.last_y = 0

    def xy(self, xRaw, yRaw) -> bool:
        if xRaw < 0 or yRaw < 0:
            return False

        x=ceil(xRaw/self._letterWidth)
        y=ceil(yRaw/self._letterHeight)

        self.last_x, self.last_y = x, y
        self.setCursor(x, y)
        self.resetSelectionRange()
        self.updateClearSelectionObservers()
        return True

    def makeSelect(self, current_x, current_y) -> bool:
        if (current_x < 0 or current_y < 0): #or (self.last_x == current_x or self.last_y == current_y):
            self.resetXY()
            return False

        x1 = self.last_x
        y1 = self.last_y

        x2Raw = current_x
        y2Raw = current_y

        x2=ceil(x2Raw/self._letterWidth)
        y2=ceil(y2Raw/self._letterHeight)

        if x1==x2 and y1==y2:
            return False

        if y1<y2:
            self.setSelect(LocationRange(x1, y1, x2, y2))
        elif y1>y2:
            self.setSelect(LocationRange(x2, y2, x1, y1))
        else:
            if x1<x2:
                self.setSelect(LocationRange(x1, y1, x2, y2))
            elif x1>x2:
                self.setSelect(LocationRange(x2, y2, x1, y1))
            else:
                self.resetSelectionRange()
        

#endregion


#region 2.5 delete
    def attachTextObserver(self, observer):
        self._textObservers.append(observer)

    def detachSelectionObserver(self, observer):
        self._textObservers.remove(observer)

    def updateTextObservers(self):
        for textObserver in self._textObservers:
            textObserver.updateTextLis(self.cursor, self.selection)


    @staticmethod
    def trimRange(oldstr, x1, x2):
        #TODO: pazi na of-by-one
        newstr = oldstr[:x1] + oldstr[x2:]
        return newstr
    
    def trimLine(self, lineY, x1, x2):
        oldstr = self.lines[lineY]
        newstr = TextEditorModel.trimRange(oldstr, x1-1, x2-1)
        self.lines[lineY] = newstr

    def removeLine(self, skipCreatingActions=False):
        beforeCursor, afterCursor = self.splitLine()
        self.moveCursorToEndOfPrevLine()
        savedCursorX = len(self.lines[self.cursor.y-1])+1
        del(self.lines[self.cursor.y])
        assert beforeCursor != '' "Ovo se ne bi trebalo pozivati ako cursor nije uz lijevi rub, tj x<2"
        cursorBeforeInsert=copy(self.cursor)
        succ=self.insert(afterCursor, skipCreatingActions=skipCreatingActions)
        self.setCursor(cursorBeforeInsert.x, cursorBeforeInsert.y)
        return succ
        
        


    def deleteBefore(self, skipCreatingActions=False):
        if self.delSelectFlag == 1:
            self.deleteRange(self.selection, skipCreatingActions)
            return

        currentPos = self.cursor
        if currentPos.x < 2:
            skipCreatingActions=False
            if not skipCreatingActions:
                self._undoManager.push(DeleteLineEditAction(self))
                skipCreatingActions=True
            succ=self.removeLine(skipCreatingActions)
        else:
            try:
                oldstr = self.lines[currentPos.y-1]
                newstr = oldstr[:(currentPos.x-2)] + oldstr[currentPos.x-1:]
                self.lines[currentPos.y-1] = newstr
                self.cursorLeft()

                charBeingDeleted=self.getRange(oldstr, currentPos.x-1, currentPos.x)
                if not skipCreatingActions:
                    self._undoManager.push(DeleteEditAction(self, copy(charBeingDeleted)))
            except:
                return False

        self.updateClearSelectionObservers()
        self.updateCursorObservers()
        self.updateTextObservers()
        return True
        

    def deleteAfter(self, skipCreatingActions=False):
        if self.delSelectFlag == 1:
            self.deleteRange(self.selection, skipCreatingActions=skipCreatingActions)
            return
        succ = self.cursorRight()
        if succ:
            return self.deleteBefore(skipCreatingActions=skipCreatingActions)


    
    def deleteAll(self):
        self._lines=list()
        self.setCursor(1,1)

        self.updateClearSelectionObservers()
        self.updateCursorObservers()
        self.updateTextObservers()
        return True





    def trimAndAppendTwoLines(self, firstIndex, rangeParam, skipCreatingActions=False):
        line1Y = firstIndex
        line2Y = firstIndex+1
        x11 = rangeParam.p1.x
        x12 = len(self.lines[line1Y])+1
        x21 = 1
        x22 = rangeParam.p2.x+1
        try:
            #brisemo [x1-end] u prvoj liniji
            self.trimLine(line1Y, x11, x12)

            #brisemo [0-x2] u zadnjoj liniji
            self.trimLine(line2Y, x21, x22)

            self.setCursor(1,line2Y+1)
            self.removeLine(skipCreatingActions=skipCreatingActions)
            return True
        except:
            return False


    def deleteRange(self, rangeParam: LocationRange, skipCreatingActions=False):
        if not skipCreatingActions:
            self._undoManager.push(DeleteRangeEditAction(self))

        affectedLines = range(rangeParam.p1.y-1, rangeParam.p2.y)
        lineCount = len(affectedLines)
        if lineCount==1:
            #unutar jedne linije, brisemo [x1-x2]
            lineY = affectedLines[0]
            x1 = rangeParam.p1.x
            x2 = rangeParam.p2.x+1
            try:
                self.trimLine(lineY, x1, x2)
            except Exception as e:
                return False
        elif lineCount==2:
            #dvije linije, brisemo [x1-end, 0-x2]
            self.trimAndAppendTwoLines(affectedLines[0], rangeParam, skipCreatingActions=skipCreatingActions)
        else:
            #tri ili vise linija
            firstIndex = affectedLines[0]
            linesToDelete = affectedLines[1:-1]
            newLastIndex = affectedLines[:-0]
            for i in linesToDelete:
                #brisemo cijele "srednje" linije
                del(self.lines[firstIndex+1])
            self.trimAndAppendTwoLines(firstIndex, rangeParam, skipCreatingActions=skipCreatingActions)

        self.resetSelectionRange()
        self.updateClearSelectionObservers()
        self.updateCursorObservers()
        self.updateTextObservers()
        self.setCursor(rangeParam.p1.x, rangeParam.p1.y)

#endregion


#region 2.6 text      
    def splitLine(self):
        currentPos = self.cursor
        oldstr = self.lines[currentPos.y-1]
        beforeCursor = oldstr[:currentPos.x-1]
        afterCursor = oldstr[currentPos.x-1:]
        return beforeCursor, afterCursor
    
    def shaveLine(self, line: str, maxLetterNum: int):
        """newstr1 is oldstr trimmed to maxlen, newstr2 is the rest of the oldstr"""
        oldstr = line
        newstr1 = oldstr[:maxLetterNum-1]
        newstr2 = oldstr[maxLetterNum-1:]
        return newstr1, newstr2

    def expandLine(self, lineY, x1, char):
        """inserts passed character char at specified location x1 in specified lineNum lineY"""
        oldstr = self.lines[lineY]
        newstr = oldstr[:x1-1] + char + oldstr[x1-1:]
        return newstr



    def insert(self, char: str, linesFlag=False, skipCreatingActions=False):
        if len(char)>1:
            return self.insertLines(char, skipCreatingActions)
        if self.delSelectFlag == 1:
            self.resetSelectionRange()

        currentPos = self.cursor
        if linesFlag!=True and not skipCreatingActions:
            self._undoManager.push(InsertEditAction(self, copy(char)))
        try:
            maxRowNum = self._maxRowNum
            maxLetterNum = self._maxLetterNum

            newLineFlag = False
            if char == '\r': #ENTER == <Return> == '\r'
                newLineFlag = True
            elif char == '': #special characters don't have an ascii value, ei event.char of <Shift> == ''
                return True
            else:
                newstr = self.expandLine(currentPos.y-1, currentPos.x, char)


            if newLineFlag or len(newstr) > maxLetterNum: #line doesn't fit or enter was pressed
                if len(self.lines) > maxRowNum: #no more space on canvas
                    return False

                if not newLineFlag:
                    oldLineTrimmed, trimmedPart = self.shaveLine(newstr, maxLetterNum) #"abcd", "e"
                else:
                    oldLineTrimmed, trimmedPart = self.splitLine() #"abc", ""

                self.lines[currentPos.y-1] = oldLineTrimmed
                tmp1 = trimmedPart
                for i in range(currentPos.y, len(self.lines)+2): #shift all the remaining lines
                    try:
                        tmp2=self.lines[i]
                        self.lines[i] = tmp1
                        tmp1=tmp2
                    except:
                        self.lines.append(tmp1)
                        break


                self.setCursor(0, currentPos.y+1)

            else:
                self.lines[currentPos.y-1] = newstr
                self.cursorRight()


            self.updateClearSelectionObservers()
            self.updateCursorObservers()
            self.updateTextObservers()
            return True
        except Exception as e:
            return False


    def insertLines(self, string: str, skipCreatingActions=False):
        linesFlag=True
        if not skipCreatingActions:
            self._undoManager.push(InsertLinesEditAction(self, copy(string)))
        for char in string:
            if char.isalnum() or char.isspace():
                succ=self.insert(char, linesFlag, skipCreatingActions=skipCreatingActions)
                if succ:
                    continue
                else:
                    return False
        return True


        
#endregion


#region 2.7 clipboard
    @staticmethod
    def getRange(oldstr, x1, x2):
        #TODO: pazi na of-by-one
        if x1==x2:
            newstr=oldstr[x1]
        else:
            newstr = oldstr[x1:x2]
        return newstr
    
    def getTrimmedLine(self, lineY, x1, x2):
        oldstr = self.lines[lineY]
        newstr = TextEditorModel.getRange(oldstr, x1-1, x2)
        return newstr

    def getFirstAndLastLineTrimmed(self, affectedLines, rangeParam):
        lineY1=affectedLines[0]
        x11=rangeParam.p1.x
        x12=len(self.lines[lineY1])

        lineY2=affectedLines[-1]
        x21=1
        x22=rangeParam.p2.x

        line1 = self.getTrimmedLine(lineY1, x11, x12)
        line2 = self.getTrimmedLine(lineY2, x21, x22)
        return line1, line2



    def getTextInSelection(self) -> str:
        if self.delSelectFlag == 0: #if selection doesnt exist
            return ""

        rangeParam = self.getSelectionRange()
        
        affectedLines = range(rangeParam.p1.y-1, rangeParam.p2.y)
        lineCount = len(affectedLines)
        if lineCount==1:
            #unutar jedne linije, vracamo [x1-x2]
            lineY = affectedLines[0]
            x1 = rangeParam.p1.x
            x2 = rangeParam.p2.x
            
            return self.getTrimmedLine(lineY, x1, x2)

        elif lineCount==2:
            #dvije linije, vracamo [x1-end, 0-x2]
            
            line1, line2 = self.getFirstAndLastLineTrimmed(affectedLines, rangeParam)
            return line1+'\r'+line2
        
        else:
            #tri do n linija, vracamo [x1-end@y1, @y1+1, @y1+2,..., 0-x2@y1+n-1]
            line1, lineN = self.getFirstAndLastLineTrimmed(affectedLines, rangeParam)
            rez = line1
            for lineI in self.linesRange(affectedLines[1], affectedLines[-1]): #-2, ali range radi [a,b>
                rez += '\r'+lineI[0]
            rez += '\r'+lineN
            return rez

        #self.updateCursorObservers()
#endregion


#region 2.8 undo/redo, tj. EditAction inline klase
    #ovo su mogle biti i anonimne kalse, ali mislim da bi to znatno umanjilo citljivost koda

    #note: u svijetu sa danom duljim od 24h, ovo bi bio posao tvornice. Ali, klasa je dovoljno
    #malo da je ova veza prihvatljiva

    #update: "TextEditorModel not defined" je bio jer sam tabulirao insertEditAction, a inline klase
    #ne funkcioniraju tako

    #TODO: ova metoda sa skipCreatingActions prevencije stvaranja novih EditActiona je losa. Bolje
    #rjesenje bilo bi mutex, u ulasku u undo/redo staviti global skipCreatingActions i prije izlaska
    #iz undo/redo ga maknuti

class InsertEditAction(EditAction):
    def __init__(self, model: TextEditorModel, charBeingInserted: str):
        self._charBeingInserted = charBeingInserted
        self._model = model
        self._orgCursorLocation = self._model.cursor

    def execute_do(self):
        charBeingReInserted = self._charBeingInserted
        #self._model.setCursor(self._orgCursorLocation)
        self._model.insert(charBeingReInserted, skipCreatingActions=True)

    def execute_undo(self):
        #self._model.setCursor(self._orgCursorLocation)
        self._model.deleteBefore(skipCreatingActions=True)

class InsertLinesEditAction(EditAction):
    def __init__(self, model: TextEditorModel, charsBeingInserted: str):
        self._charsBeingInserted = charsBeingInserted
        self._model = model
        self._orgCursorLocation = self._model.cursor

    def execute_do(self):
        charBeingReInserted = self._charsBeingInserted
        #self._model.setCursor(self._orgCursorLocation)
        for charBeingReInserted in charBeingReInserted:
            self._model.insert(charBeingReInserted, skipCreatingActions=True)

    def execute_undo(self):
        #self._model.setCursor(self._orgCursorLocation)
        for char in self._charsBeingInserted:
            self._model.deleteBefore()

class DeleteEditAction(EditAction):
    def __init__(self, model: TextEditorModel, charBeingDeleted: str):
        self._charBeingDeleted = charBeingDeleted
        self._model = model
        self._orgCursorLocation = self._model.cursor

    def execute_do(self):
        #self._model.setCursor(self._orgCursorLocation)
        self._model.deleteBefore(skipCreatingActions=True)

    def execute_undo(self):
        charBeingUnDeleted = self._charBeingDeleted
        #self._model.setCursor(self._orgCursorLocation)
        self._model.insert(charBeingUnDeleted, skipCreatingActions=True)

class DeleteLineEditAction(EditAction):
    def __init__(self, model: TextEditorModel):
        self._model = model
        self._orgCursorLocation = self._model.cursor
        _, self._lineRemainder = self._model.splitLine()

    def execute_do(self):
        #self._model.setCursor(self._orgCursorLocation)
        self._model.removeLine(skipCreatingActions=True)

    def execute_undo(self):
        charsBeingUnDeleted = '\r'+self._lineRemainder
        #self._model.setCursor(self._orgCursorLocation)
        for char in self._lineRemainder:
            self._model.deleteAfter(skipCreatingActions=True)
        self._model.insert(charsBeingUnDeleted, skipCreatingActions=True)
        self._model.cursorHome()

class DeleteRangeEditAction(EditAction):
    def __init__(self, model: TextEditorModel):
        self._model = model
        self._orgCursorLocation = self._model.cursor
        self._orgSelection = self._model.selection
        self._charsBeingDeleted = self._model.getTextInSelection()

    def execute_do(self):
        self._model.setSelect(self._orgSelection) #takodjer postavi model.deleteRange=1
        self._model.deleteBefore(skipCreatingActions=True) #deleteBefore samo pozove deleteRange jer je model.deleteRange==1

    def execute_undo(self):
        charsBeingUnDeleted = self._charsBeingDeleted
        #self._model.setCursor(self._orgCursorLocation)
        self._model.insert(charsBeingUnDeleted, skipCreatingActions=True)
        
#endregion