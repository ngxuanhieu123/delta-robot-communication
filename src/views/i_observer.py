from abc import ABC, abstractmethod


class IObserver(ABC):
    @abstractmethod
    def model_is_changed(self) -> None:
        pass
