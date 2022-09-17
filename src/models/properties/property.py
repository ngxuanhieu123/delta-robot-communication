from .i_property import ISetValuableProperty
from ...views import IObserver
from ..i_model import Model


class Property(Model, ISetValuableProperty):
    BYTEORDER = 'big'

    def __init__(self, num_bytes=2, reverse=False):
        Model.__init__(self)
        self._value = 0
        self._num_bytes = num_bytes
        self._observers = []
        self._reverse = reverse
    
    def to_hex(self) -> bytearray:
        hex_value = None

        if self._value >= 0:
            hex_value = self._value.to_bytes(self._num_bytes, byteorder=self.BYTEORDER)
        else:
            hex_value = (2 ** (self._num_bytes * 8) + self._value).to_bytes(self._num_bytes, byteorder=self.BYTEORDER)

        if self._reverse:
            return hex_value[::-1]
        else:
            return hex_value

    def set_value(self, new_value:object) -> None:
        self._value = new_value

        for observer in self._observers:
            observer.model_is_changed(self)

    def get_value(self) -> object:
        return self._value

    @property
    def changable(self):
        return True

    def add_observer(self, observer:IObserver) -> None:
        self._observers.append(observer)

    def remove_observer(self, observer:IObserver) -> None:
        self._observers.remove(observer)

    def is_reverse(self) -> bool:
        return self._reverse
