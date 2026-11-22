"""Locale detection and per-application language preferences for Zelix tools."""
import json
import os
from pathlib import Path
import tempfile

LANGUAGE_NAMES = {'en': 'English', 'tr': 'Türkçe', 'es': 'Español'}


def detect_language(environment=None):
    environment = os.environ if environment is None else environment
    for key in ('LC_ALL', 'LC_MESSAGES', 'LANG'):
        value = environment.get(key, '').strip().lower()
        if value:
            return next((code for code in LANGUAGE_NAMES if value.startswith(code)), 'en')
    return 'en'


class LanguagePreference:
    def __init__(self, application):
        base = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config')
        self.path = base/'zelix'/(application+'-language.json')
        try:
            saved = json.loads(self.path.read_text())
            code = saved.get('language') if isinstance(saved, dict) else None
        except (OSError, ValueError):
            code = None
        self.language = code if isinstance(code, str) and code in LANGUAGE_NAMES else detect_language()

    def set_language(self, code):
        if code not in LANGUAGE_NAMES:
            raise ValueError('Unsupported language: ' + str(code))
        self.language = code
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                             prefix=self.path.name+'.', delete=False) as stream:
                temporary = Path(stream.name)
                json.dump({'language': code}, stream)
                stream.write('\n')
            temporary.replace(self.path)
            return True
        except OSError:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            return False


def apply_qt_language(code):
    """Translate standard Qt controls when the matching qtbase catalog is installed."""
    from PyQt6.QtCore import QCoreApplication, QLibraryInfo, QTranslator
    application = QCoreApplication.instance()
    if application is None:
        return False
    previous = getattr(application, '_zelix_qt_translator', None)
    if previous is not None:
        application.removeTranslator(previous)
        previous.deleteLater()
        application._zelix_qt_translator = None
    if code == 'en':
        return True
    translator = QTranslator(application)
    directory = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if translator.load('qtbase_' + code, directory):
        application.installTranslator(translator)
        application._zelix_qt_translator = translator
        return True
    translator.deleteLater()
    return False
