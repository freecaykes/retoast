# retoast
Server script to fetch twitter feed from list of handlers in twitter_handles to post on the specified subreddit.  Runs as a service to continuously check for updates for all the Twitter handles listed in twitter_handles.json

## Dependencies

Installl with pip

* [praw](https://github.com/praw-dev/praw) reddit api
* [tweepy](https://github.com/praw-dev/praw) twitter api
* [selenium](https://github.com/baijum/selenium-python)

## Setup

### Twitter App Setup

To initialize the Twitter API service minimally need a consumer key and consumer secret.

1. https://apps.twitter.com/ create the app
2. In the "Keys and Access Token" tab copy the Consumer Key and Secret
3. Either generate the Access token and secret with the Twitter api management or use
   get_access_token.py script to generate them

  Alternatively use the already provided consumer key and secret and access token and secret.
  This will route all access to [twitter-retoaster](https://apps.twitter.com/app/13462249/show)
4. Enter the credentials to configure.json

### Reddit App Setup

Similarlly setting up the Reddit API through praw requires OAUTH authentication with its own
token and secret

1. https://ssl.reddit.com/prefs/apps create the app
2. Client secret and id will be displayed under the "edit" link in the reddit app
[](img/preferences  reddit.com .png)
3. Enter the credentials to configure.json

### Initialize Selenium (Allternative method for access token and secret)

get_access_token.py requires Selenium to fetch access token.

1. Dowload the geckodriver (https://github.com/mozilla/geckodriver/releases)
2. Extract to desired location
3. Add to PATH: in terminal
  Linux/Unix:
    $ export PATH=$PATH:/path/to/directory/of/executable/downloaded/in/previous/step
  Windows:
    update the Path system variable to add the full directory path to the executable geckodriver manually or command line(don't forget to restart your system after adding executable geckodriver into system PATH to take effect). The principle is the same as on Unix.
    (http://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path)
4. This allows for:
    ```python
      webdriver.Firefox()
    ```
## Twitter List to follow

In twitter_handles.json add a list of Twitter handles to follow.  "name" key can be set arbitrarily it will appear in the reddit
post as:

"[<name>] <tweet content from the handle>"

Example of NBA Correspondents to follow.

```javascript
{
  "NBA_Correspondents": [
    {"handle": "WojVerticalNBA", "name":"WOJNAROWSKI", "max_id":0 },
    {"handle": "ZachLowe_NBA", "name":"LOWE", "max_id":0},
    {"handle":"SeanCunningham", "name":"CUNNINGHAM", "max_id":0}
  ]
}
```
