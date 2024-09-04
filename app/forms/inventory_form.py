import re
from flask import session, g

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
from app.models.inventory import InventoryModel


class AddInventoryForm(Form):
    inventory_serial_number = StringField("Inventory Serial Number", validators=[Optional()])
    date_of_purchase = DateField("Date of Purchase", format="%Y-%m-%d", validators=[Optional()])
    specifications = StringField("Specifications", validators=[Optional()])
    store_id = IntegerField("Store ID", validators=[Optional()])
    type_id = IntegerField("Type ID", validators=[Optional()])
    quantity = IntegerField("Quantity", validators=[Optional()])
    price = IntegerField("Price", validators=[Optional()])
    cost = IntegerField("Cost", validators=[Optional()])
    image = StringField("Image", validators=[Optional()])
    is_deleted = BooleanField("Is Deleted", validators=[Optional()])
    created_at = DateField("Created At", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    updated_at = DateField("Updated At", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    generated_inventory_serial_number = StringField("Generated Inventory Serial Number", validators=[Optional()])


class AddEquipmentForm(Form):
    equipment_serial_number = StringField("Equipment Serial Number", validators=[Optional()])
    type_id = IntegerField("Type ID", validators=[Optional()])
    inventory_id = IntegerField("Inventory ID", validators=[Optional()])
    details = StringField("Details", validators=[Optional()])
    store_id = IntegerField("Store ID", validators=[Optional()])
    cost = IntegerField("Cost", validators=[Optional()])
    status = SelectField("Status", choices=[
        ("active", "active"),
        ("inactive", "inactive"),
        ],
        validators=[Optional()],
    )
    shipping_price = IntegerField("Shipping Price", validators=[Optional()])
    is_deleted = BooleanField("Is Deleted", validators=[Optional()])
    created_at = DateField("Created At", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    updated_at = DateField("Updated At", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    generated_equipment_serial_number = StringField("Generated Equipment Serial Number", validators=[Optional()])
