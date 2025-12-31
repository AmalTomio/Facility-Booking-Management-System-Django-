from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, TextAreaField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, EqualTo, Length, InputRequired
from datetime import datetime, date
from wtforms import HiddenField


class LoginForm(FlaskForm):
    """Login form"""
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={
            "id": "login-email",
            "placeholder": "you@example.com"
        }
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "id": "login-password",
            "placeholder": "Enter your password"
        }
    )

    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={
            "id": "register-name",
            "placeholder": "John Doe"
        }
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "id": "register-email",
            "placeholder": "you@example.com"
        }
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)],
        render_kw={
            "id": "register-password",
            "placeholder": "At least 6 characters"
        }
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
        render_kw={
            "id": "register-confirm-password",
            "placeholder": "Confirm your password"
        }
    )

    role = SelectField(
        'Register As',
        choices=[
            ('staff', 'Staff'),
            ('admin', 'Admin')
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField('Register')

    
class FacilityForm(FlaskForm):
    """Facility add/edit form"""
    facility_id = HiddenField() 
    
    name = StringField('Facility Name', 
                      validators=[DataRequired(), Length(min=3, max=100)],
                      render_kw={"placeholder": "e.g., Conference Room A"})
    
    capacity = IntegerField('Capacity', 
                           validators=[DataRequired(), NumberRange(min=1, max=1000)],
                           render_kw={"placeholder": "Number of people"})
    
    description = TextAreaField('Description', 
                               validators=[Length(max=500)],
                               render_kw={"placeholder": "Brief description of the facility", "rows": 3})
    
    status = SelectField('Status', 
                        choices=[('active', 'Active'), ('inactive', 'Inactive')],
                        validators=[DataRequired()])


class BookingForm(FlaskForm):
    """Booking request form"""
    facility_id = HiddenField(validators=[InputRequired()])
    
    booking_date = DateField('Booking Date', 
                            validators=[DataRequired()],
                            format='%Y-%m-%d')
    
    start_time = TimeField('Start Time', 
                          validators=[DataRequired()],
                          format='%H:%M')
    
    end_time = TimeField('End Time', 
                        validators=[DataRequired()],
                        format='%H:%M')
    
    purpose = TextAreaField('Purpose', 
                           validators=[Length(max=500)],
                           render_kw={"placeholder": "Brief description of the meeting purpose", "rows": 3})
    
    def validate_booking_date(self, field):
        """Validate that booking date is not in the past"""
        if field.data < date.today():
            raise ValidationError('Cannot book for past dates')
    
    def validate_end_time(self, field):
        """Validate that end time is after start time"""
        if self.start_time.data and field.data:
            if field.data <= self.start_time.data:
                raise ValidationError('End time must be after start time')
            
            # Check if duration is reasonable (e.g., max 8 hours)
            start_datetime = datetime.combine(date.today(), self.start_time.data)
            end_datetime = datetime.combine(date.today(), field.data)
            duration_hours = (end_datetime - start_datetime).total_seconds() / 3600
            
            if duration_hours > 8:
                raise ValidationError('Maximum booking duration is 8 hours')
            
            if duration_hours < 0.5:
                raise ValidationError('Minimum booking duration is 30 minutes')