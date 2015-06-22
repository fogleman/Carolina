from gcode import GCode
from shapely.geometry import Polygon
import shapefile

SHAPEFILE = 'shapefiles/cb_2014_us_state_20m/albers.shp'

def load_shapes():
    skip = set(['AK', 'HI', 'AS', 'GU', 'MP', 'VI', 'PR'])
    result = []
    sf = shapefile.Reader(SHAPEFILE)
    for item in sf.shapeRecords():
        if item.record[4] in skip:
            continue
        result.append(item.shape)
    return result

def main():
    m = 1
    shapes = load_shapes()
    g = GCode.from_shapes(shapes, 0.2, -0.01)
    g = g.rotate(90).scale_to_fit(6 * m, 8 * m).move(3 * m, 4 * m, 0.5, 0.5)
    im = g.render(0, 0, 6 * m, 8 * m, 96)
    im.write_to_png('usa.png')

if __name__ == '__main__':
    main()
