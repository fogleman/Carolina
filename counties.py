from collections import namedtuple
import csv

County = namedtuple('County', ['name', 'fips', 'seat', 'created', 'population'])

def load_counties(path):
    result = []
    with open(path, 'rb') as fp:
        for row in csv.reader(fp):
            county = County(*row)
            result.append(county)
    return result

COUNTIES = load_counties('counties.csv')
