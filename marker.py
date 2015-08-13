from gcode import GCode
from shapely.wkt import loads
from shapely.affinity import scale

WKT = 'POLYGON ((287.42775874 1.03942901, 282.56685958 2.80089628, 278.11493009 4.84629968, 273.81119151 7.38499523, 269.39486192 10.62665161, 264.60516569 14.78046848, 259.18132091 20.05627089, 245.38807379 34.81125631, 231.16324842 50.77031234, 217.11967312 67.02393648, 203.28976916 83.52647379, 189.70596089 100.23195665, 176.40067272 117.09473013, 163.40632746 134.06899858, 150.75535058 151.10891944, 138.48016396 168.16872834, 126.61319136 185.20261399, 115.18685841 202.16482766, 104.23358559 219.00954242, 93.78579883 235.6909939, 83.87592253 252.16338646, 74.53637793 268.38092444, 65.79958941 284.29782783, 57.69798293 299.86830099, 51.06800058 313.26664705, 44.86330171 326.38432473, 39.07968827 339.23509305, 33.71296532 351.83272668, 28.75893949 364.19101591, 24.2134127 376.32370411, 20.07219159 388.24458158, 16.33108122 399.96742297, 12.98588352 411.50597167, 10.03240669 422.8740336, 7.46645265 434.08535216, 5.28382647 445.15373326, 3.48033322 456.09292028, 2.05177795 466.91668789, 0.99396573 477.63881075, 0.30270006 488.27306349, 0.02215208 496.81162987, -3.07e-06 505.34350436, 0.23368294 513.86290192, 0.72066469 522.36406878, 1.45839363 530.8412199000001, 2.44432279 539.2886015, 3.67590518 547.70042854, 5.15059225 556.07093161, 6.86583547 564.39435695, 8.819089399999999 572.66491951, 11.0078055 580.87686551, 13.4294368 589.02440992, 16.08143475 597.10179897, 18.96125079 605.10323196, 22.06633796 613.0229864200001, 25.39415082 620.85524601, 28.94213928 628.59428825, 32.70775634 636.23429681, 36.68845503 643.76953356, 40.8816868 651.19421345, 45.2849031 658.50258272, 49.89555852 665.68885633, 54.71110607 672.74726486, 59.72899409 679.67205454, 64.94667871 686.4574403399999, 70.36161138999999 693.09765284, 75.97124358000001 699.58693827, 81.77302831 705.91951159, 87.76441702 712.08960339, 93.9428643 718.0914599, 100.30582004 723.91929608, 106.85073881 729.56734252, 116.60476451 737.40282298, 126.59778751 744.7807222, 136.81547686 751.7002271699999, 147.2435088 758.16055612, 157.86755625 764.16091165, 168.67329282 769.70051199, 179.64639114 774.7785754, 190.77252573 779.39428882, 202.03737 783.5468705, 213.4265958 787.23553868, 224.92587814 790.45949596, 236.52089042 793.2179449400001, 248.19730606 795.51010386, 259.94079849 797.33517532, 271.73703957 798.69237757, 283.57170583 799.58091319, 295.43046758 800.00000043, 307.29899667 799.9488731599999, 319.16297746 799.42667145, 331.00807087 798.43264479, 342.81995501 796.9659958, 354.584308 795.02594271, 366.28679229 792.61170376, 377.91308602 789.72245028, 389.44886728 786.3574317699999, 400.87981419 782.51583521, 412.19157359 778.1968788299999, 423.36985486 773.39978087, 434.40030484 768.1237283, 445.26861728 762.36793936, 455.96045465 756.13163227, 466.46147943 749.41400965, 474.50248525 743.84132511, 482.33044515 738.02848314, 489.94160667 731.98280102, 497.33224863 725.71159606, 504.4986342 719.2221855499999, 511.43704218 712.5219024199999, 518.14373577 705.61806397, 524.61497812 698.51797186, 530.84704805 691.2289590300001, 536.83620874 683.75834277, 542.57872336 676.11344037, 548.07087072 668.30156915, 553.308914 660.33004638, 558.28911637 652.20620501, 563.00775664 643.93736233, 567.461098 635.5308199999999, 571.64541924 626.99391096, 575.55698354 618.3339525, 579.19203845 609.5582619199999, 582.54689404 600.67415652, 585.61778222 591.68896923, 588.4009818 582.6100017, 590.8927715999999 573.44458688, 593.08939914 564.20002643, 594.98715888 554.8836689, 596.58231399 545.50280034, 597.8711276499999 536.0647693, 598.8498630300001 526.57686181, 599.5147833 517.04642644, 599.86218292 507.48078049, 599.88829379 497.88722562, 599.58942599 488.27309476, 598.92871159 477.85864236, 597.94372211 467.45244537, 596.62606142 457.02642288, 594.96734902 446.55249399, 592.95915751 436.00256215, 590.59313767 425.34854645, 587.86087773 414.56235034, 584.75398157 403.61589292, 581.26406868 392.48107765, 577.38272732 381.12983924, 573.10160825 369.53406552, 568.4122840700001 357.66567559, 563.30637428 345.49657289, 557.7754827700001 332.99869216, 551.8112290399999 320.1439212, 545.40521695 306.90419476, 537.09955326 290.53840334, 528.2343352300001 273.97914134, 518.82580791 257.24961146, 508.89024758 240.37295388, 498.44389927 223.37234004, 487.50302364 206.27095701, 476.08389697 189.0919606, 464.20274868 171.85852225, 451.8758394 154.59379777, 439.11944544 137.32097423, 425.94981183 120.06322306, 412.38321485 102.84366882, 398.4358839 85.68554546999999, 384.12409527 68.61200882, 369.46409399 51.64619904, 354.47215635 34.81125631, 342.46544136 21.75488445, 338.00851953 17.19517649, 334.21708085 13.62252186, 330.81700812 10.79301067, 327.53419976 8.462263950000001, 324.09453857 6.38652816, 320.22390735 4.32158069, 316.95098047 2.97554202, 312.94382224 1.84698968, 308.45145531 0.96094006, 303.72291792 0.34209686, 299.00726085 0.01563284, 294.55348797 -2.41e-06, 290.61063909 0.33302842, 287.42774467 1.03301856, 287.42775874 1.03942901), (262.42146068 373.86047992, 263.20322318 426.75143489, 269.04347375 432.10178617, 274.88373995 437.45212181, 299.94606068 437.45212181, 325.00837203 437.45212181, 330.84863823 432.10178617, 336.6888888 426.75143489, 337.4706513 373.86047992, 338.2524138 320.96950931, 370.3046763 320.55572242, 387.56059814 320.4231355, 397.954584 320.68499467, 401.32457451 321.01303785, 403.8745587 321.49874689, 405.90302913 322.1617753, 407.70846272 323.02183913, 411.33165047 325.1262187, 412.8008011 326.25173781, 414.06267523 327.5634102, 415.13301754 329.16414709, 416.027604 331.15690661, 416.76217931 333.64459997, 417.35251945 336.73016965, 418.1635355 345.10670793, 418.58670354 357.1099988, 418.7739513 395.29074771, 418.87120255 422.95822943, 419.1897395 441.42319388, 419.76941639 451.97467361, 420.16964752 454.68570088, 420.65011876 455.90173245, 422.20440332 456.65747789, 425.02733208 457.25103889, 428.82607242 457.63899634, 433.30783865 457.77799372, 437.55907876 457.92136896, 441.29154128 458.36778662, 444.55428961 459.14148133, 447.39641845 460.266719, 449.86700684 461.76773427, 452.01513384 463.66882432, 453.88987849 465.99423941, 455.54031985 468.76824547, 456.53877128 470.9209536, 457.27644237 473.0433137, 457.74188813 475.15835651, 457.92363228 477.28912838, 457.81027671 479.45866003, 457.39026699 481.68999783, 456.65218938 484.0061725, 455.58459888 486.43021475, 452.41503663 491.69408746, 447.78992642 497.66587739, 441.61761442 504.52989286, 433.80643114 512.47044219, 418.77393566 527.29305007, 418.77393566 563.88222434, 418.69278871 584.06018678, 418.29476215 595.6895293699999, 417.90434996 599.2573214400001, 417.34764125 601.83857613, 416.59563263 603.81682614, 415.61928945 605.57561977, 413.63126741 608.54725539, 411.63008049 610.88424057, 409.41650434 612.66007663, 406.79133023 613.94824924, 403.55534944 614.82222845, 399.50936889 615.35553119, 394.45414859 615.62161187, 388.19051109 615.69400308, 380.07046908 615.56657579, 374.22627843 615.14115628, 370.12652826 614.35284261, 367.23982332 613.13676413, 365.26359026 611.77310453, 363.45667133 610.13784501, 361.84810117 608.27954864, 360.46689882 606.24677851, 359.34209894 604.0880820899999, 358.50272054 601.85199117, 357.97781393 599.5870844900001, 357.79639812 597.34189386, 357.48813353 593.79927455, 357.15446166 592.48169204, 356.74699141 591.71287552, 356.11881397 591.91222496, 354.72596336 592.89110106, 349.99892696 596.87486895, 343.27131341 603.03925388, 335.24852266 610.75928365, 326.91369923 618.76587628, 319.3365131 625.71052274, 313.35208989 630.84907892, 309.79564902 633.43744765, 307.02286252 634.66759785, 304.27016731 635.47978655, 301.5228944 635.87279419, 298.76632009 635.84527615, 295.98574723 635.39605978, 293.16647243 634.52384736, 290.29379388 633.2273568000001, 287.35300818 631.50533727, 284.28829748 628.99269005, 278.74288082 623.91078038, 261.66640631 607.5031959299999, 239.03654116 585.21058157, 213.76624503 559.96099745, 188.76847443 534.68247248, 166.95618901 512.3030043, 151.24234405 495.75065308, 146.58263687 490.57463483, 144.53989943 487.95341644, 143.06442223 484.26477953, 142.28330202 480.53347403, 142.17975133 476.82695039, 142.73698319 473.21272163, 143.93821053 469.75825386, 145.7666461 466.53101318, 148.20550288 463.59852823, 151.2379937 461.02823385, 153.95536591 459.45055895, 157.09219873 458.45212316, 161.13846384 457.92917095, 166.58413261 457.77797808, 171.06589728 457.63898071, 174.86464075 457.25102325, 177.68756168 456.65746225, 179.2418525 455.90171681, 179.72232686 454.68568524, 180.12255643 451.97465797, 180.70222863 441.42317824, 181.02076871 422.95821379, 181.1180825 395.29073207, 181.30531618 357.10998317, 181.72849361 345.1066923, 182.53949715 336.73015402, 183.12983572 333.64458433, 183.86441573 331.15689098, 184.7589975 329.16413146, 185.82934294 327.56339456, 187.09121081 326.25172217, 188.56036456 325.12620306, 192.18357108 323.0218235, 193.98900623 322.1617753, 196.01747041 321.49874689, 198.56745303 321.01303785, 201.93744824 320.68499467, 212.3314341 320.42311986, 229.5873575 320.55570678, 261.63962 320.96949368, 262.4213825 373.86046428, 262.42146068 373.86047992))'

