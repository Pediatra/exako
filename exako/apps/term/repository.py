from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate as paginate_query
from sqlmodel import and_, func, or_, select

from exako.apps.term import constants, models
from exako.core.repository import BaseRepository


class TermRepository(BaseRepository):
    model = models.Term
    ordering = [models.Term.content]

    @staticmethod
    def get_term_by_content_statement(content: str, language: str):
        return select(models.Term).where(
            or_(
                and_(
                    func.clean_text(models.Term.content) == func.clean_text(content),
                    models.Term.language == language,
                ),
                models.Term.id.in_(
                    select(models.TermLexical.term_id).where(
                        func.clean_text(models.TermLexical.content)
                        == func.clean_text(content),
                        models.Term.language == language,
                        models.TermLexical.type == constants.TermLexicalType.INFLECTION,
                    )
                ),
            ),
        )

    @staticmethod
    def search_term_statement(content, language):
        return select(models.Term).where(
            or_(
                and_(
                    func.clean_text(models.Term.content) == func.clean_text(content),
                    models.Term.language == language,
                ),
                models.Term.id.in_(
                    select(models.TermLexical.term_id)
                    .join(models.Term, models.TermLexical.term_id == models.Term.id)
                    .where(
                        func.clean_text(models.TermLexical.content).icontains(
                            func.clean_text(content)
                        ),
                        models.TermLexical.type == constants.TermLexicalType.INFLECTION,
                        models.Term.language == language,
                    )
                ),
            ),
        )

    @staticmethod
    def search_reverse_term_statement(content, language, translation_language):
        return (
            select(models.Term)
            .join(
                models.TermDefinition, models.TermDefinition.term_id == models.Term.id
            )
            .join(
                models.TermDefinitionTranslation,
                models.TermDefinition.id
                == models.TermDefinitionTranslation.term_definition_id,
            )
            .where(
                func.clean_text(models.TermDefinitionTranslation.meaning).icontains(
                    func.clean_text(content)
                ),
                models.Term.language == language,
                models.TermDefinitionTranslation.language == translation_language,
            )
        )

    @staticmethod
    def index_term_statement(char, language):
        return select(models.Term).where(
            models.Term.language == language,
            models.Term.content.istartswith(char),
        )


class TermLexicalRepository(BaseRepository):
    model = models.TermLexical
    ordering = [models.TermLexical.id]

    def create(self, **kwargs):
        exists_query = select(models.TermLexical).where(
            models.TermLexical.term_id == kwargs['term_id'],
            models.TermLexical.type == kwargs['type'],
        )
        if kwargs.get('content') is not None:
            exists_query = exists_query.where(
                func.clean_text(models.TermLexical.content)
                == (func.clean_text(kwargs['content']))
            )
        else:
            exists_query = exists_query.where(
                models.TermLexical.term_content_id == kwargs['term_content_id']
            )
        if self.session.exec(exists_query).first():
            raise HTTPException(
                status_code=409,
                detail='lexical already exists to this term.',
            )
        return super().create(**kwargs)


class TermImageRepository(BaseRepository):
    model = models.TermImage


class TermPronunciationRepository(BaseRepository):
    model = models.TermPronunciation


class TermExampleRepository(BaseRepository):
    model = models.TermExample

    def list(self, statement=None, paginate=False, **kwargs):
        filter_params = kwargs.pop('filter_params')
        link_params = kwargs.pop('link_params')

        subq_highlight = (
            select(models.TermExampleLink.highlight)
            .where(
                models.TermExampleLink.term_example_id == models.TermExample.id,
            )
            .filter_by(**link_params)
            .limit(1)
        )

        statement = (
            select(
                models.TermExample.__table__.columns, subq_highlight.label('highlight')
            )
            .where(
                models.TermExample.id.in_(
                    (
                        select(models.TermExampleLink.term_example_id)
                        .filter_by(**link_params)
                        .distinct()
                    )
                )
            )
            .filter_by(**filter_params)
            .order_by(models.TermExample.content)
        )
        if paginate:
            return paginate_query(self.session, statement, unique=False)
        return self.session.exec(statement)


class TermExampleLinkRepository(BaseRepository):
    model = models.TermExampleLink


class TermExampleTranslationRepository(BaseRepository):
    model = models.TermExampleTranslation


class TermDefinitionRepository(BaseRepository):
    model = models.TermDefinition
    ordering = [models.TermDefinition.content]

    def create(self, **kwargs):
        if self.session.exec(
            select(models.TermDefinition).where(
                models.TermDefinition.id == kwargs['term_id'],
                models.TermDefinition.part_of_speech == kwargs['part_of_speech'],
                func.clean_text(models.TermDefinition.content)
                == func.clean_text(models.TermDefinition.content),
            )
        ).first():
            raise HTTPException(
                status_code=409,
                detail='definition already exists to this term.',
            )
        return super().create(**kwargs)


class TermDefinitionTranslationRepository(BaseRepository):
    model = models.TermDefinitionTranslation

    def list_meaning(self, term_id, translation_language):
        return self.session.exec(
            select(models.TermDefinitionTranslation.meaning)
            .join(
                models.TermDefinition,
                models.TermDefinition.id
                == models.TermDefinitionTranslation.term_definition_id,
            )
            .where(
                models.TermDefinition.term_id == term_id,
                models.TermDefinitionTranslation.language == translation_language,
            )
        ).all()
