import argparse
from pyteamcity import TeamCity
from prettytable import PrettyTable
from dateutil.parser import parse
import time
import requests
import json


##################
# Initialization #
##################


with open('settings.json') as fh:
    global_settings = json.load(fh)


tc = TeamCity(**global_settings['teamcity'])


########################
# Teamcity interaction #
########################


def get_all_bts():
    return [bt['id'] for bt in tc.get_build_types()['buildType']]


def get_last_build(btid):
    bt = tc.get_build_type(btid)
    running = tc.get_builds(build_type_id=btid, count=1, running='true')['build']
    lbs = running or tc.get_builds(build_type_id=btid, count=1)['build']
    r = dict(title='{} [{}]'.format(bt['name'], bt['id']))
    if not lbs:
        return r
    lbid = lbs[0]['id']
    b = tc.get_build_by_build_id(lbid)
    for k in ['startDate', 'finishDate']:
        if b.get(k):
            dt = parse(b[k], fuzzy=True)
            b[k] = dt.strftime("%Y-%m-%d %H:%M:%S")
        else: b[k] = '?'

    keys = ['id', 'number', 'state', 'status', 'startDate', 'finishDate', 'statusText', 'webUrl']
    for k in keys:
        r[k] = b[k]
    return r


def print_build(b):
    print(b['title'])
    if b.get('id'):
        keys = ['id', 'number', 'state', 'status', 'startDate', 'finishDate']
        pt = PrettyTable()
        pt.field_names = keys
        pt.add_row([b[k] for k in keys])
        print(pt)
        print(b['statusText'])
        print(b['webUrl'])
    else: print('No builds found')


def print_build_types(btids):
    bts = [tc.get_build_type(tid) for tid in btids]
    bts.sort(key=lambda x: x['projectName'])
    keys = ['projectId', 'id', 'name']
    pt = PrettyTable()
    pt.field_names = keys
    for bt in bts:
        pt.add_row([bt[k] for k in keys])

    print(pt)


##################
# Build watching #
##################


def watch_builds(bt_ids):
    builds = dict()
    while True:
        for btid in bt_ids:
            lbid_stored = builds.get(btid)
            lbids = tc.get_builds(build_type_id=btid, count=1)['build']
            lbid = lbids and lbids[0]['id']
            if lbid_stored and lbid_stored != lbid:
                tg_message_build(get_last_build(btid))

            builds[btid] = lbid

        time.sleep(global_settings['polling_interval'])


def tg_message_build(b):
    tg_settings = global_settings['telegram']
    tg_chat_id=tg_settings['chat_id']
    tg_token=tg_settings['bot_token']

    sign = '✅'
    if b['status'] == 'FAILURE':
        sign = '❌'

    message = "{} <b>{}</b>\n<i>{}</i>\n<pre>{}</pre>\n<a href=\"{}\">View</a>".format(
        sign,
        b['title'],
        b['statusText'],
        '''Id:     {}
Number: {}
Start:  {}
Finish: {}
'''.format(
    b['id'],
    b['number'],
    b['startDate'],
    b['finishDate']
),
        b['webUrl'].replace('localhost', '127.0.0.1')
    )

    payload = dict(
        chat_id=tg_chat_id,
        text=message,
        parse_mode='html'
    )
    r = requests.post(
        "https://api.telegram.org/bot{}/sendMessage".format(tg_token),
        data=payload
    )


########
# Main #
########


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=['run', 'watch', 'status', 'info']
    )
    parser.add_argument('build_type_id',
                        nargs='*',
                        help='build type ids to operate on')
    args = parser.parse_args()

    btids = args.build_type_id or get_all_bts()
    if args.command == 'run':
        for x in btids:
            tc.trigger_build(x)

        print('Builds triggered: {}'.format(btids))
    elif args.command == 'watch':
        watch_builds(btids)
    elif args.command == 'status':
        for x in btids:
            print_build(get_last_build(x))
            print(end='\n\n')
    elif args.command == 'info':
        info = tc.get_server_info()
        print('Teamcity {}\n{}\n'.format(
            info['version'],
            tc.base_base_url))
        print_build_types(btids)

