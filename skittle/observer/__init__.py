import typing

class Signal():
    type _Callback = typing.Callable[..., typing.Any]

    def __init__(self) -> None:
        self._callbacks: list[Signal._Callback] = []

    def emit(self, *args: ...):
        for c in self._callbacks:
            c(*args)

    def bind(self, callback: _Callback) -> int:
        i = len(self._callbacks)
        self._callbacks.append(callback)
        return i
    
    def unbind(self, idx: int):
        """you probably shouldnt do this. does not free memory, simply replaces the callback with a no op function"""
        self._callbacks[idx] = lambda: None