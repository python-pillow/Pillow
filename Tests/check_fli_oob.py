#!/usr/bin/env python3

from PIL import Image

repro_ss2 = (
    "images/fli_oob/06r/06r00.fli",
    "images/fli_oob/06r/others/06r01.fli",
    "images/fli_oob/06r/others/06r02.fli",
    "images/fli_oob/06r/others/06r03.fli",
    "images/fli_oob/06r/others/06r04.fli",
)

repro_lc = (
    "images/fli_oob/05r/05r00.fli",
    "images/fli_oob/05r/others/05r03.fli",
    "images/fli_oob/05r/others/05r06.fli",
    "images/fli_oob/05r/others/05r05.fli",
    "images/fli_oob/05r/others/05r01.fli",
    "images/fli_oob/05r/others/05r04.fli",
    "images/fli_oob/05r/others/05r02.fli",
    "images/fli_oob/05r/others/05r07.fli",
    "images/fli_oob/patch0/000000",
    "images/fli_oob/patch0/000001",
    "images/fli_oob/patch0/000002",
    "images/fli_oob/patch0/000003",
)


repro_advance = (
    "images/fli_oob/03r/03r00.fli",
    "images/fli_oob/03r/others/03r01.fli",
    "images/fli_oob/03r/others/03r09.fli",
    "images/fli_oob/03r/others/03r11.fli",
    "images/fli_oob/03r/others/03r05.fli",
    "images/fli_oob/03r/others/03r10.fli",
    "images/fli_oob/03r/others/03r06.fli",
    "images/fli_oob/03r/others/03r08.fli",
    "images/fli_oob/03r/others/03r03.fli",
    "images/fli_oob/03r/others/03r07.fli",
    "images/fli_oob/03r/others/03r02.fli",
    "images/fli_oob/03r/others/03r04.fli",
)

repro_brun = (
    "images/fli_oob/04r/initial.fli",
    "images/fli_oob/04r/others/04r02.fli",
    "images/fli_oob/04r/others/04r05.fli",
    "images/fli_oob/04r/others/04r04.fli",
    "images/fli_oob/04r/others/04r03.fli",
    "images/fli_oob/04r/others/04r01.fli",
    "images/fli_oob/04r/04r00.fli",
)

repro_copy = (
    "images/fli_oob/02r/others/02r02.fli",
    "images/fli_oob/02r/others/02r04.fli",
    "images/fli_oob/02r/others/02r03.fli",
    "images/fli_oob/02r/others/02r01.fli",
    "images/fli_oob/02r/02r00.fli",
)


for path in repro_ss2 + repro_lc + repro_advance + repro_brun + repro_copy:
    im = Image.open(path)
    try:
        im.load()
    except Exception as msg:
        print(msg)
