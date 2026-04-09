# Incident Response Plan — Pillow

This document describes how the Pillow maintainers detect, triage, fix, communicate, and
learn from security incidents. It supplements the existing [Security Policy](SECURITY.md)
and [Release Checklist](../RELEASING.md).

---

## 1. Preparation

Maintaining readiness before an incident occurs reduces response time and errors under pressure.

### 1.1 Version Support Matrix

Security fixes are applied to the **latest stable release only**. Users on older versions
are expected to upgrade. Reporters should assume only the latest release will receive a patch.

| Branch | Status |
|---|---|
| `main` / latest stable | ✅ Security fixes applied |
| All older releases | ❌ No security support — please upgrade |

### 1.2 Team Readiness

The four members of the Pillow core team are in regular contact and share collective
responsibility for incident response. Any core team member may act as Incident Lead.
Contact details are known to all team members.

### 1.3 Readiness Review

At each quarterly release, maintainers should re-read this document and update any stale content.

---

## 2. Scope

This plan covers:

| Incident type | Examples |
|---|---|
| Vulnerability in Pillow's own Python or C code | Buffer overflow in an image decoder, integer overflow in `ImagingNew` |
| Vulnerability in a bundled or wheel-shipped C library | libjpeg, libwebp, libtiff, libpng, openjpeg, libavif |
| Supply-chain compromise | Malicious commit, stolen maintainer credentials, tampered PyPI wheel |
| CI/CD or infrastructure compromise | GitHub Actions secret leak, Codecov breach, PyPI token exposure |
| Critical non-security regression | Data-loss bug shipped in a release, crash on all supported platforms |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Incident** | Any event that compromises or threatens the confidentiality, integrity, or availability of Pillow's code, release artifacts, or infrastructure. |
| **Vulnerability** | A security flaw in Pillow or a bundled library that can be exploited by a crafted image or API call. |
| **Incident Lead** | The maintainer who owns coordination of the response from triage to closure. |
| **Embargo** | A period during which fix details are kept private to allow coordinated patching before public disclosure. |
| **Yank** | A PyPI action that keeps a release downloadable by pinned users but removes it from default `pip install` resolution. |
| **CVE** | Common Vulnerabilities and Exposures — a public identifier assigned to a specific vulnerability. |
| **CNA** | CVE Numbering Authority — GitHub is a CNA and can assign CVEs directly through the advisory workflow. |

---

## 4. Roles

| Role | Responsibility |
|---|---|
| **Incident Lead** | First maintainer to triage the report. Owns the incident until resolution. |
| **Patch Owner** | Writes and tests the fix (may be the same person as Incident Lead). |
| **Release Manager** | Cuts the point release following [RELEASING.md](../RELEASING.md). |
| **Communications Owner** | Drafts the GitHub Security Advisory, announces on Mastodon, notifies distros. |
| **Tidelift Contact** | For reports that arrive via Tidelift, coordinate through the Tidelift security portal. |

One person may fill multiple roles.

---

## 5. Severity Classification

