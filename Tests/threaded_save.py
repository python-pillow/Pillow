from PIL import Image

import io
import queue
import sys
import threading
import time

try:
    format = sys.argv[1]
except:
    format = "PNG"

im = Image.open("Tests/images/hopper.ppm")
im.load()

queue = queue.Queue()

result = []


class Worker(threading.Thread):
    def run(self):
        while True:
            im = queue.get()
            if im is None:
                queue.task_done()
                sys.stdout.write("x")
                break
            f = io.BytesIO()
            im.save(f, format, optimize=1)
            data = f.getvalue()
            result.append(len(data))
            im = Image.open(io.BytesIO(data))
            im.load()
            sys.stdout.write(".")
            queue.task_done()

t0 = time.time()

threads = 20
jobs = 100

for i in range(threads):
    w = Worker()
    w.start()

for i in range(jobs):
    queue.put(im)

for i in range(threads):
    queue.put(None)

queue.join()

print()
print(time.time() - t0)
print(len(result), sum(result))
print(result)
