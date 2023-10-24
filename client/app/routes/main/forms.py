from flask_wtf import FlaskForm
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import (
    StringField,
    HiddenField,
    SubmitField,
    TextAreaField,
    FileField,
    SelectMultipleField,
    BooleanField,
    SelectField,
    RadioField,
)
from wtforms.validators import DataRequired, Length

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
