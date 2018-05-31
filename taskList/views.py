from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.contrib.auth.tokens import default_token_generator

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Imports the class for our database
from taskList.models import *
from taskList.forms import *

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

from datetime import timedelta 

from django.core.exceptions import ObjectDoesNotExist

from dateutil.relativedelta import relativedelta
#deal with add month and year 

from django.db.models import Q
#deal with complicated queries 

import math 



@transaction.atomic
def register(request):
    '''Register new users'''

    context = {}

    # display the registration form if this is a GET request
    if request.method == 'GET':
        context['userform'] = UserForm()
        context['regform'] = RegistrationForm()
        return render(request, 'taskList/register.html', context)

    # creates a bound form from the request POST parameters and makes the form available in the request context dictionary
    userform = UserForm(request.POST)
    regform = RegistrationForm(request.POST)
    context['userform'] = userform
    context['regform'] = regform

    # validates the form
    if not userform.is_valid() or not regform.is_valid():
        return render(request, 'taskList/register.html', context)

    # the form data is valid, so register and login the user
    new_user = User.objects.create_user(username=userform.cleaned_data['username'], 
                                        password=userform.cleaned_data['password1'],
                                        email=userform.cleaned_data['email'],
                                        first_name=userform.cleaned_data['first_name'],
                                        last_name=userform.cleaned_data['last_name'])
    new_user.save()
    new_userprofile = UserProfile(user = new_user, 
                                department=regform.cleaned_data['department'],
                                title=regform.cleaned_data['title'], 
                                creation_time=datetime.now(),
                                update_time=datetime.now())
    new_userprofile.save()


    #login the new user and redirects to his/her tasklist
    new_user = authenticate(username=userform.cleaned_data['username'],
                            password=userform.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('home'))


@login_required
@transaction.atomic
def add_task(request):
    '''
    get task form to add new task and save form data

    '''
    context = {}

    if request.method == "GET":
        context['new_task'] = TaskForm(user = request.user)
        return render(request, 'taskList/index.html', context)


    new_task = TaskForm(request.POST, user = request.user)

    context['new_task'] = new_task

    if not new_task.is_valid():
        errors.append(new_task.errors)
        context['errors'] = errors
        return render(request, 'taskList/index.html', context) 

    time_diff = new_task.cleaned_data['event_due_date'] -  new_task.cleaned_data['event_start_date'] 
    alter_task = new_task.save(commit=False)
    alter_task.rank = time_diff.total_seconds()
    alter_task.is_active = True

    #check if it is a recurring task 
    if new_task.cleaned_data['recurring'] == True:
        #create a recurring task object
        new_recurr = RecurringTask(recurr_task_name=new_task.cleaned_data['task_name'], 
            recurr_last_date = new_task.cleaned_data['event_start_date'], 
            due_date = new_task.cleaned_data['repeat_end_date'], 
            nums_curr_task = 1 , 
            recurring_pattern = new_task.cleaned_data['repeats'])
        new_recurr.save()
        #create new task if it's needed to be create 
        handle_recurr_tasks(new_recurr, datetime.now(), new_task)
        alter_task.recurr_task = new_recurr

    alter_task.save()
    new_task.save_m2m()

    return redirect(reverse('home'))



def cal_rank(each_duration, priority):
    '''
    calculate rank value 
    '''
    priority_value = 0
    if priority == 'HIG':
        priority_value = 0.3
    elif priority == 'MED':
        priority_value = 0.2
    else:
        priority_value = 0.1
    return each_duration.total_seconds()*priority_value


