from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from exako.apps.term import constants


class TermSchema(BaseModel):
    content: str = Field(examples=['Casa'], max_length=256)
    language: constants.Language
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermView(BaseModel):
    id: int
    content: str = Field(examples=['Casa'], max_length=256)
    language: constants.Language
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermLexicalSchema(BaseModel):
    term_id: int
    content: str | None = Field(examples=['Lar'], default=None, max_length=256)
    term_content_id: int | None = None
    type: constants.TermLexicalType
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )

    @model_validator(mode='after')
    def validation(self):
        if not any([self.content, self.term_content]):
            raise ValueError('you need to provied at least one content ref.')
        if all([self.content, self.term_content]):
            raise ValueError(
                'you cannot reference two values at once (content, term_content).'
            )
        return self


class TermLexicalView(BaseModel):
    id: int
    content: str | None = Field(examples=['Lar'], default=None, max_length=256)
    term_content_id: int | None = None
    type: constants.TermLexicalType


class TermLexicalFilter(BaseModel):
    term_id: int
    type: constants.TermLexicalType | None = None


class TermImageSchema(BaseModel):
    term_id: int
    image_url: str = Field(
        default=None,
        examples=['https://mylink.com/my-image.svg'],
        max_length=256,
    )

    @field_validator('image_url')
    @classmethod
    def validate_image_url(cls, image_url: str) -> str:
        value_exception = ValueError('invalid image_url.')
        try:
            result = urlparse(image_url)
            if not all([result.scheme, result.netloc, result.path]):
                raise value_exception
        except ValueError:
            raise value_exception

        path = result.path.lower()
        if not path.endswith('.svg'):
            raise value_exception
        return image_url


class TermImageView(BaseModel):
    id: int
    image_url: str = Field(
        default=None,
        examples=['https://mylink.com/my-image.svg'],
        max_length=256,
    )


class TermExampleLinkSchema(BaseModel):
    term_id: int | None = None
    term_definition_id: int | None = None
    term_lexical_id: int | None = None

    @model_validator(mode='after')
    def link_validator(self):
        link_attributes = {
            field: getattr(self, field)
            for field in {
                'term_id',
                'term_definition_id',
                'term_lexical_id',
            }
            if getattr(self, field, None) is not None
        }
        link_count = len(link_attributes.values())
        if link_count == 0:
            raise ValueError('you need to provide at least one object to link.')
        if link_count > 1:
            raise ValueError('you can reference only one object.')
        return self


class TermExampleFilter(TermExampleLinkSchema):
    level: constants.Level | None = None


class TermExampleSchema(TermExampleLinkSchema):
    language: constants.Language
    content: str = Field(
        examples=["Yesterday a have lunch in my mother's house."],
        max_length=256,
    )
    highlight: list[list[int]] = Field(
        examples=[[[4, 8], [11, 16]]],
        description='Highlighted positions in the given sentence where the term appears.',
    )
    level: constants.Level | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )

    @model_validator(mode='after')
    def validate_highlight(self):
        content = getattr(self, 'content', None)

        intervals = []
        for value in self.highlight:
            if len(value) != 2:
                raise ValueError(
                    'highlight must consist of pairs of numbers representing the start and end positions.'
                )

            v1, v2 = value
            example_len = len(content) - 1
            if v1 > example_len or v2 > example_len:
                raise ValueError(
                    'highlight cannot be greater than the length of the example.'
                )
            if v1 < 0 or v2 < 0:
                raise ValueError(
                    'both highlight values must be greater than or equal to 0.'
                )
            if v1 > v2:
                raise ValueError(
                    'highlight beginning value cannot be greater than the ending value, since it represents the start and end positions.'
                )

            interval = range(v1, v2 + 1)
            if any([i in intervals for i in interval]):
                raise ValueError(
                    'highlight interval must not overlap with any other intervals in highlight list.'
                )
            intervals.extend(interval)

        return self


