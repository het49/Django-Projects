# BeerBuddy (User Guide)

BeerBuddy is a web app with two main areas:

1. **Platform/Admin portal** (for managing users, breweries, events, and check-ins)
2. **Brewery portal** (for brewery owners to manage their profile and offers)

## Platform/Admin portal: what you can do

### 1) Sign in

- Login: `/web/users/login/`

### 2) See a dashboard summary

- Dashboard: `/web/users/dashboard/`
- You can switch the charts between **Weekly**, **Monthly**, and **Yearly**.

### 3) Register breweries (create brewery-owner accounts)

- Brewery registration: `/web/users/brewery_registration/`
- Fill in **email**, **password**, **confirm password**, and **contact number**, then click **Register**.

### 4) Manage brewery-owner users

- Brewery management: `/web/users/brewery_management/`
- Actions shown in the list typically include:
  - Viewing user details
  - Viewing a user’s **Connections (friend list)** and **Favourites**
  - Enabling/disabling a user
  - Deleting a user (trash icon)

### 5) Manage your settings (platform content)

- Privacy Policy: `/web/users/privacy-policy/`
- Terms & Conditions: `/web/users/terms-condition/`
- Change Password: `/web/users/change_password/`

### 6) View events and check-ins

Depending on your account access, these screens may be used to monitor activity:

- Event management: `/web/events/event_management/`
  - View all events
  - Turn events **Active/Inactive**
  - Open an event to see its **Invitee List**
- Check Ins: `/web/beershops/check-in/`
  - View check-in details (beer shop, location, message, invitees, images)
  - View ratings/feedback (via modal links)
  - Turn a check-in/user **Active/Inactive**
  - Export check-in user list to Excel: `/web/beershops/exportcheckinuser/`

### 7) Manage beer-shop media

- Check-out images: `/web/beershops/checkout_images/<id>/` (opened from the check-in screen)
- Delete images: available on the Images screen (Select image(s) and click **Delete**).

## Brewery portal: what brewery owners can do

### 1) Sign in

- Login: `/web/brewery/login/`

### 2) Update brewery profile

- Profile: `/web/brewery/profile/`
- You can edit:
  - Brewery name
  - Owner first/last name
  - Profile picture upload
  - Address (with a map/address picker)
  - “About brewery” description
- Click **Save Profile** to apply changes.

### 3) Create and manage offers

- Offers page: `/web/brewery/offers/`
- Create offers (Create Offers form on the Offers page):
  - Offer title, description
  - Offer image upload
  - Start and end dates
  - Click **Save Offer**
- Control offer visibility:
  - Offers list shows whether an offer is **Live** or **Expired**
  - Use **Live On/Live Off** buttons to toggle the offer status

### 4) Change password

- Change password: `/web/brewery/changepassword/`

## Need a starting point?

- If you are managing platform content/users: start at `/web/users/login/`
- If you manage a brewery’s profile/offers: start at `/web/brewery/login/`
# BeerBuddy-Python

BeerBuddy is a Django application that serves:

- **REST APIs** under `/api/...` (Django REST Framework + JWT auth)
- **Web/admin pages** under `/web/...` (server-rendered templates)

The Django project lives in `BeerBuddy-Python/BeerBuddy/`.

## Tech stack

- **Python** (virtualenv recommended)
- **Django** `3.1.4` (see `BeerBuddy/requirements.txt`)
- **Django REST Framework** + **SimpleJWT**
- **Database** via `DATABASE_URL` (commonly MySQL or Postgres)
- **Static files** via WhiteNoise; optional **S3** storage via `django-storages`

## Project structure (high level)

- `BeerBuddy-Python/BeerBuddy/manage.py`: Django entrypoint
- `BeerBuddy-Python/BeerBuddy/BeerBuddy/settings.py`: settings (uses `python-decouple`)
- `BeerBuddy-Python/BeerBuddy/BeerBuddy/urls.py`: routes
- Apps: `users`, `event`, `beershop`, `brewery`, `notification`, `base/staticcontent`