@transaction.atomic
def create_tasks(new_task, duration, add_time, recurring_task, rank_value):
    '''
    create a new task from the recurring task 

    '''
    new_recurr_task = Task(task_name=new_task.cleaned_data['task_name'],
    note=new_task.cleaned_data['note'], 
    feedback=new_task.cleaned_data['feedback'], 
    recurring=new_task.cleaned_data['recurring'], 
    recurr_task=recurring_task, 
    repeats=new_task.cleaned_data['repeats'], 
    event_start_date=recurring_task.recurr_last_date + add_time, 
    event_due_date= recurring_task.recurr_last_date + add_time + duration, 
    event_start_time=new_task.cleaned_data['event_start_time'],
    event_end_time=new_task.cleaned_data['event_end_time'],
    repeat_start_date=new_task.cleaned_data['repeat_start_date'],
    repeat_end_date=new_task.cleaned_data['repeat_end_date'],
    priority=new_task.cleaned_data['priority'], 
    status=new_task.cleaned_data['status'],
    rank=rank_value, 
    is_active=True)
    new_recurr_task.save()
    new_recurr_task.assigned_users.set(new_task.cleaned_data['assigned_users'])
    new_recurr_task.manager.set(new_task.cleaned_data['manager'])


def cal_time_pattern(recurring_pattern):
    '''
    calculate the timedelta()/relativedelta() object for each recurring pattern

    '''

    if recurring_pattern == 'YEAR':
        add_time = relativedelta(years=+1)
    elif recurring_pattern == 'MONT':
        add_time = relativedelta(months=+1)
    elif recurring_pattern == 'WEEK':
        add_time = timedelta(weeks=1)
    elif recurring_pattern == 'DAIL':
        add_time = timedelta(days=1)
    else:
        add_time = timedelta()
    return add_time


@transaction.atomic
def handle_recurr_tasks(recurring_task, curr_time, new_task=None):
    #curr_time is not used here, but it could be used to see if we need to 
    #create more tasks too 
    '''
    create recurring new tasks when a new task is added / updated (if new_task != None). 
    check and create new tasks for a recurring tasks if the due date is None (if new_task == None)
    '''

    n_task_for_no_due_task = 30 #number of tasks we want to have for a without due recurring task

    #check if it's an active recurring task 
    if not recurring_task.is_active:
        return False 

    add_time  = cal_time_pattern(recurring_task.recurring_pattern)

    #calculate for info to be added into the tasks
    duration = new_task.cleaned_data['event_due_date'] -  new_task.cleaned_data['event_start_date']
    rank_value = cal_rank(duration, new_task.cleaned_data['priority'])

    #check if there is a due date
    if recurring_task.due_date != None:
        #if so, create all the recurring tasks
        while recurring_task.recurr_last_date < recurring_task.due_date:
            create_tasks(new_task, duration, add_time, recurring_task, rank_value)
            recurring_task.recurr_last_date += add_time
            recurring_task.save()

    #if not, create some tasks until n tasks exist:
    else:
        for i in range(recurring_task.nums_curr_task, n_task_for_no_due_task):
            create_tasks(new_task, duration, add_time, recurring_task, rank_value)
            recurring_task.recurr_last_date += add_time
            recurring_task.nums_curr_task += 1
            recurring_task.save()

def values_stay_the_same(task, data):
    '''
    check if all the old data is the same as the form data 

    '''

    return data['task_name'] == task.task_name and data['assigned_users'] == task.assigned_users and data['manager'] == task.manager and data['note'] == task.note and data['feedback'] == task.feedback and data['recurring'] == task.recurring and data['event_start_date'] == task.event_start_date and data['event_due_date'] == task.event_due_date and data['event_start_time'] == task.event_start_time and data['event_end_time'] == task.event_end_time and data['repeats'] == task.repeats and data['repeat_start_date'] == task.repeat_start_date and data['repeat_end_date'] == task.repeat_end_date and data['priority'] == task.priority and data['status'] == task.status


