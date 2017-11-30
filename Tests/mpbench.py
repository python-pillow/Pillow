from PIL import Image
import time
import math

def timeit(n, f, *args, **kwargs):
    def run():
        start = time.time()
        f(*args, **kwargs)
        return time.time() - start

    runs = [run() for _ in range(n)]
    mean = sum(runs)/float(n)
    stddev = math.sqrt(sum((r-mean)**2 for r in runs)/float(n))
    return {'mean':mean,
            'median': sorted(runs)[int(n/2)],
            'min': min(runs),
            'max': max(runs),
            'stddev':stddev,
            'dev_pct': stddev/mean*100.0
            }

    #return min(run() for _ in range(n))

n = 400
image = Image.open('5k_image.jpg').copy()
print 'warmup {mean:.4}'.format(**timeit(n // 4, image.im.resize, (2048, 1152), Image.ANTIALIAS))
print "%s runs"%n
print "Interpolation | Size  |  min  |  max  |  mean | median| stddev | Dev %"
print "--------- | --------- | ----- | ----- | ----- | ----- | -----  | ----"
print 'Antialias | 2048x1152 | {min:5.3f} | {max:5.3f} | {mean:5.3f} | {median:5.3f} | {stddev:5.4f} | {dev_pct:4.1f}%'.format(**timeit(n, image.im.resize, (2048, 1152), Image.ANTIALIAS))
print 'Antialias | 320x240   | {min:5.3f} | {max:5.3f} | {mean:5.3f} | {median:5.3f} | {stddev:5.4f} | {dev_pct:4.1f}%'.format(**timeit(n, image.im.resize, (320, 240),   Image.ANTIALIAS))
print 'Bicubic   | 2048x1152 | {min:5.3f} | {max:5.3f} | {mean:5.3f} | {median:5.3f} | {stddev:5.4f} | {dev_pct:4.1f}%'.format(**timeit(n, image.im.resize, (2048, 1152), Image.BICUBIC))
print 'Bicubic   | 320x240   | {min:5.3f} | {max:5.3f} | {mean:5.3f} | {median:5.3f} | {stddev:5.4f} | {dev_pct:4.1f}%'.format(**timeit(n, image.im.resize, (320, 240),   Image.BICUBIC))
print 'Bilinear  | 2048x1152 | {min:5.3f} | {max:5.3f} | {mean:5.3f} | {median:5.3f} | {stddev:5.4f} | {dev_pct:4.1f}%'.format(**timeit(n, image.im.resize, (2048, 1152), Image.BILINEAR))
print 'Bilinear  | 320x240   | {min:5.3f} | {max:5.3f} | {mean:5.3f} | {median:5.3f} | {stddev:5.4f} | {dev_pct:4.1f}%'.format(**timeit(n, image.im.resize, (320, 240),   Image.BILINEAR))

