from Location import Location

class LocationRange:
    def __init__(self, x1: int=1, y1: int=1, x2: int=1, y2: int=1):
        self._p1 = Location(x1, y1)
        self._p2 = Location(x2, y2)
    
    def _get_p1(self):
        return self._p1
    def _set_p1(self, p1: Location):
        self._p1 = p1
    p1 = property(_get_p1, _set_p1)

    def _get_p2(self):
        return self._p2
    def _set_p2(self, p2: Location):
        self._p2 = p2
    p2 = property(_get_p2, _set_p2)

    def __iter__(self):
        return iter([self.p1.x, self.p1.y, self.p2.x, self.p2.y])

    #r1 = LocationRange(1, 2, 3, 4)
    #x1, y2 = r1.p1.x, r1.p2.y

    def isDefault(self):
        return True if self.p1==self.p2 else False