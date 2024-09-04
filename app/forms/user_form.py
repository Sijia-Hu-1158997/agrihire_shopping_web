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

class UpdateUserInfoForm(Form):
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[Optional()]
    )
    password = PasswordField("Password", validators=[Optional(), Length(min=1)])
    role = SelectField(
        "Role",
        choices=[
            ("customer", "customer"),
            ("staff", "staff"),
            ("local_manager", "local_manager"),
            ("national_manager", "national_manager"),
            ("admin", "admin"),
        ],
        validators=[Optional()],
    )
    title = SelectField(
        "Title",
        choices=[("Mr", "Mr"), ("Ms", "Ms"), ("Mrs", "Mrs"), ("", "")],
        validators=[Optional()],
    )
    first_name = StringField("First Name", validators=[Optional(), Length(max=255)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional()])
    profile_image = TextAreaField("Profile Image", validators=[Optional()])
    is_deleted = BooleanField("Is Deleted", validators=[Optional()])
    created_at = DateField("Created At", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    updated_at = DateField("Updated At", format="%Y-%m-%dT%H:%M", validators=[Optional()])

    onboarding = IntegerField("Onboarding", validators=[Optional()])

    # Check if the username already exists
    def validate_username(form, field):
        me = session.get("me") or {}
        userModel = UserModel()
        user = userModel.get_user_by_field(
            field_name="username", field_value=field.data
        )
        # For update only
        if user and user.get("id") != me.get('id'):
            raise ValidationError("Username already exists.")

    def validate_date_of_birth(form, field):
        date_of_birth = field.data
        min_birth_date = (datetime.now() - timedelta(days=18*365)).date()
        if date_of_birth.year < 1900:
            raise ValidationError("Invalid date of birth.")
        if date_of_birth > min_birth_date:
            raise ValidationError("You must be at least 18 years old to register.")


class RegisterForm(Form):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=50)]
    )
    email = StringField("Email", validators=[DataRequired()])
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[DataRequired()]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])

     # Check if the username already exists
    def validate_username(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="username", field_value=field.data):
            raise ValidationError("Username already exists.")

    def validate_email(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="email", field_value=field.data):
            raise ValidationError("Email already exists.")

    def validate_password(form, field):
        password = field.data
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")
        
    def validate_date_of_birth(form, field):
        date_of_birth = field.data
        min_birth_date = (datetime.now() - timedelta(days=18*365)).date()
        if date_of_birth.year < 1900:
            raise ValidationError("Invalid date of birth.")
        if date_of_birth > min_birth_date:
            raise ValidationError("You must be at least 18 years old to register.")

class AdminRegisterForm(Form):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=50)]
    )
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[DataRequired()]
    )
    role = SelectField(
        "Role",
        choices=[
            ("customer", "Customer"),
            ("staff", "Staff"),
            ("local_manager", "Local Manager"),
            ("national_manager", "National Manager"),
            ("admin", "Admin"),
        ],
        validators=[Optional()],
    )
    title = SelectField(
        "Title",
        choices=[("Mr", "Mr"), ("Ms", "Ms"), ("Mrs", "Mrs"), ("", "")],
        validators=[Optional()],
    )
    first_name = StringField("First Name", validators=[Optional(), Length(max=255)])
    last_name = StringField("Last Name", validators=[Optional(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional()])

    # Check if the username already exists
    def validate_username(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="username", field_value=field.data):
            raise ValidationError("Username already exists.")

    def validate_email(form, field):
        userModel = UserModel()
        if userModel.get_user_by_field(field_name="email", field_value=field.data):
            raise ValidationError("Email already exists.")

    def validate_password(form, field):
        password = field.data
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")
        
    def validate_date_of_birth(form, field):
        date_of_birth = field.data
        min_birth_date = (datetime.now() - timedelta(days=18*365)).date()
        if date_of_birth.year < 1900:
            raise ValidationError("Invalid date of birth.")
        if date_of_birth > min_birth_date:
            raise ValidationError("You must be at least 18 years old to register.")


class UpdatePasswordForm(Form):
    password = PasswordField("Old Password", validators=[DataRequired(),
                                                         Length(min=8, message="Password must be at least 8 characters long.")])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long.")
           
        ]
    )
    confirm_password = PasswordField(
        "Confirm_Password", 
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")]
    )

    def validate_password(form, field):
        password = field.data
        if not re.search(r"[A-Za-z]", password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit.")
     

class SignInForm(Form):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    