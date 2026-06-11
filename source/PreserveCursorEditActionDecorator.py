from EditAction import EditAction
from copy import copy

class PreserveCursorEditActionDecorator(EditAction):
    def __init__(self, orgAction: EditAction):
        self._orgAction = orgAction

    def execute_do(self):
        currentCursorLocation = copy(self._orgAction._model.cursor)

        self._orgAction.execute_do()

        self._orgAction._model.setCursor(currentCursorLocation.x, currentCursorLocation.y)

    def execute_undo(self):
        currentCursorLocation = copy(self._orgAction._model.cursor)

        self._orgAction.execute_undo()

        self._orgAction._model.setCursor(currentCursorLocation.x, currentCursorLocation.y)


"""
usage:

orgAction = EditAction(model, char)
orgActionSaveCursor = PreserveCursorEditActionDecorator(orgAction)
"""