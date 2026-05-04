from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    submit = SubmitField("Register")


class SearchForm(FlaskForm):
    query = StringField("Search", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Search")


class QuantityForm(FlaskForm):
    quantity = IntegerField(
        "Quantity",
        validators=[DataRequired(), NumberRange(min=1, max=10, message="Please select at least 1 item")],
        default=1,
    )
    size = SelectField(
        "Size",
        choices=[(s, s) for s in ["PH 5", "PH 5.5", "PH 6", "PH 6.5", "PH 7", "PH 7.5", "PH 8", "PH 8.5", "PH 9", "PH 9.5", "PH 10", "PH 10.5", "PH 11", "PH 11.5", "PH 12"]],
        validators=[DataRequired()],
    )
    submit = SubmitField("Add to Cart")


class CartUpdateForm(FlaskForm):
    quantity = IntegerField(
        "Quantity",
        validators=[DataRequired(), NumberRange(min=1, max=50, message="Quantity must be at least 1")],
    )
    update = SubmitField("Update")
    remove = SubmitField("Remove")


class CheckoutForm(FlaskForm):
    address = TextAreaField("Delivery Address", validators=[DataRequired(), Length(max=255)])
    city = StringField("City", validators=[DataRequired(), Length(max=80)])
    zip_code = StringField("ZIP Code", validators=[DataRequired(), Length(max=20)])
    submit = SubmitField("Place Order")


class AddressForm(FlaskForm):
    address = TextAreaField("Delivery Address", validators=[DataRequired(), Length(max=255)])
    city = StringField("City", validators=[DataRequired(), Length(max=80)])
    state = StringField("State", validators=[DataRequired(), Length(max=80)])
    zip_code = StringField("ZIP Code", validators=[DataRequired(), Length(max=20)])
    submit = SubmitField("Save Address")


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match")],
    )
    submit = SubmitField("Change Password")


class NotificationSettingsForm(FlaskForm):
    notify_push = BooleanField("Push Notifications")
    notify_in_app = BooleanField("In-App Notifications")
    notify_email = BooleanField("Email Notifications")
    submit = SubmitField("Save Settings")


class PrivacyForm(FlaskForm):
    invisible_on_comments = BooleanField("Invisible on comments")
    submit = SubmitField("Save Privacy")


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=140)])
    category = SelectField("Category", choices=[(c, c) for c in ["Running", "Basketball", "Training", "Football", "Lifestyle"]], validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=300)])
    submit = SubmitField("Save Product")