Use the [CVSS v3.1](https://www.first.org/cvss/v3.1/specification-document) base score as
a guide, mapped to the following levels:

| Severity | CVSS | Definition | Target Response SLA |
|---|---|---|---|
| **Critical** | 9.0 – 10.0 | Remote code execution, arbitrary write, or complete integrity/confidentiality loss achievable by opening a crafted image | Best effort; embargoed release where possible |
| **High** | 7.0 – 8.9 | Heap/stack buffer overflow, use-after-free, or significant information disclosure | Best effort |
| **Medium** | 4.0 – 6.9 | Denial of service via crafted image, out-of-bounds read, limited info disclosure | Next scheduled quarterly release, or earlier point release if needed |
| **Low** | 0.1 – 3.9 | Minor information disclosure, unlikely to be exploitable in practice | Next quarterly release |

Supply-chain and CI/CD incidents are always treated as **Critical** regardless of CVSS.

> **Note:** These are good-faith targets for a small volunteer maintainer team, not contractual SLAs. Public safety and transparency will always be prioritised, even when timing varies.

---

## 6. Detection Sources

Vulnerabilities and incidents may be reported or discovered through:

1. **GitHub private security advisory** — preferred channel; see [SECURITY.md](SECURITY.md)
2. **Tidelift security contact** — <https://tidelift.com/security>
3. **Direct maintainer contact** — DM on Mastodon or email
4. **External researcher / coordinated disclosure** — e.g. Google Project Zero, vendor PSIRT
5. **Automated scanning** — Dependabot, GitHub code-scanning (CodeQL), CI fuzzing
6. **Distro security teams** — Debian, Red Hat, Ubuntu, Alpine may report upstream
7. **User bug report** — public issue (reassess if it has security implications before it stays public)

---

## 7. Response Process

### 7.1 Triage (all severities)

1. **Acknowledge receipt** to the reporter within **72 hours** using the template in
   [Appendix A](#appendix-a-communication-templates). Ask the reporter:
   - How they would like to be credited (name, handle, or anonymous)
   - Whether they intend to publish their own advisory, and if so, their preferred timeline
   - Thank them explicitly — reporters do the project a favour by disclosing privately.
2. Reproduce the issue. If the report is invalid, close it and notify the reporter.
3. Assign a severity level ([Section 5: Severity Classification](#5-severity-classification)).
4. If the GitHub Security Advisory was not created by the reporter, create one now and keep
   it **private** until the fix is released. Add the reporter as a collaborator if they wish
   to be involved.
5. **Request a CVE** through the GitHub Security Advisory workflow (GitHub is a CVE
   Numbering Authority — no separate MITRE form required). The CVE is reserved privately
   and published automatically when the advisory goes public.
6. **Escalation** — Escalate beyond the core maintainer team if any of the following apply:
   - The vulnerability is being actively exploited in the wild → notify [GitHub Security](mailto:security@github.com) and the [Python Security Response Team](https://www.python.org/news/security/)
   - The fix requires changes to CPython or a dependency outside Pillow's control → contact the relevant upstream immediately
   - A legal concern arises (e.g. GDPR-reportable data exposure) → contact the project's legal/fiscal sponsor
   - The Incident Lead is unreachable for > 24 hours on a Critical issue → any other maintainer may assume the role

### 7.2 Fix Development

1. Develop the fix in a **private fork** or directly in the private security advisory
   workspace on GitHub. Do **not** push to a public branch before the embargo lifts.
2. Write a regression test that fails before the fix and passes after.
3. Run the full test suite locally across all supported Python versions:
   ```bash
   make release-test
   ```
4. Review the patch with at least one other maintainer.

### 7.3 Standard (Non-Embargoed) Release

For Medium and Low severity, or when no distro pre-notification is needed:

1. Merge the fix to `main`, then cherry-pick to all affected release branches
   (see [RELEASING.md — Point release](../RELEASING.md)).
2. Amend commit messages to include the CVE identifier.
3. Tag and push; the GitHub Actions "Wheels" workflow will build and upload to PyPI.
4. Publish the GitHub Security Advisory (this simultaneously publishes the CVE).
5. Announce on [Mastodon](https://fosstodon.org/@pillow).

### 7.4 Embargoed Release

For Critical and High severity where distro pre-notification improves user safety:

1. Prepare patches against all affected release branches and test locally.
2. Agree on an **embargo date** with the reporter (typically 7–14 days out, up to 90 days for
   complex issues).
3. Privately send the patch to distros via the
   [linux-distros](https://oss-security.openwall.org/wiki/mailing-lists/distros) mailing list
   or directly to individual distro security teams.
4. On the embargo date:
   - Amend commit messages with the CVE identifier.
   - Tag and push all affected release branches (see [RELEASING.md — Embargoed release](../RELEASING.md)).
   - Confirm the "Wheels" workflow has passed and wheels are live on PyPI.
   - Publish the GitHub Security Advisory.
   - Announce on [Mastodon](https://fosstodon.org/@pillow).

### 7.5 Supply-Chain / Infrastructure Compromise

1. **Immediately** revoke any potentially compromised credentials:
   - PyPI API tokens (regenerate and update in GitHub secrets)
   - GitHub personal access tokens and OAuth apps
   - Codecov or other CI service tokens
2. Audit recent commits and releases for tampering:
   - Verify release tags against known-good SHAs
   - Re-inspect any wheel published since the potential compromise window
3. If a PyPI release is suspected to be tampered: yank it immediately via
   [https://pypi.org/manage/project/pillow/](https://pypi.org/manage/project/pillow/);
   file a report with the [PyPI security team](mailto:security@pypi.org).
4. Notify GitHub Security if repository access or Actions secrets are involved.
5. Issue a public advisory describing the scope and any user action required.

### 7.6 Recovery

After the fix is released and the advisory is public:

1. Verify that the patched wheels are live on PyPI and passing CI across all supported platforms.
2. Confirm any yanked releases are handled correctly .
3. Resume normal development operations on `main`.
4. Monitor the GitHub issue tracker and Mastodon for user reports of residual problems for at least **72 hours** post-release.
5. Close the private GitHub Security Advisory once recovery is confirmed.

---

## 8. Communication

### Internal (during embargo)
- Use the **private GitHub Security Advisory** thread for coordination with the reporter.
- Do not discuss details in public issues, PRs, or Gitter/IRC channels.

### External (at or after disclosure)

| Audience | Channel | Timing |
|---|---|---|
| General users | [GitHub Security Advisory](https://github.com/python-pillow/Pillow/security/advisories) | At release |
| PyPI ecosystem | CVE published via advisory | At release |
| Downstream distros | Direct email or linux-distros list | Before embargo date (embargoed) |
| Tidelift subscribers | Tidelift security portal | At release (or coordinated) |
| Community | [Mastodon @pillow](https://fosstodon.org/@pillow) | At release |

**Advisory content should include:**
- CVE identifier and CVSS score
- Affected Pillow versions
- Fixed version(s)
- Nature of the vulnerability (without full exploit details if still fresh)
- Credit to the reporter (with their consent)
- Upgrade instructions (`pip install --upgrade Pillow`)

---

## 9. Dependency Map

Understanding what Pillow depends on (upstream) and what depends on Pillow (downstream)
is essential for scoping impact and coordinating notifications during an incident.

### 10.1 Upstream Dependencies

#### Bundled C libraries (shipped in official wheels)

These libraries are compiled into Pillow's binary wheels. A CVE in any of them may
require a Pillow point release even if Pillow's own code is unchanged.

| Library | Purpose | Security advisory tracker |
|---|---|---|
| [libjpeg-turbo](https://libjpeg-turbo.org/) | JPEG encode/decode | [GitHub](https://github.com/libjpeg-turbo/libjpeg-turbo/security) |
| [libpng](http://www.libpng.org/pub/png/libpng.html) | PNG encode/decode | [SourceForge](https://sourceforge.net/p/libpng/bugs/) |
| [libtiff](https://libtiff.gitlab.io/libtiff/) | TIFF encode/decode | [GitLab](https://gitlab.com/libtiff/libtiff/-/issues) |
| [libwebp](https://chromium.googlesource.com/webm/libwebp) | WebP encode/decode | [Chromium tracker](https://bugs.chromium.org/p/webm/) |
| [libavif](https://github.com/AOMediaCodec/libavif) | AVIF encode/decode | [GitHub](https://github.com/AOMediaCodec/libavif/security) |
| [aom](https://aomedia.googlesource.com/aom/) | AV1 codec (AVIF) | [Chromium tracker](https://bugs.chromium.org/p/aomedia/) |
| [dav1d](https://code.videolan.org/videolan/dav1d) | AV1 decode (AVIF) | [VideoLAN Security](https://www.videolan.org/security/) |
| [openjpeg](https://www.openjpeg.org/) | JPEG 2000 encode/decode | [GitHub](https://github.com/uclouvain/openjpeg/security) |
| [freetype2](https://freetype.org/) | Font rendering | [GitLab](https://gitlab.freedesktop.org/freetype/freetype/-/issues) |
| [lcms2](https://www.littlecms.com/) | ICC color management | [GitHub](https://github.com/mm2/Little-CMS) |
| [harfbuzz](https://harfbuzz.github.io/) | Text shaping (via raqm) | [GitHub](https://github.com/harfbuzz/harfbuzz/security) |
| [raqm](https://github.com/HOST-Oman/libraqm) | Complex text layout | [GitHub](https://github.com/HOST-Oman/libraqm) |
| [fribidi](https://github.com/fribidi/fribidi) | Unicode bidi (via raqm) | [GitHub](https://github.com/fribidi/fribidi) |
| [zlib](https://zlib.net/) | Deflate compression | [zlib.net](https://zlib.net/) |
| [liblzma / xz-utils](https://tukaani.org/xz/) | XZ/LZMA compression | [GitHub](https://github.com/tukaani-project/xz) |
| [bzip2](https://gitlab.com/bzip2/bzip2) | BZ2 compression | [GitLab](https://gitlab.com/bzip2/bzip2/-/issues) |
| [zstd](https://github.com/facebook/zstd) | Zstandard compression | [GitHub](https://github.com/facebook/zstd/security) |
| [brotli](https://github.com/google/brotli) | Brotli compression | [GitHub](https://github.com/google/brotli) |
| [libyuv](https://chromium.googlesource.com/libyuv/libyuv/) | YUV conversion | [Chromium tracker](https://bugs.chromium.org/p/libyuv/) |

#### Python-level dependencies

| Package | Required? | Purpose |
|---|---|---|
| `setuptools` | Build-time only | Package build backend |
| `pybind11` | Build-time only | C++ ↔ Python bindings |
| `olefile` | Optional (`fpx`, `mic` extras) | OLE2 container parsing (FPX, MIC formats) |
| `defusedxml` | Optional (`xmp` extra) | Safe XML parsing for XMP metadata |

### 10.2 Downstream Dependencies

A vulnerability in Pillow can have wide impact. Notify or consider the blast radius of
these downstream consumers when assessing severity and planning communications.

#### Linux distribution packages

| Distribution | Package name | Security contact |
|---|---|---|
| Debian / Ubuntu | `python3-pil` | [Debian Security](https://www.debian.org/security/) / [Ubuntu Security](https://ubuntu.com/security) |
| Fedora / RHEL / CentOS | `python3-pillow` | [Red Hat Security](https://access.redhat.com/security/) |
| Alpine Linux | `py3-pillow` | [Alpine security](https://security.alpinelinux.org/) |
| Arch Linux | `python-pillow` | [Arch security tracker](https://security.archlinux.org/) |
| Homebrew (macOS) | `pillow` | [Homebrew maintainers](https://github.com/Homebrew/homebrew-core) |
| conda-forge | `pillow` | [conda-forge](https://github.com/conda-forge/pillow-feedstock) |

#### Major Python ecosystem consumers

These are high-profile projects known to depend on Pillow; a critical vulnerability may
warrant proactive notification.

| Project | Usage |
|---|---|
| [matplotlib](https://matplotlib.org/) | Image I/O for plots |
| [scikit-image](https://scikit-image.org/) | Image processing |
| [torchvision](https://github.com/pytorch/vision) (PyTorch) | Dataset loading, transforms |
| [Keras / TensorFlow](https://keras.io/) | Image preprocessing utilities |
| [Django](https://www.djangoproject.com/) | `ImageField` validation and thumbnail generation |
| [Wagtail](https://wagtail.org/) | CMS image renditions |
| [Plone](https://plone.org/) | CMS image handling |
| [Jupyter / IPython](https://jupyter.org/) | Inline image display |
| [ReportLab](https://www.reportlab.com/) | PDF image embedding |
| [Wand](https://docs.wand-py.org/) | Sometimes used alongside Pillow |
| [Tidelift subscribers](https://tidelift.com/) | Enterprise consumers (coordinated via Tidelift) |

#### Pillow ecosystem plugins

Third-party plugins extend Pillow and are distributed separately on PyPI. Their
maintainers should be notified for Critical/High issues that affect the plugin API
or the formats they decode. See the
[full plugin list](https://pillow.readthedocs.io/en/stable/handbook/third-party-plugins.html).

### 10.3 Responding to an Upstream Vulnerability

When a CVE is published for a bundled C library:

1. Assess whether the vulnerable code path is reachable through Pillow's API.
2. If reachable, treat as a Pillow vulnerability and follow Section 5.
3. Update the bundled library version in the wheel build scripts and rebuild wheels.
4. Reference the upstream CVE in Pillow's release notes and GitHub Security Advisory.
5. If not reachable, document the rationale in a public issue so downstream distributors
   can make informed decisions about patching their system packages.

---

## 11. Plan Maintenance

This document is a living record. It should be kept current so it is useful when an
incident actually occurs.

- **Quarterly review** — revisit during the Section 1.3 readiness review at each quarterly release.

---

## 12. References

- [Security Policy](SECURITY.md)
- [Release Checklist](../RELEASING.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Tidelift Security Contact](https://tidelift.com/security)
- [GitHub: Privately reporting a security vulnerability](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
- [GitHub as a CVE Numbering Authority (CNA)](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/about-repository-security-advisories)
- [FIRST CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
- [linux-distros mailing list](https://oss-security.openwall.org/wiki/mailing-lists/distros)
- [OpenSSF CVD Guide](https://github.com/ossf/oss-vulnerability-guide) *(basis for this plan)*

---

## Appendix A: Communication Templates

### A.1 Reporter Acknowledgment

> Subject: Re: [Security] \<brief issue description\>
>
> Hi \<name\>,
>
> Thank you for taking the time to report this — we genuinely appreciate it.
>
> We have received your report and will assess it within the next few days. We will keep
> you updated on our progress.
>
> A few quick questions so we can handle this well:
> - How would you like to be credited in the advisory? (name, handle, organisation, or anonymous)
> - Do you plan to publish your own write-up or advisory? If so, is there a disclosure date
>   that works for you?
>
> We aim to treat all vulnerability reports in line with coordinated disclosure principles.
> If you have any questions or concerns at any point, please reply to this thread.
>
> Thanks again,
> The Pillow maintainers

### A.2 Embargoed Distro Notification

> Subject: [EMBARGOED] Pillow security issue — \<CVE-XXXX-XXXXX\> — disclosure \<DATE\>
>
> This is an embargoed notification of a vulnerability in Pillow. Please keep this
> information confidential until the disclosure date listed below.
>
> **CVE:** \<CVE-XXXX-XXXXX\>
> **Affected versions:** \<e.g. Pillow < 11.x.x\>
> **Fixed version:** \<version\>
> **Severity:** \<Critical / High / Medium / Low\> (CVSS \<score\>: \<vector\>)
> **Reporter:** \<name / affiliation, or "reported privately"\>
> **Public disclosure date:** \<DATE TIME UTC\>
>
> **Summary:**
> \<One paragraph describing the vulnerability class and impact without a full exploit.\>
>
> **Proof of concept:**
> \<Minimal reproducer or attached patch.\>
>
> **Remediation:**
> Upgrade to Pillow \<fixed version\>. No known workaround.
>
> Please do not share this information, issue public patches, or make user communications
> before the disclosure date. We will notify this list immediately if the date changes.
>
> — The Pillow maintainers

### A.3 Public Disclosure Advisory

*(Published as a GitHub Security Advisory; the CVE and date are included automatically.)*

> **Summary:** \<One-paragraph technical summary.\>
>
> **CVE:** \<CVE-XXXX-XXXXX\>
> **Affected versions:** Pillow \< \<fixed version\>
> **Fixed version:** \<version\>
> **Severity:** \<rating\> (CVSS \<score\>)
> **Reporter:** \<credited name / "reported privately"\>
>
> **Details:**
> \<Fuller technical description. Include attack scenario where helpful.\>
>
> **Remediation:**
> ```
> pip install --upgrade Pillow
> ```
>
> **Timeline:**
> - Reported: \<date\>
> - Fixed: \<date\>
> - Disclosed: \<date\>
