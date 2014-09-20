import sys
sys.path.insert(0, ".")

import helper
import timeit


def bench(mode):
    im = helper.hopper(mode)
    get = im.im.getpixel
    xy = 50, 50  # position shouldn't really matter
    t0 = timeit.default_timer()
    for i in range(1000000):
        get(xy)
    print(mode, timeit.default_timer() - t0, "us")

bench("L")
bench("I")
bench("I;16")
bench("F")
bench("RGB")
