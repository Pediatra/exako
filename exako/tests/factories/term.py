import factory
from factory import fuzzy

from exako.apps.term import models
from exako.apps.term.constants import Language, Level, PartOfSpeech, TermLexicalType


class TermFactory(factory.alchemy.SQLAlchemyModelFactory):
    content = factory.Faker('sentence')
    language = Language.PORTUGUESE_BRAZIL
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.Term
        sqlalchemy_session_persistence = 'commit'


class TermLexicalFactory(factory.alchemy.SQLAlchemyModelFactory):
    content = factory.Faker('sentence')
    type = fuzzy.FuzzyChoice(TermLexicalType)
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.TermLexical
        sqlalchemy_session_persistence = 'commit'


class TermExampleFactory(factory.alchemy.SQLAlchemyModelFactory):
    language = Language.PORTUGUESE_BRAZIL
    content = factory.Faker('sentence', nb_words=8)
    level = fuzzy.FuzzyChoice(Level)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.TermExample
        sqlalchemy_session_persistence = 'commit'


class TermExampleTranslationFactory(factory.alchemy.SQLAlchemyModelFactory):
    language = Language.CHINESE
    translation = factory.Faker('sentence')
    term_example = factory.SubFactory(TermExampleFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.TermExampleTranslation
        sqlalchemy_session_persistence = 'commit'


class TermDefinitionFactory(factory.alchemy.SQLAlchemyModelFactory):
    level = fuzzy.FuzzyChoice(Level)
    part_of_speech = fuzzy.FuzzyChoice(PartOfSpeech)
    content = factory.Faker('sentence')
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.TermDefinition
        sqlalchemy_session_persistence = 'commit'


class TermDefinitionTranslationFactory(factory.alchemy.SQLAlchemyModelFactory):
    language = Language.CHINESE
    translation = factory.Faker('sentence')
    meaning = factory.Faker('sentence')
    term_definition = factory.SubFactory(TermDefinitionFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.TermDefinitionTranslation
        sqlalchemy_session_persistence = 'commit'


class TermPronunciationFactory(factory.alchemy.SQLAlchemyModelFactory):
    audio_url = factory.Faker('url')
    phonetic = factory.Faker('name')
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = models.TermPronunciation
        sqlalchemy_session_persistence = 'commit'


class TermImageFactory(factory.alchemy.SQLAlchemyModelFactory):
    term = factory.SubFactory(TermFactory)
    image_url = factory.Faker('url')

    class Meta:
        model = models.TermImage
        sqlalchemy_session_persistence = 'commit'
