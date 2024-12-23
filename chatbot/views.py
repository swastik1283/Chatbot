from django.shortcuts import render
from django.http import JsonResponse
import openai
from django.contrib import auth 

openai.api_key='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'


def ask_openai(message):
    response=openai.Completion.create(
    model="gpt-3.5-turbo",
    prompt=message,
    max_tokens=150,
    n=1,
    stop=None,
    temperature=0.7,
    )
    answer=response.choices[0].text.strip()
    return answer
   
def chatbot(request):
    if request.method =='POST':
        message=request.POST.get('message')
        response=ask_openai(message)
        return JsonResponse({'message':message,'response':response})
    return render(request,'chatbot.html')

def login(request):
    return render(request,'login.html')

def register(request):
    return render(request,'register.html')

def logout(request):
    auth.logout(request)