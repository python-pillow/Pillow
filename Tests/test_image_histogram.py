from __future__ import annotations

import base64
import hashlib

import pytest

from PIL import Image

from .helper import hopper

expected_data = {
    "1": (256, 16384, 0, 10994, b"zk4Al^)(jtioYSyJT@emR4<LAz}yHLJ6>*b*%R1K"),
    "CMYK": (1024, 65536, 0, 16384, b"zqm8<<;r>h42v|$3xNIR#fG2=P&z(awe2&{GK(8o"),
    "F": (256, 16384, 0, 662, b"*EIrB8n_NEx9e()#ao<>L)@gEjm|N%I8B)YhA8V~"),
    "HSV": (768, 49152, 0, 1696, b"F6vt%@sQf%X04Md4^n!Qpv!qJ8Oz()CqPx=rjFvu"),
    "I": (256, 16384, 0, 662, b"*EIrB8n_NEx9e()#ao<>L)@gEjm|N%I8B)YhA8V~"),
    "I;16": (256, 16384, 0, 8192, b"S+c=3i+Fs3wK2>Q<8rq@PgsAg=nE1VLdMtHZ2K8$"),
    "I;16B": (256, 16384, 0, 8192, b"S+c=3i+Fs3wK2>Q<8rq@PgsAg=nE1VLdMtHZ2K8$"),
    "I;16L": (256, 16384, 0, 8192, b"S+c=3i+Fs3wK2>Q<8rq@PgsAg=nE1VLdMtHZ2K8$"),
    "I;16N": (256, 16384, 0, 8192, b"S+c=3i+Fs3wK2>Q<8rq@PgsAg=nE1VLdMtHZ2K8$"),
    "L": (256, 16384, 0, 662, b"EmZC)FNJ#AK=O?2(qxYeY#*-vk97Iz%f8!<LaY}1"),
    "LA": (512, 32768, 0, 662, b"Eds{eGw)qbudo%xtTJ_6#d5In@<fQMK3Kn%5!9;0"),
    "La": (512, 32768, 0, 662, b"Eds{eGw)qbudo%xtTJ_6#d5In@<fQMK3Kn%5!9;0"),
    "LAB": (768, 49152, 0, 1946, b"9X3PUSDkz%k~jXeBH}f4?u?ga;js`?-81}2(RAPF"),
    "P": (256, 16384, 0, 1551, b"mCdCL$^NJhLi#i!x{jz~<&y%a{iVi(H(JP}W5-Op"),
    "PA": (512, 32768, 0, 1551, b"r_3_AMV`<vvmH_kY7ulvv|2QT==P{6rpFz6)D>~q"),
    "RGB": (768, 49152, 4, 675, b"!TjBr^o$}ZXlfh|aIU7&4VKP8=rBq&RecVDIcndZ"),
    "RGBA": (1024, 65536, 0, 16384, b"du`JBXvzDrPu^Ybc}8Y+4y1MDTEK|!Q|rR~Jk^@J"),
    "RGBa": (1024, 65536, 0, 16384, b"du`JBXvzDrPu^Ybc}8Y+4y1MDTEK|!Q|rR~Jk^@J"),
    "RGBX": (1024, 65536, 0, 16384, b"du`JBXvzDrPu^Ybc}8Y+4y1MDTEK|!Q|rR~Jk^@J"),
    "YCbCr": (768, 49152, 0, 1908, b"%z+JjEuI^YFOt*}($tSuSk^nX-~-HI>QDL>T%9H9"),
}


# Python's basic hash() function isn't necessarily deterministic, so use this instead.
def deterministic_hash(data: list[int]) -> bytes:
    data_bytes = str(data).encode("ascii")
    hash_digest = hashlib.sha256(data_bytes).digest()
    return base64.b85encode(hash_digest)


@pytest.mark.parametrize("mode", Image.MODES)
def test_histogram(mode: str) -> None:
    h = hopper(mode).histogram()
    data = (len(h), sum(h), min(h), max(h), deterministic_hash(h))
    assert data == expected_data[mode]
