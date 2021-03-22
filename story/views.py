from django.views.decorators.http import require_http_methods
# from django.contrib.auth.decorators import method_decorator
from django.shortcuts import render
from django.http import (HttpResponse,Http404,HttpResponseBadRequest)
from .models import Author,Story
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
import json
from django.http import JsonResponse


# @require_http_methods(["POST"])
@csrf_exempt
def HandleLoginRequest(request):
  # BEGIN_LOGIN
  # """""""""""
  # BEGIN_BASIC_CHECK
  # +++++++++++++++++
  #  Wrong request method
  #  ^^^^^^^^^^^^^^^^^^^^
  if request.method!='POST':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
  #  Payload is empty
  #  ^^^^^^^^^^^^^^^^
  if not request.POST:
    return HttpResponse("EMPTY CONTENT",content_type="text/plain",status=205)
  #  Key values are not matched
  #  ^^^^^^^^^^^^^^^^^^^^^^^^^^
  if (not 'username' in request.POST) or (not 'password' in request.POST):
    NotKeyValue="Require the key [username, password]"
    return HttpResponse(NotKeyValue,content_type="text/plain",status=205)
  # +++++++++++++++
  # END_BASIC_CHECK

  # Setup
  # ^^^^^
  un=request.POST.get('username')
  pw=request.POST.get('password')
  user=authenticate(request,username=un,password=pw)
  if user is None:
    # Cannot find username
    # ^^^^^^^^^^^^^^^^^^^^
    if not User.objects.filter(username=un, is_active=True).exists():
      NotFoundAuthor=("'{username}' NOT REGISTERED").format(username=un)
      return HttpResponse(NotFoundAuthor,content_type="text/plain",status=403)
    # Wrong password with given username
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    if not User.objects.filter(username=un,password=pw).exists():
      WrongPassword=("'{password}' WRONG PASSWORD OF '{username}'").format(password=pw,username=un)
      return HttpResponse(WrongPassword,content_type="text/plain",status=403)
  else:
    # Login
    # ^^^^^
    if not user.is_active:
      DisabledAccount=("'{username}' is a disabled account").format(username=un)
      return HttpResponse(DisabledAccount,content_type="text/plain",status=403)
    else:
      login(request,user)
      if(user.is_authenticated):
        return HttpResponse("Welcome to ml17x44z site!!!",content_type="text/plain",status=200)
  # """""""""
  # END_LOGIN

@csrf_exempt
def HandleLogoutRequest(request):
  if request.method!='POST':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
  logout(request)
  if(request.user.is_authenticated==True):
    return HttpResponse("Logout Failed",content_type="text/plain",status=200)
  else:
    return HttpResponse("Bye-bye Butterfly!",content_type="text/plain",status=200)

@csrf_exempt
def HandlePostStoryRequest(request):
  Post_Success="Succeed to Post Story by '{username}'".format(username=request.user.username)
  Post_Failure="Failed to Post Story"
  Login_Required="Logging First"
  content_type="text/plain"
  author_obj=User.objects.all()
  if request.user.is_authenticated:
    received_json_data=json.loads(request.body.decode('utf8'))
    # author_obj=Author.objects.get(Username=request.user.id)
    author_obj=request.user.author
    headline=received_json_data['headline']
    category=received_json_data['category']
    region=received_json_data['region']
    details=received_json_data['details']
    story_obj=Story.objects.create(Story_Headline=headline,
                                   Story_Category=category,
                                   Story_Region=region,
                                   Story_Details=details,
                                   Authors=author_obj)
    if story_obj is None:
      return HttpResponse(Post_Failure,content_type=content_type,status=403)
    return HttpResponse(Post_Success,content_type=content_type,status=201)
  else:
    return HttpResponse(Login_Required,content_type=content_type,status=403)

@csrf_exempt
def HandleGetStoriesRequest(request):
  Login_Required="Logging First"
  text_content_type="text/plain"
  all_story=[]
  if request.user.is_authenticated:
    cat=request.GET.get('story_cat')
    region=request.GET.get('story_region')
    date=request.GET.get('story_date')
    if cat is None or region is None or date is None:
      SomethingNone=("cat={cat},region={region},date={date},request={request}").format(
                                        cat=cat,region=region,date=date,request=request.body)
      return HttpResponse(SomethingNone,content_type=text_content_type,status=403)

    if cat=='*' and region=='*' and date=='*':
      obj_set=Story.objects.all()
    if cat!='*' and region=='*' and date=='*':
      obj_set=Story.objects.filter(Story_Category=cat)
    if cat!='*' and region!='*' and date=='*':
      obj_set=Story.objects.filter(Story_Category=cat,Story_Region=region)
    if cat!='*' and region!='*' and date!='*':
      obj_set=Story.objects.filter(Story_Category=cat,Story_Region=region,Post_Date__gte=date)
    if cat=='*' and region!='*' and date=='*':
      obj_set=Story.objects.filter(Story_Region=region)
    if cat=='*' and region!='*' and date!='*':
      obj_set=Story.objects.filter(Story_Region=region,Post_Date__gte=date)
    if cat!='*' and region=='*' and date!='*':
      obj_set=Story.objects.filter(Story_Category=cat,Post_Date__gte=date)
    if cat=='*' and region=='*' and date!='*':
      obj_set=Story.objects.filter(Post_Date__gte=date)
    print(obj_set)
    # obj_set=Story.objects.all()
    # if story_cat!='*':
      # obj_set=obj_set.objects.filter(Story_Category=story_cat)
    # if story_region!='*':
      # obj_set=obj_set.objects.filter(Story_Region=story_region)
    # if story_date!='*':
      # obj_set=obj_set.objects.filter(Post_Date__gte=story_date)
    if len(obj_set)==0:
      NoStory="No Story Found"
      return HttpResponseBadRequest(NoStory,text_content_type,status=404)
    for obj in obj_set:
      datelist=obj.date.isoformat().split('-')
      date=datelist[2]+'/'+datelist[1]+'/'+datelist[0]
      story_dict={"key":obj.id,"headline":obj.Story_Headline,
                  "story_cat":obj.Story_Category,"story_region":obj.Story_Region,
                  "author":obj.Authors.Username,"story_details":obj.Story_Details}
      all_story.append(story_dict)
    response=JsonResponse({"stories":all_story})
    response['Content-Type']='application/json'
    response.status_code=200
    response.status_phrase="OK"
    return response
  else:
    return HttpResponse(Login_Required,content_type=text_content_type,status=403)


@csrf_exempt
def HandleDeleteStoryRequest(request):
  Login_Required="Logging First"
  content_type="text/plain"
  if request.user.is_authenticated:
    received_json_data=json.loads(request.body)
    key=received_json_data['story_key']
    story_obj=Story.objects.filter(id=key)
    if not story_obj:
      return HttpResponse(("Cannot Find Any Story with story_key={key}").format(key=key),content_type=content_type,status=503)
    story_obj.delete()
    return HttpResponse("SUCCESS",content_type=content_type,status=201)
  else:
    return HttpResponse(Login_Required,content_type=content_type,status=503)