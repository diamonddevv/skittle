import skittle
import json
import os

class _I18n():
    I18NS: dict[str, dict[str, str]] = {}
    CURRENT_LANG_KEY: str = ''
    FALLBACK_LANG_KEY: str = ''

def load_i18ns(lang_path: str, lang: str, fallback: str | None = None):
    for file in os.listdir(lang_path):
        key = file.removesuffix('.json')
        with open(os.path.join(lang_path, file), 'rb') as f:
            _I18n.I18NS[key] = json.load(f)

    skittle.log(f"loaded {len(_I18n.I18NS)} languages.")

    set_lang_key(lang, fallback if fallback != None else lang)


def set_lang_key(key: str | None = None, fallback: str | None = None):

    logstr_fallback = ""
    if fallback != None:
        _I18n.FALLBACK_LANG_KEY = fallback
        if _I18n.FALLBACK_LANG_KEY != "":
            logstr_fallback = f"fallback language to {endonym(fallback)} ({exonym(fallback)})"
        else:
            logstr_fallback = f"no fallback language"

    if key == None:
        key = _I18n.FALLBACK_LANG_KEY

    _I18n.CURRENT_LANG_KEY = key

    logstr_main = ""
    if _I18n.CURRENT_LANG_KEY != "":
        logstr_main = f"language to {endonym(key)} ({exonym(key)})"
    else:
        logstr_main = f"no language"

    skittle.log("set " + logstr_main + ("" if fallback == None else ", " + logstr_fallback))
    

def tr(key: str, *args) -> str:
    if not _I18n.FALLBACK_LANG_KEY in _I18n.I18NS:
        return key
    lang = _I18n.I18NS.get(_I18n.CURRENT_LANG_KEY, _I18n.I18NS.get(_I18n.FALLBACK_LANG_KEY, None))
    if lang != None:
        return lang.get(key, _I18n.I18NS[_I18n.FALLBACK_LANG_KEY].get(key, key)).format(*args)
    else:
        return key

def endonym(key: str):
    """
    `lang.endonym`; The name a language is called in that language. (Français, Deutsch, Español, Suomi, etc.)
    """

    lang = _I18n.I18NS.get(key, None)
    if lang != None:
        return lang.get("lang.endonym", key)
    else:
        return key
    

def exonym(key: str):
    """
    `lang.exonym`; The name a language is called in English. (French, German, Spanish, Finnish, etc.)
    """

    lang = _I18n.I18NS.get(key, None)
    if lang != None:
        return lang.get("lang.exonym", key)
    else:
        return key