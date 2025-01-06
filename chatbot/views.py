from dotenv import load_dotenv
import os
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone

load_dotenv()


openai.api_key = os.getenv('OPENAI_API_KEY')

logging.basicConfig(level=logging.DEBUG)
def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        max_tokens=150,
        temperature=0.7,
    )
    answer = response['choices'][0]['message']['content'].strip()
    return answer


def chatbot(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        message = request.POST.get('message')
        response = ask_openai(message)
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid credentials'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        logging.debug(f"Received data: {username}, {email}")

        try:
            if User.objects.filter(username=username).exists():
                error_message = 'Username already taken'
                return render(request, 'register.html', {'error_message': error_message})
            if User.objects.filter(email=email).exists():
                error_message = 'Email already registered'
                return render(request, 'register.html', {'error_message': error_message})
            if password1 != password2:
                error_message = 'Passwords do not match'
                return render(request, 'register.html', {'error_message': error_message})
            user = User.objects.create_user(username, email, password1)
            user.save()
            auth.login(request, user)
            logging.debug(f"New user created: {username}")
            return redirect('chatbot')
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            error_message = 'Error creating account'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
