from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageWin

from .helper import hopper, is_win32

# see https://github.com/python-pillow/Pillow/pull/1431#issuecomment-144692652

if is_win32():
    import ctypes
    import ctypes.wintypes

    class BITMAPFILEHEADER(ctypes.Structure):
        _pack_ = 2
        _fields_ = [
            ("bfType", ctypes.wintypes.WORD),
            ("bfSize", ctypes.wintypes.DWORD),
            ("bfReserved1", ctypes.wintypes.WORD),
            ("bfReserved2", ctypes.wintypes.WORD),
            ("bfOffBits", ctypes.wintypes.DWORD),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        _pack_ = 2
        _fields_ = [
            ("biSize", ctypes.wintypes.DWORD),
            ("biWidth", ctypes.wintypes.LONG),
            ("biHeight", ctypes.wintypes.LONG),
            ("biPlanes", ctypes.wintypes.WORD),
            ("biBitCount", ctypes.wintypes.WORD),
            ("biCompression", ctypes.wintypes.DWORD),
            ("biSizeImage", ctypes.wintypes.DWORD),
            ("biXPelsPerMeter", ctypes.wintypes.LONG),
            ("biYPelsPerMeter", ctypes.wintypes.LONG),
            ("biClrUsed", ctypes.wintypes.DWORD),
            ("biClrImportant", ctypes.wintypes.DWORD),
        ]

    BI_RGB = 0
    DIB_RGB_COLORS = 0

    memcpy = ctypes.cdll.msvcrt.memcpy
    memcpy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]

    windll = getattr(ctypes, "windll")
    CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
    CreateCompatibleDC.argtypes = [ctypes.wintypes.HDC]
    CreateCompatibleDC.restype = ctypes.wintypes.HDC

    DeleteDC = windll.gdi32.DeleteDC
    DeleteDC.argtypes = [ctypes.wintypes.HDC]

    SelectObject = windll.gdi32.SelectObject
    SelectObject.argtypes = [ctypes.wintypes.HDC, ctypes.wintypes.HGDIOBJ]
    SelectObject.restype = ctypes.wintypes.HGDIOBJ

    DeleteObject = windll.gdi32.DeleteObject
    DeleteObject.argtypes = [ctypes.wintypes.HGDIOBJ]

    CreateDIBSection = windll.gdi32.CreateDIBSection
    CreateDIBSection.argtypes = [
        ctypes.wintypes.HDC,
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
    ]
    CreateDIBSection.restype = ctypes.wintypes.HBITMAP

    def serialize_dib(bi: BITMAPINFOHEADER, pixels: ctypes.c_void_p) -> bytearray:
        bf = BITMAPFILEHEADER()
        bf.bfType = 0x4D42
        bf.bfOffBits = ctypes.sizeof(bf) + bi.biSize
        bf.bfSize = bf.bfOffBits + bi.biSizeImage
        bf.bfReserved1 = bf.bfReserved2 = 0

        buf = (ctypes.c_byte * bf.bfSize)()
        bp = ctypes.addressof(buf)
        memcpy(bp, ctypes.byref(bf), ctypes.sizeof(bf))
        memcpy(bp + ctypes.sizeof(bf), ctypes.byref(bi), bi.biSize)
        memcpy(bp + bf.bfOffBits, pixels, bi.biSizeImage)
        return bytearray(buf)

    def test_pointer(tmp_path: Path) -> None:
        im = hopper()
        (width, height) = im.size
        opath = str(tmp_path / "temp.png")
        imdib = ImageWin.Dib(im)

        hdr = BITMAPINFOHEADER()
        hdr.biSize = ctypes.sizeof(hdr)
        hdr.biWidth = width
        hdr.biHeight = height
        hdr.biPlanes = 1
        hdr.biBitCount = 32
        hdr.biCompression = BI_RGB
        hdr.biSizeImage = width * height * 4
        hdr.biClrUsed = 0
        hdr.biClrImportant = 0

        hdc = CreateCompatibleDC(None)
        pixels = ctypes.c_void_p()
        dib = CreateDIBSection(
            hdc, ctypes.byref(hdr), DIB_RGB_COLORS, ctypes.byref(pixels), None, 0
        )
        SelectObject(hdc, dib)

        imdib.expose(hdc)
        bitmap = serialize_dib(hdr, pixels)
        DeleteObject(dib)
        DeleteDC(hdc)

        with Image.open(BytesIO(bitmap)) as im:
            im.save(opath)
