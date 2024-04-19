from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from wtforms.widgets import TextArea


class LogInForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    register = SubmitField("Register")
    login = SubmitField("Login")


class SignUpForm(FlaskForm):
    first_name = StringField("Enter First Name", validators=[DataRequired()])
    last_name = StringField("Enter Last Name", validators=[DataRequired()])
    username = StringField("Enter User Name", validators=[DataRequired()])
    psw1 = PasswordField("Enter password", validators=[DataRequired()])
    psw2 = PasswordField("Confirm password", validators=[DataRequired()])

    cancel = SubmitField("Cancel")
    register = SubmitField("Register")


class SubmitRatingForm(FlaskForm):

    comment = StringField("Comment", widget=TextArea())
    rating = HiddenField("Rating", default=0)
    submit = SubmitField("Rate This Item")
    itemID = HiddenField("itemID")
    item_name = HiddenField("item_name")
    winnerID = HiddenField("winnerID")
    form_name = HiddenField("form_name", default=__qualname__)


class ListItemForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    category = SelectField(
        "Category",
        coerce=str,
        choices=[("Category 1"), ("Category 2")],
        validators=[DataRequired()],
    )
    condition = SelectField(
        "Condition",
        coerce=str,
        choices=[
            ("New"),
            ("Very Good"),
            ("Good"),
            ("Fair"),
            ("Poor"),
        ],
        validators=[DataRequired()],
    )

    returnable = BooleanField("Returnable")
    starting_bid = DecimalField(
        "Starting Bid", validators=[DataRequired(), NumberRange(min=0)]
    )
    min_sale_price = DecimalField(
        "Minimum Sale Price", validators=[DataRequired(), NumberRange(min=0)]
    )

    get_it_now_price = DecimalField(
        "Get It Now Price (Optional)", validators=[Optional()]
    )

    auction_end_time = SelectField(
        "Auction Ends In",
        choices=[
            ("1", "1 day"),
            ("3", "3 days"),
            ("5", "5 days"),
            ("7", "7 days"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")
    cancel = SubmitField("Cancel")

    def __init__(self, categories, *args, **kwargs):
        super(ListItemForm, self).__init__(*args, **kwargs)
        self.category.choices = categories
