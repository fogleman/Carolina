from counties import COUNTIES
from pyquery import PyQuery as pq
import requests

HEIGHT = 1.0
G0Z = 0.2
G1Z = -0.1
DECIMALS = 6

def text_to_gcode(text, height, g0z, g1z, decimals):
    url = 'http://microtechstelladata.com/TextToNCcode.aspx'
    data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': '/wEPDwUKLTE5MjQ4NjQyMw9kFgJmD2QWBAIDDxYCHgdWaXNpYmxlaGQCBQ9kFgICAQ9kFgICIw8QZGQWAWZkZP1tK90CYj/RyRAXxCXZ9MsdtjZh',
        '__VIEWSTATEGENERATOR': 'B79F8C8F',
        '__EVENTVALIDATION': '/wEdAA4YgLztMITv6WUVAM0YlAVA/7tJmonIhf59Tn/tHHjiiTHCxj6r94D91iNj2eP793nF3NePEBXQLJqM6z9L7HtafqRdbq8oQ+/3q0t201+XA+iB45D2wcqc3NGIeG+zC+reKNcVx0azo6w3jhRVDUE5knyMHhMDgqHg5ixcDBsa6K8KXjNqDNqpvMONBB9efaR9r9Eq32XHfl/N2l08K35Tt+UCGtlKjl/HDt/gEIgOxAKoj62QTBYGh/bSap+LjkNzBLQbnkRMGNvG4i8XSTQk6EkGRZdrvveosdMrbkvNkKrsc435POiCQNnrAnNkAyiTwjBJ',
        'ctl00$phContent$TextBox_Text': text,
        'ctl00$phContent$TextBox_Height': str(height),
        'ctl00$phContent$TextBox_G0Z': str(g0z),
        'ctl00$phContent$TextBox_G1Z': str(g1z),
        'ctl00$phContent$TextBox_Decimals': str(decimals),
        'ctl00$phContent$DropDown_Font': 'Single Line (Arc & Lines)',
        'ctl00$phContent$Button_CreateNC': 'Create G-code',
        'ctl00$phContent$TextBox_NcCode': '',
    }
    r = requests.post(url, data=data)
    d = pq(r.text)
    return d('#ctl00_phContent_TextBox_NcCode').text()

def fetch():
    for county in COUNTIES:
        text = county.name
        print text
        code = text_to_gcode(text, HEIGHT, G0Z, G1Z, DECIMALS)
        with open('text/%s.nc' % text, 'w') as fp:
            fp.write(code)

if __name__ == '__main__':
    fetch()
