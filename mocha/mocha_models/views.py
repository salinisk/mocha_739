from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from mocha_models.models import *
from mocha_models.forms import *
from django.views.generic.edit import FormView
from django.db import connections, transaction
from django.http import Http404
from django.db import connection

def loginview(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)

def auth_and_login(request, onsuccess='/', onfail='/login/'):
    user = authenticate(username=request.POST['email'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return redirect(onsuccess)
    else:
        return redirect(onfail)  

def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    return user

def user_exists(username):
    user_count = User.objects.filter(username=username).count()
    if user_count == 0:
        return False
    return True

def sign_up_in(request):
    post = request.POST
    if not user_exists(post['email']): 
        user = create_user(username=post['email'], email=post['email'], password=post['password'])
    	return auth_and_login(request)
    else:
    	return redirect("/login/")

#def tabs(request):
#     return render_to_response('index.html')

@login_required(login_url='/login/')
def create_topic(request):
    if request.method == 'POST': # If the form has been submitted...
        form = TopicContentForm(request.POST) # A form bound to the POST data
	obj = form.save(commit=False)
	obj.userid = request.user
	obj.save()
	return redirect("/home/")
    else:
        form = TopicContentForm() # An unbound form
	return render(request, 'createTopic.html', {'form': form,})

@login_required(login_url='/login/')
def subscribe_topic(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UserTopicForm(request.POST) # A form bound to the POST data
	obj = form.save(commit=False)
	obj.userid = request.user
	obj.save()
	return redirect("/home/")
    else:
        form = UserTopicForm() # An unbound form
	return render(request, 'subscribeTopic.html', {'form': form,})

    
#@login_required(login_url='/login/')
#def secured(request):
#    return render_to_response("display.html")


DBNAME = 'default'
#allll results of a SQL as a list of dicts
def dbfetchall(sql, params=[]):
    #"Returns all rows from SQL query as a dict"
    global DBNAME
    cur = connections[DBNAME].cursor()
    cur.execute(sql, params)
    desc = cur.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cur.fetchall()
    ]

def dbfetchcontent(topic):
   rows = dbfetchall('select content from topic_content where topic = \'' + str(topic) + '\' ORDER BY timestamp') 
   return [c['content'] for c in rows] 


def dbfetchtopics(username):
   rows = dbfetchall('select topic from user_topic where userid = \'' + str(username) + '\' ORDER BY timestamp') 
   return [c['topic'] for c in rows] 


@login_required(login_url='/login/')
def render_topics(request):
   username = request.user
   topics = dbfetchtopics(username)
   print topics
   return render(request, 'display.html', { 'topics' : topics })


@login_required(login_url='/login/')
def render_content(request, topic):
   content = dbfetchcontent(topic)
   return render(request, 'displayContent.html', { 'topic' : topic , 'content' : content })



