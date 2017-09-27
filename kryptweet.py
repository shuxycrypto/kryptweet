#!/usr/bin/env python

#author: shuxy
import click
import sys
import twitter
import ujson
from datetime import datetime
from terminaltables import AsciiTable, SingleTable
from tinydb import TinyDB, Query

def unix_time_millis(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def get_api():
    db = TinyDB('db.json')
    Settings = Query()
    results = db.search(Settings.type == 'auth')

    if len(results) == 0:
        click.UsageError('Please setup the required authentication details first.')

    api = twitter.Api(consumer_key=results[0]['consumer_key'],
        consumer_secret=results[0]['consumer_secret'],
        access_token_key=results[0]['access_token'],
        access_token_secret=results[0]['access_token_secret'],
        sleep_on_rate_limit=True)
    return api

@click.group()
def cli():
    pass

@click.group()
def following():
    pass

@click.group()
def banlist():
    pass

@click.command(short_help='Sets up Kryptweet with your Twitter credentials.')
@click.argument('consumer_key', nargs=1)
@click.argument('consumer_secret', nargs=1)
@click.argument('access_token', nargs=1)
@click.argument('access_token_secret', nargs=1)
@click.option('--overwrite', is_flag=True, help='Use to overwrite existing Twitter credentials.')
def setup(consumer_key, consumer_secret, access_token, access_token_secret, overwrite):
    """Sets up Kryptweet with your Twitter credentials."""
    db = TinyDB('db.json')
    Settings = Query()
    results = db.search(Settings.type == 'auth')

    if len(results) > 0:
        if overwrite:
            db.remove(Settings.type == 'auth')
        else:
            raise click.UsageError('You already have existing Twitter credentials set up.')

    db.insert({'type': 'auth', 'consumer_key': consumer_key, 'consumer_secret': consumer_secret
        , 'access_token': access_token, 'access_token_secret': access_token_secret})
    click.echo('Setup successful.')

@following.command(short_help='Gets a list of people that the specified user is currently following.', name='list')
@click.argument('screen_name', nargs=1)
@click.option('--newonly', is_flag=True, help='Specify this is you only want to see new users that the specified user has followed or unfollowed since you last checked.')
def get_following(screen_name, newonly):
    """Gets a list of people that the specified user is currently following."""
    api = get_api()
    results = api.GetFriends(screen_name = screen_name)
    following_list = []
    for r in results:
        following_list.append(r.screen_name)
        #following_list.append({'id': r.id, 'screen_name': r.screen_name})

    #Do some comparison work
    db = TinyDB('db.json')
    Following = Query()
    results = db.search(Following.screen_name == screen_name)

    if len(results) > 0:
        last_updated_timestamp = 0
        last_updated_following = None

        for result in results:
            if result['timestamp'] > last_updated_timestamp:
                last_updated_timestamp = result['timestamp']
                last_updated_following = result['following']

        last_updated_following_set = set(last_updated_following)
        latest_following_set = set(following_list)

        new_following = list(latest_following_set - last_updated_following_set)
        new_unfollowing = list(last_updated_following_set - latest_following_set)

        if len(new_following) > 0:
            new_following_table_list = []
            for f in new_following:
                #new_following_table_list.append([f['screen_name']])
                new_following_table_list.append([f])

            new_following_table = AsciiTable(new_following_table_list)
            new_following_table.inner_heading_row_border = False
            click.echo(screen_name + ' newly followed the people below since we last checked:')
            click.echo(new_following_table.table)

        if len(new_unfollowing) > 0:
            new_unfollowing_table_list = []
            for f in new_unfollowing:
                #new_unfollowing_table_list.append([f['screen_name']])
                new_unfollowing_table_list.append([f])

            new_unfollowing_table = AsciiTable(new_unfollowing_table_list)
            new_unfollowing_table.inner_heading_row_border = False
            click.echo(screen_name + ' unfollowed the people below since we last checked:')
            click.echo(new_unfollowing_table.table)

    if not newonly and len(following_list) > 0:
        all_following_table_list = []
        for f in following_list:
            #all_following_table_list.append([f['screen_name']])
            all_following_table_list.append([f])

        all_following_table = AsciiTable(all_following_table_list)
        all_following_table.inner_heading_row_border = False
        click.echo(screen_name + ' is following all the people below:')
        click.echo(all_following_table.table)

    #Store latest results into DB
    db.insert({'type': 'following', 'timestamp': unix_time_millis(datetime.now()), 'id': api.GetUser(screen_name=screen_name).id,
        'screen_name': screen_name, 'following': following_list})

@following.command(short_help='Follows/copies the list of people that the specified user is currently following.', name='copy')
@click.argument('screen_name', nargs=1)
def follow_following(screen_name):
    """Follows/copies the list of people that the specified user is currently following."""
    api = get_api()
    user_following = api.GetFriendIDs(screen_name=screen_name)
    my_following = api.GetFriendIDs()

    db = TinyDB('db.json')
    Banlist = Query()
    results = db.search(Banlist.type == 'banlist')
    banlist_ids = []
    for result in results:
        banlist_ids.append(result['id'])

    currently_not_following = list(set(user_following) - set(my_following) - set(banlist_ids))

    if len(currently_not_following) > 0:
        new_followed_table_list = []
        for cnf in currently_not_following:
            result = api.CreateFriendship(user_id=cnf)
            new_followed_table_list.append([result.screen_name])

        new_followed_table = AsciiTable(new_followed_table_list)
        new_followed_table.inner_heading_row_border = False
        click.echo('You are now following the people below:')
        click.echo(new_followed_table.table)

@banlist.command(short_help='Lists banlist of people not to follow.', name='list')
def banlist_list():
    """Lists banlist of people not to follow."""
    db = TinyDB('db.json')
    Banlist = Query()

    results = db.search(Banlist.type == 'banlist')

    if len(results) > 0:
        banlist_table_list = []

        for result in results:
            banlist_table_list.append([result['screen_name']])

        banlist_table = AsciiTable(banlist_table_list)
        banlist_table.inner_heading_row_border = False
        click.echo('The people below are in your banlist:')
        click.echo(banlist_table.table)

@banlist.command(short_help='Unfollows everyone on the banlist that you are currently following.', name='unfollow')
def banlist_unfollow():
    """Unfollows everyone on the banlist that you are currently following."""
    db = TinyDB('db.json')
    Banlist = Query()
    api = get_api()

    results = db.search(Banlist.type == 'banlist')

    for result in results:
        api.DestroyFriendship(user_id=result['id'])

@banlist.command(short_help='Takes in one or more Twitter screen names to be added to the banlist.', name='add')
@click.argument('screen_names', nargs=-1)
def banlist_add(screen_names):
    """Takes in one or more Twitter screen names to be added to the banlist."""
    db = TinyDB('db.json')
    Banlist = Query()
    api = get_api()

    for screen_name in screen_names:
        results = db.search((Banlist.type == 'banlist') & (Banlist.screen_name==screen_name))

        if len(results) == 0:
            db.insert({'type': 'banlist', 'id': api.GetUser(screen_name=screen_name).id, 'screen_name': screen_name})

@banlist.command(short_help='Takes in one or more Twitter screen names to be removed from the banlist.', name='remove')
@click.argument('screen_names', nargs=-1)
def banlist_remove(screen_names):
    """Takes in one or more Twitter screen names to be removed from the banlist."""
    db = TinyDB('db.json')
    Banlist = Query()

    for screen_name in screen_names:
        results = db.remove((Banlist.type == 'banlist') & (Banlist.screen_name==screen_name))

@banlist.command(short_help='Purges the banlist. (Clears it so there''s no one in the banlist.', name='purge')
def banlist_purge():
    """Purges the banlist. (Clears it so there''s no one in the banlist."""
    db = TinyDB('db.json')
    Banlist = Query()
    results = db.remove(Banlist.type == 'banlist')

cli.add_command(setup)
cli.add_command(following)
cli.add_command(banlist)

if __name__== "__main__":
    cli()
