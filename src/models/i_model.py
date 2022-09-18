from abc import ABC, abstractmethod
from ..views import IObserver


class IModel(ABC):
    @abstractmethod
    def add_observer(self, observer:IObserver) -> None:
        pass

    @abstractmethod
    def remove_observer(self, observer:IObserver) -> None:
        pass 

    @abstractmethod
    def model_is_changed(self) -> None:
        pass


class Model(IModel):
    def __init__(self):
        self._observers = []

    def add_observer(self, observer:IObserver) -> None:
        self._observers.append(observer)
        self.model_is_changed()

    def remove_observer(self, observer:IObserver) -> None:
        self._observers.remove(observer)

    def model_is_changed(self) -> None:
        for observer in self._observers:
            observer.model_is_changed(self)