@login_required
@transaction.atomic
def edit_tasks(request, task):
    '''
    edit single task when user only want to update info of the one task 

    '''
    #TODO: time update
    errors = []
    target_task = Task.objects.select_for_update().filter(        
                Q(assigned_users__username=request.user) |
                Q(manager__username=request.user), id=task).first()

    if target_task == None:
        errors.append("you aren't authorized to edit the task")
        return {'errors': errors}

    task_form = TaskForm(request.POST, instance=target_task, user=request.user)


    if not task_form.is_valid():
        errors.append(task_form.errors)
        context =  {'errors': errors, 'tasks': target_task, 'task_form':task_form}
        return context

    #if the values aren't changed
    if values_stay_the_same(target_task, task_form.cleaned_data):
       context =  {'errors': errors, 'tasks': target_task, 'task_form':task_form} 
       return context


    #if any part of the task changed and if it was a recurring task 
    #then it won't be recurring task anymore 
    if target_task.recurring:
        target_task.recurring = False
        target_task.recurr_task = None
        target_task.save()
    #if the task wasn't recurring but it is set to be recurring task now
    elif task_form.cleaned_data['recurring'] and not target_task.recurring:
        new_recurr = RecurringTask(recurr_task_name=task_form.cleaned_data['task_name'], 
            recurr_last_date = task_form.cleaned_data['event_start_date'], 
            due_date = task_form.cleaned_data['repeat_end_date'], 
            nums_curr_task = 1 , 
            recurring_pattern = task_form.cleaned_data['repeats'])
        new_recurr.save()
        handle_recurr_tasks(new_recurr, datetime.now(), task_form)
        #will create all recurr task after/except the current one

    target_task.save()
    task_form.save()


    
    #recalculate rank and duration 
    duration = target_task.event_due_date -  target_task.event_start_date
    rank_value = cal_rank(duration, target_task.priority)
    target_task.rank = rank_value
    target_task.save()

    context = {'message': 'Task updated', 'tasks': target_task, 
    'task_form': task_form}
    return context

@login_required
@transaction.atomic
def edit_recurr_tasks(request, task):
    '''
    edit all task when user want to update info of all the tasks 

    '''
    errors = []
    target_task = Task.objects.select_for_update().filter(        
                Q(assigned_users__username=request.user) |
                Q(manager__username=request.user), id=task).first()

    if target_task == None:
        errors.append("you aren't authorized to edit the task")
        return {'errors': errors}

    all_tasks = Task.objects.select_for_update().select_for_update().filter(
                Q(assigned_users__username=request.user) |
                Q(manager__username=request.user), 
                recurr_task=target_task.recurr_task)
    
    event_start = target_task.event_start_date
    event_end = target_task.event_due_date

    task_form = TaskForm(request.POST, instance=target_task, user=request.user)

    if not task_form.is_valid():
        errors.append(task_form.errors)
        context =  {'errors': errors, 'tasks': target_task, 'task_form':task_form}
        return context
    
    task_form.save()
    target_task.save()
        
    if len(all_tasks) == 0:
        errors.append("you aren't authorized to edit the recurring task")
        return {'errors': errors}

    #There are 3 kinds possiblity to change all the task:

    #1. change to non-recurring task, which means all the other recurring tasks should be deleted 
    if target_task.repeats == False:
        target_task.recurr_task.set(None)
        delete_recurr_tasks(request, task=task)

    #2. change the recurring pattern(end date due date etc), which may change the number of recurring tasks.
    #here I delete all the other recurring tasks (only the current one will have same task id & notes & feedacks), 
    #and create new tasks since it's hard to say which one matches which one if the number of recurring tasks is changed 
    elif target_task.repeat_start_date != all_tasks[0].repeat_start_date or target_task.repeat_end_date != all_tasks[0].repeat_start_date or target_task.event_start_date != event_start or target_task.event_due_date != event_end:

        new_recurr = RecurringTask(recurr_task_name=task_form.cleaned_data['task_name'], 
            recurr_last_date = task_form.cleaned_data['event_start_date'], 
            due_date = task_form.cleaned_data['repeat_end_date'], 
            nums_curr_task = 1, 
            recurring_pattern = task_form.cleaned_data['repeats'])
        new_recurr.save()
        handle_recurr_tasks(new_recurr, datetime.now(), task_form) #create new task after the current one
        to_delete_recurring_task = target_task.recurr_task
        target_task.recurr_task.set(None)
        delete_recurr_tasks(request, recurr_task=to_delete_recurring_task)

    #3. doesn't change anything related to recurring patren, so just upadte the info for all
    else:
        sample_task = target_task
        for task in all_tasks:
            task.task_name = sample_task.task_name
            task.note = sample_task.note
            task.feedback = sample_task.feedback
            task.recurring = sample_task.recurring
            task.priority = sample_task.priority
            task.status = sample_task.status
            task.event_start_time = sample_task.event_start_time
            task.event_end_time = sample_task.event_end_time
            task.manager.set(sample_task.manager)
            task.assigned_users.set(sample_task.assigned_users)

    context = {'message': 'Tasks are updated', 'tasks': target_task, 'task_form': task_form}
    return context


