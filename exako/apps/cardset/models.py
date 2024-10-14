from tortoise import fields, models


class CardSet(models.Model):
    user = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE)
    name = fields.CharField(max_length=256)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_review = fields.DatetimeField(auto_now=True)
    pinned = fields.BooleanField(default=False)
    language = fields.CharField(max_length=7, null=True)


class Card(models.Model):
    note = fields.TextField(null=True)
    created_at = fields.DateField(auto_now_add=True)
    last_review = fields.DateField(auto_now=True)
    cardset = fields.ForeignKeyField('models.CardSet', on_delete=fields.CASCADE)
    term = fields.ForeignKeyField('models.Term', on_delete=fields.CASCADE)
