"""Input backend abstraction — pluggable keyboard/mouse simulation drivers."""
from __future__ import annotations
import abc
from typing import Optional


class InputBackend(abc.ABC):
    """Abstract base class for all input simulation backends."""

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """Short identifier used in config, e.g. 'pynput'."""

    @classmethod
    @abc.abstractmethod
    def display_name(cls) -> str:
        """Human-readable name shown in the UI."""

    @classmethod
    @abc.abstractmethod
    def is_available(cls) -> bool:
        """Return True if this backend can actually be used on the current system."""

    @classmethod
    def unavailable_reason(cls) -> str:
        """Human-readable explanation when is_available() is False."""
        return '该驱动不可用'

    # ------------------------------------------------------------------ mouse
    @abc.abstractmethod
    def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to absolute screen coordinates (x, y)."""

    @abc.abstractmethod
    def mouse_click(self, x: int, y: int, button: str = 'left', count: int = 1) -> None:
        """Move to (x, y) then click. button: 'left' | 'right' | 'middle'."""

    @abc.abstractmethod
    def mouse_scroll(self, dx: int, dy: int) -> None:
        """Scroll the mouse wheel. dy>0 = scroll up."""

    # ----------------------------------------------------------------- keyboard
    @abc.abstractmethod
    def key_press(self, key: str) -> None:
        """Press (hold) a key. key is a canonical name like 'a', 'ctrl', 'f1'."""

    @abc.abstractmethod
    def key_release(self, key: str) -> None:
        """Release a key."""

    def key_tap(self, key: str) -> None:
        """Press and immediately release a key (default implementation)."""
        self.key_press(key)
        self.key_release(key)

    def combo(self, keys: list[str]) -> None:
        """Press modifiers + final key, then release all.
        e.g. combo(['ctrl', 'c'])
        """
        for k in keys[:-1]:
            self.key_press(k)
        self.key_tap(keys[-1])
        for k in reversed(keys[:-1]):
            self.key_release(k)


# ─────────────────────────────────────────── Global singleton registry

_BACKENDS: dict[str, type[InputBackend]] = {}
_active: Optional[InputBackend] = None
_active_name: str = 'pynput'


def register_backend(cls: type[InputBackend]) -> type[InputBackend]:
    """Decorator to register a backend class."""
    _BACKENDS[cls.name()] = cls
    return cls


def get_available_backends() -> list[type[InputBackend]]:
    """Return all registered backend classes."""
    return list(_BACKENDS.values())


def set_backend(name: str, **kwargs) -> None:
    """Activate a backend by name. Raises ValueError if not registered."""
    global _active, _active_name
    if name not in _BACKENDS:
        raise ValueError(f'Unknown backend: {name}')
    _active = _BACKENDS[name](**kwargs)
    _active_name = name


def get_backend() -> InputBackend:
    """Return the currently active backend, initialising pynput as default."""
    global _active
    if _active is None:
        # Lazy-initialise with pynput
        _ensure_defaults_registered()
        set_backend('pynput')
    return _active


def get_active_name() -> str:
    return _active_name


def _ensure_defaults_registered() -> None:
    """Import backends to trigger their @register_backend decorators."""
    if not _BACKENDS:
        from core.backends import pynput_backend, dd_backend, interception_backend  # noqa: F401
