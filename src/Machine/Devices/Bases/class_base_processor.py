from abc import ABC

from Machine.Devices.Bases.class_base_device import BaseDevice


class BaseProcessor(BaseDevice, ABC):
    """
    The BaseProcessor class is an abstract base class for all processors in the system.
    It inherits from the BaseDevice class and provides a common interface
    for all processors, including a method to cycle the processor.
    """