## Quickstart (local development)

Run these commands from `BeerBuddy-Python/BeerBuddy/`.

1) Create & activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

2) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Create a `.env`

This project expects environment variables (see **Environment variables** below). For local dev you can create a file named `.env` in `BeerBuddy-Python/BeerBuddy/`.

4) Run migrations

```bash
python manage.py migrate
```

5) Create an admin user (optional)

```bash
python manage.py createsuperuser
```

6) Start the server

```bash
python manage.py runserver
```

## Key routes

From `BeerBuddy-Python/BeerBuddy/BeerBuddy/urls.py`:

- **Django admin**: `/admin/`
- **Users API**: `/api/users/`
- **Events API**: `/api/events/`
- **Beer shops API**: `/api/beershops/`
- **Notifications API**: `/api/notification/`
- **Brewery API**: `/api/brewery/`
- **Web UIs**: `/web/users/`, `/web/events/`, `/web/beershops/`, `/web/brewery/`

## Environment variables

Settings are loaded via `python-decouple` in `BeerBuddy/BeerBuddy/settings.py`. At minimum you’ll need:

- **Core**
  - `SECRET_KEY`: Django secret key
  - `DEBUG`: `True` / `False`
  - `ALLOWED_HOSTS`: comma-separated list (example: `localhost,127.0.0.1`)
- **Database**
  - `DATABASE_URL`: e.g. `mysql://USER:PASSWORD@HOST:3306/DBNAME?charset=utf8mb4` or `postgres://...`

Common optional settings used by the codebase:

- **Email**
  - `EMAIL_BACKEND`
  - `EMAIL_HOST`
  - `EMAIL_HOST_USER`
  - `EMAIL_HOST_PASSWORD`
  - `EMAIL_PORT`
  - `EMAIL_USE_SSL`
  - `DEFAULT_FROM_EMAIL`
- **JWT**
  - `DEFAULT_ACCESS_TOKEN_LIFETIME` (days; defaults to 7 in code)
- **Push notifications**
  - `NOTIFICATIONS_APNS_CERT_NAME`
  - `NOTIFICATIONS_SANDBOX`
  - `NOTIFICATIONS_IOS_APP_BUNDLE_ID`
  - `NOTIFICATIONS_FCM_KEY`
- **Google**
  - `GOOGLE_PLACE_DETAIL_API_KEY`
- **SMS (CLX/Mblox)**
  - `CLX_MBLOX_SERVICEPLAN`
  - `CLX_MBLOX_TOKEN`
  - `CLX_MBLOX_DYNAMIC_SENDER_ID`
- **S3 (optional)**
  - `USE_S3` (`True`/`False` as a string)
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_STORAGE_BUCKET_NAME`
  - `AWS_STORAGE_FOLDER_NAME`

Example `.env` (safe placeholders):

```dotenv
DATABASE_URL=mysql://root:password@localhost:3306/beerbuddy?charset=utf8mb4
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional:
USE_S3=False
DEFAULT_ACCESS_TOKEN_LIFETIME=30
```

## Static & media files

- **Static**: `STATIC_URL=/static/`, `STATIC_ROOT=BeerBuddy-Python/static_cdn/`
- **Media**:
  - If `USE_S3 == 'True'`: served from S3 via `django-storages`
  - Else: `MEDIA_URL=/media/`, `MEDIA_ROOT=BeerBuddy-Python/media_cdn/`

For production-like behavior you may need:

```bash
python manage.py collectstatic
```

## Scheduled jobs (cron)

This project defines cron jobs via `django-crontab`:

- `users.tasks.checkin_user`
- `users.tasks.checkout_user`

To manage them:

```bash
python manage.py crontab add
python manage.py crontab show
python manage.py crontab remove
```

## Security note

If you have a committed `.env` (or any file containing credentials/API keys), **treat those secrets as compromised and rotate them**. Do not commit real credentials to source control.