from ClipboardObserver import ClipboardObserver
ClipboardObservers = list[ClipboardObserver]

class ClipboardStack:
    def __init__(self):
        self.items = []
        self._clipboardObservers = ClipboardObservers()

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        if item != '':
            self.items.append(item)
        else:
            self.clear()
        self.updateClipboardObservers()

    def pop(self):
        if not self.isEmpty():
            self.items.pop()
        else:
            pass
            #raise IndexError 
        self.updateClipboardObservers()

    def peek(self):
        if not self.isEmpty():
            self.updateClipboardObservers()
            return self.items[len(self.items)-1]
        else:
            return None
        

    def size(self):
        return len(self.items)

    def clear(self):
        self.items = []
        self.updateClipboardObservers()


    def attachClipboardObserver(self, observer):
        self._clipboardObservers.append(observer)

    def detachClipboardObserver(self, observer):
        self._clipboardObservers.remove(observer)

    def updateClipboardObservers(self):
        for cursorObserver in self._clipboardObservers:
            cursorObserver.updateClipboardLis(self.isEmpty())

