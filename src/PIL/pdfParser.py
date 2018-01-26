import codecs
import collections
import io
import mmap
import re
import sys

try:
    from UserDict import UserDict
except ImportError:
    UserDict = collections.UserDict


if str == bytes:  # Python 2.x
    make_bytes = lambda s: s  # pragma: no cover
else:  # Python 3.x
    def make_bytes(s):
        return s.encode("us-ascii")


# see 7.9.2.2 Text String Type on page 86 and D.3 PDFDocEncoding Character Set on page 656
def encode_text(s):
    return codecs.BOM_UTF16_BE + s.encode("utf_16_be")


PDFDocEncoding = {
    0x16: u"\u0017",
    0x18: u"\u02D8",
    0x19: u"\u02C7",
    0x1A: u"\u02C6",
    0x1B: u"\u02D9",
    0x1C: u"\u02DD",
    0x1D: u"\u02DB",
    0x1E: u"\u02DA",
    0x1F: u"\u02DC",
    0x80: u"\u2022",
    0x81: u"\u2020",
    0x82: u"\u2021",
    0x83: u"\u2026",
    0x84: u"\u2014",
    0x85: u"\u2013",
    0x86: u"\u0192",
    0x87: u"\u2044",
    0x88: u"\u2039",
    0x89: u"\u203A",
    0x8A: u"\u2212",
    0x8B: u"\u2030",
    0x8C: u"\u201E",
    0x8D: u"\u201C",
    0x8E: u"\u201D",
    0x8F: u"\u2018",
    0x90: u"\u2019",
    0x91: u"\u201A",
    0x92: u"\u2122",
    0x93: u"\uFB01",
    0x94: u"\uFB02",
    0x95: u"\u0141",
    0x96: u"\u0152",
    0x97: u"\u0160",
    0x98: u"\u0178",
    0x99: u"\u017D",
    0x9A: u"\u0131",
    0x9B: u"\u0142",
    0x9C: u"\u0153",
    0x9D: u"\u0161",
    0x9E: u"\u017E",
    0xA0: u"\u20AC",
    }
def decode_text(b):
    if b[:len(codecs.BOM_UTF16_BE)] == codecs.BOM_UTF16_BE:
        return b[len(codecs.BOM_UTF16_BE):].decode("utf_16_be")
    elif str == bytes:  # Python 2.x
        return u"".join(PDFDocEncoding.get(ord(byte), byte) for byte in b)
    else:
        return "".join(PDFDocEncoding.get(byte, chr(byte)) for byte in b)


class PdfFormatError(RuntimeError):
    pass


def check_format_condition(condition, error_message):
    if not condition:
        raise PdfFormatError(error_message)


class IndirectReference(collections.namedtuple("IndirectReferenceTuple", ["object_id", "generation"])):
    def __str__(self):
        return "%s %s R" % self

    def __bytes__(self):
        return self.__str__().encode("us-ascii")

    def __eq__(self, other):
        return other.__class__ is self.__class__ and other.object_id == self.object_id and other.generation == self.generation

    def __ne__(self, other):
        return not (self == other)


class IndirectObjectDef(IndirectReference):
    def __str__(self):
        return "%s %s obj" % self


