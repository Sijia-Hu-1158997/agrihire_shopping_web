import re
import datetime
from datetime import datetime, timezone, date, timedelta
from flask import session
from wtforms import (
    Form,
    IntegerField,
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    TextAreaField,
    DateField,
)
from wtforms.validators import (
    Length,
    Optional,
    DataRequired,
    EqualTo,
    ValidationError,
)
from app.models.user import UserModel


class ContactForm(Form):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=255)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=255)])
    email = StringField("Email", validators=[DataRequired(), Length(max=255)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=20)])
    enquiry_type = SelectField(
        "Enquiry Type",
        choices=[
            ("general", "General"),
            ("booking", "Booking"),
            ("item_issues", "Issues"),
            ("resource", "Resource"),
        ],
        validators=[DataRequired()],
    )
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])
