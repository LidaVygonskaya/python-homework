from abc import ABC, abstractmethod


class TextHistory:
    def __init__(self, text='', version=0):
        self._text = text
        self._version = version
        self._actions = []

    def __len__(self):
        return len(self._text)

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def action(self, action):
        self._actions.append(action)
        self._text = action(self.text)
        self._version = action.to_version
        return action.to_version

    def insert(self, text_to_insert, pos=None):
        return self.action(InsertAction(text_to_insert, self.version, self.version + 1, pos))

    def replace(self, text_replace, pos=None):
        return self.action(ReplaceAction(text_replace, self.version, self.version + 1, pos))

    def delete(self, pos, length):
        return self.action(DeleteAction(pos, length, self.version, self.version + 1))

    def get_actions(self, from_version=0, to_version=None):
        if to_version is None:
            to_version = self.version

        if from_version < 0 or to_version > self.version or to_version < from_version:
            raise ValueError('Error: could not get such actions.')

        return [action for action in self._actions if from_version < action.to_version <= to_version]


class Action(ABC):
    """
    Класс от которого наследуются все действия.
    """
    def __init__(self, from_version: int, to_version: int):
        """
        :param from_version: Значение версии 1
        :param to_version: Значение версии 2
        """
        self._validate_versions(from_version, to_version)
        self._from_version = from_version
        self._to_version = to_version

    @property
    def from_version(self):
        return self._from_version

    @property
    def to_version(self):
        return self._to_version

    def __call__(self, text_to_change):
        return self.apply(text_to_change)

    @staticmethod
    def _validate_versions(v1, v2):
        if v1 >= v2:
            raise ValueError(f'Error: v2={v2} < v1={v1}')

    @staticmethod
    def _validate_pos(text_to_change_len: int, pos: int):
        if (pos < 0 or pos >= text_to_change_len) or (pos != 0 and text_to_change_len == 0):
            raise ValueError('Error: position is out of range.')

    @abstractmethod
    def apply(self, text: str):
        """
        Принимает на вход строку и возвращает модифицированную.
        :param text: Строка
        :return:
        """
        pass


class InsertAction(Action):
    def __init__(self, text: str, from_version: int, to_version: int, pos: int=None):
        super().__init__(from_version, to_version)
        self.text = text
        self.pos = pos

    def apply(self, text_to_change: str) -> str:
        if self.pos is not None and len(text_to_change):
            self._validate_pos(len(text_to_change), self.pos)
            text_to_change = text_to_change[:self.pos] + self.text + text_to_change[self.pos:]
        else:
            self.pos = len(text_to_change)
            text_to_change += self.text
        return text_to_change


class ReplaceAction(Action):
    def __init__(self, text, from_version: int, to_version: int, pos: int=None):
        super().__init__(from_version, to_version)
        self.text = text
        self.pos = pos

    def apply(self, text_to_change: str) -> str:
        if self.pos is not None:
            self._validate_pos(len(text_to_change), self.pos)
            if self.pos + len(self.text) >= len(text_to_change):
                text_to_change = text_to_change[:self.pos] + self.text
            else:
                text_to_change = text_to_change[:self.pos] + self.text + text_to_change[self.pos + len(self.text):]
        else:
            text_to_change += self.text
        return text_to_change


class DeleteAction(Action):
    def __init__(self, pos: int, length: int, from_version: int, to_version: int):
        super().__init__(from_version, to_version)
        self.pos = pos
        self.length = length

    def apply(self, text_to_change: str) -> str:
        self._validate_pos(len(text_to_change), self.pos)
        if self.pos + self.length > len(text_to_change):
            raise ValueError('Error: sequence to delete is too long')
        else:
            text_to_change = text_to_change[:self.pos] + text_to_change[self.pos + self.length:]
        return text_to_change
