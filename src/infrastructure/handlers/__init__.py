import importlib
import os
from types import ModuleType
from typing import Iterator

from src.infrastructure.handlers.handlers import UserHandler, SubscriptionHandler
from src.infrastructure.handlers.models import (
    UserCredentials,
    UserIdentity,
    SubscriptionActivationData,
    SubscriptionCancelData,
)


class Handlers:
    handlers_base_path = ("src", "infrastructure", "handlers")
    ignored = ("__init__.py", "models.py", "handlers.py", "__pycache__")

    @classmethod
    def __all_module_names(cls) -> list[str]:
        base_path = os.path.join(*cls.handlers_base_path)
        return [module for module in os.listdir(base_path) if module not in cls.ignored]

    @classmethod
    def __module_namespace(cls, handler_name: str) -> str:
        return f"{'.'.join(cls.handlers_base_path)}.{handler_name}"

    @classmethod
    def iterator(cls) -> Iterator[ModuleType]:
        for module in cls.__all_module_names():
            yield importlib.import_module(cls.__module_namespace(module[:-3]))

    @classmethod
    def module(cls):
        return map(lambda module: cls.__module_namespace(module[:-3]), cls.__all_module_names())


__all__ = [
    "UserHandler",
    "SubscriptionHandler",
    "UserCredentials",
    "UserIdentity",
    "SubscriptionActivationData",
    "SubscriptionCancelData",
    "Handlers",
]
