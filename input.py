from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class URLForm(FlaskForm):
    url = StringField('Youtube URL', validators=[DataRequired(), Length(min=43, max=43)])
    submit = SubmitField('Go')
