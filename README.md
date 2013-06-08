# Tastypie Session User

Tastypie API for session authentication and default django authorization

## Install

* Clone this repo into your project
* Install requirements - `pip install -r requirements.txt` and add **tastypie** and **registration** to INSTALLED_APPS
* Add `ACCOUNT_ACTIVATION_DAYS` setting to settings.py
* Add api urls to your project urls.py file `url(r'^api/', include('session_user.urls'))`
* Run tests `./manage.py test session_user`

Note: **Application doesn't send activation e-mails**