class XrefTable:
    def __init__(self):
        self.existing_entries = {}          # object ID => (offset, generation)
        self.new_entries = {}               # object ID => (offset, generation)
        self.deleted_entries = {0: 65536}   # object ID => generation
        self.reading_finished = False

    def __setitem__(self, key, value):
        if self.reading_finished:
            self.new_entries[key] = value
        else:
            self.existing_entries[key] = value
        if key in self.deleted_entries:
            del self.deleted_entries[key]

    def __getitem__(self, key):
        try:
            return self.new_entries[key]
        except KeyError:
            return self.existing_entries[key]

    def __delitem__(self, key):
        if key in self.new_entries:
            generation = self.new_entries[key][1] + 1
            del self.new_entries[key]
            self.deleted_entries[key] = generation
        elif key in self.existing_entries:
            generation = self.existing_entries[key][1] + 1
            self.deleted_entries[key] = generation
        elif key in self.deleted_entries:
            generation = self.deleted_entries[key]
        else:
            raise IndexError("object ID " + str(key) + " cannot be deleted because it doesn't exist")

    def __contains__(self, key):
        return key in self.existing_entries or key in self.new_entries

    def __len__(self):
        return len(set(self.existing_entries.keys()) | set(self.new_entries.keys()) | set(self.deleted_entries.keys()))

    def keys(self):
        return (set(self.existing_entries.keys()) - set(self.deleted_entries.keys())) | set(self.new_entries.keys())

    def write(self, f):
        keys = sorted(set(self.new_entries.keys()) | set(self.deleted_entries.keys()))
        deleted_keys = sorted(set(self.deleted_entries.keys()))
        startxref = f.tell()
        f.write(b"xref\n")
        while keys:
            # find a contiguous sequence of object IDs
            prev = None
            for index, key in enumerate(keys):
                if prev is None or prev+1 == key:
                    prev = key
                else:
                    contiguous_keys = keys[:index]
                    keys = keys[index:]
                    break
            else:
                contiguous_keys = keys
                keys = None
            f.write(make_bytes("%d %d\n" % (contiguous_keys[0], len(contiguous_keys))))
            for object_id in contiguous_keys:
                if object_id in self.new_entries:
                    f.write(make_bytes("%010d %05d n \n" % self.new_entries[object_id]))
                else:
                    this_deleted_object_id = deleted_keys.pop(0)
                    assert object_id == this_deleted_object_id
                    try:
                        next_in_linked_list = deleted_keys[0]
                    except IndexError:
                        next_in_linked_list = 0
                    f.write(make_bytes("%010d %05d f \n" % (next_in_linked_list, self.deleted_entries[object_id])))
        return startxref


class PdfName():
    def __init__(self, name):
        if isinstance(name, PdfName):
            self.name = name.name
        elif isinstance(name, bytes):
            self.name = name
        else:
            self.name = name.encode("us-ascii")

    @classmethod
    def from_pdf_stream(klass, data):
        return klass(PdfParser.interpret_name(data))

    allowed_chars = set(range(33,127)) - set((ord(c) for c in "#%/()<>[]{}"))
    def __bytes__(self):
        if str == bytes:  # Python 2.x
            result = bytearray(b"/")
            for b in self.name:
                if ord(b) in self.allowed_chars:
                    result.append(b)
                else:
                    result.extend(b"#%02X" % ord(b))
        else:  # Python 3.x
            result = bytearray(b"/")
            for b in self.name:
                if b in self.allowed_chars:
                    result.append(b)
                else:
                    result.extend(make_bytes("#%02X" % b))
        return bytes(result)

    __str__ = __bytes__


class PdfArray(list):
    def __bytes__(self):
        return b"[ " + b" ".join(pdf_repr(x) for x in self) + b" ]"

    __str__ = __bytes__


class PdfDict(UserDict):
    def __init__(self, *args, **kwargs):
        UserDict.__init__(self, *args, **kwargs)

    def __setattr__(self, key, value):
        if key == "data":
            UserDict.__setattr__(self, key, value)
        else:
            if isinstance(key, str):
                key = key.encode("us-ascii")
            self[key] = value

    def __getattr__(self, key):
        try:
            value = self[key]
        except KeyError:
            value = self[key.encode("us-ascii")]
        if isinstance(value, bytes):
            return decode_text(value)
        else:
            return value

    def __bytes__(self):
        out = bytearray(b"<<")
        for key, value in self.items():
            if value is None:
                continue
            value = pdf_repr(value)
            out.extend(b"\n")
            out.extend(bytes(PdfName(key)))
            out.extend(b" ")
            out.extend(value)
        out.extend(b"\n>>")
        return bytes(out)
        #return out + b"\n>>"

    if str == bytes:
        __str__ = __bytes__


