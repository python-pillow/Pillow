from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("Tests/fonts/NotoSans-Regular.ttf", 16)


def test(anchor):
    im = Image.new("RGBA", (200, 100), "white")
    d = ImageDraw.Draw(im)
    d.line(((100, 0), (100, 100)), "gray")
    d.line(((0, 50), (200, 50)), "gray")
    d.text((100, 50), f"{anchor} example", "black", font, anchor)
    return im


if __name__ == "__main__":
    im = Image.new("RGBA", (600, 300), "white")
    d = ImageDraw.Draw(im)
    for y, row in enumerate(
        (("ma", "mt", "mm"), ("ms", "mb", "md"), ("ls", "ms", "rs"))
    ):
        for x, anchor in enumerate(row):
            im.paste(test(anchor), (x * 200, y * 100))
            if x != 0:
                d.line(((x * 200, y * 100), (x * 200, (y + 1) * 100)), "black", 3)
            if y != 0:
                d.line(((x * 200, y * 100), ((x + 1) * 200, y * 100)), "black", 3)
    im.save("docs/example/anchors.png")
    im.show()