@login_required
@transaction.atomic
def delete_tasks(request, task):
    '''
    delete single task when user only want to delete the one task 

    '''
    errors = []
    target_task = Task.objects.select_for_update().filter(id=task).first()
    if target_task != None:
        target_task.is_active = False
        recurr_task = target_task.recurr_task
        target_task.recurr_task.nums_curr_task -= 1
        target_task.save()
        recurr_task.save()
    else:
        errors.append('Task not found.')
    context = {'message': 'Task is deleted', 'errors': errors}
    return context

@login_required
@transaction.atomic
def delete_recurr_tasks(request, task = None, recurr_task = None):
    '''
    delete all recurring task when user only want to delete a set of task of the recurring task 
    can either pass one of the set of tasks or the recurring task

    '''
    all_tasks = []

    if task != None and recurr_task == None:
        target_task = Task.objects.select_for_update().filter(id=task).first()
        if target_task != None:
            recurr_task = target_task.recurr_task

    if recurr_task != None:
        all_tasks = Task.objects.select_for_update().filter( 
            Q(assigned_users__username=request.user) | Q(manager__username=request.user), 
            recurr_task=recurr_task)
        recurr_task.is_active = False
        recurr_task.nums_curr_task = 0
        recurr_task.save()
    else:
        context = {'message': 'Task not found'}
        return context


    for task in all_tasks:
        task.is_active = False
        task.save()

    context = {'message': 'All tasks are deleted'}

    return context


@login_required
@transaction.atomic
def add_notes(request, task):
    '''
    add notes for individual task

    '''
    append_task = Task.objects.filter(id=task).first()
    if append_task != None:
        new_note = Note(auther=request.user, datetime=datetime.now(), task_id = append_task)
        note_form = NoteForm(request.POST, instance=new_note)
        if not note_form.is_valid():
            return note_form.errors
        note_form.save()


@login_required
@transaction.atomic
def add_feedback(request, task):
    '''
    add feedback for individual task

    '''
    append_task = Task.objects.filter(id=task).first()
    if append_task != None:
        new_feedback = Feedback(auther=request.user, datetime=datetime.now(), task_id = append_task)
        feedback_form = FeedbackForm(request.POST, instance=new_feedback)
        if not feedback_form.is_valid():
            return feedback_form.errors
        feedback_form.save()




@login_required
def task(request, task):
    '''
    look at individual task and edit it 

    '''

    errors = []
    error = None
    context = {}

    if request.method == 'GET' or 'add_note' in request.POST or 'add_feedback' in request.POST :

        if 'add_note' in request.POST:
            error = add_notes(request, task)
        elif 'add_feedback' in request.POST:
            error = add_feedback(request, task)
        if error:
            errors.append(error)

        task_to_display = Task.objects.filter(
            Q(assigned_users__username=request.user) |
            Q(manager__username=request.user), 
            id=task, 
            is_active=True
        )

        note_to_display = Note.objects.filter(task_id = task)
        feedback_to_display = Feedback.objects.filter(task_id = task)

        if len(task_to_display) == 0:
            errors.append('The task did not exist.')
            context = {'errors': errors}    
            return render(request, 'taskList/task.html', context)

        task_form = TaskForm(instance=task_to_display[0], user = request.user)
        note_form = NoteForm()
        feedback_form = FeedbackForm()
        context = {'errors': errors, 'tasks': task_to_display, 
            'task_form':task_form, 'feedbacks': feedback_to_display, 
            'notes': note_to_display, 'note_form': note_form, 'feedback_form': feedback_form}
        
        return render(request, 'taskList/task.html', context)
    else: #post method

        if 'update_one_task' in request.POST:
            context = edit_tasks(request, task)
        elif 'update_all_task' in request.POST:
            context = edit_recurr_tasks(request, task)
        elif 'delete_one_task' in request.POST:
            context = delete_tasks(request, task)
        elif 'delete_all_task' in request.POST:
            context = delete_recurr_tasks(request, task=task)

        note_to_display = Note.objects.filter(task_id = task)
        feedback_to_display = Feedback.objects.filter(task_id = task)
        note_form = NoteForm()
        feedback_form = FeedbackForm()

        context['notes'] = note_to_display
        context['feedbacks'] = feedback_to_display
        context['note_form'] = NoteForm()
        context['feedback_form'] = FeedbackForm()



        
        return render(request, 'taskList/task.html', context)       




