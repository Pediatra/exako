import re
import string
from abc import ABC, abstractmethod
from functools import cached_property
from random import randint, sample, shuffle

from django.db.models import OuterRef, Subquery
from django.db.models.functions import Random
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from ninja import Field, File, Router, Schema, UploadedFile
from pydantic import create_model

from exako.apps.core.schema import NotAuthenticated, NotFound
from exako.apps.exercise import constants
from exako.apps.exercise.api.schema import ExerciseResponse
from exako.apps.exercise.constants import ExerciseSubType, ExerciseType
from exako.apps.exercise.models import Exercise as ExerciseModel
from exako.apps.exercise.models import ExerciseHistory
from exako.apps.term.constants import TermLexicalType
from exako.apps.term.models import (
    Term,
    TermDefinition,
    TermExampleLink,
    TermImage,
    TermLexical,
    TermPronunciation,
)
from exako.apps.user.models import User


def _shuffle_dict(dict_):
    dict_ = list(dict_.items())
    shuffle(dict_)
    return dict(dict_)


def _camel_to_snake(name):
    pattern = re.compile(r'(?<!^)(?<![A-Z])(?=[A-Z])')
    return pattern.sub('_', name).lower()


def _normalize_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()


class Exercise(ABC):
    html_template: str
    exercise: ExerciseModel
    exercise_type: ExerciseType
    title: str
    description: str
    short_description: str

    def __init__(self, exercise_id: int):
        self.exercise = get_object_or_404(
            ExerciseModel,
            id=exercise_id,
            type=self.exercise_type,
        )

    def render_template(self, request, **extra):
        build = self.build()
        response = {
            key: value
            for key, value in build.items()
            if key not in ['title', 'description']
        }
        return render(
            request,
            self.html_template,
            context={**build, **extra, 'response': response},
        )

    @abstractmethod
    def build(self) -> dict:
        pass

    @cached_property
    @abstractmethod
    def correct_answer(self):
        pass

    @abstractmethod
    def assert_answer(self, answer: dict) -> bool:
        pass

    def get_correct_feedback(self):
        return constants.CORRECT_FEEDBACK

    def get_incorrect_feedback(self):
        return constants.INCORRECT_FEEDBACK

    def check(self, user: User, answer: dict, exercise_request: dict) -> dict:
        correct = self.assert_answer(answer)
        check_response = {
            'correct': correct,
            'correct_answer': self.correct_answer,
        }
        ExerciseHistory.objects.create(
            exercise=self.exercise,
            user=user,
            correct=correct,
            response={**answer, **check_response},
            request=exercise_request,
        )
        feedback = self.get_correct_feedback if correct else self.get_incorrect_feedback
        check_response.update(feedback=feedback)
        return check_response

    @classmethod
    def _generate_build_endpoint(cls, exercise_schema: type[Schema]):
        def build_endpoint(request, exercise_id: int):
            exercise = cls(exercise_id)
            return exercise_schema(**exercise.build())

        return build_endpoint

    @classmethod
    def _generate_check_endpoint(cls, CheckSchema: type[Schema], **answer_fields):
        field_definitions = dict()
        for field, field_info in answer_fields.items():
            if not isinstance(field_info, tuple):
                field_info = (field_info, ...)
            field_definitions[field] = field_info
        AnswerSchema = create_model(
            f'AnswerSchema{cls.__name__}',
            **field_definitions,
        )
        CheckSchema = create_model(
            f'CheckSchema{cls.__name__}',
            __base__=CheckSchema,
            answer=(AnswerSchema, ...),
        )

        def check_endpoint(
            request,
            exercise_id: int,
            answer: CheckSchema,  # pyright: ignore[reportInvalidTypeForm]
        ):
            exercise = cls(exercise_id)
            return ExerciseResponse(
                **exercise.check(
                    request.user,
                    answer=answer.model_dump()['answer'],
                    exercise_request=answer.model_dump(exclude={'answer'}),
                )
            )

        return check_endpoint

    @classmethod
    def as_endpoint(
        cls,
        router: Router,
        path: str,
        ExerciseSchema: type[Schema],
        **answer_fields,
    ):
        router.get(
            path=path,
            response={
                200: ExerciseSchema,
                401: NotAuthenticated,
                404: NotFound,
            },
            summary=cls.title,
            description=cls.description,
            url_name=_camel_to_snake(cls.__name__),
            operation_id=cls.__name__,
        )(cls._generate_build_endpoint(ExerciseSchema))

        CheckSchema = create_model(
            f'CheckSchema{cls.__name__}',
            time_to_answer=(int, Field(gt=0)),
            **{
                name: (field.annotation, field)
                for name, field in ExerciseSchema.model_fields.items()
                if name not in {'title', 'description'}
            },
        )
        router.post(
            path=path,
            response={
                200: ExerciseResponse,
                401: NotAuthenticated,
                404: NotFound,
            },
            url_name=f'check_{_camel_to_snake(cls.__name__)}',
            operation_id=f'check_{cls.__name__}',
        )(cls._generate_check_endpoint(CheckSchema, **answer_fields))


