from flask import session
from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField, DateTimeField, TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email

from app import bcrypt
from app.models import *


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=3, max=20)])
    passport = StringField("Passport", validators=[DataRequired(), Length(min=7, max=12)])
    email = EmailField("Email", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=5, max=16)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    secret_code = PasswordField("Secret word(always remember)", validators=[DataRequired()])
    submit = SubmitField("Register", validators=[DataRequired()])

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username already registered.")

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That Email already registered.")

    def validate_phone(self, phone):
        user = Users.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError("This phone number already registered.")

    def validate_passport(self, passport):
        user = Users.query.filter_by(passport=passport.data).first()
        if user:
            raise ValidationError("This passport already registered.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login", validators=[DataRequired()])

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError("That username does not exist.")


class ChangeInfo(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=3, max=20)])
    last_name = StringField("First Name", validators=[DataRequired(), Length(min=3, max=20)])
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField("Email", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=5, max=16)])
    submit = SubmitField("Change", validators=[DataRequired()])

    def validate_username(self, username):
        user1 = Users.query.filter_by(username=username.data)
        user2 = Users.query.filter_by(id=session.get("user_id")).first()
        if len(list(user1)) == 1 and user1.first() == user2:
            raise ValidationError("That username already registered.")

    def validate_email(self, email):
        user1 = Users.query.filter_by(username=email.data)
        user2 = Users.query.filter_by(id=session.get("user_id")).first()
        if len(list(user1)) == 1 and user1.first() == user2:
            raise ValidationError("That Email already registered.")

    def validate_phone(self, phone):
        user1 = Users.query.filter_by(username=phone.data)
        user2 = Users.query.filter_by(id=session.get("user_id")).first()
        if len(list(user1)) == 1 and user1.first() == user2:
            raise ValidationError("This phone number already registered.")


class AddBalance(FlaskForm):
    balance = IntegerField("Balance", validators=[DataRequired()])
    submit = SubmitField("Add", validators=[DataRequired()])

    def validate_balance(self, balance):
        if balance.data >= 1000000:
            raise ValidationError("Too many numbers.")


class TransferMoney(FlaskForm):
    amount = IntegerField("Amount", validators=[DataRequired()])
    receiver = IntegerField("Enter wallet id", validators=[DataRequired()])
    submit = SubmitField("Transfer", validators=[DataRequired()])

    def validate_amount(self, amount):
        wallet = E_wallets.query.filter_by(user_id=session.get("user_id")).first()
        if amount.data > wallet.balance:
            raise ValidationError("You don't have enough money.")

    def validate_receiver(self, receiver):
        wallet = E_wallets.query.filter_by(id=receiver.data).first()
        if not wallet:
            raise ValidationError("This wallet does not exist.")


class ChangePassword(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    new_password = PasswordField("New password", validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Change password", validators=[DataRequired()])

    def validate_old_password(self, old_password):
        user = Users.query.filter_by(id=session.get("user_id")).first()
        equalto = bcrypt.check_password_hash(user.password, old_password.data)
        if not equalto:
            raise ValidationError("Incorrect password.")


class ForgotPassword(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    secret_word = StringField("Secret word which you entered when you were registered", validators=[DataRequired()])
    new_password = PasswordField("New password", validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Change password", validators=[DataRequired()])

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError("That username does not exist.")

    def validate_secret_word(self, secret_word):
        user = Users.query.filter_by(username=self.username.data).first()
        if not bcrypt.check_password_hash(user.secret_code, secret_word.data):
            raise ValidationError("Incorrect secret word.")


class HistoryForm(FlaskForm):
    from_date = DateField("From date", validators=[DataRequired()])
    from_time = TimeField("From time", validators=[DataRequired()])
    to_date = DateField("To date", validators=[DataRequired()])
    to_time = TimeField("To time", validators=[DataRequired()])
    submit = SubmitField("Change date", validators=[DataRequired()])

    def validate_from_date(self, from_date):
        if from_date.data >= self.to_date.data:
            raise ValidationError("From date cannot be greater than to date.")


    def validate_from_time(self, from_time):
        if from_time.data >= self.to_time.data:
            raise ValidationError("From time cannot be greater than to time.")


class DeleteForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Delete", validators=[DataRequired()])

    def validate_password(self, password):
        user = Users.query.filter_by(id=session.get("user_id")).first()
        if not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError("Incorrect password.")