@login_required
def user(request, user, page=1):
    per_page_items = 10
    page = int(page)

    '''
    display each user's profile
    '''
    context = {}

    errors = []

    try: 
        user_to_display = User.objects.get(id=user)
        userprofile_to_display = UserProfile.objects.get(user__username=user_to_display.username)
        task_to_display = Task.objects.filter(
            Q(assigned_users__username=user_to_display.username) |
            Q(manager__username=user_to_display.username), 
            is_active=True).order_by('status','rank')[(page - 1)*per_page_items : page*per_page_items]
        task_count = Task.objects.filter(
            Q(assigned_users__username=user_to_display.username) |
            Q(manager__username=user_to_display.username), 
            is_active=True).count()
    except ObjectDoesNotExist:
        errors.append('The user did not exist.')
        context = {'errors': errors}    
        return render(request, 'taskList/user.html', context)


    total_page_number = math.ceil(task_count/per_page_items) + 1



    context = {'query_user': user_to_display, 'userprofile': userprofile_to_display, 'errors': errors, 'tasks': task_to_display, 
    'total_page_number':range(1, total_page_number)}

    return render(request, 'taskList/user.html', context)




@login_required
def home(request):
    '''
    display user's tasks and allow the user to create/assign new tasks to others
    '''
    context = {}
    per_cat_tasks = 5

    #to customize status' order

    NEW = 'NEW'
    IN_PROGRESS = 'INP'
    COMPLETED = 'COM'
    ON_HOLD = 'ONH'
    CANCELLED = 'CAN'

    context['tasklists'] = []
    tasks_status_order = [NEW, IN_PROGRESS, COMPLETED, ON_HOLD, CANCELLED]
    tasks_status_names_urls = [("New Tasks", "new_tasks"), ("In Progress Tasks", "in_progress_tasks") , ("Completed Tasks", "completed_tasks"), ("On Hold Tasks",  "on_hold_tasks"), ("Cancelled Tasks", "cancelled_tasks")]
    for name, url in tasks_status_names_urls:
        tasks = {'name': name, 'tasks':[], 'url':url}
        context['tasklists'].append(tasks)



    #check all the recurring task without a due date and number is too small
    #if so, create new tasks for them, pass one children task object 
    all_recurr_tasks = Task.objects.exclude(recurr_task=None).filter(Q(assigned_users__username=request.user) |
         Q(manager__username=request.user), 
            is_active=True).values_list('recurr_task', flat=True).distinct()
    if len(all_recurr_tasks) != 0:
        for recurr_task in all_recurr_tasks:
            try:
                recurr_task_obj = RecurringTask.objects.get(id=recurr_task)
                handle_recurr_tasks(recurr_task_obj, datetime.now)
            except:
                pass #put error message here, might be concurrency issue

    #in order to customize the order of status, we don't just sort 
    #by default
    order_num = 0
    for task_status in tasks_status_order:
        tasks = Task.objects.filter(
            Q(assigned_users__username=request.user) |
            Q(manager__username=request.user), 
            is_active=True, status=task_status
            ).order_by('rank')[:per_cat_tasks]
        context['tasklists'][order_num]['tasks'] = tasks
        order_num += 1

    
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        new_task = TaskForm(request.POST, user = request.user)
    else:
        new_task = TaskForm(user = request.user)

    context['new_task'] = new_task
    context['user'] = user 

    return render(request, 'taskList/index.html', context)

