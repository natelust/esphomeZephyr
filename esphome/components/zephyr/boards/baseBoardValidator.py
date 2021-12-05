from abc import ABC, abstractclassmethod


class BaseZephyrBoard(ABC):
    @abstractclassmethod
    def validate_gpio_pin(cls, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def validate_supports(cls, value):
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def get_device_and_pin(cls, pin):
        raise NotImplementedError("Not implemented on the base class")

    @abstractclassmethod
    def can_openthread(cls) -> bool:
        raise NotImplementedError("Not implemented on the base class")
