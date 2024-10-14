from exako.apps.core.enum import IntegerChoices, TextChoices
from exako.apps.core.i18n import _


class Level(TextChoices):
    BEGINNER = 'A1', _('Beginner')
    ELEMENTARY = 'A2', _('Elementary')
    INTERMEDIATE = 'B1', _('Intermediate')
    UPPER_INTERMEDIATE = 'B2', _('Upper Intermediate')
    ADVANCED = 'C1', _('Advanced')
    MASTER = 'C2', _('Master')


class PartOfSpeech(IntegerChoices):
    ADJECTIVE = 0, _('Adjective')
    NOUN = 1, _('Noun')
    VERB = 2, _('Verb')
    ADVERB = 3, _('Adverb')
    CONJUNCTION = 4, _('Conjunction')
    PREPOSITION = 5, _('Preposition')
    PRONOUN = 6, _('Pronoun')
    DETERMINER = 7, _('Determiner')
    NUMBER = 8, _('Number')
    PREDETERMINER = 9, _('Predeterminer')
    PREFIX = 10, _('Prefix')
    SUFFIX = 11, _('Suffix')
    SLANG = 12, _('Slang')
    PHRASAL_VERB = 13, _('Phrasal verb')


class Language(TextChoices):
    ARABIC = 'ar', _('Arabic')
    CHINESE = 'zh', _('Chinese')
    CHINESE_SIMPLIFIED = 'zh-CN', _('Chinese (Simplified)')
    CHINESE_TRADITIONAL = 'zh-TW', _('Chinese (Traditional)')
    ENGLISH_USA = 'en-US', _('English (USA)')
    ENGLISH_UK = 'en-GB', _('English (UK)')
    FRENCH = 'fr', _('French')
    FRENCH_CANADA = 'fr-CA', _('French (Canada)')
    GERMAN = 'de', _('German')
    ITALIAN = 'it', _('Italian')
    JAPANESE = 'ja', _('Japanese')
    KOREAN = 'ko', _('Korean')
    POLISH = 'pl', _('Polish')
    PORTUGUESE_BRAZIL = 'pt-BR', _('Portuguese (Brazil)')
    PORTUGUESE_PORTUGAL = 'pt-PT', _('Portuguese (Portugal)')
    ROMANIAN = 'ro', _('Romanian')
    RUSSIAN = 'ru', _('Russian')
    SPANISH = 'es', _('Spanish')
    SPANISH_LATAM = 'es-419', _('Spanish (Latin America)')
    SWEDISH = 'sv', _('Swedish')
    TURKISH = 'tr', _('Turkish')
    DUTCH = 'nl', _('Dutch')
    GREEK = 'el', _('Greek')
    HINDI = 'hi', _('Hindi')
    HEBREW = 'he', _('Hebrew')
    NORWEGIAN = 'no', _('Norwegian')
    DANISH = 'da', _('Danish')
    FINNISH = 'fi', _('Finnish')
    CZECH = 'cs', _('Czech')
    HUNGARIAN = 'hu', _('Hungarian')


language_emoji_map: dict[Language, str] = {
    Language.ARABIC: '🇸🇦',
    Language.CHINESE: '🇨🇳',
    Language.CHINESE_SIMPLIFIED: '🇨🇳',
    Language.CHINESE_TRADITIONAL: '🇹🇼',
    Language.ENGLISH_USA: '🇺🇸',
    Language.ENGLISH_UK: '🇬🇧',
    Language.FRENCH: '🇫🇷',
    Language.FRENCH_CANADA: '🇨🇦',
    Language.GERMAN: '🇩🇪',
    Language.ITALIAN: '🇮🇹',
    Language.JAPANESE: '🇯🇵',
    Language.KOREAN: '🇰🇷',
    Language.POLISH: '🇵🇱',
    Language.PORTUGUESE_BRAZIL: '🇧🇷',
    Language.PORTUGUESE_PORTUGAL: '🇵🇹',
    Language.ROMANIAN: '🇷🇴',
    Language.RUSSIAN: '🇷🇺',
    Language.SPANISH: '🇪🇸',
    Language.SPANISH_LATAM: '🌎',
    Language.SWEDISH: '🇸🇪',
    Language.TURKISH: '🇹🇷',
    Language.DUTCH: '🇳🇱',
    Language.GREEK: '🇬🇷',
    Language.HINDI: '🇮🇳',
    Language.NORWEGIAN: '🇳🇴',
    Language.DANISH: '🇩🇰',
    Language.FINNISH: '🇫🇮',
    Language.CZECH: '🇨🇿',
    Language.HUNGARIAN: '🇭🇺',
}

language_alphabet_map: dict[Language, str] = {
    Language.ARABIC: 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي',
    Language.CHINESE: '阿贝色德饿佛日哈伊鸡卡勒马娜哦佩苦耳斯特乌维独埃克斯伊格黑克',
    Language.CHINESE_SIMPLIFIED: '阿贝色德饿佛日哈伊鸡卡勒马娜哦佩苦耳斯特乌维独埃克斯伊格黑克',
    Language.CHINESE_TRADITIONAL: '阿貝色德餓佛日哈伊雞卡勒馬娜哦佩苦耳斯特烏維獨埃克斯伊格黑克',
    Language.ENGLISH_USA: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.ENGLISH_UK: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.FRENCH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ',
    Language.FRENCH_CANADA: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ',
    Language.GERMAN: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß',
    Language.ITALIAN: 'ABCDEFGHILMNOPQRSTUVZ',
    Language.JAPANESE: 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
    Language.KOREAN: 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ',
    Language.POLISH: 'AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ',
    Language.PORTUGUESE_BRAZIL: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÇÉÊÍÓÔÕÚ',
    Language.PORTUGUESE_PORTUGAL: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÀÇÉÊÍÓÔÕÚ',
    Language.ROMANIAN: 'AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ',
    Language.RUSSIAN: 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
    Language.SPANISH: 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ',
    Language.SPANISH_LATAM: 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ',
    Language.SWEDISH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ',
    Language.TURKISH: 'ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ',
    Language.DUTCH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.GREEK: 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ',
    Language.HINDI: 'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',
    Language.NORWEGIAN: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ',
    Language.DANISH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ',
    Language.FINNISH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ',
    Language.CZECH: 'AÁBCČDĎEFGHIJKLMNŇOÓPQRŘSŠTŤUVWXYÝZŽ',
    Language.HUNGARIAN: 'AÁBCDEÉFGHIÍJKLMNOÓÖŐPQRSTUÚÜŰVWXYZ',
}
