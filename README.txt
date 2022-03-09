
TITLE: Image sharer (take 2)

DESCRIPTION: I created the project the first time as part of a recruitment
assignment, then it was abandoned. I went back to it to write it in a better way
than I did the first time. The API I created is a site for sharing photos with
others via links. Users can upload any photo, get a link to the original or
created thumbnail and share with others. Each user can have a different tier
account, which allows them to share more thumbnails or create a link that
expires after a certain number of seconds.

INSTALLATION WITH PROJECT FILES: First, install all required modules using "pip
install -r requirements.txt". Then perform the migrations using "python
manage.py makemigrations" and "python manage.py migrate". Before starting the
server, run the starter.py file once, which creates account tiers. Additionally,
you should create an administrator using "python manage.py createsuperuser", and
then you can run the server using "python manage.py runserver".
