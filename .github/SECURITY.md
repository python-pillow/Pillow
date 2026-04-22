# Security policy

## Reporting a vulnerability

To report sensitive vulnerability information, report it [privately on GitHub](https://github.com/python-pillow/Pillow/security/advisories/new).

If you cannot use GitHub, use the [Tidelift security contact](https://tidelift.com/docs/security). Tidelift will coordinate the fix and disclosure.

**DO NOT report sensitive vulnerability information in public.**

## Threat model

Pillow's primary attack surface is parsing untrusted image data. A full STRIDE threat model covering spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege is maintained in the [Security handbook page](https://pillow.readthedocs.io/en/latest/handbook/security.html).

Key risks to be aware of when using Pillow to process untrusted images:

- **Decompression bombs** — do not set `Image.MAX_IMAGE_PIXELS = None` in production.
- **EPS files invoke Ghostscript** — block EPS input at the application layer unless strictly required.
- **`ImageMath.unsafe_eval()`** — never pass user-controlled strings to this function; use `lambda_eval` instead.
- **C extension memory safety** — keep Pillow and its bundled C libraries (libjpeg, libpng, libtiff, libwebp, etc.) up to date.
- **Sandboxing** — for high-risk deployments, run image processing in a sandboxed subprocess.
