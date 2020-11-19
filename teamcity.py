import sys
from pyteamcity import TeamCity
from prettytable import PrettyTable
from dateutil.parser import parse


tc = TeamCity()


def show_last_build(buildTypeId):
    bt = tc.get_build_type(buildTypeId)
    print('{} [{}]'.format(bt['name'], bt['id']))

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
    print(pt)
    print(b['statusText'])
    print(b['webUrl'])


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
    print('Usage: teamcity [buildTypeId]\n')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        show_summary()
    else:
        for bt in sys.argv[1:]:
            show_last_build(bt)
            print('\n')
