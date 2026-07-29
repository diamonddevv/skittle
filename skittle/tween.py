from __future__ import annotations
import skittle
import typing
import time
import math

type _Tweener = typing.Callable[[float], float] # f(t) = x

class _Tween():
    TWEENER_DONT: _Tweener = lambda t: 0
    TWEENER_EASE_LINEAR: _Tweener = lambda t: t
    TWEENER_EASE_IN_EXP: _Tweener = lambda t: 0 if t == 0 else math.pow(2, 10 * t - 10)
    TWEENER_EASE_OUT_EXP: _Tweener = lambda t: 1 if t == 1 else 1 - math.pow(2, -10 * t)

    NEXT_TWEEN_ID: int = 0
    TWEENS: dict[int, _Tween] = {}

    def __init__(self, idx: int, initial: float, target: float, object: object, attribute: str, duration: float, tweener: _Tweener, delay: float = 0.0, depends: int = -1) -> None:
        
        self.idx = idx
        self.initial = initial
        self.target = target 
        self.object = object
        self.attribute = attribute
        self.duration = duration
        self.tweener = tweener
        self.delay = delay
        self.depends = depends

        self.started = False
        self.starttime = 0.0

    def update(self, dt: float):
        
        if self.dependent_done():
            self.start_if_needed()

            t = self.tweener((time.time() - self.starttime - self.delay) / self.duration)
            value = skittle.math.lerpf(self.initial, self.target, t)
            self.set_value(value)

            if (time.time() - self.starttime - self.delay) >= self.duration:
                self.set_value(value)
                self.delete_self()

    def dependent_done(self) -> bool:
        return not self.depends in _Tween.TWEENS
    
    def start_if_needed(self):
        if not self.started:
            self.started = True
            self.starttime = time.time()
    
    def delete_self(self):
        del _Tween.TWEENS[self.idx]

    def set_value(self, value: float):
        if self.object != None:
            if self.attribute in dir(self.object):
                self.object.__setattr__(self.attribute, value)
            else:
                skittle.err(f"no attribute '{self.attribute}' in tweened object {self.object}")

class _ConstantTween(_Tween):
    def __init__(self, idx: int, initial: float, object: object, attribute: str, speed: float, duration: float, delay: float = 0.0, depends: int = -1) -> None:
        super().__init__(idx, initial, -1, object, attribute, duration, _Tween.TWEENER_DONT, delay, depends)
        self.speed = speed
        self.val = initial

    def update(self, dt: float):

        if self.dependent_done():
            self.start_if_needed()

            self.val += self.speed * dt
            self.set_value(self.val)

            if (time.time() - self.starttime) >= self.duration:
                self.delete_self()

class _SleepTween(_Tween):
    def __init__(self, idx: int, duration: float, depends: int = -1) -> None:
        super().__init__(idx, -1, 0, None, "", duration, _Tween.TWEENER_DONT, 0.0, depends)

    def update(self, dt: float):

        if self.dependent_done():
            self.start_if_needed()

            if (time.time() - self.starttime) >= self.duration:
                self.delete_self()

class _FunctionCallTween(_Tween):
    def __init__(self, idx: int, function: typing.Callable[[], typing.Any], depends: int = -1) -> None:
        super().__init__(idx, -1, 0, None, "", 0, _Tween.TWEENER_DONT, 0.0, depends)
        self.func = function

    def update(self, dt: float):
        if self.dependent_done():
            self.func()
            self.delete_self()

def _create_tween(tweenfunc: typing.Callable[[int], _Tween]) -> int:
    idx = _Tween.NEXT_TWEEN_ID
    _Tween.NEXT_TWEEN_ID += 1
    _Tween.TWEENS[idx] = tweenfunc(idx)
    return idx

def tween(initial_value: float, object: object, attribute: str, duration: float, target: float, tweener: _Tweener, delay: float = 0.0, depends: int = -1) -> int:
    return _create_tween(lambda idx: _Tween(idx, initial_value, target, object, attribute, duration, tweener, delay, depends))

def tween_continuous(initial_value: float, object: object, attribute: str, duration: float, speed: float, delay: float = 0.0, depends: int = -1) -> int:
    return _create_tween(lambda idx: _ConstantTween(idx, initial_value, object, attribute, speed, duration, delay, depends))

def tween_wait(duration: float, depends: int = -1) -> int:
    return _create_tween(lambda idx: _SleepTween(idx, duration, depends))

def tween_call_func(function: typing.Callable[[], typing.Any], depends: int = -1) -> int:
    return _create_tween(lambda idx: _FunctionCallTween(idx, function, depends))

def chain_tweens(tweens: list[typing.Callable[[int], int]]) -> list[int]:
    """
    takes a list of functions that create tweens and return their indexes. 
    supplies the index of the previous element (or `-1` for the first element) to be used as the dependency index.
    returns a list of each index in order.
    """
    idx = -1
    indices = []
    for createtween in tweens:
        idx = createtween(idx)
        indices.append(idx)
    return indices

def cancel_tween(idx: int):
    if idx in _Tween.TWEENS:
        del _Tween.TWEENS[idx]

def update_tweens(dt: float):
    for idx in _Tween.TWEENS.copy():
        _Tween.TWEENS[idx].update(dt)