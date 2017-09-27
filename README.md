# Kryptweet

## Introduction
I wrote this as I wanted to fill my Twitter account with useful accounts to follow for the cryptosphere. As they say, the best form of flattery is imitation, so essentially I wanted to copy the friends/following of influential people in the Twittersphere.

Quick command-line tool to:
* Copy someone's friends/following list on Twitter
* See the new friends/following since you last checked

## How to install
Either download or `git clone` this repository. Once done, you can quickly use `pip install -r requirements.txt` to get the required libraries for this to work.

## Setup
To get started, you first need to make sure you have a your Twitter consumer key, consumer secret, access token and access token secret. You can get them by following the instructions at https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.

Once you have them, you can run the following:

```
kryptweet.py setup CONSUMER_KEY CONSUMER_SECRET ACCESS_TOKEN ACCESS_TOKEN_SECRET
```

If by some chance you set it up wrongly, you can overwrite your existing credentials by running:

```
kryptweet.py setup --overwrite CONSUMER_KEY CONSUMER_SECRET ACCESS_TOKEN ACCESS_TOKEN_SECRET
```

## Using it
Finally we get to this.

### Listing all friends/following someone has
```
kryptweet.py following list screen_name
```

E.g. If you want to list all the people I am following
```
kryptweet.py following list shuxycrypto
```

### Copying all friends/following someone has
```
kryptweet.py following copy screen_name
```

E.g. If you want to follow all the people I am following
```
kryptweet.py following copy shuxycrypto
```

### Seeing changes and updates
If you want to see the additional friends/following or unfriended/unfollowed since the last time you listed (or copied) someone:
```
kryptweet.py following list --newonly screen_name
```

E.g. If you want to list all the new people I have followed or unfollowed since the last time you listed/copied me:
```
kryptweet.py following list --newonly shuxycrypto
```

### Banlist
I prefer to keep my Twitter free of certain things, such as politics. However, many of the people I've copied tend to follow certain political figures, and I end up following them as well. To combat this, you can use the banlist function to basically say "I want to follow everyone person A is following minus whoever is on my banlist".

You can run the following to see the list of banlist functions (add/remove/list/purge/unfollow)

```
kryptweet.py banlist --help
```

### Others
Append `--help` at the end of your command to see instructions.

## Potential issues
If you hit your rate limit, the tool will wait for a while and then try again. It will eventually succeed, just that it may take a while.
