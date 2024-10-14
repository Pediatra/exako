from enum import Enum
from typing import Dict

class Level(str, Enum):
    BEGINNER = 'A1', 'Beginner'
    ELEMENTARY = 'A2', 'Elementary'
    INTERMEDIATE = 'B1', 'Intermediate'
    UPPER_INTERMEDIATE = 'B2', 'Upper Intermediate'
    ADVANCED = 'C1', 'Advanced'
    MASTER = 'C2', 'Master'

    def __new__(cls, value, label):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self):
        return self._value_

class PartOfSpeech(int, Enum):
    ADJECTIVE = 0, 'Adjective'
    NOUN = 1, 'Noun'
    VERB = 2, 'Verb'
    ADVERB = 3, 'Adverb'
    CONJUNCTION = 4, 'Conjunction'
    PREPOSITION = 5, 'Preposition'
    PRONOUN = 6, 'Pronoun'
    DETERMINER = 7, 'Determiner'
    NUMBER = 8, 'Number'
    PREDETERMINER = 9, 'Predeterminer'
    PREFIX = 10, 'Prefix'
    SUFFIX = 11, 'Suffix'
    SLANG = 12, 'Slang'
    PHRASAL_VERB = 13, 'Phrasal verb'
    LEXICAL = 14, 'Lexical'

    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self):
        return str(self._value_)

class Language(str, Enum):
    PORTUGUESE_BRASILIAN = 'pt-BR', 'Portuguese Brazil'
    ENGLISH_USA = 'en-US', 'English USA'
    DEUTSCH = 'de', 'Deutsch'
    FRENCH = 'fr', 'French'
    SPANISH = 'es', 'Spanish'
    ITALIAN = 'it', 'Italian'
    CHINESE = 'zh', 'Chinese'
    JAPANESE = 'ja', 'Japanese'
    RUSSIAN = 'ru', 'Russian'

    def __new__(cls, value, label):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self):
        return self._value_

class TermLexicalType(int, Enum):
    SYNONYM = 0, 'Synonym'
    ANTONYM = 1, 'Antonym'
    INFLECTION = 2, 'Inflection'
    IDIOM = 3, 'Idiom'
    RHYME = 4, 'Rhyme'

    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self):
        return str(self._value_)

language_emoji_map: Dict[Language, str] = {
    Language.PORTUGUESE_BRASILIAN: '🇧🇷',
    Language.ENGLISH_USA: '🇺🇸',
    Language.DEUTSCH: '🇩🇪',
    Language.FRENCH: '🇫🇷',
    Language.SPANISH: '🇪🇸',
    Language.ITALIAN: '🇮🇹',
    Language.CHINESE: '🇨🇳',
    Language.JAPANESE: '🇯🇵',
    Language.RUSSIAN: '🇷🇺',
}

language_alphabet_map: Dict[Language, str] = {
    Language.PORTUGUESE_BRASILIAN: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.ENGLISH_USA: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.DEUTSCH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß',
    Language.FRENCH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ',
    Language.SPANISH: 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ',
    Language.ITALIAN: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.CHINESE: '阿贝色德饿佛日哈伊鸡卡勒马娜哦佩苦耳斯特乌维独埃克斯伊格黑克',
    Language.JAPANESE: 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
    Language.RUSSIAN: 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
}