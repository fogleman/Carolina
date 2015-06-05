import random

class Node(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.right = None
        self.down = None
    def insert(self, w, h):
        if self.right:
            result = self.right.insert(w, h)
            if result:
                return result
            result = self.down.insert(w, h)
            if result:
                return result
            return None
        elif w <= self.w and h <= self.h:
            self.right = Node(self.x + w, self.y, self.w - w, h)
            self.down = Node(self.x, self.y + h, self.w, self.h - h)
            return (self.x, self.y, w, h)
        else:
            return None

def try_pack(tw, th, items):
    result = []
    node = Node(0, 0, tw, th)
    for index, (w, h) in items:
        rotated = False
        position = node.insert(w, h)
        if position is None:
            rotated = True
            position = node.insert(h, w)
            if position is None:
                return None
        result.append((index, rotated, position))
    return result

class Bin(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.items = []
    def add(self, item):
        layout = try_pack(self.width, self.height, self.items + [item])
        if layout is None:
            return False
        self.items.append(item)
        return True
    def layout(self):
        return try_pack(self.width, self.height, self.items)

def pack_bins(width, height, sizes, seed=None):
    bins = []
    items = list(enumerate(sizes))
    if seed is not None:
        r = random.Random(seed)
        r.shuffle(items)
    for item in items:
        for b in bins:
            if b.add(item):
                break
        else:
            b = Bin(width, height)
            b.add(item)
            bins.append(b)
    result = [b.layout() for b in bins]
    return result

def best_seed(width, height, sizes, iterations):
    best = (len(sizes) + 1, None)
    for i in xrange(iterations):
        print i, iterations
        seed = int(random.getrandbits(31))
        result = pack_bins(width, height, sizes, seed)
        best = min(best, (len(result), seed))
    return best[1]

def main():
    sizes = [
        (2.796303, 4.608439),
        (2.969545, 3.448883),
        (2.389097, 4.136028),
        (4.211018, 4.479503),
        (3.892448, 4.525951),
        (2.981819, 4.001485),
        (5.598131, 7.279581),
        (4.911953, 5.937876),
        (5.043486, 7.47855),
        (5.759114, 7.216851),
        (4.261401, 6.154586),
        (3.992446, 5.682565),
        (3.629748, 4.514655),
        (3.474979, 5.695182),
        (1.608547, 7.29097),
        (4.664706, 10.929071),
        (3.410576, 3.610378),
        (3.159717, 5.592945),
        (4.081008, 5.953425),
        (3.415935, 5.789518),
        (2.401783, 3.840703),
        (1.948522, 4.788107),
        (4.04277, 4.581349),
        (5.703452, 8.089674),
        (4.497644, 8.076961),
        (4.777673, 5.204438),
        (3.154485, 7.229238),
        (2.756838, 6.651178),
        (4.068647, 5.899639),
        (3.137532, 3.617026),
        (4.901308, 5.528174),
        (2.728631, 4.501734),
        (4.15774, 4.864285),
        (3.271605, 4.403709),
        (3.950064, 4.913542),
        (2.952528, 4.929043),
        (2.913893, 4.539156),
        (2.74825, 4.232396),
        (3.100285, 5.967405),
        (3.096809, 3.588219),
        (4.032702, 4.858762),
        (4.393324, 7.316425),
        (4.206678, 6.38567),
        (3.545411, 5.913528),
        (3.64894, 4.400476),
        (3.507051, 4.745325),
        (3.579581, 4.237857),
        (4.264548, 7.038648),
        (3.663635, 6.532058),
        (3.29721, 5.872043),
        (4.931198, 5.672635),
        (3.379987, 6.528652),
        (2.698226, 3.409745),
        (3.565255, 5.183341),
        (1.833549, 5.541963),
        (3.783002, 5.768361),
        (3.425811, 5.017416),
        (2.982607, 6.073248),
        (4.134148, 5.18733),
        (4.359352, 5.611329),
        (2.601352, 4.257002),
        (4.050707, 5.376776),
        (4.478288, 6.358188),
        (3.311229, 6.247856),
        (2.75939, 4.99192),
        (4.343492, 7.637077),
        (4.945037, 6.07679),
        (2.804834, 4.378152),
        (3.236164, 5.271111),
        (1.834742, 5.711892),
        (4.791471, 6.972421),
        (2.792891, 4.308481),
        (3.288685, 3.485517),
        (4.474283, 5.294111),
        (2.502778, 3.6085),
        (4.683384, 4.809318),
        (4.232971, 5.646356),
        (5.584648, 6.146236),
        (3.431915, 4.806705),
        (3.869438, 6.022825),
        (4.760191, 5.576543),
        (4.776974, 8.704121),
        (3.136611, 4.001484),
        (3.794912, 4.598745),
        (3.338892, 3.89138),
        (3.710804, 4.897786),
        (3.796671, 7.44883),
        (3.408572, 4.870256),
        (3.466923, 4.566983),
        (4.41129, 5.161794),
        (2.142341, 4.324989),
        (5.108186, 6.904415),
        (3.89205, 3.903081),
        (3.231258, 4.800171),
        (3.095798, 4.029599),
        (4.367326, 5.436798),
        (4.661692, 6.517788),
        (3.025184, 4.209169),
        (2.70936, 4.123304),
        (2.91546, 4.207589),
    ]
    p = 0.25
    sizes = [(w + p, h + p) for w, h in sizes]
    seed = best_seed(6, 8, sizes, 100)
    bins = pack_bins(6, 8, sizes, seed)
    for b in bins:
        print b
    print seed
    print len(bins)

if __name__ == '__main__':
    main()