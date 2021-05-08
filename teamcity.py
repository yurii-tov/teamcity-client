import sys
import argparse
from pyteamcity import TeamCity
from prettytable import PrettyTable
from dateutil.parser import parse
import time
import requests
import json
import io


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


def show_last_build(buildTypeId, **kwargs):
    bt = tc.get_build_type(buildTypeId)
    print('{} [{}]'.format(bt['name'], bt['id']), **kwargs)

    running = tc.get_builds(build_type_id=buildTypeId, count=1, running='true')['build']
    completed = tc.get_builds(build_type_id=buildTypeId, count=1)['build']
    lbs = running or completed
    if not lbs:
        print('No builds found')
        return
    lbid = lbs[0]['id']
    b = tc.get_build_by_build_id(lbid)
    for k in ['startDate', 'finishDate']:
        if b.get(k):
            dt = parse(b[k], fuzzy=True)
            b[k] = dt.strftime("%Y-%m-%d %H:%M:%S")
        else: b[k] = '?'

    keys = ['id', 'number', 'state', 'status', 'startDate', 'finishDate']
    pt = PrettyTable()
    pt.field_names = keys
    pt.add_row([b[k] for k in keys])
    print(pt, **kwargs)
    print(b['statusText'], **kwargs)
    print(b['webUrl'], **kwargs)


def show_build_types():
    tids = [t['id'] for t in tc.get_build_types()['buildType']]
    bts = [tc.get_build_type(tid) for tid in tids]
    bts.sort(key=lambda x: x['projectName'])
    keys = ['projectId', 'id', 'name']
    pt = PrettyTable()
    pt.field_names = keys
    for bt in bts:
        pt.add_row([bt[k] for k in keys])

    print(pt)


def show_summary():
    info = tc.get_server_info()
    print('Teamcity {}\n{}\n'.format(
        info['version'],
        tc.base_base_url))
    show_build_types()


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
                with io.StringIO() as o:
                    show_last_build(btid, file=o)
                    tg_message(o.getvalue())

            builds[btid] = lbid

        time.sleep(10)


def tg_message(message):
    tg_settings = global_settings['telegram']
    tg_chat_id=tg_settings['chat_id']
    tg_token=tg_settings['bot_token']
    payload = dict(
        chat_id=tg_chat_id,
        text="<pre>{}</pre>".format(message),
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
    parser.add_argument('-w', '--watch',
                        help='watch (and report about) fresh builds',
                        action='store_true')
    parser.add_argument('build_type_id',
                        nargs='*',
                        help='build type ids to operate on')
    args = parser.parse_args()
    if args.watch:
        watch_builds(args.build_type_id or get_all_bts())
    elif args.build_type_id:
        for x in args.build_type_id:
            show_last_build(x)
            print(end='\n\n')
    else:
        show_summary()
