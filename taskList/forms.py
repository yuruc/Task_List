from django import forms
from django.contrib.auth.models import User
from .models import *
from datetime import *
import re

class TaskForm(forms.ModelForm):
    option_users = []
    option_manager = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['assigned_users'].queryset = Manage.objects.all()

        
        self.option_users = [(self.user.id, self.user)]
        self.option_manager = [(self.user.id, self.user)]

        for e in Manage.objects.filter(user=self.user):
            for each_user in e.manage_employee.all():
                self.option_users.append((each_user.id, each_user))

        self.fields['assigned_users'] = forms.MultipleChoiceField(choices=self.option_users)
        self.fields['manager'] = forms.ChoiceField(choices=self.option_manager)


    YEARLY = 'YEAR'
    MONTHLY = 'MONT'
    WEEKLY = 'WEEK'
    DAILY = 'DAIL'
    NONE = 'NONE'


    RECURRING_CHOICES = (
        (NONE, 'no repeat'),
        (YEARLY, 'every year'), 
        (MONTHLY, 'every month'),  
        (WEEKLY, 'every week'), 
        (DAILY, 'every day'),
    )

    HIGH = 'HIG'
    MED = 'MED'
    LOW = 'LOW'

    PRIORITY_CHOICES = (
        (HIGH, 'high'),
        (MED, 'medium'), 
        (LOW, 'low')

    )

    task_name = forms.CharField(max_length = 160, widget = forms.TextInput())
    note = forms.CharField(max_length = 200, widget = forms.Textarea())
    feedback = forms.CharField(max_length = 200, widget = forms.Textarea())
    recurring = forms.BooleanField(required=False, initial=False)
    event_start_date = forms.DateField(widget = forms.SelectDateWidget())
    event_due_date  = forms.DateField(widget = forms.SelectDateWidget())
    event_start_time = forms.TimeField(required=False, initial=time().min)
    event_end_time = forms.TimeField(required=False, initial=time().max)
    repeats = forms.ChoiceField(widget=forms.Select, choices=RECURRING_CHOICES)
    repeat_start_date = forms.DateField(widget = forms.SelectDateWidget(), required=False)
    repeat_end_date = forms.DateField(widget = forms.SelectDateWidget(), required=False)


    priority = forms.ChoiceField(widget=forms.Select, choices=PRIORITY_CHOICES)

    NEW = 'NEW'
    IN_PROGRESS = 'INP'
    COMPLETED = 'COM'
    ON_HOLD = 'ONH'
    CANCELLED = 'CAN'
    STATUS_CHOICES = (
        (NEW, 'New'), 
        (IN_PROGRESS, 'In Progress'), 
        (COMPLETED, 'Completed'), 
        (ON_HOLD, 'On Hold'), 
        (CANCELLED, 'Cancelled'),
    ) 
    status = forms.ChoiceField(widget=forms.Select, choices=STATUS_CHOICES)
    class Meta:
        model = Task
        fields = ('task_name', 'assigned_users', 'note', 'feedback', 'recurring', 
        'event_start_date', 'event_due_date', 'event_start_time', 'event_end_time', 'repeats', 'repeat_start_date','repeat_end_date' , 'priority', 'status', 'manager' )
        exclude = ('rank', 'is_active', 'recurr_task')
    
    def clean(self):
        cleaned_data = super(TaskForm, self).clean()
        print(self.cleaned_data)
        return cleaned_data
    
    def clean_event_due_date(self): 
        #django cleans the data one by one so can only check the value by check event_due_date
        #because until then the event_start_date is avaliable 
        event_start_date = self.cleaned_data.get('event_start_date')
        event_due_date = self.cleaned_data.get('event_due_date')
        if not(event_start_date <= event_due_date):
            raise forms.ValidationError("event start date can't be later then event due date")
        return event_due_date

    def clean_event_end_time(self):
        event_start_date = self.cleaned_data.get('event_start_date')
        event_due_date = self.cleaned_data.get('event_due_date')
        event_start_time = self.cleaned_data.get('event_start_time')
        event_end_time = self.cleaned_data.get('event_end_time')
        if (event_start_date == event_due_date) and (event_start_time > event_end_time):
            raise forms.ValidationError("event start time can't be later then event end time")
        return event_end_time

    def clean_repeat_end_date(self):
        recurring = self.cleaned_data.get('recurring')
        repeats = self.cleaned_data.get('repeats')
        repeat_start_date = self.cleaned_data.get('repeat_start_date')
        repeat_end_date = self.cleaned_data.get('repeat_end_date')
        if recurring and repeats == 'NONE':
            raise forms.ValidationError("need to assign repeat pattern for recurring tasks")
        if repeats != 'NONE' and not(repeat_start_date or repeat_end_date):
            raise forms.ValidationError("need to assign repeat start and end date for recurring tasks")
        if not(repeat_start_date <= repeat_end_date):
            raise forms.ValidationError("repeat start date can't be later then repeat due date")
        return repeat_end_date

    



class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('text', )
        exclude = ('task_id', 'auther', 'datetime', )
    
    def clean(self):
        print("clean")
        cleaned_data = super(NoteForm, self).clean()
        print(cleaned_data)
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) > 500:
            raise forms.ValidationError("Maximum length: 500 charaters.")
        if len(text) <= 0:
            raise forms.ValidationError("Minimum length: 1 charaters.")
        return text
    

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('text', )
        exclude = ('task_id', 'auther', 'datetime')
    
    def clean(self):
        cleaned_data = super(FeedbackForm, self).clean()
    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) > 500:
            raise forms.ValidationError("Maximum length: 500 charaters.")
        if len(text) <= 0:
            raise forms.ValidationError("Minimum length: 1 charaters.")
        return text
    


class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    username   = forms.CharField(max_length = 20)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        print(cleaned_data)

        # confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    
    # customizes form validation for the username field.
    def clean_username(self):
        # confirm that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        print(username)
        if re.match('\w+' , username) == None:
            raise forms.ValidationError("Username must be the combination of charaters and numbers")
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # return the cleaned data we got from the cleaned_data
        # dictionary
        return username
    


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('department', 'title')
        exclude = (
            'user'
            'creation_time',
            'update_time',
        )

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        print(cleaned_data)
        return cleaned_data
    def clean_department(self):
        department_choice = set(['IT', 'RD', 'MR', 'HR', 'AF'])
        department = self.cleaned_data.get('department')
        if department not in department_choice:
            raise forms.ValidationError("please choose valid departments")
        return department      
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) > 160:
            raise forms.ValidationError("Maximum length: 160 charaters.")
        return title

class EditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')


