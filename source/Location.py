class Location:
    def __init__(self, x: int =1, y: int=1):
        self._x = x
        self._y = y
    
    def _get_x(self):
        return self._x
    def _set_x(self, x: int):
        self._x = x
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self._y
    def _set_y(self, y: int):
        self._y = y
    y = property(_get_y, _set_y)

    #p1 = Location(1, 2)
    #x1, y1 = p1.x, p2.y

    def __eq__(self, obj):
        if isinstance(obj, Location):
            if self.x == obj.x and self.y == obj.y:
                return True
        return False