class PdfBinary:
    def __init__(self, data):
        self.data = data

    if str == bytes:  # Python 2.x
        def __str__(self):
            return "<%s>" % "".join("%02X" % ord(b) for b in self.data)

    else:  # Python 3.x
        def __bytes__(self):
            return make_bytes("<%s>" % "".join("%02X" % b for b in self.data))


def pdf_repr(x):
    if x is True:
        return b"true"
    elif x is False:
        return b"false"
    elif x is None:
        return b"null"
    elif isinstance(x, PdfName) or isinstance(x, PdfDict) or isinstance(x, PdfArray) or isinstance(x, PdfBinary):
        return bytes(x)
    elif isinstance(x, int):
        return str(x).encode("us-ascii")
    elif isinstance(x, dict):
        return bytes(PdfDict(x))
    elif isinstance(x, list):
        return bytes(PdfArray(x))
    elif isinstance(x, str) and str != bytes:
        return pdf_repr(encode_text(x))
    elif isinstance(x, bytes):
        return b"(" + x.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)") + b")"  # XXX escape more chars? handle binary garbage
    else:
        return bytes(x)


class PdfParser:
    """Based on http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
    Supports PDF up to 1.4
    """

    def __init__(self, filename=None, f=None, buf=None, start_offset=0):
        self.filename = filename
        self.buf = buf
        self.start_offset = start_offset
        if buf is not None:
            self.read_pdf_info()
        elif f is not None:
            self.read_pdf_info_from_file(f)
        elif filename is not None:
            with open(filename, "rb") as f:
                self.read_pdf_info_from_file(f)
        else:
            self.file_size_total = self.file_size_this = 0
            self.root = PdfDict()
            self.root_ref = None
            self.info = PdfDict()
            self.info_ref = None
            self.page_tree_root = {}
            self.pages = []
            self.pages_ref = None
            self.last_xref_section_offset = None
            self.trailer_dict = {}
            self.xref_table = XrefTable()
        self.xref_table.reading_finished = True

    def write_header(self, f):
        f.write(b"%PDF-1.4\n")

    def write_comment(self, f, s):
        f.write(("%% %s\n" % (s,)).encode("utf-8"))

    def write_catalog(self, f):
        self.del_root()
        self.root_ref = self.next_object_id(f.tell())
        self.pages_ref = self.next_object_id(0)
        self.write_obj(f, self.root_ref,
            Type=PdfName(b"Catalog"),
            Pages=self.pages_ref)
        self.write_obj(f, self.pages_ref,
            Type=PdfName("Pages"),
            Count=len(self.pages),
            Kids=self.pages)
        return self.root_ref

    def write_xref_and_trailer(self, f, new_root_ref=None):
        if new_root_ref:
            self.del_root()
            self.root_ref = new_root_ref
        if self.info:
            self.info_ref = self.write_obj(f, None, self.info)
        start_xref = self.xref_table.write(f)
        num_entries = len(self.xref_table)
        trailer_dict = {b"Root": self.root_ref, b"Size": num_entries}
        if self.last_xref_section_offset is not None:
            trailer_dict[b"Prev"] = self.last_xref_section_offset
        if self.info:
            trailer_dict[b"Info"] = self.info_ref
        self.last_xref_section_offset = start_xref
        f.write(b"trailer\n" + bytes(PdfDict(trailer_dict)) + make_bytes("\nstartxref\n%d\n%%%%EOF" % start_xref))

    def write_page(self, f, ref, *objs, **dict_obj):
        if isinstance(ref, int):
            ref = self.pages[ref]
        if "Type" not in dict_obj:
            dict_obj["Type"] = PdfName("Page")
        if "Parent" not in dict_obj:
            dict_obj["Parent"] = self.pages_ref
        return self.write_obj(f, ref, *objs, **dict_obj)

    def write_obj(self, f, ref, *objs, **dict_obj):
        if ref is None:
            ref = self.next_object_id(f.tell())
        else:
            self.xref_table[ref.object_id] = (f.tell(), ref.generation)
        f.write(bytes(IndirectObjectDef(*ref)))
        stream = dict_obj.pop("stream", None)
        if stream is not None:
            dict_obj["Length"] = len(stream)
        if dict_obj:
            f.write(pdf_repr(dict_obj))
        for obj in objs:
            f.write(pdf_repr(obj))
        if stream is not None:
            f.write(b"stream\n")
            f.write(stream)
            f.write(b"\nendstream\n")
        f.write(b"endobj\n")
        return ref

    def del_root(self):
        if self.root_ref is None:
            return
        del self.xref_table[self.root_ref.object_id]
        del self.xref_table[self.root[b"Pages"].object_id]
        # XXX TODO delete Pages tree recursively

    def read_pdf_info_from_file(self, f):
        if hasattr(f, "getbuffer"):
            self.buf = f.getbuffer()
            need_close = False
        elif hasattr(f, "getvalue"):
            self.buf = f.getvalue()
            need_close = False
        else:
            self.buf = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            need_close = True
        try:
            self.read_pdf_info()
        finally:
            if need_close:
                self.buf.close()
            self.buf = None

    def read_pdf_info(self):
        self.file_size_total = len(self.buf)
        self.file_size_this = self.file_size_total - self.start_offset
        self.read_trailer()
        self.root_ref = self.trailer_dict[b"Root"]
        self.info_ref = self.trailer_dict.get(b"Info", None)
        self.root = PdfDict(self.read_indirect(self.root_ref))
        if self.info_ref is None:
            self.info = PdfDict()
        else:
            self.info = PdfDict(self.read_indirect(self.info_ref))
        #print(repr(self.root))
        check_format_condition(b"Type" in self.root, "/Type missing in Root")
        check_format_condition(self.root[b"Type"] == b"Catalog", "/Type in Root is not /Catalog")
        check_format_condition(b"Pages" in self.root, "/Pages missing in Root")
        check_format_condition(isinstance(self.root[b"Pages"], IndirectReference), "/Pages in Root is not an indirect reference")
        self.pages_ref = self.root[b"Pages"]
        self.page_tree_root = self.read_indirect(self.pages_ref)
        #print("page_tree_root: " + str(self.page_tree_root))
        self.pages = self.linearize_page_tree(self.page_tree_root)
        #print("pages: " + str(self.pages))

    def next_object_id(self, offset=None):
        try:
            # TODO: support reuse of deleted objects
            reference = IndirectReference(max(self.xref_table.keys()) + 1, 0)
        except ValueError:
            reference = IndirectReference(1, 0)
        if offset is not None:
            self.xref_table[reference.object_id] = (offset, 0)
        return reference

    delimiter = br"[][()<>{}/%]"
    delimiter_or_ws = br"[][()<>{}/%\000\011\012\014\015\040]"
    whitespace = br"[\000\011\012\014\015\040]"
    whitespace_or_hex = br"[\000\011\012\014\015\0400-9a-fA-F]"
    whitespace_optional = whitespace + b"*"
    whitespace_mandatory = whitespace + b"+"
    newline_only = br"[\r\n]+"
    newline = whitespace_optional + newline_only + whitespace_optional
    re_trailer_end = re.compile(whitespace_mandatory + br"trailer" + whitespace_optional + br"\<\<(.*\>\>)" + newline \
        + br"startxref" + newline + br"([0-9]+)" + newline + br"%%EOF" + whitespace_optional + br"$", re.DOTALL)
    re_trailer_prev = re.compile(whitespace_optional + br"trailer" + whitespace_optional + br"\<\<(.*?\>\>)" + newline \
        + br"startxref" + newline + br"([0-9]+)" + newline + br"%%EOF" + whitespace_optional, re.DOTALL)
    def read_trailer(self):
        search_start_offset = len(self.buf) - 16384
        if search_start_offset < self.start_offset:
            search_start_offset = self.start_offset
        #data_at_end = self.buf[search_start_offset:]
        #m = self.re_trailer_end.search(data_at_end)
        m = self.re_trailer_end.search(self.buf, search_start_offset)
        check_format_condition(m, "trailer end not found")
        # make sure we found the LAST trailer
        last_match = m
        while m:
            last_match = m
            m = self.re_trailer_end.search(self.buf, m.start()+16)
        if not m:
            m = last_match
        trailer_data = m.group(1)
        #print(trailer_data)
        self.last_xref_section_offset = int(m.group(2))
        self.trailer_dict = self.interpret_trailer(trailer_data)
        self.xref_table = XrefTable()
        self.read_xref_table(xref_section_offset=self.last_xref_section_offset)
        #print(self.xref_table)
        if b"Prev" in self.trailer_dict:
            self.read_prev_trailer(self.trailer_dict[b"Prev"])

    def read_prev_trailer(self, xref_section_offset):
        trailer_offset = self.read_xref_table(xref_section_offset=xref_section_offset)
        m = self.re_trailer_prev.search(self.buf[trailer_offset:trailer_offset+16384])
        check_format_condition(m, "previous trailer not found")
        trailer_data = m.group(1)
        #print(trailer_data)
        check_format_condition(int(m.group(2)) == xref_section_offset, "xref section offset in previous trailer doesn't match what was expected")
        trailer_dict = self.interpret_trailer(trailer_data)
        if b"Prev" in trailer_dict:
            self.read_prev_trailer(trailer_dict[b"Prev"])

    re_whitespace_optional = re.compile(whitespace_optional)
    re_name = re.compile(whitespace_optional + br"/([!-$&'*-.0-;=?-Z\\^-z|~]+)(?=" + delimiter_or_ws + br")")
    re_dict_start = re.compile(whitespace_optional + br"\<\<")
    re_dict_end = re.compile(whitespace_optional + br"\>\>" + whitespace_optional)
    @classmethod
    def interpret_trailer(klass, trailer_data):
        trailer = {}
        offset = 0
        while True:
            m = klass.re_name.match(trailer_data, offset)
            if not m:
                m = klass.re_dict_end.match(trailer_data, offset)
                check_format_condition(m and m.end() == len(trailer_data), "name not found in trailer, remaining data: " + repr(trailer_data[offset:]))
                break
            key = klass.interpret_name(m.group(1))
            #print(key)
            value, offset = klass.get_value(trailer_data, m.end())
            #print(value)
            trailer[key] = value
        check_format_condition(b"Size" in trailer and isinstance(trailer[b"Size"], int), "/Size not in trailer or not an integer")
        check_format_condition(b"Root" in trailer and isinstance(trailer[b"Root"], IndirectReference), "/Root not in trailer or not an indirect reference")
        return trailer

    re_hashes_in_name = re.compile(br"([^#]*)(#([0-9a-fA-F]{2}))?")
    @classmethod
    def interpret_name(klass, raw, as_text=False):
        name = b""
        for m in klass.re_hashes_in_name.finditer(raw):
            if m.group(3):
                name += m.group(1) + bytearray.fromhex(m.group(3).decode("us-ascii"))
            else:
                name += m.group(1)
        if as_text:
            return name.decode("utf-8")
        else:
            return bytes(name)

    re_null = re.compile(whitespace_optional + br"null(?=" + delimiter_or_ws + br")")
    re_true = re.compile(whitespace_optional + br"true(?=" + delimiter_or_ws + br")")
    re_false = re.compile(whitespace_optional + br"false(?=" + delimiter_or_ws + br")")
    re_int = re.compile(whitespace_optional + br"([-+]?[0-9]+)(?=" + delimiter_or_ws + br")")
    re_real = re.compile(whitespace_optional + br"([-+]?([0-9]+\.[0-9]*|[0-9]*\.[0-9]+))(?=" + delimiter_or_ws + br")")
    re_array_start = re.compile(whitespace_optional + br"\[")
    re_array_end = re.compile(whitespace_optional + br"]")
    re_string_hex = re.compile(whitespace_optional + br"\<(" + whitespace_or_hex + br"*)\>")
    re_string_lit = re.compile(whitespace_optional + br"\(")
    re_indirect_reference = re.compile(whitespace_optional + br"([-+]?[0-9]+)" + whitespace_mandatory + br"([-+]?[0-9]+)" + whitespace_mandatory + br"R(?=" + delimiter_or_ws + br")")
    re_indirect_def_start = re.compile(whitespace_optional + br"([-+]?[0-9]+)" + whitespace_mandatory + br"([-+]?[0-9]+)" + whitespace_mandatory + br"obj(?=" + delimiter_or_ws + br")")
    re_indirect_def_end = re.compile(whitespace_optional + br"endobj(?=" + delimiter_or_ws + br")")
    re_comment = re.compile(br"(" + whitespace_optional + br"%[^\r\n]*" + newline + br")*")
    @classmethod
    def get_value(klass, data, offset, expect_indirect=None, max_nesting=-1):
        #if max_nesting == 0:
        #    return None, None
        m = klass.re_comment.match(data, offset)
        if m:
            offset = m.end()
        m = klass.re_indirect_def_start.match(data, offset)
        if m:
            assert int(m.group(1)) > 0
            assert int(m.group(2)) >= 0
            check_format_condition(expect_indirect is None or expect_indirect == IndirectReference(int(m.group(1)), int(m.group(2))),
                "indirect object definition different than expected")
            object, offset = klass.get_value(data, m.end(), max_nesting=max_nesting-1)
            if offset is None:
                return object, None
            m = klass.re_indirect_def_end.match(data, offset)
            check_format_condition(m, "indirect object definition end not found")
            return object, m.end()
        check_format_condition(not expect_indirect, "indirect object definition not found")
        m = klass.re_indirect_reference.match(data, offset)
        if m:
            assert int(m.group(1)) > 0
            assert int(m.group(2)) >= 0
            return IndirectReference(int(m.group(1)), int(m.group(2))), m.end()
        m = klass.re_dict_start.match(data, offset)
        if m:
            offset = m.end()
            result = {}
            #print("<<")
            m = klass.re_dict_end.match(data, offset)
            while not m:
                key, offset = klass.get_value(data, offset, max_nesting=max_nesting-1)
                #print ("key " + str(key))
                if offset is None:
                    return result, None
                value, offset = klass.get_value(data, offset, max_nesting=max_nesting-1)
                result[key] = value
                #print ("value " + str(value))
                if offset is None:
                    return result, None
                m = klass.re_dict_end.match(data, offset)
            #print(">>")
            return result, m.end()
        m = klass.re_array_start.match(data, offset)
        if m:
            offset = m.end()
            result = []
            m = klass.re_array_end.match(data, offset)
            while not m:
                value, offset = klass.get_value(data, offset, max_nesting=max_nesting-1)
                result.append(value)
                #print ("item " + str(value))
                if offset is None:
                    return result, None
                m = klass.re_array_end.match(data, offset)
            return result, m.end()
        m = klass.re_null.match(data, offset)
        if m:
            return None, m.end()
        m = klass.re_true.match(data, offset)
        if m:
            return True, m.end()
        m = klass.re_false.match(data, offset)
        if m:
            return False, m.end()
        m = klass.re_name.match(data, offset)
        if m:
            return klass.interpret_name(m.group(1)), m.end()
        m = klass.re_int.match(data, offset)
        if m:
            return int(m.group(1)), m.end()
        m = klass.re_real.match(data, offset)
        if m:
            return float(m.group(1)), m.end()  # XXX Decimal instead of float???
        m = klass.re_string_hex.match(data, offset)
        if m:
            hex_string = bytearray([b for b in m.group(1) if b in b"0123456789abcdefABCDEF"])  # filter out whitespace
            if len(hex_string) % 2 == 1:
                hex_string.append(ord(b"0"))  # append a 0 if the length is not even - yes, at the end
            return bytearray.fromhex(hex_string.decode("us-ascii")), m.end()
        m = klass.re_string_lit.match(data, offset)
        if m:
            return klass.get_literal_string(data, m.end())
        # XXX TODO: stream
        #return None, offset  # fallback (only for debugging)
        raise PdfFormatError("unrecognized object: " + repr(data[offset:offset+32]))


    re_lit_str_token = re.compile(br"(\\[nrtbf()\\])|(\\[0-9]{1,3})|(\\(\r\n|\r|\n))|(\r\n|\r|\n)|(\()|(\))")
    escaped_chars = {
        b"n": b"\n",
        b"r": b"\r",
        b"t": b"\t",
        b"b": b"\b",
        b"f": b"\f",
        b"(": b"(",
        b")": b")",
        b"\\": b"\\",
        ord(b"n"): b"\n",
        ord(b"r"): b"\r",
        ord(b"t"): b"\t",
        ord(b"b"): b"\b",
        ord(b"f"): b"\f",
        ord(b"("): b"(",
        ord(b")"): b")",
        ord(b"\\"): b"\\",
        }
    @classmethod
    def get_literal_string(klass, data, offset):
        nesting_depth = 0
        result = bytearray()
        for m in klass.re_lit_str_token.finditer(data, offset):
            result.extend(data[offset:m.start()])
            if m.group(1):
                result.extend(klass.escaped_chars[m.group(1)[1]])
            elif m.group(2):
                #result.append(eval(m.group(1)))
                result.append(int(m.group(2)[1:], 8))
            elif m.group(3):
                pass
            elif m.group(5):
                result.extend(b"\n")
            elif m.group(6):
                result.extend(b"(")
                nesting_depth += 1
            elif m.group(7):
                if nesting_depth == 0:
                    return bytes(result), m.end()
                result.extend(b")")
                nesting_depth -= 1
            offset = m.end()
        raise PdfFormatError("unfinished literal string")


    re_xref_section_start = re.compile(whitespace_optional + br"xref" + newline)
    re_xref_subsection_start = re.compile(whitespace_optional + br"([0-9]+)" + whitespace_mandatory + br"([0-9]+)" + whitespace_optional + newline_only)
    re_xref_entry = re.compile(br"([0-9]{10}) ([0-9]{5}) ([fn])( \r| \n|\r\n)")
    def read_xref_table(self, xref_section_offset):
        subsection_found = False
        m = self.re_xref_section_start.match(self.buf, xref_section_offset + self.start_offset)
        check_format_condition(m, "xref section start not found")
        offset = m.end()
        while True:
            m = self.re_xref_subsection_start.match(self.buf, offset)
            if not m:
                check_format_condition(subsection_found, "xref subsection start not found")
                break
            subsection_found = True
            offset = m.end()
            first_object = int(m.group(1))
            num_objects = int(m.group(2))
            for i in range(first_object, first_object+num_objects):
                m = self.re_xref_entry.match(self.buf, offset)
                check_format_condition(m, "xref entry not found")
                offset = m.end()
                is_free = m.group(3) == b"f"
                generation = int(m.group(2))
                if not is_free:
                    new_entry = (int(m.group(1)), generation)
                    check_format_condition(i not in self.xref_table or self.xref_table[i] == new_entry, "xref entry duplicated (and not identical)")
                    self.xref_table[i] = new_entry
        return offset


    def read_indirect(self, ref, max_nesting=-1):
        offset, generation = self.xref_table[ref[0]]
        assert generation == ref[1]
        return self.get_value(self.buf, offset + self.start_offset, expect_indirect=IndirectReference(*ref), max_nesting=max_nesting)[0]


    def linearize_page_tree(self, node=None):
        if node is None:
            node = self.page_tree_root
        check_format_condition(node[b"Type"] == b"Pages", "/Type of page tree node is not /Pages")
        pages = []
        for kid in node[b"Kids"]:
            kid_object = self.read_indirect(kid, max_nesting=3)
            if kid_object[b"Type"] == b"Page":
                pages.append(kid)
            else:
                pages.extend(self.linearize_page_tree(node=kid_object))
        return pages
