import json
import requests
import sys

HEADERS = {'content-type': 'application/json'}

class Fabmo(object):
    def __init__(self, host, port=9876):
        self.url = 'http://%s:%s' % (host, port)

    def direct_gcode(self, cmd):
        url = self.url + '/direct/gcode'
        data = dict(cmd=cmd)
        r = requests.post(url, data=json.dumps(data), headers=HEADERS)
        return r.json()

    def direct_gcode_file(self, path):
        with open(path) as fp:
            cmd = fp.read()
        return self.direct_gcode(cmd)

def main():
    args = sys.argv[1:]
    fabmo = Fabmo(args[0])
    print fabmo.direct_gcode_file(args[1])

if __name__ == '__main__':
    main()
