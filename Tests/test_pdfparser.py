import time

import pytest

from PIL.PdfParser import (
    IndirectObjectDef,
    IndirectReference,
    PdfBinary,
    PdfDict,
    PdfFormatError,
    PdfName,
    PdfParser,
    PdfStream,
    decode_text,
    encode_text,
    pdf_repr,
)


def test_text_encode_decode():
    assert encode_text("abc") == b"\xFE\xFF\x00a\x00b\x00c"
    assert decode_text(b"\xFE\xFF\x00a\x00b\x00c") == "abc"
    assert decode_text(b"abc") == "abc"
    assert decode_text(b"\x1B a \x1C") == "\u02D9 a \u02DD"


def test_indirect_refs():
    assert IndirectReference(1, 2) == IndirectReference(1, 2)
    assert IndirectReference(1, 2) != IndirectReference(1, 3)
    assert IndirectReference(1, 2) != IndirectObjectDef(1, 2)
    assert IndirectReference(1, 2) != (1, 2)
    assert IndirectObjectDef(1, 2) == IndirectObjectDef(1, 2)
    assert IndirectObjectDef(1, 2) != IndirectObjectDef(1, 3)
    assert IndirectObjectDef(1, 2) != IndirectReference(1, 2)
    assert IndirectObjectDef(1, 2) != (1, 2)


def test_parsing():
    assert PdfParser.interpret_name(b"Name#23Hash") == b"Name#Hash"
    assert PdfParser.interpret_name(b"Name#23Hash", as_text=True) == "Name#Hash"
    assert PdfParser.get_value(b"1 2 R ", 0) == (IndirectReference(1, 2), 5)
    assert PdfParser.get_value(b"true[", 0) == (True, 4)
    assert PdfParser.get_value(b"false%", 0) == (False, 5)
    assert PdfParser.get_value(b"null<", 0) == (None, 4)
    assert PdfParser.get_value(b"%cmt\n %cmt\n 123\n", 0) == (123, 15)
    assert PdfParser.get_value(b"<901FA3>", 0) == (b"\x90\x1F\xA3", 8)
    assert PdfParser.get_value(b"asd < 9 0 1 f A > qwe", 3) == (b"\x90\x1F\xA0", 17)
    assert PdfParser.get_value(b"(asd)", 0) == (b"asd", 5)
    assert PdfParser.get_value(b"(asd(qwe)zxc)zzz(aaa)", 0) == (b"asd(qwe)zxc", 13)
    assert PdfParser.get_value(b"(Two \\\nwords.)", 0) == (b"Two words.", 14)
    assert PdfParser.get_value(b"(Two\nlines.)", 0) == (b"Two\nlines.", 12)
    assert PdfParser.get_value(b"(Two\r\nlines.)", 0) == (b"Two\nlines.", 13)
    assert PdfParser.get_value(b"(Two\\nlines.)", 0) == (b"Two\nlines.", 13)
    assert PdfParser.get_value(b"(One\\(paren).", 0) == (b"One(paren", 12)
    assert PdfParser.get_value(b"(One\\)paren).", 0) == (b"One)paren", 12)
    assert PdfParser.get_value(b"(\\0053)", 0) == (b"\x053", 7)
    assert PdfParser.get_value(b"(\\053)", 0) == (b"\x2B", 6)
    assert PdfParser.get_value(b"(\\53)", 0) == (b"\x2B", 5)
    assert PdfParser.get_value(b"(\\53a)", 0) == (b"\x2Ba", 6)
    assert PdfParser.get_value(b"(\\1111)", 0) == (b"\x491", 7)
    assert PdfParser.get_value(b" 123 (", 0) == (123, 4)
    assert round(abs(PdfParser.get_value(b" 123.4 %", 0)[0] - 123.4), 7) == 0
    assert PdfParser.get_value(b" 123.4 %", 0)[1] == 6
    with pytest.raises(PdfFormatError):
        PdfParser.get_value(b"]", 0)
    d = PdfParser.get_value(b"<</Name (value) /N /V>>", 0)[0]
    assert isinstance(d, PdfDict)
    assert len(d) == 2
    assert d.Name == "value"
    assert d[b"Name"] == b"value"
    assert d.N == PdfName("V")
    a = PdfParser.get_value(b"[/Name (value) /N /V]", 0)[0]
    assert isinstance(a, list)
    assert len(a) == 4
    assert a[0] == PdfName("Name")
    s = PdfParser.get_value(
        b"<</Name (value) /Length 5>>\nstream\nabcde\nendstream<<...", 0
    )[0]
    assert isinstance(s, PdfStream)
    assert s.dictionary.Name == "value"
    assert s.decode() == b"abcde"
    for name in ["CreationDate", "ModDate"]:
        for date, value in {
            b"20180729214124": "20180729214124",
            b"D:20180729214124": "20180729214124",
            b"D:2018072921": "20180729210000",
            b"D:20180729214124Z": "20180729214124",
            b"D:20180729214124+08'00'": "20180729134124",
            b"D:20180729214124-05'00'": "20180730024124",
        }.items():
            d = PdfParser.get_value(b"<</" + name.encode() + b" (" + date + b")>>", 0)[
                0
            ]
            assert time.strftime("%Y%m%d%H%M%S", getattr(d, name)) == value


def test_pdf_repr():
    assert bytes(IndirectReference(1, 2)) == b"1 2 R"
    assert bytes(IndirectObjectDef(*IndirectReference(1, 2))) == b"1 2 obj"
    assert bytes(PdfName(b"Name#Hash")) == b"/Name#23Hash"
    assert bytes(PdfName("Name#Hash")) == b"/Name#23Hash"
    assert bytes(PdfDict({b"Name": IndirectReference(1, 2)})) == b"<<\n/Name 1 2 R\n>>"
    assert bytes(PdfDict({"Name": IndirectReference(1, 2)})) == b"<<\n/Name 1 2 R\n>>"
    assert pdf_repr(IndirectReference(1, 2)) == b"1 2 R"
    assert pdf_repr(IndirectObjectDef(*IndirectReference(1, 2))) == b"1 2 obj"
    assert pdf_repr(PdfName(b"Name#Hash")) == b"/Name#23Hash"
    assert pdf_repr(PdfName("Name#Hash")) == b"/Name#23Hash"
    assert (
        pdf_repr(PdfDict({b"Name": IndirectReference(1, 2)})) == b"<<\n/Name 1 2 R\n>>"
    )
    assert (
        pdf_repr(PdfDict({"Name": IndirectReference(1, 2)})) == b"<<\n/Name 1 2 R\n>>"
    )
    assert pdf_repr(123) == b"123"
    assert pdf_repr(True) == b"true"
    assert pdf_repr(False) == b"false"
    assert pdf_repr(None) == b"null"
    assert pdf_repr(b"a)/b\\(c") == br"(a\)/b\\\(c)"
    assert pdf_repr([123, True, {"a": PdfName(b"b")}]) == b"[ 123 true <<\n/a /b\n>> ]"
    assert pdf_repr(PdfBinary(b"\x90\x1F\xA0")) == b"<901FA0>"
