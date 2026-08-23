import pygame
import skittle


class _MusicStream():
    def __init__(self, path: str, filetype: str) -> None:
        self._stream_data = open(path, 'rb')
        self._filetype = filetype
        self._sound = pygame.Sound(path)

    def length(self):
        return self._sound.get_length() * 1000

    def release(self):
        self._stream_data.close()


class AudioManager():
    INSTANCE: AudioManager

    def __init__(self) -> None:
        self._current_music_pos_ms: float = 0
        self._music_playing: bool = False

        self.sounds: dict[str, pygame.Sound] = {}
        self.music: dict[str, _MusicStream] = {}

    def update(self, dt: float):
        if self._music_playing:
            self._current_music_pos_ms += dt * 1000

    def release(self):
        for uid in self.music:
            self.music[uid].release()



def load_sound(uid: str, path: str):
    if uid in AudioManager.INSTANCE.sounds:
        skittle.err(f"uid '{uid}' already exists in sound cache!")
    else:
        sfx = pygame.Sound(path)
        AudioManager.INSTANCE.sounds[uid] = sfx

def play_sound(uid: str, volume: float = 0.5):
    if not _assert_sound_exists(uid):
        return
    channel = pygame.mixer.find_channel()
    if channel != None:
        sound = AudioManager.INSTANCE.sounds[uid]
        channel.set_volume(volume)
        channel.play(sound)

def get_sound_length_ms(uid: str) -> float:
    if not _assert_sound_exists(uid):
        return -1
    return AudioManager.INSTANCE.sounds[uid].get_length()


def load_music(uid: str, path: str, filetype: str):
    if uid in AudioManager.INSTANCE.music:
        skittle.err(f"uid '{uid}' already exists in music cache!")
    else:
        music = _MusicStream(path, filetype)
        AudioManager.INSTANCE.music[uid] = music

def play_music(uid: str, fadein_ms: int, volume: float = 0.5):
    if not _assert_music_exists(uid):
        return

    music = AudioManager.INSTANCE.music[uid]

    pygame.mixer_music.unload()
    pygame.mixer_music.load(music._stream_data, music._filetype)
    pygame.mixer_music.set_volume(volume)
    pygame.mixer_music.play(fade_ms=fadein_ms)
    AudioManager.INSTANCE._music_playing = True

def set_music_volume(vol: float = 0.5):
    pygame.mixer_music.set_volume(vol)

def get_music_volume() -> float:
    return pygame.mixer_music.get_volume()

def seek_music_ms(pos: float):
    restart_music()
    AudioManager.INSTANCE._current_music_pos_ms = pos
    pygame.mixer_music.set_pos(pos/1000)

def get_music_pos() -> float:
    return AudioManager.INSTANCE._current_music_pos_ms

def fadeout_music(ms: int = 100):
    pygame.mixer_music.fadeout(ms)

def pause_music():
    AudioManager.INSTANCE._music_playing = False
    pygame.mixer_music.pause()

def resume_music():
    AudioManager.INSTANCE._music_playing = True
    pygame.mixer_music.unpause()

def restart_music():
    AudioManager.INSTANCE._current_music_pos_ms = 0
    pygame.mixer_music.rewind()

def get_music_length_ms(uid: str) -> float:
    if not _assert_music_exists(uid):
        return -1
    return AudioManager.INSTANCE.music[uid].length()



def _assert_music_exists(uid: str) -> bool:
    if not uid in AudioManager.INSTANCE.music:
        skittle.err(f"music with uid '{uid}' does not exist in music cache!")
        return False
    return True

def _assert_sound_exists(uid: str) -> bool:
    if not uid in AudioManager.INSTANCE.sounds:
        skittle.err(f"sound with uid '{uid}' does not exist in sound cache!")
        return False
    return True 