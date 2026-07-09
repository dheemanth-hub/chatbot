# Simple Theory of the Django Auth Update

## Why the error happened

Django’s auth system uses a default redirect destination after login. If that destination is `/accounts/profile/` and the project does not define a route for it, Django returns a 404 error.

The app also needs to pass the `next` parameter through the login form so the original destination is preserved after login.

## What changed in this update

1. Added a route for `accounts/profile/` in `chatbot/urls.py`.
2. Added a `profile_redirect()` view in `core_app/views.py`.
3. Added a hidden `next` field in `core_app/templates/registration/login.html`.
4. Kept login settings in `chatbot/settings.py` for redirect control:
   - `LOGIN_URL = '/accounts/login/'`
   - `LOGIN_REDIRECT_URL = '/'`
   - `LOGOUT_REDIRECT_URL = '/accounts/login/'`

## What this fix means

- When Django redirects to `/accounts/profile/`, the URL now exists.
- The `profile_redirect()` view sends users to the chat page.
- Login forms keep the `next` value, so users return to the intended page after signing in.

## Simple flow

1. User requests a protected page.
2. Django sends the user to `/accounts/login/?next=/desired/page/`.
3. User logs in and the form sends the `next` value.
4. Django redirects to the original page or the chat page.

## Why this is useful

This keeps the auth flow working smoothly instead of breaking on a missing profile page. It also means logout and login behave predictably in the chat app.
