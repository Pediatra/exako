import factory
from factory import fuzzy

from exako.apps.term import models
from exako.apps.term.constants import Language, Level, PartOfSpeech, TermLexicalType


class TermFactory(factory.alchemy.SQLAlchemyModelFactory):
    content = factory.Faker('sentence')
    language = Language.PORTUGUESE_BRAZIL
    additional_content = {'syllable': ['ca', 'sa']}

    class Meta:
        model = models.Term
        sqlalchemy_session_persistence = 'commit'


class TermLexicalFactory(factory.alchemy.SQLAlchemyModelFactory):
    content = factory.Faker('sentence')
    type = fuzzy.FuzzyChoice(TermLexicalType)
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa']}

    class Meta:
        model = models.TermLexical
        sqlalchemy_session_persistence = 'commit'


class TermExampleFactory(factory.alchemy.SQLAlchemyModelFactory):
    language = Language.PORTUGUESE_BRAZIL
    content = factory.Faker('sentence', nb_words=8)
    level = fuzzy.FuzzyChoice(Level)
    additional_content = {'syllable': ['ca', 'sa']}

    class Meta:
        model = models.TermExample
        sqlalchemy_session_persistence = 'commit'


class TermExampleTranslationFactory(factory.alchemy.SQLAlchemyModelFactory):
    language = Language.ARABIC
    translation = factory.Faker('sentence')
    term_example = factory.SubFactory(TermExampleFactory)

    class Meta:
        model = models.TermExampleTranslation
        sqlalchemy_session_persistence = 'commit'


class TermDefinitionFactory(factory.alchemy.SQLAlchemyModelFactory):
    level = fuzzy.FuzzyChoice(Level)
    part_of_speech = fuzzy.FuzzyChoice(PartOfSpeech)
    content = factory.Faker('sentence')
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa']}

    class Meta:
        model = models.TermDefinition
        sqlalchemy_session_persistence = 'commit'


class TermDefinitionTranslationFactory(factory.alchemy.SQLAlchemyModelFactory):
    language = Language.ARABIC
    translation = factory.Faker('sentence')
    meaning = factory.Faker('sentence')
    term_definition = factory.SubFactory(TermDefinitionFactory)

    class Meta:
        model = models.TermDefinitionTranslation
        sqlalchemy_session_persistence = 'commit'


class TermPronunciationFactory(factory.alchemy.SQLAlchemyModelFactory):
    audio_url = 'https://www.example.com/audio.mp3'
    phonetic = factory.Faker('name')
    additional_content = {'syllable': ['ca', 'sa']}

    class Meta:
        model = models.TermPronunciation
        sqlalchemy_session_persistence = 'commit'


class TermImageFactory(factory.alchemy.SQLAlchemyModelFactory):
    term = factory.SubFactory(TermFactory)
    image_url = 'https://www.example.com/image.svg'

    class Meta:
        model = models.TermImage
        sqlalchemy_session_persistence = 'commit'
