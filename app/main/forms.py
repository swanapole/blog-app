from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,SelectField
from wtforms.validators import Required, Email, Length

class PitchForm(FlaskForm):
    title = StringField('Title', validators = [Required()])
    text = TextAreaField('Pitch',validators = [Required()])
    category = SelectField('Category', choices = [('cuisine', 'Cuisine'),('voyage','Voyage'), ('health','Health'),('empower','Empowerment')], validators = [Required()])
    submit = SubmitField('Post')

class UpdateProfile(FlaskForm):
    bio = TextAreaField('Update Bio', validators = [Required()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    name = StringField('Your name', validators = [Required(), Length(min = 3, max = 20)])
    text = TextAreaField('Leave a Comment',validators = [Required()])
    submit = SubmitField('Add Comment')

class SubscriberForm(FlaskForm):
    name  = StringField('Your name', validators = [Required()])
    email = StringField('Your email address', validators = [Required(), Email()])
    submit = SubmitField('Subscribe')