@login_required
def task_cat(request, task_cat, page=1):
    per_page_items = 10
    page = int(page)

    NEW = 'NEW'
    IN_PROGRESS = 'INP'
    COMPLETED = 'COM'
    ON_HOLD = 'ONH'
    CANCELLED = 'CAN'

    url_cat_mapping = { 
        'new_tasks': NEW, 'in_progress_tasks': IN_PROGRESS, 
        'completed_tasks': COMPLETED, 'on_hold_tasks':ON_HOLD, 
        'cancelled_tasks':CANCELLED 
    }

    names_urls_mapping = {'new_tasks': 'New Tasks', "in_progress_tasks":"In Progress Tasks",'completed_tasks':"Completed Tasks", "on_hold_tasks":"On Hold Tasks", "cancelled_tasks":"Cancelled Tasks"}

    if task_cat not in url_cat_mapping:
        return bad_request(request)

    context = {}

    tasks = Task.objects.filter(
            Q(assigned_users__username=request.user) |
            Q(manager__username=request.user), 
            is_active=True, status=url_cat_mapping[task_cat]
            ).order_by('rank')[(page - 1)*per_page_items : page*per_page_items]

    task_count = Task.objects.filter(
            Q(assigned_users__username=request.user) |
            Q(manager__username=request.user), 
            is_active=True, status=url_cat_mapping[task_cat]
            ).count()

    total_page_number = math.ceil(task_count/per_page_items) + 1



    context['tasks'] = tasks
    context['title'] = names_urls_mapping[task_cat]
    context['total_page_number'] = range(1, total_page_number)
    context['task_url'] = task_cat


    user = User.objects.get(username=request.user)

    if request.method == "POST":
        new_task = TaskForm(request.POST, user = request.user)
    else:
        new_task = TaskForm(user = request.user)

    context['new_task'] = new_task

    return render(request, 'taskList/task_cat.html', context)


@login_required
@transaction.atomic
def edit_user(request, user):
    '''
    edit user's profile. Users can only edit their own profiles.
    '''
    context = {}
    try:
        if request.method == 'GET':
            user = User.objects.get(username=request.user) 
            userprofile = UserProfile.objects.get(user__username=request.user)
            userprofile_form = RegistrationForm(instance=userprofile)
            user_form = EditForm(instance=user)
            context = { 'user': user, 'userprofile':userprofile, 'userprofile_form': userprofile_form, 'user_form': user_form }
            return render(request, 'taskList/edit_user.html', context)

        user = User.objects.select_for_update().get(username=request.user)
        userprofile = UserProfile.objects.select_for_update().get(user__username=request.user)
        db_update_time = userprofile.update_time  # Copy timestamp to check after form is bound
        user_form = EditForm(request.POST, instance=user)
        userprofile_form = RegistrationForm(request.POST, instance=userprofile)
        if not user_form.is_valid() or not userprofile_form.is_valid():
            context =  { 'user': user, 'userprofile':userprofile, 'userprofile_form': userprofile_form, 'user_form': user_form }
            return render(request, 'taskList/edit_user.html', context)

        # if update times do not match, someone else updated DB record while were editing
        userprofile.update_time = datetime.now()
        user_form.save()
        userprofile.save()
        userprofile_form.save()
        context = {
            'message': 'Entry updated.',
            'user': user, 'user_form': user_form , 
            'userprofile':userprofile, 'userprofile_form': userprofile_form
        }
        return render(request, 'taskList/edit_user.html', context)
    
    except:
        context = { 'user': user, 'message':"You typed in invalid value"}
        return render(request, 'taskList/edit.html', context)
    
def server_error(request):
    response = render_to_response('500.html', {} ,context_instance = RequestContext(request))
    response.status_code = 500
    return response 


def bad_request(request):
    response = render_to_response('400.html', {} ,context_instance = RequestContext(request))
    response.status_code = 400
    return response 

def permission_denied(request):
    response = render_to_response('403.html', {} ,context_instance = RequestContext(request))
    response.status_code = 403
    return response 

def page_not_found(request):
    response = render_to_response('404.html', {} ,context_instance = RequestContext(request))
    response.status_code = 404
    return response 