# Django Chatbot Manual

## Overview

This Django project is a simple chatbot application with user authentication, chat history storage, and an Ollama-based backend API.

Users must log in to access the chat page. The application tracks chat history in the database and displays it on the chat screen.

## Setup (step-by-step)

1. Clone the repository.
2. Open a terminal in the project folder (`f:\chatbotmanual`).
3. Create and activate a Python virtual environment.

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. Install Django, requests, and the PostgreSQL database driver.

   ```powershell
   pip install django requests psycopg2-binary
   ```

5. Create a PostgreSQL database and user, then set environment variables for connection details.

   ```powershell
   $env:POSTGRES_DB = 'chatbotdb'
   $env:POSTGRES_USER = 'chatbotuser'
   $env:POSTGRES_PASSWORD = 'chatbotpass'
   $env:POSTGRES_HOST = '127.0.0.1'
   $env:POSTGRES_PORT = '5432'
   ```

   Or configure these values in your system environment.

6. Run migrations.

   ```powershell
   python manage.py migrate
   ```

6. Create a superuser (optional).

   ```powershell
   python manage.py createsuperuser
   ```

7. Start the development server.

   ```powershell
   python manage.py runserver
   ```

8. Open the browser at `http://127.0.0.1:8000/` and log in.

## Django update and auth flow fix

The project uses Django authentication URLs and a custom redirect for login/logout.

### Important settings

In `chatbot/settings.py`:

```python
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
```

These settings tell Django where to send users after login, where to require login, and where to go after logout.

### Fixed auth redirect error

Django can redirect authenticated users to `/accounts/profile/` by default. If that path does not exist, the browser returns a 404 error.

To solve this, the project now includes:

- `chatbot/urls.py` with `path('accounts/profile/', views.profile_redirect, name='profile')`
- `core_app/views.py` with a `profile_redirect()` view that sends users to the chat page
- `core_app/templates/registration/login.html` with a hidden `next` field so Django preserves the original destination after login

### Relevant code snippets

`chatbot/urls.py`

```python
from django.contrib import admin
from django.urls import include, path
from core_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile_redirect, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.chat_view, name='chat'),
    path('api/', include('core_app.urls')),
]
```

`core_app/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def chat_view(request):
    messages = ChatMessage.objects.order_by('created_at')[:100]
    return render(request, 'core/chat.html', {'messages': messages})


def profile_redirect(request):
    return redirect('chat')


def logout_view(request):
    logout(request)
    return redirect('login')
```

`core_app/templates/registration/login.html`

```html
<form method="post">
    {% csrf_token %}
    {% if next %}
        <input type="hidden" name="next" value="{{ next }}" />
    {% endif %}
    {{ form.as_p }}
    <button type="submit">Login</button>
</form>
```

## How to use

- Visit `/accounts/login/` to sign in
- Use `/accounts/logout/` to log out
- The chat page is at `/`
- The API endpoint is at `/api/chat-api/`

## Notes

- Keep `DEBUG = True` only during development.
- If you want a production-ready setup, add `ALLOWED_HOSTS` and switch `DEBUG` to `False`.
- The chat backend expects a local Ollama instance at `http://127.0.0.1:11434/api/generate`.
