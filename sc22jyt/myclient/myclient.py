import requests
from datetime import datetime
import random

session = requests.Session()
def login(url):
    username = input('Enter username: ')
    password = input('Enter password: ')
    response = session.post(url, data={'username': username, 'password': password})
    print(response.text)

def logout():
    response = session.post('http://127.0.0.1:8000/myapp/api/logout')
    if response.status_code == 200:
        print(response.text)
    else:
        print('Log out failed')

def post_story():
    url = 'http://127.0.0.1:8000/myapp/api/stories'
    headline = input('Enter headline: ')
    while not headline:
        print('Headline cannot be empty. Please enter the headline.')
        headline = input('Enter headline: ')
    valid_categories = {'pol', 'art', 'tech', 'trivia'}
    category = input('Enter category (pol, art, tech, trivia): ')
    while category not in valid_categories:
        print('Invalid category. It must be one of the following: pol, art, tech, trivia.')
        category = input('Enter category (pol, art, tech, trivia): ')
    valid_regions = {'uk', 'eu', 'world'}
    region = input('Enter region (uk, eu, world): ')
    while region not in valid_regions:
        print('Invalid region. It must be one of the following: uk, eu, world.')
        region = input('Enter region (uk, eu, world): ')
    details = input('Enter details: ')
    while not details:
        print('Details cannot be empty. Please enter the details.')
        details = input('Enter details: ')
    response = session.post(url, json={
        'headline': headline, 
        'category': category, 
        'region': region, 
        'details': details, 
        })
    if response.status_code == 404:
        print('You need to be logged in to proceed with this operation.')
    else:
        print(response.text)
    

def get_stories(command):
    valid_categories = {'pol', 'art', 'tech', 'trivia'}
    valid_regions = {'uk', 'eu', 'world'}
    valid_commands = {'-id', '-cat', '-reg', '-date'}

    url = 'https://newssites.pythonanywhere.com/api/directory/'
    response = session.get(url)
    if response.status_code == 200:
        agencies = response.json()

    params = {}
    words = command.split()
    invalid_commands = [word.split('=')[0] for word in words if not word.split('=')[0] in valid_commands]
    if invalid_commands:
        print(f"Invalid command. Please use only the valid commands: {', '.join(valid_commands)}.")
        return
    agency_id = next((word.split('=')[1] for word in words if word.startswith('-id=')), None)
    if agency_id:
        agencies = [agency for agency in agencies if agency['agency_code'] == agency_id]
    else:
        agencies = random.sample(agencies, 20)  # Random sample if no specific id

    for word in words:
        if word.startswith('-cat='):
            category = word.split('=')[1]
            if category not in valid_categories:
                print('Invalid category. It must be one of the following: pol, art, tech, trivia.')
                return
            params['cat'] = category
        elif word.startswith('-reg='):
            region = word.split('=')[1]
            if region not in valid_regions:
                print('Invalid region. It must be one of the following: uk, eu, world.')
                return
            params['reg'] = word.split('=')[1]
        elif word.startswith('-date='):
            params['date'] = word.split('=')[1]

    all_stories = []
    for agency in agencies:
        try:
            agency_url = f"{agency['url'].rstrip('/')}/api/stories"
            stories_response = requests.get(agency_url, params=params)
            if stories_response.status_code == 200:
                data = stories_response.json()
                stories = data.get('stories', [])
                if 'reg' in params:
                    # Filter stories by region
                    stories = [story for story in stories if story.get('story_region') == params['reg']]
                if 'cat' in params:
                    # Filter stories by category
                    stories = [story for story in stories if story.get('story_cat') == params['cat']]
                if 'date' in params:
                    # Filter stories by date
                    date = datetime.strptime(params['date'], '%Y-%m-%d')
                    stories = [story for story in stories if datetime.strptime(story.get('story_date'), '%Y-%m-%d') >= date]
                all_stories.extend(stories)
            else:
                print(f"Error retrieving stories from {agency['url']}: HTTP {stories_response.status_code}")
        except ConnectionError as e:
            print(f"Error connecting to {agency['url']}: {e}")
    if all_stories:
        for story in all_stories:
            id = story.get('key')
            headline = story.get('headline')
            category = story.get('story_cat')
            region = story.get('story_region')
            author = story.get('author')
            date = story.get('story_date')
            details = story.get('story_details')
            print(f"Key: {id}")
            print(f"Headline: {headline}")
            print(f"Category: {category}")
            print(f"Region: {region}")
            print(f"Author: {author}")
            print(f"Date: {date}")
            print(f"Details: {details}")
            print("-" * 30)
    else:
        print("No stories found.")      
    # response = session.get(agency_url, params=params)
    # if response.status_code == 200:
    #     print('Stories retrieved successfully:')
    #     print(response.json())  # Assumes that the JSON response contains the stories
    # elif response.status_code == 404:
    #     print('No stories found')
    # else:
    #     print(f'Failed to retrieve stories. Status code: {response.status_code}')

def delete_story(command):
    story_key = command.split()[1]
    url = f'http://127.0.0.1:8000/myapp/api/stories/{story_key}'
    response = session.delete(url)
    
    if response.status_code == 200:
        print(response.text)
    elif response.status_code == 404:
        print('You need to be logged in to proceed with this operation.')
    else:
        print(f'Failed to delete story. Status code: {response.status_code} - {response.text}')

def register_agency():
    url = 'https://newssites.pythonanywhere.com/api/directory/'
    agency_name = input('Enter the name of the news agency: ')
    while not agency_name:
        print('Agency name cannot be empty. Please enter the agency name.')
        agency_name = input('Enter the name of the news agency: ')
    agency_url = input('Enter the URL of the news agency: ')
    while not agency_url:
        print('Agency URL cannot be empty. Please enter the agency URL.')
        agency_url = input('Enter the URL of the news agency: ')
    agency_code = input('Enter the agency code: ')
    while not agency_code:
        print('Agency code cannot be empty. Please enter the agency code.')
        agency_code = input('Enter the agency code: ')
    response = session.post(url, json={
        'agency_name': agency_name,
        'url': agency_url,
        'agency_code': agency_code
    })
    if response.status_code == 201:
        print('Agency registered successfully.')
    elif response.status_code == 503:
        print(f'Service Unavailable: {response.text}')
    else:
        print(f'An error occurred: {response.text}')

def list_agencies():
    url = 'https://newssites.pythonanywhere.com/api/directory/'
    response = session.get(url)
    if response.status_code == 200:
        agencies = response.json()
        random_agencies = random.sample(agencies, 20)
        for record in random_agencies:
            print(record)
    else:
        print(response.json())
        

    

def main():
    while True:
        command = input('Enter command (login, logout, post, exit): ')
        words = command.split() #Split the command by spaces
        if words[0] == 'exit':
            print('You have exited the program')
            break
        elif words[0] == 'login':
            url = words[1]
            login(url)
        elif words[0] == 'logout':
            logout()
        elif words[0] == 'post':
            post_story()
        elif words[0] == 'news':
            get_stories(command)
        elif words[0] == 'delete':
            delete_story(command)
        elif words[0] == 'list':
            list_agencies()
        else:
            print('Invalid command. Please try again.')


if __name__ == "__main__":
    main()
