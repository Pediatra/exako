from tortoise import fields, models
from tortoise.contrib.postgres.fields import ArrayField


class Term(models.Model):
    expression = fields.CharField(max_length=256)
    language = fields.CharField(max_length=7)
    additional_content = fields.JSONField(null=True)

    class Meta:
        unique_together = (('expression', 'language'),)
        indexes = (('expression', 'language'),)
        ordering = ['expression']


class TermLexical(models.Model):
    term = fields.ForeignKeyField('models.Term', on_delete=fields.CASCADE)
    term_content = fields.ForeignKeyField(
        'models.Term',
        null=True,
        on_delete=fields.CASCADE,
        related_name='term_lexicals_content',
    )
    content = fields.CharField(max_length=256, null=True)
    type = fields.SmallIntField()
    additional_content = fields.JSONField(null=True)


class TermImage(models.Model):
    term = fields.OneToOneField('models.Term', on_delete=fields.CASCADE)
    image_url = fields.CharField(max_length=256)


class TermExample(models.Model):
    language = fields.CharField(max_length=7)
    content = fields.CharField(max_length=256)
    level = fields.CharField(max_length=2, null=True)
    additional_content = fields.JSONField(null=True)

    class Meta:
        ordering = ['content']


class TermExampleTranslation(models.Model):
    language = fields.CharField(max_length=7)
    translation = fields.CharField(max_length=256)
    term_example = fields.ForeignKeyField(
        'models.TermExample',
        on_delete=fields.CASCADE,
    )

    class Meta:
        unique_together = (('language', 'term_example'),)


class TermDefinition(models.Model):
    part_of_speech = fields.SmallIntField()
    content = fields.CharField(max_length=712)
    level = fields.CharField(max_length=2, null=True)
    term = fields.ForeignKeyField('models.Term', on_delete=fields.CASCADE)
    term_lexical = fields.ForeignKeyField(
        'models.TermLexical',
        on_delete=fields.CASCADE,
        null=True,
    )
    additional_content = fields.JSONField(null=True)


class TermDefinitionTranslation(models.Model):
    language = fields.CharField(max_length=2)
    translation = fields.CharField(max_length=712)
    meaning = fields.CharField(max_length=256)
    term_definition = fields.ForeignKeyField(
        'models.TermDefinition',
        on_delete=fields.CASCADE,
    )

    class Meta:
        unique_together = (('language', 'term_definition'),)


class TermPronunciation(models.Model):
    phonetic = fields.CharField(max_length=256)
    audio_url = fields.CharField(max_length=256, null=True)
    term = fields.OneToOneField(
        'models.Term',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_example = fields.OneToOneField(
        'models.TermExample',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_lexical = fields.OneToOneField(
        'models.TermLexical',
        on_delete=fields.CASCADE,
        null=True,
    )


class TermExampleLink(models.Model):
    highlight = ArrayField(element_type='int[]')
    term_example = fields.ForeignKeyField(
        'models.TermExample',
        on_delete=fields.CASCADE,
    )
    term = fields.ForeignKeyField(
        'models.Term',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_definition = fields.ForeignKeyField(
        'models.TermDefinition',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_lexical = fields.ForeignKeyField(
        'models.TermLexical',
        on_delete=fields.CASCADE,
        null=True,
    )

    class Meta:
        unique_together = [
            ['term', 'term_example'],
            ['term_definition', 'term_example'],
            ['term_lexical', 'term_example'],
        ]
