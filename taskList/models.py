from django.db import models
# User class for built-in authentication module
from django.contrib.auth.models import User
from datetime import time


class RecurringTask(models.Model):
    recurr_task_name = models.CharField(max_length=160)
    recurr_last_date = models.DateField(blank= True, null=True)
    #last start date of all the set of existing  tasks belongs to the recurring task 
    due_date = models.DateField()
    #the end of repeat/recurring 
    nums_curr_task = models.IntegerField(default=0)
    #the number of not yet deleted tasks that belongs to the recurring task 

    YEARLY = 'YEAR'
    MONTHLY = 'MONT'
    WEEKLY = 'WEEK'
    DAILY = 'DAIL'


    RECURRING_CHOICES = (
        (YEARLY, 'every year'), 
        (MONTHLY, 'every month'),  
        (WEEKLY, 'every week'), 
        (DAILY, 'every day'),
    )

    recurring_pattern =  models.CharField(
        max_length = 4, 
        choices= RECURRING_CHOICES, 
        blank = True, 
        )
    is_active = models.BooleanField(default=True)        
        

class Task(models.Model):
    task_name = models.CharField(max_length=160)
    assigned_users = models.ManyToManyField(User, related_name='task_taker')
    manager = models.ManyToManyField(User, related_name='task_manager', default=None)
    note = models.CharField(max_length = 200, blank=True)
    feedback = models.CharField(max_length = 200, blank=True)
    recurring = models.BooleanField(default=False)
    recurr_task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE, null=True, blank=True)


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

    event_start_date = models.DateField(blank=True)
    event_due_date  = models.DateField(blank=True)
    event_start_time = models.TimeField(blank=True, default=time().min)
    event_end_time = models.TimeField(blank=True, default=time().max)
    repeats = models.CharField(
        max_length = 4, 
        choices= RECURRING_CHOICES, 
        blank = True, 
        default = NONE, 
        )
    repeat_start_date = models.DateField(blank=True, null=True)
    repeat_end_date =  models.DateField(blank=True, null=True)
    
    HIGH = 'HIG'
    MED = 'MED'
    LOW = 'LOW'

    PRIORITY_CHOICES = (
        (HIGH, 'high'),
        (MED, 'medium'), 
        (LOW, 'low')

    )

    priority = models.CharField(
        max_length = 3, 
        choices = PRIORITY_CHOICES, 
        default = LOW, 
        )

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
    status = models.CharField(
        max_length = 3, 
        choices = STATUS_CHOICES, 
        default = NEW, 
    )

    #rank = models.DurationField(default=None, blank=True)
    rank = models.BigIntegerField(default=None, blank=True)
    is_active =  models.BooleanField(default=True)

class Note(models.Model):
    text = models.CharField(max_length=500)
    auther = models.ForeignKey(User, default=None)
    datetime = models.DateTimeField()
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_id_note')

class Feedback(models.Model):
    text = models.CharField(max_length=500)
    auther = models.ForeignKey(User, default=None)
    datetime = models.DateTimeField()
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, 
        related_name='task_id_feedback')

class Manage(models.Model):
	user = models.OneToOneField(User, related_name='manager_user')
	manage_employee = models.ManyToManyField(User, related_name='manage_employee', default = None)

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    IT = 'IT'
    RD = 'RD'
    Marketing = 'MR'
    HR = 'HR'
    Account_Finance = 'AF'


    DEPARTMENT_CHOICES = (
        (IT, 'Information Technology'), 
        (RD, 'Research and Development'),
        (Marketing, 'Marketing'),
        (HR, 'Human Resource'),
        (Account_Finance, 'Accounting and Finance'),
    )     
    department = models.CharField(
    	max_length = 2, 
    	choices = DEPARTMENT_CHOICES, 
    	default = IT, 
    )
    title = models.CharField(max_length = 160)
    creation_time = models.DateTimeField()
    update_time   = models.DateTimeField()

 