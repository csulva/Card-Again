# Card-Again

[Card Again](http://cardagain.net/) is your one-stop website to view the current market value of your Pokemon cards. Search for more than 14,000 cards, add them to your collection, follow your friends to see their collections, and find links to buy and sell each card. You can find all of these features on Card Again. Be sure to register for an account today, and start collecting!


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
```python
export FLASK_APP=cardagain
flask shell
```
```python
>>> db.create_all()
>>> Role.insert_roles()
>>> User.add_self_follows()
>>> exit()
```
Add yourself to the database in a flask shell session:
```python
>>> u = User(username='yourusername', email='youremail', confirmed=True)
>>> u.set_password('yourpassword)
>>> db.session.add(u)
>>> db.session.commit()
>>> exit()
```
Note: you can also register in your own app!
First, run the program:

```python
flask run
```
Then, navigate to your *register* template: __localhost:5000/auth/register__ and register your email address. Confirm yourself as a user by opening the link sent to you in an email (see [Send Emails](#send-emails)).

Now you can add as many cards to your collection as you want. You can also search for other users and follow them. 

## Card Data
