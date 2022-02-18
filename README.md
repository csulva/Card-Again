# Card Again

[Card Again](http://www.cardagain.net/) is your one-stop website to view the current market value of your Pokémon cards. Search for more than 14,000 cards, add them to your collection, follow your friends to see their collections, and find links to buy and sell each card. You can find all of these features on Card Again. Be sure to register for an account today, and start collecting!

# Table of Contents
[Installation](#installation)

[Usage](#usage)

[Card Data](#card-data)

[Schdedule Tasks To Update Cards](#schdedule-tasks-to-update-cards-table-automatically)

[Migrations](#migrations)

[Send Emails](#send-emails)

[Environment Variables](#environment-variables)

[Contributing](#contributing)

[References](#references)



## Installation

It is  recommended to install requirements in a virtual environment (venv).
```bash
python3 -m venv venv
. venv/bin/activate
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Card Again requirements.

```bash
pip install -r requirements/common.txt
```

For use with Production on Amazon Web Services, see [aws-README.md](https://github.com/csulva/Card-Again/blob/main/aws-README.md):



## Usage
To start using the app, open a ```flask shell``` session:
```bash
export FLASK_APP=cardagain
flask shell
```
```shell
>>> db.create_all()
>>> Role.insert_roles()
>>> User.add_self_follows()
>>> exit()
```
Add yourself to the database in a ```flask shell``` session:

```shell
>>> u = User(username='yourusername', email='youremail', confirmed=True)
>>> u.set_password('yourpassword)
>>> db.session.add(u)
>>> db.session.commit()
>>> exit()
```
Note: you can also register in your own app!
First, run the program:

```bash
flask run
```
Then, navigate to your *register* template: __localhost:5000/auth/register__ and register your email address. Confirm yourself as a user by opening the link sent to you in an email (see [Send Emails](#send-emails)).

Now you can add as many cards to your collection as you want. You can also search for other users and follow them. 

## Card Data

The card data is requested from [Pokémon TCG Developers API](https://pokemontcg.io/) and stored locally in ```API/card_data.json```.

To update the card data from the API, run the ```load_cards()``` function in ```API/load.py```.
Next, you can add the card data to the database.
First, open a ```flask shell``` session, then run:

```shell
>>> Card.insert_cards()
```

To update the cards inforamation periodically, as prices change all the time, in a ```flask shell``` session, run:
```shell
>>> Card.update_cards()
```
## Schdedule Tasks to Update Cards Table Automatically

While running, the app will load, add, and update cards automatically. In the application factory, you will notice the class instance ```scheduler```:
```python
# app/__init__.py
from flask_apscheduler import APScheduler
scheduler = APScheduler()
```
Also, in the ```create_app()``` function in the applicaton factory, it loads your tasks from ```tasks.py```
```python
# app/__init__.py
...

    # Importing and running scheduled tasks from tasks.py
    with app.app_context():
        scheduler.init_app(app)
        from app import tasks
        scheduler.start()
```
In the ```tasks.py``` file in the ```app``` directory, you will see the scheduled tasks to be run every Monday:

```python
# app/tasks.py

@scheduler.task('cron', id='update_cards', day_of_week=0, hour=0)   # for day_of_week, 0 is Monday
def update_cards():
    with scheduler.app.app_context():
        load_cards()
        Card.insert_cards()
        Card.update_cards()
```
This means you will not need to manually update your cards as long as the app is running. The function loads the new data, inserts cards (any new cards, skips existing cards), and updates existing cards. You can change the methods in the scheduler decorator function to run the task whenever you wish. Follow me @Chris

## Migrations
Whenever a database migration needs to be made. Run the following commands:
```bash
flask db migrate
```
This will generate a new migration script. To apply the migration, run:
```bash
flask db upgrade
```

For a full migration command reference, run ```flask db --help```.

## Send Emails

For email sending to work properly with this app, including confirmation emails, you must have an email that accepts SMTP authentication. Then, you must then set the environment variables MAIL_USERNAME, MAIL_PASSWORD, and CARDAGAIN_ADMIN that are found in ```config.py```

You can configure those variables in a bash script:

```bash
export MAIL_USERNAME=<your_username>
export MAIL_PASSWORD=<your_password>
export CARDAGAIN_ADMIN=<yourusername@example.com>
```
## Environment Variables

It might be useful to save your environment variables in your project, so you do not need to set them up each time you run the app. To do so, run the following:

```bash
touch .env
```
Be sure to create it in your root directory and not to push it to GitHub or any public space where it can be viewed. Then you can add your environment variables to the file. For example:
```python
# .env
FLASK_APP=cardagain.py
```

NOTE: For deploying with [Amazon Web Services](https://aws.amazon.com/), I needed to explicitly write out all of my would-be environment variables in my code in order to deploy my app, including creating the app with the correct configuration:
```python
# app/__init__.py
def create_app(config_name='aws'):
```
See ```config.py``` for the AWS Configuration. While you're there, be sure to connect it to the correct database link and not to look for the environment variable. I used MySQL through [Amazon Relational Database Service](https://aws.amazon.com/rds/).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## References
[CodingNomads Python Web Development](https://codingnomads.co/career-track/professional-python-web-development-course)

[Pokémon TCG Developers API](https://pokemontcg.io/)