class TermExampleView(BaseModel):
    id: int
    language: constants.Language
    content: str = Field(
        examples=["Yesterday a have lunch in my mother's house."],
        max_length=256,
    )
    highlight: list[list[int]] = Field(
        examples=[[[4, 8], [11, 16]]],
        description='highlighted positions in the given sentence where the term appears.',
    )
    level: constants.Level | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermExampleTranslationSchema(TermExampleLinkSchema):
    term_example_id: int
    language: constants.Language
    translation: str = Field(
        examples=['Ontem eu almoçei na casa da minha mãe.'], max_length=256
    )


class TermExampleTranslationView(BaseModel):
    language: constants.Language
    translation: str = Field(
        examples=['Ontem eu almoçei na casa da minha mãe.'], max_length=256
    )


class TermDefinitionSchema(BaseModel):
    term_id: int
    part_of_speech: constants.PartOfSpeech = Field(examples=(['noun']))
    content: str = Field(
        examples=['Set of walls, rooms, and roof with specific purpose of habitation.'],
        max_length=512,
    )
    level: constants.Level | None = None
    term_lexical_id: int | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermDefinitionView(BaseModel):
    id: int
    part_of_speech: constants.PartOfSpeech = Field(examples=(['noun']))
    content: str = Field(
        examples=['Set of walls, rooms, and roof with specific purpose of habitation.'],
        max_length=512,
    )
    level: constants.Level | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class ListTermDefintionFilter(BaseModel):
    term_id: int
    part_of_speech: constants.PartOfSpeech | None = None
    level: constants.Level | None = None
    term_lexical_id: int | None = None


class TermDefinitionTranslationSchema(BaseModel):
    term_definition_id: int
    language: constants.Language
    meaning: str = Field(examples=['Casa, lar'], max_length=256)
    translation: str = Field(
        examples=['Conjunto de parades, quartos e teto com a finalidade de habitação.'],
        max_length=512,
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermDefinitionTranslationView(BaseModel):
    language: constants.Language
    meaning: str = Field(examples=['Casa, lar'], max_length=256)
    translation: str = Field(
        examples=['Conjunto de parades, quartos e teto com a finalidade de habitação.'],
        max_length=512,
    )


class TermMeaningView(BaseModel):
    meaning: list[str] = Field(examples=[['casa', 'ave', 'test']])


class TermPronunciationLinkSchema(BaseModel):
    term_id: int | None = None
    term_example_id: int | None = None
    term_lexical_id: int | None = None

    @model_validator(mode='after')
    def link_validator(self):
        link_attributes = {
            field: getattr(self, field)
            for field in {
                'term_id',
                'term_example_id',
                'term_lexical_id',
            }
            if getattr(self, field, None) is not None
        }
        link_count = len(link_attributes.values())
        if link_count == 0:
            raise ValueError('you need to provide at least one object to link.')
        if link_count > 1:
            raise ValueError('you can reference only one object.')
        return self


class TermPronunciationSchema(TermPronunciationLinkSchema):
    phonetic: str = Field(examples=['/ˈhaʊ.zɪz/'])
    audio_url: str | None = Field(
        default=None,
        examples=['https://mylink.com/my-audio.mp3'],
        max_length=256,
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )

    @field_validator('audio_url')
    @classmethod
    def validate_audio_url(cls, audio_url: str) -> str:
        audio_extensions = ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a']

        value_exception = ValueError('invalid audio_url.')
        try:
            result = urlparse(audio_url)
            if not all([result.scheme, result.netloc, result.path]):
                raise value_exception
        except ValueError:
            raise value_exception

        path = result.path.lower()
        if not any(path.endswith(ext) for ext in audio_extensions):
            raise value_exception
        return audio_url


class TermPronunciationView(BaseModel):
    id: int
    phonetic: str = Field(examples=['/ˈhaʊ.zɪz/'])
    audio_url: str | None = Field(
        default=None,
        examples=['https://mylink.com/my-audio.mp3'],
        max_length=256,
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )
