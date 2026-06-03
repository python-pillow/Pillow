Security
========

Pillow's primary attack surface is **parsing untrusted image data**. This page
documents the threat model for developers integrating Pillow into applications
that handle images from untrusted sources, along with recommended mitigations.

To report a vulnerability see :ref:`security-reporting`.

.. _security-threat-model:

Threat model (STRIDE)
---------------------

The analysis below follows the `STRIDE
<https://en.wikipedia.org/wiki/STRIDE_model>`_ framework and covers the
boundary between untrusted image input and the Pillow API.

.. code-block:: text

                    ┌──────────────────────────────────────────┐
   Untrusted zone   │             Pillow API                   │
   ─────────────    │                                          │
   Image files ────►│  Image.open()  ──►  Format plugins       │
   Byte streams     │  (40+ parsers)      (Python + C FFI)     │
   User metadata    │                                          │
                    │  ImageMath.unsafe_eval(expr)  ───────────┼──► Python eval()
                    │  ImageShow.show(image)  ─────────────────┼──► os.system / subprocess
                    │  EpsImagePlugin.open(eps)  ──────────────┼──► Ghostscript (gs)
                    └──────────────┬───────────────────────────┘
                                   │ C extensions:
                                   │  _imaging · _imagingft · _imagingcms
                                   │  _webp · _avif · _imagingtk
                                   │  _imagingmath · _imagingmorph
                                   ▼
                    ┌──────────────────────────────────────────┐
                    │  C libraries (bundled or system)         │
                    │  libjpeg · libpng · libtiff · libwebp    │
                    │  openjpeg · freetype · littlecms2        │
                    └──────────────────────────────────────────┘

Spoofing
^^^^^^^^

**S-1 — Format sniffing bypass**

``Image.open()`` detects format by magic bytes, not file extension or MIME
type. An attacker can name a file ``safe.png`` while its content is TIFF, JPEG
2000, or EPS, causing a different — potentially more dangerous — parser to run.

*Mitigations:* validate MIME type and magic bytes independently before calling
``Image.open()``; pass the ``formats`` argument with an allowlist of accepted
formats.

**S-2 — Plugin registry spoofing**

Pillow's format registry is a global mutable dictionary. A malicious package
installed in the same environment could register a replacement parser for a
well-known format.

*Mitigations:* use isolated virtual environments with pinned, hash-verified
dependencies; audit ``Image.registered_extensions()`` at startup.

Tampering
^^^^^^^^^

**T-1 — Malicious metadata propagation**

Pillow preserves EXIF, XMP, IPTC, ICC profiles, and comments when
round-tripping images. Applications that store or render metadata without
sanitisation are vulnerable to second-order injection (SQLi, XSS, command
injection).

*Mitigations:* treat all values from ``image.info``, ``image._getexif()``,
``image.getexif()``, and ``image.text`` as untrusted; sanitise before storing
or rendering; strip metadata when it is not required.

**T-2 — Covert data channel (steganography)**

Pillow does not remove hidden data (JPEG comments, PNG text chunks) when
re-saving. An attacker can embed data that survives the
encode-decode cycle invisibly.

*Mitigations:* to guarantee a clean output when saving, create a new image instance via
``image.copy()`` and delete the ``image.info`` contents.

**T-3 — Supply chain tampering**

Pre-compiled wheels bundle libjpeg-turbo, libpng, libtiff, libwebp, openjpeg,
freetype, littlecms2, and other libraries. A compromised PyPI release or build pipeline
could ship malicious binaries.

*Mitigations:* pin with hash verification
(``python3 -m pip install --require-hashes``); monitor `Pillow security advisories
<https://github.com/python-pillow/Pillow/security/advisories>`_; use
Dependabot or OSV-Scanner for bundled C library CVEs.

Repudiation
^^^^^^^^^^^

**R-1 — No structured audit trail**

Without application-level logging there is no record of which images were
opened, what formats were detected, or what operations were performed, making
forensic investigation harder after an incident.

*Mitigations:* log the filename/hash, detected format, and dimensions of every
image processed; log and alert on ``Image.DecompressionBombWarning``,
``Image.DecompressionBombError``, and ``PIL.UnidentifiedImageError``.

Information disclosure
^^^^^^^^^^^^^^^^^^^^^^

**I-1 — Metadata in saved images**

GPS coordinates, author names, software version strings, and ICC profiles can
be inadvertently included in output images served publicly.

*Mitigations:* explicitly strip EXIF and XMP on save (set ``exif=b""``,
``icc_profile=None``, omit ``pnginfo``); verify output with ``exiftool`` in CI.

**I-2 — Temporary file exposure**

Several code paths write pixel data to temporary files via
``tempfile.mkstemp()``. Exception paths can leave these files behind on shared
filesystems.

*Mitigations:* files are created with mode ``0o600``; mount ``/tmp`` as a
per-container ``tmpfs``; ensure ``try/finally`` cleanup is in place.

Denial of service
^^^^^^^^^^^^^^^^^

**D-1 — Decompression bomb**

A small compressed image can expand to gigabytes in memory.
:py:data:`PIL.Image.MAX_IMAGE_PIXELS` raises
``Image.DecompressionBombError`` at 2× the limit and
``Image.DecompressionBombWarning`` at 1×. PNG text chunks are
separately capped by ``PngImagePlugin.MAX_TEXT_CHUNK`` and
``MAX_TEXT_MEMORY``. Check the values in your installed Pillow version at
runtime or in the reference/source for the current defaults.

*Mitigations:* **never** set ``Image.MAX_IMAGE_PIXELS = None`` in production;
treat ``Image.DecompressionBombWarning`` as an error; set OS/container memory limits
per worker.

**D-2 — CPU exhaustion**

Large-but-legal images (within ``MAX_IMAGE_PIXELS``) can still saturate CPU
through high-quality resampling, convolution filters, or complex draw
operations.

*Mitigations:* apply per-request CPU time limits; set a practical dimension
ceiling below ``MAX_IMAGE_PIXELS``; rate-limit processing requests.

**D-3 — Algorithmic complexity in parsers**

Formats such as TIFF (nested IFD chains), animated GIF/WebP (many frames), and
PNG (many text chunks) can exhaust CPU or memory before pixel data is decoded.

*Mitigations:* restrict accepted formats to the minimum required; enforce a
file-size limit before passing data to Pillow; use per-request timeouts.

Elevation of privilege
^^^^^^^^^^^^^^^^^^^^^^

**E-1 — C extension memory corruption (RCE)**

Pillow's ~87 C source files and its bundled C libraries process
attacker-controlled bytes. Historical CVEs include buffer overflows, integer
overflows, and use-after-free vulnerabilities that allow arbitrary code
execution.

*Mitigations:* keep Pillow and all C libraries up to date; compile with
hardening flags (ASLR, stack canaries, PIE, ``_FORTIFY_SOURCE=2``); run image
processing in a sandboxed subprocess (seccomp-bpf, AppArmor, or a restricted
container).

**E-2 — Ghostscript exploitation via EPS (RCE)**

Opening an EPS file invokes the system Ghostscript binary (``gs``) via
``subprocess``. Ghostscript has a long history of sandbox-escape CVEs
permitting arbitrary code execution from malicious PostScript.

*Mitigations:* **block EPS files** at the application input layer before
passing files to Pillow; if EPS must be supported, run Ghostscript in a fully
isolated sandbox with no network and no sensitive mounts. Pillow does not
provide a stable public API for unregistering individual format plugins, so do
not rely on mutating internal registries such as ``Image.OPEN`` as a security
control.


**E-3 — ImageMath.unsafe_eval() code injection**

:py:meth:`~PIL.ImageMath.unsafe_eval` calls Python's built-in ``eval()`` with
only a minimal ``__builtins__`` restriction, which can be bypassed via
introspection. Any user-controlled string passed to this function results in
arbitrary code execution.

*Mitigations:* **never** pass user-controlled strings to
``ImageMath.unsafe_eval()``; use :py:meth:`~PIL.ImageMath.lambda_eval` instead,
which accepts a Python callable and never calls ``eval``.

**E-4 — Font path traversal via ImageFont**

``ImageFont.truetype(font, size)`` passes the filename to the FreeType C
library. If font paths are constructed from user input without
canonicalisation, an attacker may supply a path like
``../../../../etc/passwd``.

*Mitigations:* never construct font paths from user input; if font selection
must be user-driven, resolve names against an explicit allowlist of
pre-validated absolute paths.

.. _security-recommendations:

Recommendations
---------------

The following mitigations are listed in priority order.

1. **Sandbox image processing** — run Pillow workers in a seccomp/AppArmor
   restricted subprocess, isolated from the main application process.
2. **Block or sandbox EPS** — reject EPS at the application boundary, or run
   Ghostscript in an isolated container.
3. **Never use** ``ImageMath.unsafe_eval()`` **with user input** — migrate all
   callers to :py:meth:`~PIL.ImageMath.lambda_eval`.
4. **Keep all dependencies current** — Pillow and its C library dependencies
   (including libjpeg, libpng, libtiff, libwebp, openjpeg, freetype,
   littlecms2, Ghostscript, and others). Subscribe to `Pillow security
   advisories <https://github.com/python-pillow/Pillow/security/advisories>`_.
5. **Enforce** ``MAX_IMAGE_PIXELS`` — never set it to ``None``; treat
   ``Image.DecompressionBombWarning`` as an error.
6. **Allowlist image formats** — restrict accepted formats when opening
   images, for example with ``Image.open(..., formats=...)``, and isolate
   installs/environments if you need to minimise supported formats.
7. **Strip metadata on output** — never pass through EXIF/XMP/ICC from user
   uploads to publicly served images.
8. **Sanitise all metadata** returned by Pillow before using it downstream.
9. **Pin dependencies with hash verification** — use
   ``pip install --require-hashes`` and lockfiles.
10. **Log and alert** on ``Image.DecompressionBombWarning``,
    ``Image.DecompressionBombError``, ``PIL.UnidentifiedImageError``,
    and all exceptions from ``Image.open()``.

.. _security-reporting:

Reporting a vulnerability
-------------------------

To report sensitive vulnerability information, report it `privately on GitHub
<https://github.com/python-pillow/Pillow/security/advisories/new>`_.

If you cannot use GitHub, use the `Tidelift security contact
<https://tidelift.com/docs/security>`_. Tidelift will coordinate the fix and
disclosure.

**Do not report sensitive vulnerability information in public.**
