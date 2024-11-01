from enum import Enum, auto


class Level(Enum):
    BEGINNER = 'A1'
    ELEMENTARY = 'A2'
    INTERMEDIATE = 'B1'
    UPPER_INTERMEDIATE = 'B2'
    ADVANCED = 'C1'
    MASTER = 'C2'


class PartOfSpeech(Enum):
    ADJECTIVE = auto()
    NOUN = auto()
    VERB = auto()
    ADVERB = auto()
    CONJUNCTION = auto()
    PREPOSITION = auto()
    PRONOUN = auto()
    DETERMINER = auto()
    NUMBER = auto()
    PREDETERMINER = auto()
    PREFIX = auto()
    SUFFIX = auto()
    SLANG = auto()
    PHRASAL_VERB = auto()
    PLURAL = auto()
    CONJUGATION = auto()
    SUPERLATIVE = auto()
    COMPARATIVE = auto()
    CONTRACTION = auto()
    ARTICLE = auto()
    INTERJECTION = auto()
    PARTICLE = auto()
    AUXILIARY_VERB = auto()
    PROPER_NOUN = auto()
    GERUND = auto()
    INFINITIVE = auto()
    MODAL_VERB = auto()
    ONOMATOPOEIA = auto()
    CLASSIFIER = auto()
    CARDINAL_NUMBER = auto()
    ORDINAL_NUMBER = auto()


class Language(Enum):
    ARABIC = 'ar'
    CHINESE_SIMPLIFIED = 'zh-CN'
    CHINESE_TRADITIONAL = 'zh-TW'
    ENGLISH_USA = 'en-US'
    ENGLISH_UK = 'en-GB'
    FRENCH = 'fr'
    GERMAN = 'de'
    ITALIAN = 'it'
    JAPANESE = 'ja'
    KOREAN = 'ko'
    POLISH = 'pl'
    PORTUGUESE_BRAZIL = 'pt-BR'
    PORTUGUESE_PORTUGAL = 'pt-PT'
    ROMANIAN = 'ro'
    RUSSIAN = 'ru'
    SPANISH = 'es'
    SPANISH_LATAM = 'es-419'
    SWEDISH = 'sv'
    TURKISH = 'tr'
    DUTCH = 'nl'
    GREEK = 'el'
    HINDI = 'hi'
    HEBREW = 'he'
    NORWEGIAN = 'no'
    DANISH = 'da'
    FINNISH = 'fi'
    CZECH = 'cs'
    HUNGARIAN = 'hu'


class TermLexicalType(Enum):
    SYNONYM = auto()
    ANTONYM = auto()
    INFLECTION = auto()
    IDIOM = auto()
    RHYME = auto()
