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

class OOBForm(FlaskForm):
    handshake = BooleanField("Handshake", validators=[])
    # anoncreds = BooleanField("AnonCreds", validators=[])
    attachement = SelectField("Attachement", validators=[])
    submit = SubmitField("Create Invitation")

class BackchannelForm(FlaskForm):

    endpoint = StringField("Backchannel Endpoint", validators=[DataRequired()])
    submit = SubmitField("POST to Backchannel")