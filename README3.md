# Chatbot Project Guide

## 1. Project overview

This project is a simple web-based chatbot built with Django. It lets users log in, send messages, and see chat history. The chatbot can respond using a local Ollama model or a cloud-based Groq API.

### Main features
- User authentication and login system
- Chat page with message history
- Backend logic for sending prompts to an LLM
- PostgreSQL database for storing chat data
- Docker support for running the app in a container
- Ollama integration for local AI model inference

## 2. What this project is about

The whole idea of this project is to learn how to connect a web application to an AI model in a practical way.

In simple terms:
1. A user types a message in the browser.
2. Django receives the message.
3. The app sends the message to an AI backend.
4. The AI backend returns a reply.
5. The reply is shown to the user and saved in the database.

This project teaches three important things:
- Django web development
- Docker container basics
- Connecting a web app to local or cloud AI models

## 3. Tech stack used

- Python
- Django
- PostgreSQL
- Docker
- Ollama
- Requests library

## 4. The main error and why it happened

One common issue appeared when running the app inside Docker:

The chatbot was working on the laptop, but inside the Docker container it could not reach Ollama.

### Why?

Inside Docker, localhost means the container itself, not your laptop. So the app inside the container was trying to connect to an Ollama server that did not exist inside that container.

### The error in simple words
The app inside Docker could not find the Ollama service at localhost:11434 because that address pointed to the container, not to the host computer.

## 5. The solution

The fix was to make the container reach the host machine where Ollama was running.

### What changed
- The app was updated to use environment-based settings for the AI backend.
- Docker was configured to use host.docker.internal so the container could reach the host PC.
- Ollama was configured to listen on all interfaces using:

```powershell
$env:OLLAMA_HOST = '0.0.0.0:11434'
```

Or in CMD:

```cmd
set OLLAMA_HOST=0.0.0.0:11434
```

### Why this works
- From your laptop: Ollama is available at localhost:11434
- From the Docker container: Ollama is accessible through host.docker.internal:11434

## 6. How the app uses AI now

The app can use:
- Ollama for local model responses
- Groq for cloud-based model responses

In the current setup, the chatbot uses Ollama running on your local machine.

### Environment variables used
- LLM_PROVIDER=ollama
- OLLAMA_URL=http://localhost:11434 for local use
- OLLAMA_URL=http://host.docker.internal:11434 for Docker use
- OLLAMA_MODEL=llama3.2

## 7. How to run the project locally

### 1. Start Ollama
In PowerShell:

```powershell
$env:OLLAMA_HOST = '0.0.0.0:11434'
ollama serve
```

### 2. Start the Django app

```powershell
python manage.py migrate
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## 8. How to run the project with Docker

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8000/
```

## 9. Why .env is useful

The .env file is useful because it stores configuration values such as:
- AI provider
- Ollama URL
- model name
- API keys

This keeps secrets and settings out of the code and allows the same project to run in different environments.

## 10. How to share this project with a team

To share it with others:
1. Put the code in GitHub or GitLab
2. Add a README file with setup steps
3. Share a sample .env file instead of the real secret values
4. Ask each teammate to create their own .env
5. Make sure Docker and Ollama are installed on their machine

## 11. What happens after the project is done

Once the project works locally, the next step is usually deployment.

### Possible next steps
- Run the app on a server
- Deploy with Docker on a cloud machine
- Use a reverse proxy like Nginx
- Add HTTPS
- Store secrets securely in the cloud
- Add CI/CD for automatic deployment

## 12. How deployment works conceptually

When the project is deployed:
- Your laptop is no longer the host
- The app runs on a server or cloud instance
- The AI model must also be available there

You have two common choices:

### Option A: Run Ollama on the server
The server hosts both the app and the model.

### Option B: Use a remote Ollama service
The app connects to a remote AI service instead of a local one.

## 13. Next steps to learn deployment

Here is a good learning path:

1. Learn Docker basics
   - containers
   - images
   - docker compose

2. Learn environment variables
   - how .env works
   - how secrets are managed

3. Learn server deployment
   - cloud VM
   - Docker hosting
   - Linux basics

4. Learn production setup
   - Nginx
   - HTTPS
   - domain names
   - static files

5. Learn CI/CD
   - GitHub Actions
   - automatic builds and deployment

## 14. Suggested practice projects after this one

After finishing this chatbot, you can learn more by building:
- a chatbot with user accounts and file upload
- a chatbot connected to your own documents
- a multi-user chatbot app
- a deployed AI web app on a cloud platform

## 15. Summary

This project is a beginner-friendly way to learn how a web app talks to an AI model. It covers Django, Docker, Ollama, environment variables, and the important idea of network communication between containers and the host machine.

The biggest lesson from this project is:
- local apps and containerized apps do not always use the same network rules
- you must configure the connection carefully when the app runs inside Docker
