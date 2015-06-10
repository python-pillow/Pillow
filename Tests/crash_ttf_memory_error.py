from PIL import Image, ImageFont, ImageDraw

font = "../pil-archive/memory-error-2.ttf"

s = "Test Text"
f = ImageFont.truetype(font, 64, index=0, encoding="unicode")
w, h = f.getsize(s)
i = Image.new("RGB", (500, h), "white")
d = ImageDraw.Draw(i)

# this line causes a MemoryError
d.text((0, 0), s, font=f, fill=0)

i.show()