class OrderSentenceExercise(Exercise):
    exercise_type = ExerciseType.ORDER_SENTENCE
    html_template = 'exercise/exercises/order_sentence.html'
    title = _('Reordenar frases')
    short_description = _('Aprenda a estruturar frases corretamente')
    description = _("""
        Esse exercício apresenta uma frase relacionada a um termo ou conceito específico, mas com as palavras embaralhadas.
        O objetivo do usuário é reordenar as palavras para reconstruir a frase na ordem correta.

        Instruções para o usuário:
        1. Uma frase embaralhada aparecerá.
        2. O usuário deve tentar reordenar as palavras da frase para formar uma frase lógica.
    """)

    def _get_distractors(self, min_distractors=0):
        distractors_dict = self.exercise.additional_content.get('distractors', {})
        distractors_list = distractors_dict.get('term', [])
        number_of_distractors = randint(min_distractors, len(distractors_list))
        distractors = list(sample(distractors_list, number_of_distractors))
        return list(
            Term.objects.filter(id__in=distractors).values_list('expression', flat=True)
        )

    def build(self) -> dict:
        sentence = self.correct_answer
        sentence_parts = sentence.split()

        sentence_parts += self._get_distractors()
        shuffle(sentence_parts)

        return {
            'sentence': sentence_parts,
            'title': self.title,
            'description': self.description,
            'header': constants.ORDER_SENTENCE_HEADER,
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_example.example

    def assert_answer(self, answer: dict) -> bool:
        sentence = _normalize_text(answer['sentence'])
        correct_answer = _normalize_text(self.correct_answer)
        return sentence == correct_answer

    def get_incorrect_feedback(self):
        return constants.INCORRECT_FEEDBACK_CORRECT_ANSWER.format(
            answer=self.correct_answer
        )


class ListenTermExercise(Exercise):
    exercise_type = ExerciseType.LISTEN_TERM
    html_template = 'exercise/exercises/listen.html'
    title = _('Escutar termo')
    short_description = _('Aprimore sua compreensão auditiva')
    description = _("""
        Esse exercício ajuda o usuário a identificar o termo correto a partir da sua pronúncia. 
        O exercício reproduz a pronúncia de um termo e apresenta uma lista de alternativas que incluem palavras semelhantes. 
        O objetivo do usuário é selecionar a alternativa que corresponde ao termo pronunciado.

        Instruções para o usuário:
        1. Ouça o áudio da pronúncia do termo.
        2. Veja a lista de alternativas fornecidas.
        3. Escolha a alternativa que corresponde ao termo pronunciado.
    """)

    def build(self) -> dict:
        return {
            'audio_file': self.exercise.term_pronunciation.audio_file,
            'title': self.title,
            'description': self.description,
            'header': constants.LISTEN_TERM_HEADER,
        }

    @cached_property
    def correct_answer(self) -> str:
        sub_type = self.exercise.additional_content.get('sub_type')
        if sub_type == ExerciseSubType.TERM_LEXICAL_VALUE:
            text = self.exercise.term_lexical.value
        elif sub_type == ExerciseSubType.TERM_LEXICAL_TERM_REF:
            text = self.exercise.term_lexical.term_value_ref.expression
        else:
            text = self.exercise.term.expression
        return text

    def assert_answer(self, answer: dict) -> bool:
        sentence = _normalize_text(answer['expression'])
        correct_answer = _normalize_text(self.correct_answer)
        return sentence == correct_answer

    def get_incorrect_feedback(self):
        return constants.INCORRECT_FEEDBACK_CORRECT_ANSWER.format(
            answer=self.correct_answer
        )


class ListenTermMChoiceExercise(Exercise):
    exercise_type = ExerciseType.LISTEN_TERM_MCHOICE
    html_template = 'exercise/exercises/listen_mchoice.html'
    title = _('Escutar termos similares')
    short_description = _('Diferencie termos semelhantes pela audição')
    description = _("""
        Esse exercício desafia o usuário a identificar um termo com base em sua pronúncia. 
        O exercício reproduz a pronúncia do termo em áudio e apresenta uma lista de alternativas que incluem palavras similares. 
        O usuário deve selecionar a alternativa que corresponde ao termo pronunciado.

        Instruções para o usuário:
        1. Ouça o áudio da pronúncia do termo.
        2. Analise a lista de alternativas fornecidas.
        3. Selecione a alternativa que corresponde ao termo pronunciado.
    """)

    def build(self) -> dict:
        choices = dict()
        choices[self.correct_answer] = self.exercise.term_pronunciation.audio_file
        choices_rhymes = (
            TermLexical.objects.filter(
                term_id=self.exercise.term_id,
                type=TermLexicalType.RHYME,
                term_value_ref__isnull=False,
            )
            .select_related('term_value_ref')
            .annotate(random_order=Random())
            .annotate(
                audio_file=Subquery(
                    TermPronunciation.objects.filter(
                        term_id=OuterRef('term_value_ref_id')
                    ).values('audio_file')
                )
            )
            .order_by('random_order')[:3]
            .values_list(
                'term_value_ref_id',
                'audio_file',
            )
        )
        choices.update({term_id: audio_file for term_id, audio_file in choices_rhymes})
        choices = _shuffle_dict(choices)

        return {
            'choices': choices,
            'title': self.title,
            'description': self.description,
            'header': constants.LISTEN_MCHOICE_HEADER.format(
                term=self.exercise.term.expression
            ),
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_id

    def assert_answer(self, answer: dict) -> bool:
        return answer['term_id'] == self.correct_answer


class ListenSentenceExercise(Exercise):
    exercise_type = ExerciseType.LISTEN_SENTENCE
    html_template = 'exercise/exercises/listen.html'
    title = _('Escutar frase')
    short_description = _('Melhore sua compreensão de frases')
    description = _("""
        Esse exercício ajuda o usuário a praticar a escrita correta de uma frase com base na sua pronúncia. 
        O exercício reproduz a pronúncia de uma frase que é relacionada a um termo específico. 
        O objetivo do usuário é ouvir a frase e digitá-la corretamente.

        Instruções para o usuário:
        1. Ouça o áudio da pronúncia da frase.
        2. Escreva a frase que você ouviu.
        3. Verifique se a frase digitada está correta.
    """)

    def build(self) -> dict:
        return {
            'audio_file': self.exercise.term_pronunciation.audio_file,
            'title': self.title,
            'description': self.description,
            'header': constants.LISTEN_SENTENCE_HEADER,
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_example.example

    def assert_answer(self, answer: dict) -> bool:
        sentence = _normalize_text(answer['sentence'])
        correct_answer = _normalize_text(self.correct_answer)
        return sentence == correct_answer

    def get_incorrect_feedback(self):
        return constants.INCORRECT_FEEDBACK_CORRECT_ANSWER.format(
            answer=self.correct_answer
        )


class SpeakTermExercise(Exercise):
    exercise_type = ExerciseType.SPEAK_TERM
    html_template = 'exercise/exercises/speak.html'
    title = _('Falar termo')
    short_description = _('Pratique a pronúncia correta de termos')
    description = _("""
        Esse exercício desafia o usuário a pronunciar corretamente um termo com base na sua fonética ou pronúncia fornecida. 
        O exercício reproduz a fonética ou pronúncia do termo e o usuário deve usar seu microfone para gravar sua própria pronúncia. 
        O sistema então verifica se a pronúncia do usuário está correta.

        Instruções para o usuário:
        1. Ouça a fonética ou pronúncia do termo fornecida.
        2. Use seu microfone para gravar a pronúncia do termo.
        3. O sistema verifica se a pronúncia gravada está correta em comparação com a pronúncia fornecida.
    """)

    def build(self) -> dict:
        return {
            'audio_file': self.exercise.term_pronunciation.audio_file,
            'phonetic': self.exercise.term_pronunciation.phonetic,
            'title': self.title,
            'description': self.description,
            'header': constants.SPEAK_TERM_HEADER.format(term=self.correct_answer),
        }

    @cached_property
    def correct_answer(self) -> str:
        sub_type = self.exercise.additional_content.get('sub_type')
        if sub_type == ExerciseSubType.TERM_LEXICAL_VALUE:
            text = self.exercise.term_lexical.value
        elif sub_type == ExerciseSubType.TERM_LEXICAL_TERM_REF:
            text = self.exercise.term_lexical.term_value_ref.expression
        else:
            text = self.exercise.term.expression
        return text

    def assert_answer(self, answer: dict) -> bool:
        # TODO: SpeechToText API
        return True

    def check(self, user: User, answer: dict, exercise_request: dict) -> dict:
        answer.pop('audio')  # TODO: SpeechToText API
        return super().check(user, answer, exercise_request)

    @classmethod
    def _generate_check_endpoint(cls, CheckSchema: type[Schema], **answer_fields):
        def check_endpoint(
            request,
            exercise_id: int,
            answer: CheckSchema,  # pyright: ignore[reportInvalidTypeForm]
            audio: UploadedFile = File(...),
        ):
            exercise = cls(exercise_id)
            return ExerciseResponse(
                **exercise.check(
                    user=request.user,
                    answer={'audio': audio},
                    exercise_request=answer.model_dump(),
                )
            )

        return check_endpoint


class SpeakSentenceExercise(Exercise):
    exercise_type = ExerciseType.SPEAK_SENTENCE
    html_template = 'exercise/exercises/speak.html'
    title = _('Falar frase')
    short_description = _('Aperfeiçoe sua pronúncia de frases')
    description = _("""
        Esse exercício desafia o usuário a pronunciar corretamente uma frase com base na sua fonética ou pronúncia fornecida. 
        O exercício reproduz a fonética ou pronúncia da frase e o usuário deve usar seu microfone para gravar sua própria pronúncia. 
        O sistema então verifica se a pronúncia do usuário está correta.

        Instruções para o usuário:
        1. Ouça a fonética ou pronúncia da frase fornecida.
        2. Use seu microfone para gravar a pronúncia da frase.
        3. O sistema verifica se a pronúncia gravada está correta em comparação com a pronúncia fornecida.
    """)

    def build(self) -> dict:
        return {
            'audio_file': self.exercise.term_pronunciation.audio_file,
            'phonetic': self.exercise.term_pronunciation.phonetic,
            'title': self.title,
            'description': self.description,
            'header': constants.SPEAK_SENTENCE_HEADER.format(
                sentence=self.correct_answer
            ),
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_example.example

    def assert_answer(self, answer: dict) -> bool:
        # TODO: SpeechToText API
        return True

    def check(self, user: User, answer: dict, exercise_request: dict) -> dict:
        answer.pop('audio')  # TODO: SpeechToText API
        return super().check(user, answer, exercise_request)

    @classmethod
    def _generate_check_endpoint(cls, CheckSchema: type[Schema], **answer_fields):
        def check_endpoint(
            request,
            exercise_id: int,
            answer: CheckSchema,  # pyright: ignore[reportInvalidTypeForm]
            audio: UploadedFile = File(...),
        ):
            exercise = cls(exercise_id)
            return ExerciseResponse(
                **exercise.check(
                    user=request.user,
                    answer={'audio': audio},
                    exercise_request=answer.model_dump(),
                )
            )

        return check_endpoint


class TermMChoiceExercise(Exercise):
    exercise_type = ExerciseType.TERM_MCHOICE
    html_template = 'exercise/exercises/multiple_choice.html'
    title = _('Completar a frase')
    short_description = _('Teste sua compreensão contextual')
    description = _("""
        Esse exercício desafia o usuário a completar uma frase com base em um termo específico que está faltando na frase.
        O exercício fornece uma frase com um espaço vazio onde o termo deve ser inserido, e o usuário deve escolher a alternativa correta que preenche o espaço de forma apropriada.
        O objetivo do usuário e entender o contexto da frase e selecionar corretamente qual das opções se encaixa na frase.

        Instruções para o usuário:
        1. Analise a frase com o espaço vazio onde um termo está faltando.
        2. Revise as alternativas fornecidas.
        3. Escolha a alternativa que completa corretamente a frase.
    """)

    def _get_distractors(self):
        is_term_lexical = self.exercise.additional_content.get('sub_type') in [
            ExerciseSubType.TERM_LEXICAL_TERM_REF,
            ExerciseSubType.TERM_LEXICAL_VALUE,
        ]
        distractor_key = 'term_lexical' if is_term_lexical else 'term'
        distractor_list = self.exercise.additional_content.get('distractors')[
            distractor_key
        ]
        distractors = sample(distractor_list, 3)

        if is_term_lexical:
            return {
                id_: value or expression
                for id_, value, expression in TermLexical.objects.select_related(
                    'term_value_ref'
                )
                .filter(id__in=distractors)
                .values_list('id', 'value', 'term_value_ref__expression')
            }
        else:
            return dict(
                Term.objects.filter(id__in=distractors).values_list('id', 'expression')
            )

    def _correct_choice(self):
        sub_type = self.exercise.additional_content.get('sub_type')
        if sub_type == ExerciseSubType.TERM_LEXICAL_VALUE:
            text = self.exercise.term_lexical.value
        elif sub_type == ExerciseSubType.TERM_LEXICAL_TERM_REF:
            text = self.exercise.term_lexical.term_value_ref.expression
        else:
            text = self.exercise.term.expression
        return {self.correct_answer: text}

    def _mask_sentence(self):
        sub_type = self.exercise.additional_content.get('sub_type')
        filter_params = {}
        if sub_type == ExerciseSubType.TERM_LEXICAL_VALUE:
            filter_params['term_lexical_id'] = self.exercise.term_lexical_id
        elif sub_type == ExerciseSubType.TERM_LEXICAL_TERM_REF:
            filter_params['term_id'] = self.exercise.term_lexical.term_value_ref_id
        else:
            filter_params['term_id'] = self.exercise.term_id
        highlight = TermExampleLink.objects.filter(
            term_example_id=self.exercise.term_example_id,
            **filter_params,
        ).values_list('highlight', flat=True)[0]

        sentence = self.exercise.term_example.example
        sentence = list(sentence)
        for start, end in list(highlight):
            for i in range(start, end + 1):
                sentence[i] = '_'
        sentence = ''.join(sentence)
        return sentence

    def build(self) -> dict:
        choices = dict()
        choices.update(self._correct_choice())
        choices.update(self._get_distractors())
        choices = _shuffle_dict(choices)
        return {
            'title': self.title,
            'description': self.description,
            'header': constants.TERM_MCHOICE_HEADER.format(
                sentence=self._mask_sentence()
            ),
            'choices': choices,
        }

    @cached_property
    def correct_answer(self) -> int:
        if self.exercise.additional_content.get('sub_type') in [
            ExerciseSubType.TERM_LEXICAL_TERM_REF,
            ExerciseSubType.TERM_LEXICAL_VALUE,
        ]:
            text_id = self.exercise.term_lexical_id
        else:
            text_id = self.exercise.term_id
        return text_id

    def assert_answer(self, answer: dict) -> bool:
        return answer['term_id'] == self.correct_answer


class TermDefinitionMChoiceExercise(Exercise):
    exercise_type = ExerciseType.TERM_DEFINITION_MCHOICE
    html_template = 'exercise/exercises/multiple_choice.html'
    title = _('Identificar significado')
    short_description = _('Aprenda a associar termos às suas definições')
    description = _("""
        Esse exercício ajuda o usuário a associar um termo com a definição correta. 
        O exercício fornece um termo e apresenta quatro alternativas de definições. 
        O usuário deve escolher a definição que melhor corresponde ao termo fornecido.

        Instruções para o usuário:
        1. Analise o termo fornecido.
        2. Revise as quatro definições apresentadas como alternativas.
        3. Selecione a definição que corresponde corretamente ao termo.
    """)

    def _get_distractors(self):
        distractors_list = self.exercise.additional_content.get('distractors')[
            'term_definition'
        ]
        distractors = list(sample(distractors_list, 3))
        return dict(
            TermDefinition.objects.filter(id__in=distractors).values_list(
                'id', 'definition'
            )
        )

    def build(self) -> dict:
        choices = dict()
        choices[self.correct_answer] = self.exercise.term_definition.definition
        choices.update(self._get_distractors())
        choices = _shuffle_dict(choices)

        return {
            'title': self.title,
            'description': self.description,
            'header': constants.TERM_DEFINITION_MCHOICE_HEADER.format(
                term=self.exercise.term.expression
            ),
            'choices': choices,
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_definition_id

    def assert_answer(self, answer: dict) -> bool:
        return answer['term_definition_id'] == self.correct_answer


class TermImageMChoiceExercise(Exercise):
    exercise_type = ExerciseType.TERM_IMAGE_MCHOICE
    html_template = 'exercise/exercises/image_mchoice.html'
    title = _('Identificar imagem')
    short_description = _('Relacione termos com suas imagens')
    description = _("""
        O exercício reproduz o áudio que fornece informações sobre o termo e apresenta várias imagens como opções. 
        O usuário deve selecionar a imagem que corresponde ao termo descrito no áudio.

        Instruções para o usuário:
        1. Ouça o áudio que descreve o termo.
        2. Analise as imagens fornecidas como opções.
        3. Escolha a imagem que corresponde ao termo descrito no áudio.
    """)

    def _get_distractors(self):
        distractors_list = self.exercise.additional_content.get('distractors')[
            'term_image'
        ]
        distractors = list(sample(distractors_list, 3))
        return {
            term.term_id: term.image.url
            for term in TermImage.objects.filter(id__in=distractors)
        }

    def build(self) -> dict:
        choices = dict()
        choices[self.correct_answer] = self.exercise.term_image.image.url
        choices.update(self._get_distractors())
        choices = _shuffle_dict(choices)

        return {
            'title': self.title,
            'description': self.description,
            'header': constants.TERM_IMAGE_MCHOICE_HEADER,
            'audio_file': self.exercise.term_pronunciation.audio_file,
            'choices': choices,
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_id

    def assert_answer(self, answer: dict) -> bool:
        return answer['term_id'] == self.correct_answer


class TermImageMChoiceTextExercise(Exercise):
    exercise_type = ExerciseType.TERM_IMAGE_MCHOICE_TEXT
    html_template = 'exercise/exercises/image_mchoice_text.html'
    title = _('Identificar imagem')
    short_description = _('Associe imagens aos seus termos')
    description = _("""
        Esse exercício desafia o usuário a identificar o termo correto com base em uma imagem fornecida. 
        O exercício exibe uma imagem e apresenta uma lista de termos como opções. 
        O usuário deve selecionar o termo que melhor corresponde à imagem exibida.

        Instruções para o usuário:
        1. Observe a imagem exibida.
        2. Analise os termos fornecidos como opções.
        3. Escolha o termo que corresponde corretamente à imagem.
    """)

    def _get_distractors(self):
        distractors_list = self.exercise.additional_content.get('distractors')['term']
        distractors = list(sample(distractors_list, 3))
        return dict(
            Term.objects.filter(id__in=distractors).values_list('id', 'expression')
        )

    def build(self) -> dict:
        choices = dict()
        choices[self.correct_answer] = self.exercise.term.expression
        choices.update(self._get_distractors())
        choices = _shuffle_dict(choices)

        return {
            'image': self.exercise.term_image.image.url,
            'title': self.title,
            'description': self.description,
            'header': constants.TERM_IMAGE_MCHOICE_TEXT_HEADER,
            'choices': choices,
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.term_id

    def assert_answer(self, answer: dict) -> bool:
        return answer['term_id'] == self.correct_answer


class TermConnectionExercise(Exercise):
    exercise_type = ExerciseType.TERM_CONNECTION
    html_template = 'exercise/exercises/term_connection.html'
    title = _('Conexões com termo')
    short_description = _('Descubra relações entre termos')
    description = _("""
        Esse exercício desafia o usuário a identificar quais alternativas estão relacionadas a um termo específico a partir de um conjunto de 12 opções. 
        O usuário deve selecionar 4 alternativas que têm conexão direta com o termo e evitar os distratores.

        Instruções para o usuário:
        1. Analise o termo fornecido.
        2. Revise as 12 alternativas apresentadas.
        3. Selecione as 4 alternativas que são relevantes para o termo e que possuem conexão com ele.
        4. Evite selecionar as opções que têm relação com o termo.
    """)

    def build(self) -> dict:
        distractors_list = self.exercise.additional_content.get('distractors')['term']
        connections_list = self.exercise.additional_content.get('connections')['term']
        choice_ids = list(sample(distractors_list, 8))
        choice_ids.extend(sample(connections_list, 4))

        choices = dict(
            Term.objects.filter(id__in=choice_ids).values_list('id', 'expression')
        )
        choices = _shuffle_dict(choices)

        return {
            'title': self.title,
            'description': self.description,
            'header': constants.TERM_CONNECTION_HEADER.format(
                term=self.exercise.term.expression
            ),
            'choices': choices,
        }

    @cached_property
    def correct_answer(self):
        return self.exercise.additional_content.get('connections')['term']

    def assert_answer(self, answer: dict) -> bool:
        return all([choice in self.correct_answer for choice in answer['choices']])


exercises_map = {
    OrderSentenceExercise,
    ListenTermExercise,
    ListenTermMChoiceExercise,
    ListenSentenceExercise,
    SpeakTermExercise,
    SpeakSentenceExercise,
    TermMChoiceExercise,
    TermDefinitionMChoiceExercise,
    TermImageMChoiceExercise,
    TermImageMChoiceTextExercise,
    TermConnectionExercise,
}
