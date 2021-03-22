from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import (HttpResponse,Http404,HttpResponseBadRequest)
from .models import Author,Story
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from django.core import serializers

@csrf_exempt
def HandleLoginRequest(request):
  if request.method!='POST':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
  if not request.POST:
    return HttpResponse("EMPTY CONTENT",content_type="text/plain",status=205)
  if (not 'username' in request.POST) or (not 'password' in request.POST):
    NotKeyValue="Require the key [username, password]"
    return HttpResponse(NotKeyValue,content_type="text/plain",status=205)
  un=request.POST.get('username')
  pw=request.POST.get('password')
  user=authenticate(request,username=un,password=pw)
  if user is None:
    if not User.objects.filter(username=un, is_active=True).exists():
      NotFoundAuthor=("'{username}' NOT REGISTERED").format(username=un)
      return HttpResponse(NotFoundAuthor,content_type="text/plain",status=403)
    if not User.objects.filter(username=un,password=pw).exists():
      WrongPassword=("'{password}' WRONG PASSWORD OF '{username}'").format(password=pw,username=un)
      return HttpResponse(WrongPassword,content_type="text/plain",status=403)
  else:
    if not user.is_active:
      DisabledAccount=("'{username}' is a disabled account").format(username=un)
      return HttpResponse(DisabledAccount,content_type="text/plain",status=403)
    else:
      login(request,user)
      if(user.is_authenticated):
        return HttpResponse("Welcome to ml17x44z site!!!",content_type="text/plain",status=200)

@csrf_exempt
def HandleLogoutRequest(request):
  if request.method!='POST':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
  if(request.user.is_authenticated==False):
    return HttpResponse("Logout Failed / Loggin First",content_type="text/plain",status=503)
  else:
    logout(request)
    return HttpResponse("Bye-bye Butterfly!",content_type="text/plain",status=200)

@csrf_exempt
def HandlePostStoryRequest(request):
  if request.method!='POST':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
  Post_Success="Succeed to Post Story by '{username}'".format(username=request.user.username)
  Post_Failure="Failed to Post Story"
  Login_Required="Logging First"
  content_type="text/plain"
  author_obj=User.objects.all()
  if request.user.is_authenticated==True:
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
  if request.method!='GET':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
  text_content_type="text/plain"
  all_story=[]
  json_data=json.loads(request.body)
  cat=json_data['story_cat']
  region=json_data['story_region']
  date=json_data['story_date']
  if date!='*':
    valid_date=date.split('/')
    date=valid_date[2]+'-'+valid_date[1]+'-'+valid_date[0]
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
  if len(obj_set)==0:
    NoStory="No Story Found"
    return HttpResponseBadRequest(NoStory,text_content_type,status=404)
  for obj in obj_set:
    datelist=obj.Post_Date.isoformat().split('-')
    date=datelist[2]+'/'+datelist[1]+'/'+datelist[0]
    story_dict={"key":obj.id,"headline":obj.Story_Headline,
                "story_cat":obj.Story_Category,"story_region":obj.Story_Region,
                "author":str(obj.Authors.Name),"story_date":str(obj.Post_Date)[:10],
                "story_details":obj.Story_Details}
    all_story.append(story_dict)
    # json_response=serializers.serialize("json",all_story)
    # json_response=json.dumps(all_story)
  response=JsonResponse({"stories":all_story},safe=True)
  response['Content-Type']='application/json'
  response.status_code=200
  response.status_phrase="OK"
  return response

@csrf_exempt
def HandleDeleteStoryRequest(request):
  if request.method!='POST':
    badResponse = "{method} Not Allowed".format(method=request.method)
    return HttpResponseBadRequest(badResponse,content_type="text/plain",status=405)
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