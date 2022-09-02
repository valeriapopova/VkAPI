from wtforms import Form, StringField, IntegerField


class VKForm(Form):
    token = StringField('token')
    age_from = IntegerField('age_from')
    age_to = IntegerField('age_to')
    sex = StringField('sex, 1 — женщина, 2 — мужчина, 0 — любой')
    city = StringField('city')
    count = IntegerField('count')