def load(buf):
    polygon = loads(WKT)
    polygon = scale(polygon, 0.01, 0.01)
    polygon = polygon.buffer(buf)
    g = GCode.from_geometry(polygon, 0.2, -0.1875)
    g = g.move(3, 4, 0.5, 0.5)
    return g

def load_text1():
    s = 0.3
    t1 = GCode.from_file('text/TransLoc.nc')
    t2 = GCode.from_file('text/OnDemand.nc')
    t1 = t1.scale(s, s)
    t2 = t2.scale(s, s)
    t1 = t1.move(3 - 0.125, 6.75, 1, 0.5)
    t2 = t2.move(3 + 0.125, 6.75, 0, 0.5)
    return t1 + t2

def load_text2():
    s = 0.3
    t1 = GCode.from_file('text/Home is where.nc')
    t2 = GCode.from_file('text/your stop is.nc')
    t1 = t1.scale(s, s)
    t2 = t2.scale(s, s)
    t1 = t1.move(3, 2.75, 0.5, 0.5)
    t2 = t2.move(3, 2.25, 0.5, 0.5)
    return t1 + t2

def main():
    g = load(0.125) + load_text1() + load_text2()
    g = g.scale_to_fit(6, 8).origin()
    im = g.render(0, 0, 6, 8, 96)
    im.write_to_png('marker.png')

if __name__ == '__main__':
    main()