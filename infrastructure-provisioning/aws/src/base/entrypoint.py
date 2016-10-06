#!/usr/bin/python
import os
from ConfigParser import SafeConfigParser
import argparse
from fabric.api import *
import json
import sys
import select

parser = argparse.ArgumentParser()
parser.add_argument('--action', type=str, default='describe')
args = parser.parse_args()


def get_from_stdin():
    lines = []
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        lines.append(line)
        if not line:
            break
    if len(lines) > 0:
        return ''.join(lines)
    else:
        return "{}"

if __name__ == "__main__":
    # Get request ID as if it will need everywhere
    request_id = 'generic'
    try:
        request_id = os.environ['request_id']
    except:
        os.environ['request_id'] = 'generic'

    # Get config from STDIN
    stdin_contents = get_from_stdin()
    try:
        passed_as_json = json.loads(stdin_contents)
    except:
        with open("/response/%s.json" % request_id, 'w') as response_file:
            reply = dict()
            reply['request_id'] = os.environ['request_id']
            reply['status'] = 'err'
            reply['response'] = dict()
            reply['response']['result'] = "Malformed config passed in stdin"
            reply['response']['stdin_contents'] = stdin_contents
            response_file.write(json.dumps(reply))
        sys.exit(1)

    for option in passed_as_json:
        os.environ[option] = passed_as_json[option]

    # Get config (defaults) from files. Will not overwrite any env
    for filename in os.listdir('/root/conf'):
        if filename.endswith('.ini'):
            config = SafeConfigParser()
            config.read(os.path.join('/root/conf', filename))
            for section in config.sections():
                for option in config.options(section):
                    varname = "%s_%s" % (section, option)
                    if varname not in os.environ:
                        os.environ[varname] = config.get(section, option)

    # Overwrite config if overwrite.ini is provided
    for filename in os.listdir('/root/conf'):
        if filename.endswith('overwrite.ini'):
            config = SafeConfigParser()
            config.read(os.path.join('/root/conf', filename))
            for section in config.sections():
                for option in config.options(section):
                    varname = "%s_%s" % (section, option)
                    os.environ[varname] = config.get(section, option)

    # Pre-execution steps: dumping config to stdout and checking for dry running
    print "[FULL DOCKER CONFIGURATION OPTIONS]"
    for item in os.environ:
        print "%s  =  %s\n" % (item, os.environ[item])

    dry_run = False
    try:
        if os.environ['dry_run'] == 'true':
            dry_run = True
    except:
        pass

    with hide('running'):
        local('chmod 600 /root/keys/*.pem')

    if dry_run:
        with open("/response/%s.json" % request_id, 'w') as response_file:
            response = {"request_id": request_id, "action": args.action, "dry_run": "true"}
            response_file.write(json.dumps(response))

    # Run execution routines
    elif args.action == 'create':
        with hide('running'):
            local("/bin/create.py")

    elif args.action == 'status':
        with hide('running'):
            local("/bin/status.py")

    elif args.action == 'describe':
        with open('/root/description.json') as json_file:
            description = json.load(json_file)
            description['request_id'] = request_id
            with open("/response/%s.json" % request_id, 'w') as response_file:
                response_file.write(json.dumps(description))

    elif args.action == 'stop':
        with hide('running'):
            local("/bin/stop.py")

    elif args.action == 'start':
        with hide('running'):
            local("/bin/start.py")

    elif args.action == 'terminate':
        with hide('running'):
            local("/bin/terminate.py")
