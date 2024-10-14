from tortoise import fields, models


class Exercise(models.Model):
    language = fields.CharField(max_length=7)
    type = fields.SmallIntField()
    level = fields.CharField(max_length=2, null=True)
    term = fields.ForeignKeyField(
        'models.Term',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_example = fields.ForeignKeyField(
        'models.TermExample',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_pronunciation = fields.ForeignKeyField(
        'models.TermPronunciation',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_lexical = fields.ForeignKeyField(
        'models.TermLexical',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_definition = fields.ForeignKeyField(
        'models.TermDefinition',
        on_delete=fields.CASCADE,
        null=True,
    )
    term_image = fields.ForeignKeyField(
        'models.TermImage',
        on_delete=fields.CASCADE,
        null=True,
    )
    additional_content = fields.JSONField(null=True)


class ExerciseHistory(models.Model):
    exercise = fields.ForeignKeyField('models.Exercise', on_delete=fields.NO_ACTION)
    user = fields.ForeignKeyField('models.User', on_delete=fields.NO_ACTION)
    created_at = fields.DatetimeField(auto_now_add=True)
    correct = fields.BooleanField()
    response = fields.JSONField(null=True)
    request = fields.JSONField(null=True)
