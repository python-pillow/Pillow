#!/usr/bin/env python3
import base64
import os

if __name__ == "__main__":
    # create font data chunk for embedding
    font = "Tests/images/courB08"
    print("    f._load_pilfont_data(")
    print(f"         # {os.path.basename(font)}")
    print("         BytesIO(base64.decodestring(b'''")
    with open(font + ".pil", "rb") as fp:
        print(base64.b64encode(fp.read()).decode())
    print("''')), Image.open(BytesIO(base64.decodestring(b'''")
    with open(font + ".pbm", "rb") as fp:
        print(base64.b64encode(fp.read()).decode())
    print("'''))))")
