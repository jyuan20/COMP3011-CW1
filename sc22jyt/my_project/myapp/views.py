from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from .models import Author, NewsStory
import json

# Create your views here.

@csrf_exempt
def api_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse('Logged in successfully', content_type ='text/plain', status = 200)
    else:
        return HttpResponse('Invalid username/password', content_type ='text/plain', status = 200)

@csrf_exempt
@login_required
def api_logout(request):
    logout(request)
    return HttpResponse('You have logged out successfully', content_type='text/plain', status=200)

@csrf_exempt
def api_stories(request):
    if request.method == 'POST':
        return api_post_story(request)
    elif request.method == 'GET':
        return api_get_stories(request)
    else:
        return HttpResponse('Method not allowed', status=405)

@csrf_exempt
@login_required
def api_post_story(request):
    if request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            author = Author.objects.get(user=request.user)
            news_story = NewsStory(
                headline=data['headline'],
                category=data['category'],
                region=data['region'],
                author=author,
                details=data['details']
            )
            news_story.save()
            return JsonResponse({'message': 'Story posted successfully'}, status=201)
        except Exception as e:
            return HttpResponse(e, content_type='text/plain', status=503)
    else:
        return HttpResponse('Please log in to access this function', content_type='text/plain', status=503)
    
@csrf_exempt
@require_http_methods(["GET"])
def api_get_stories(request):
    # Retrieve query parameters
    category = request.GET.get('cat', '*')
    region = request.GET.get('reg', '*')
    date_str = request.GET.get('date', '*')
    date = parse_date(date_str) if date_str != '*' else None

    # Build the query based on the parameters
    query = {}
    if category != '*':
        query['category'] = category
    if region != '*':
        query['region'] = region
    if date:
        query['date__gte'] = date
    try:
        stories = NewsStory.objects.filter(**query)
        if not stories.exists():
            return HttpResponse('No stories found', content_type='text/plain', status=404)
        stories_data = [
            {
                "key": str(story.pk) ,
                "headline": story.headline,
                "category": story.category,
                "region": story.region,
                "author": story.author.user.username,
                "date": story.date.strftime('%d/%m/%Y'),
                "details": story.details
            }
            for story in stories
        ]     
        for data in stories_data:
            print(f'Key: {data["key"]}')
            print(f'Headline: {data["headline"]}')
            print(f'Category: {data["category"]}')
            print(f'Region: {data["region"]}')
            print(f'Author: {data["author"]}')
            print(f'Date: {data["date"]}')
            print(f'Details: {data["details"]}\n')
        return JsonResponse({"stories": stories_data}, status=200)
    except Exception as e:
        # Handle unexpected errors
        return HttpResponse(f"An error occurred: {e}", content_type='text/plain', status=500)
    
@csrf_exempt
@login_required
def api_delete_story(request, key):
    if request.method != 'DELETE':
        return HttpResponse('Method not allowed', status=405) 
    try:
        story = NewsStory.objects.get(pk=key)
        if story.author.user != request.user:
            return HttpResponse('Unauthorized', status=401)
        story.delete()
        return HttpResponse('Story deleted successfully', status=200)
    except NewsStory.DoesNotExist:
        return HttpResponse('Story not found', status=404)
    except Exception as e:
        return HttpResponse(str(e), status=503, content_type='text/plain')
    
