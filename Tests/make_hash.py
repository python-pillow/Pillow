# brute-force search for access descriptor hash table

modes = [
    "1",
    "L", "LA",
    "I", "I;16", "I;16L", "I;16B", "I;32L", "I;32B",
    "F",
    "P", "PA",
    "RGB", "RGBA", "RGBa", "RGBX",
    "CMYK",
    "YCbCr",
    "LAB", "HSV",
    ]


def hash(s, i):
    # djb2 hash: multiply by 33 and xor character
    for c in s:
        i = (((i << 5) + i) ^ ord(c)) & 0xffffffff
    return i


def check(size, i0):
    h = [None] * size
    for m in modes:
        i = hash(m, i0)
        i = i % size
        if h[i]:
            return 0
        h[i] = m
    return h

min_start = 0

# 1) find the smallest table size with no collisions
for min_size in range(len(modes), 16384):
    if check(min_size, 0):
        print(len(modes), "modes fit in", min_size, "slots")
        break

# 2) see if we can do better with a different initial value
for i0 in range(65556):
    for size in range(1, min_size):
        if check(size, i0):
            if size < min_size:
                print(len(modes), "modes fit in", size, "slots with start", i0)
                min_size = size
                min_start = i0

print()

# print check(min_size, min_start)

print("#define ACCESS_TABLE_SIZE", min_size)
print("#define ACCESS_TABLE_HASH", min_start)

# for m in modes:
#     print m, "=>", hash(m, min_start) % min_size
