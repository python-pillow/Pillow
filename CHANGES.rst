Changelog (Pillow)
==================

4.0.0 (2017-01-01)
------------------

- Refactor out postprocessing hack to load_end in PcdImageFile
  [wiredfool]

- Add center and translate option to Image.rotate. #2328
  [lambdafu]
  
- Test: Relax WMF test condition, fixes #2323
  [wiredfool] 

- Allow 0 size images, Fixes #2259, Reverts to pre-3.4 behavior.
  [wiredfool]
  
- SGI: Save uncompressed SGI/BW/RGB/RGBA files #2325
  [jbltx]
  
- Depends: Updated pngquant to 2.8.2 #2319
  [radarhere]

- Test: Added correctness tests for opening SGI images #2324
  [wiredfool]

- Allow passing a list or tuple of individual frame durations when saving a GIF #2298
  [Xdynix]

- Unified different GIF optimize conditions #2196
  [radarhere]

- Build: Refactor dependency installation #2305
  [hugovk]

- Test: Add python 3.6 to travis, tox #2304
  [hugovk]

- Test: Fix coveralls coverage for Python+C #2300
  [hugovk]

- Remove executable bit and shebang from OleFileIO.py #2308
  [jwilk, radarhere]

- PyPy: Buffer interface workaround #2294
  [wiredfool]

- Test: Switch to Ubuntu Trusty 14.04 on Travis CI #2294

- Remove vendored version of olefile Python package in favor of upstream #2199
  [jdufresne]

- Updated comments to use print as a function #2234
  [radarhere]

- Set executable flag on selftest.py, setup.py and added shebang line #2282, #2277
  [radarhere, homm]

- Test: Increase epsilon for FreeType 2.7 as rendering is slightly different. #2286
  [hugovk]

- Test: Faster assert_image_similar #2279
  [homm]

- Removed depreciated internal "stretch" method #2276
  [homm]

- Removed the handles_eof flag in decode.c #2223
  [wiredfool]

- Tiff: Fix for writing Tiff to BytesIO using libtiff #2263
  [wiredfool]

- Doc: Design docs #2269
  [wiredfool]

- Test: Move tests requiring libtiff to test_file_libtiff #2273
  [wiredfool]

- Update Maxblock heuristic #2275
  [wiredfool]

- Fix for 2-bit palette corruption #2274
  [pdknsk, wiredfool]

- Tiff: Update info.icc_profile when using libtiff reader. #2193
  [lambdafu]

- Test: Fix bug in test_ifd_rational_save when libtiff is not available #2270
  [ChristopherHogan]

- ICO: Only save relevant sizes #2267
  [hugovk]

- ICO: Allow saving .ico files of 256x256 instead of 255x255 #2265
  [hugovk]

- Fix TIFFImagePlugin ICC color profile saving. #2087
  [cskau]

- Doc: Improved description of ImageOps.deform resample parameter #2256
  [radarhere]

- EMF: support negative bounding box coordinates #2249
  [glexey]

- Close file if opened in WalImageFile #2216
  [radarhere]

- Use Image._new() instead of _makeself() #2248
  [homm]

- SunImagePlugin fixes #2241
  [wiredfool]

- Use minimal scale for jpeg drafts #2240
  [homm]

- Updated dependency scripts to use FreeType 2.7, OpenJpeg 2.1.2, WebP 0.5.2 and Tcl/Tk 8.6.6 #2235, #2236, #2237, #2290, #2302
  [radarhere]

- Fix "invalid escape sequence" bytestring warnings in Python 3.6 #2186
  [timgraham]

- Removed support for Python 2.6 and Python 3.2 #2192
  [jdufresne]

- Setup: Raise custom exceptions when required/requested dependencies are not found #2213
  [wiredfool]

- Use a context manager in FontFile.save() to ensure file is always closed #2226
  [jdufresne]

- Fixed bug in saving to fp-objects in Python >= 3.4 #2227
  [radarhere]

- Use a context manager in ImageFont._load_pilfont() to ensure file is always closed #2232
  [jdufresne]

- Use generator expressions instead of list comprehension #2225
  [jdufresne]

- Close file after reading in ImagePalette.load() #2215
  [jdufresne]

- Changed behaviour of default box argument for paste method to match docs #2211
  [radarhere]

- Add support for another BMP bitfield #2221
  [jmerdich]

- Added missing top-level test __main__ #2222
  [radarhere]

- Replaced range(len()) #2197
  [radarhere]

- Fix for ImageQt Segfault, fixes #1370 #2182
  [wiredfool]

- Setup: Close file in setup.py after finished reading #2208
  [jdufresne]

- Setup: optionally use pkg-config (when present) to detect dependencies #2074
  [garbas]

- Search for tkinter first in builtins #2210
  [matthew-brett]

- Tests: Replace try/except/fail pattern with TestCase.assertRaises() #2200
  [jdufresne]

- Tests: Remove unused, open files at top level of tests #2188
  [jdufresne]

- Replace type() equality checks with isinstance #2184
  [jdufresne]

- Doc: Move ICO out of the list of read-only file formats #2180
  [alexwlchan]

- Doc: Fix formatting, too-short title underlines and malformed table #2175
  [hugovk]

- Fix BytesWarnings #2172
  [jdufresne]

- Use Integer division to eliminate deprecation warning. #2168
  [mastermatt]

- Doc: Update compatibility matrix
  [daavve, wiredfool]


3.4.2 (2016-10-18)
------------------

- Fix Resample coefficient calculation #2161
  [homm]


3.4.1 (2016-10-04)
------------------

- Allow lists as arguments for Image.new() #2149
  [homm]

- Fix fix for map.c overflow #2151  (also in 3.3.3)
  [wiredfool]

3.4.0 (2016-10-03)
------------------

- Removed Image.core.open_ppm, added negative image size checks in Image.py. #2146
  [wiredfool]

- Windows build: fetch dependencies from pillow-depends #2095
  [hugovk]

- Add TIFF save_all writer. #2140
  [lambdafu, vashek]

- Move libtiff fd duplication to _load_libtiff #2141
  [sekrause]

- Speed up GIF save optimization step, fixes #2093. #2133
  [wiredfool]

- Fix for ImageCms Segfault, Issue #2037. #2131
  [wiredfool]

- Make Image.crop an immediate operation, not lazy. #2138
  [wiredfool]

- Skip empty values in ImageFileDirectory #2024
  [homm]

- Force reloading palette when using mmap in ImageFile. #2139
  [lambdafu]

- Fix "invalid escape sequence" warning in Python 3.6 #2136
  [timgraham]

- Update documentation about drafts #2137
  [radarhere]

- Converted documentation parameter format, comments to docstrings #2021
  [radarhere]

- Fixed typos #2128 #2142
  [radarhere]

- Renamed references to OS X to macOS #2125 2130
  [radarhere]

- Use truth value when checking for progressive and optimize option on save #2115, #2129
  [radarhere]

- Convert DPI to ints when saving as JPEG #2102
  [radarhere]

- Added append_images parameter to GIF saving #2103
  [radarhere]

- Speedup paste with masks up to 80% #2015
  [homm]

- Rewrite DDS decoders in C, add DXT3 and BC7 decoders #2068
  [Mischanix]

- Fix PyArg_ParseTuple format in getink() #2070
  [arjennienhuis]

- Fix saving originally missing TIFF tags. #2111
  [anntzer]

- Allow pathlib.Path in Image.open on Python 2.7 #2110
  [patricksnape]

- Use modern base64 interface over deprecated #2121
  [hugovk]

- ImageColor.getrgb hexadecimal RGBA #2114
  [homm]

- Test fix for bigendian machines #2092
  [wiredfool]

- Resampling lookups, trailing empty coefficients, precision #2008
  [homm]

- Add (un)packing between RGBA and BGRa #2057
  [arjennienhuis]

- Added return for J2k (and fpx) Load to return a pixel access object #2061
  [wiredfool]

- Skip failing numpy tests on Pypy <= 5.3.1 #2090
  [arjennienhuis]

- Show warning when trying to save RGBA image as JPEG #2010
  [homm]

- Respect pixel centers during transform #2022
  [homm]

- TOC for supported file formats #2056
  [polarize]

- Fix conversion of bit images to numpy arrays Fixes #350, #2058
  [matthew-brett]

- Add ImageOps.scale to expand or contract a PIL image by a factor #2011
  [vlmath]

- Flake8 fixes #2050
  [hugovk]

- Updated freetype to 2.6.5 on Appveyor builds #2035
  [radarhere]

- PCX encoder fixes #2023, pr #2041
  [homm]

- Docs: Windows console prompts are > #2031
  [techtonik]

- Expose Pillow package version as PIL.__version__ #2027
  [techtonik]

- Add Box and Hamming filters for resampling #1959
  [homm]

- Retain a reference to core image object in PyAccess #2009
  [homm]

3.3.3 (2016-10-04)
------------------

- Fix fix for map.c overflow #2151
  [wiredfool]

3.3.2 (2016-10-03)
------------------

- Fix negative image sizes in Storage.c #2105
  [wiredfool]

- Fix integer overflow in map.c #2105
  [wiredfool]

3.3.1 (2016-08-18)
------------------

- Fix C90 compilation error for Tcl / Tk rewrite #2033
  [matthew-brett]

- Fix image loading when rotating by 0 deg #2052
  [homm]

3.3.0 (2016-07-01)
------------------

- Fixed enums for Resolution Unit and Predictor in TiffTags.py #1998
  [wiredfool]

- Fix issue converting P mode to LA #1986
  [didrix]

- Moved test_j2k_overflow to check_j2k_overflow, prevent DOS of our 32bit testing machines #1995
  [wiredfool]

- Skip CRC checks in PNG files when LOAD_TRUNCATED_IMAGES is enabled #1991
  [kkopachev]

- Added CMYK mode for opening EPS files #1826
  [radarhere]

- Docs: OSX build instruction clarification #1994
  [wiredfool]

- Docs: Filter comparison table #1993
  [homm]

- Removal of pthread based Incremental.c, new interface for file decoders/encoders to access the python file. Fixes assorted J2k Hangs. #1934
  [wiredfool]

- Skip unnecessary passes when resizing #1954
  [homm]

- Removed duplicate code in ImagePalette #1832
  [radarhere]

- test_imagecms: Reduce precision of extended info due to 32 bit machine precision #1990
  [AbdealiJK]

- Binary Tiff Metadata/ICC profile. #1988
  [wiredfool]

- Ignore large text blocks in PNG if LOAD_TRUNCATED_IMAGES is enabled #1970
  [homm]

- Replace index = index+1 in docs with +=1
  [cclauss]

- Skip extra 0xff00 in jpeg #1977
  [kkopachev]

- Use bytearray for palette mutable storage #1985
  [radarhere, wiredfool]

- Added additional uint modes for Image.fromarray, more extensive tests of fromarray #1984
  [mairsbw, wiredfool]

- Fix for program importing PyQt4 when PyQt5 also installed #1942
  [hugovk]

- Changed depends/install_*.sh urls to point to github pillow-depends repo #1983
  [wiredfool]

- Allow ICC profile from `encoderinfo` while saving PNGs #1909
  [homm]

- Fix integer overflow on ILP32 systems (32-bit Linux). #1975
  [lambdafu]

- Change function declaration to match Tcl_CmdProc type #1966
  [homm]

- Integer overflow checks on all calls to *alloc #1781
  [wiredfool]

- Change equals method on Image so it short circuits #1967
  [mattBoros]

- Runtime loading of TCL/TK libraries, eliminating build time dependency. #1932
  [matthew-brett]

- Cleanup of transform methods #1941
  [homm]

- Fix "Fatal Python error: UNREF invalid object" in debug builds #1936
  [wiredfool]

- Setup fixes for Alpine linux #1937
  [wiredfool]

- Split resample into horizontal + vertical passes #1933
  [homm]

- Box blur with premultiplied alpha #1914
  [homm]

- Add libimagequant support in quantize() #1889
  [rr-]

- Added internal Premultiplied luminosity (La) mode #1912
  [homm]

- Fixed point integer resample #1881
  [homm]

- Removed docs/BUILDME script #1924
  [radarhere]

- Moved comments to docstrings  #1926
  [hugovk]

- Include Python.h before wchar.h so _GNU_SOURCE is set consistently #1906
  [hugovk]

- Updated example decoder in documentation #1899
  [radarhere]

- Added support for GIF comment extension #1896
  [radarhere]

- Removed support for pre- 1.5.2 list form of Image info in Image.new #1897
  [radarhere]

- Fix typos in TIFF tags #1918
  [radarhere]

- Skip tests that require libtiff if it is not installed #1893 (fixes #1866)
  [wiredfool]

- Skip test when icc profile is not available, fixes #1887
  [doko42]

- Make deprecated functions raise NotImplementedError instead of Exception. #1862, #1890
  [daniel-leicht, radarhere]

- Replaced os.system with subprocess.call in setup.py #1879
  [radarhere]

- Corrected Image show documentation #1886
  [radarhere]

- Added check for executable permissions to ImageShow #1880
  [radarhere]

- Fixed tutorial code and added explanation #1877
  [radarhere]

- Added OS X support for ImageGrab grabclipboard #1837
  [radarhere]

- Combined duplicate code in ImageTk #1856
  [radarhere]

- Added --disable-platform-guessing option to setup.py build extension #1861
  [angeloc]

- Fixed loading Transparent PNGs with a transparent black color #1840
  [olt]

- Add support for LA mode in Image.fromarray #1865
  [pierriko]

- Make ImageFile load images in read-only mode #1864
  [hdante]

- Added _accept hook for XVThumbImagePlugin #1853
  [radarhere]

- Test TIFF with LZW compression #1855, TGA RLE file #1854
  [hugovk]

- Improved SpiderImagePlugin help text #1863
  [radarhere]

- Updated Sphinx project description #1870
  [radarhere]

- Remove support for Python 3.0 from _imaging.c #1851
  [radarhere]

- Jpeg qtables are unsigned chars #1814, #1921
  [thebostik]

- Added additional EXIF tags #1841, TIFF Tags #1821
  [radarhere]

- Changed documentation to refer to ImageSequence Iterator #1833
  [radarhere]

- Fix Fedora prerequisites in installation docs, depends script #1842
  [living180]

- Added _accept hook for PixarImagePlugin #1843
  [radarhere]

- Removed outdated scanner classifier #1823
  [radarhere]

- Combined identical error messages in _imaging #1825
  [radarhere]

- Added debug option for setup.py to trace header and library finding #1790
  [wiredfool]

- Fix doc building on travis #1820, #1844
  [wiredfool]

- Fix for DIB/BMP images #1813, #1847
  [wiredfool]

- Add PixarImagePlugin file extension #1809
  [radarhere]

- Catch struct.errors when verifying png files #1805
  [wiredfool]

- SpiderImagePlugin: raise an error when seeking in a non-stack file #1794
  [radarhere, jmichalon]

- Added support for 2/4 bpp Tiff grayscale images #1789
  [zwhfly]

- Removed unused variable from selftest #1788
  [radarhere]

- Added warning for as_dict method (deprecated in 3.0.0) #1799
  [radarhere]

- Removed powf support for older Python versions #1784
  [radarhere]

- Health fixes #1625 #1903
  [radarhere]

3.2.0 (2016-04-01)
------------------

- Added install docs for Fedora 23 and FreeBSD #1729, #1739, #1792
  [koobs, zandermartin, wiredfool]

- Fixed TIFF multiframe load when the frames have different compression types #1782
  [radarhere, geka000]

- Added __copy__ method to Image #1772
  [radarhere]

- Updated dates in PIL license in OleFileIO README #1787
  [radarhere]

- Corrected Tiff tag names #1786
  [radarhere]

- Fixed documented name of JPEG property #1783
  [radarhere]

- Fixed UnboundLocalError when loading a corrupt jpeg2k file #1780
  [wiredfool]

- Fixed integer overflow in path.c #1773
  [wiredfool, nedwill]

- Added debug to command line help text for pilprint #1766
  [radarhere]

- Expose many more fields in ICC Profiles #1756
  [lambdafu]

- Documentation changes, URL update, transpose, release checklist
  [radarhere]

- Fixed saving to nonexistant files specified by pathlib.Path objects #1748 (fixes #1747)
  [radarhere]

- Round Image.crop arguments to the nearest integer #1745 (fixes #1744)
  [hugovk]

- Fix uninitialized variable warning in _imaging.c:getink #1663 (fixes #486)
  [wiredfool]

- Disable multiprocessing install on cygwin #1700 (fixes #1690)
  [wiredfool]

- Fix the error reported when libz is not found #1764
  [wiredfool]

- More general error check to avoid Symbol not found: _PyUnicodeUCS2_AsLatin1String on OS X #1761
  [wiredfool]

- Added py35 to tox envlist #1724
  [radarhere]

- Fix EXIF tag name typos #1736
  [zarlant, radarhere]

- Updated freetype to 2.6.3, Tk/Tcl to 8.6.5 and 8.5.19 #1725, #1752
  [radarhere]

- Add a loader for the FTEX format from Independence War 2: Edge of Chaos #1688
  [jleclanche]

- Improved alpha_composite documentation #1698
  [radarhere]

- Extend ImageDraw.text method to pass on multiline_text method specific arguments #1647
  [radarhere]

- Allow ImageSequence to seek to zero #1686
  [radarhere]

- ImageSequence Iterator is now an iterator #1649
  [radarhere]

- Updated windows test builds to jpeg9b #1673
  [radarhere]

- Fixed support for .gbr version 1 images, added support for version 2 in GbrImagePlugin #1653
  [wiredfool]

- Clarified which YCbCr format is used #1677
  [radarhere]

- Added TiffTags documentation, Moved windows build documentation to winbuild/ #1667
  [wiredfool]

- Add tests for OLE file based formats #1678
  [radarhere]

- Add TIFF IFD test #1671
  [radarhere]

- Add a basic DDS image plugin with more tests #1654
  [jleclanche, hugovk, wiredfool]

- Fix incorrect conditional in encode.c #1638
  [manisandro]


3.1.2 (2016-04-01)
------------------

- Fixed an integer overflow in Jpeg2KEncode.c causing a buffer overflow. CVE-2016-3076
  [wiredfool]

3.1.1 (2016-02-04)
------------------

- Fixed an integer overflow in Resample.c causing writes in the Python heap.
  [nedwill]

- Fixed a buffer overflow in PcdDecode.c causing a segfault when opening PhotoCD files. CVE-2016-2533
  [wiredfool]

- Fixed a buffer overflow in FliDecode.c causing a segfault when opening FLI files. CVE-2016-0775
  [wiredfool]

- Fixed a buffer overflow in TiffDecode.c causing an arbitrary amount of memory to be overwritten when opening a specially crafted invalid TIFF file. CVE-2016-0740
  [wiredfool]


3.1.0 (2016-01-04)
------------------

- Fixing test failures on Python 2.6/Windows #1633
  [wiredfool]

- Limit metadata tags when writing using libtiff #1620
  [wiredfool]

- Rolling back exif support to pre-3.0 format #1627
  [wiredfool]

- Fix Divide by zero in Exif, add IFDRational class #1531
  [wiredfool]

- Catch the IFD error near the source #1622
  [wiredfool]

- Added release notes for 3.1.0 #1623
  [radarhere]

- Updated spacing to be consistent between multiline methods #1624
  [radarhere]

- Let EditorConfig take care of some basic formatting #1489
  [hugovk]

- Restore gpsexif data to the v1 form #1619
  [wiredfool]

- Add /usr/local include and library directories for freebsd #1613
  [leforestier]

- Updated installation docs for new versions of dependencies #1611
  [radarhere]

- Removed unrunnable test file #1610
  [radarhere]

- Changed register calls to use format property #1608
  [radarhere]

- Added field type constants to TiffTags #1596
  [radarhere]

- Allow saving RowsPerStrip with libtiff #1594
  [wiredfool]

- Enabled conversion to numpy array for HSV images #1578
  [cartisan]

- Changed some urls in the docs to use https #1580
  [hugovk]

- Removed logger.exception from ImageFile.py #1590
  [radarhere]

- Removed warnings module check #1587
  [radarhere]

- Changed arcs, chords and pie slices to use floats #1577
  [radarhere]

- Update unit test asserts #1584, #1598
  [radarhere]

- Fix command to invoke ghostscript for eps files #1478
  [baumatron, radarhere]

- Consistent multiline text spacing #1574
  [wiredfool, hugovk]

- Removed unused lines in BDFFontFile #1530
  [radarhere]

- Changed ImageQt import of Image #1560
  [radarhere, ericfrederich]

- Throw TypeError if no cursors were found in .cur file #1556
  [radarhere]

- Fix crash in ImageTk.PhotoImage on win-amd64 #1553
  [cgohlke]

- ExtraSamples tag should be a SHORT, not a BYTE #1555
  [Nexuapex]

- Docs and code health fixes #1565 #1566 #1581 #1586 #1591 #1621
  [radarhere]

- Updated freetype to 2.6.2 #1564
  [radarhere]

- Updated WebP to 0.5.0 for Travis #1515 #1609
  [radarhere]

- Fix missing 'version' key value in __array_interface__ #1519
  [mattip]

- Replaced os.popen with subprocess.Popen to pilprint script #1523
  [radarhere]

- Catch OverflowError in SpiderImagePlugin #1545
  [radarhere, MrShark]

- Fix the definition of icc_profile in TiffTags #1539
  [wiredfool]

- Remove old _imagingtiff.c and pilplus stuff #1499
  [hugovk]

- Fix Exception when requiring jpeg #1501
  [hansmosh]

- Dependency scripts for Debian and Ubuntu #1486
  [wiredfool]

- Added Usage message to painter script #1482
  [radarhere]

- Add tag info for iccprofile, fixes #1462. #1465
  [wiredfool]

- Added some requirements for make release-test #1451
  [wiredfool]

- Flatten tiff metadata value SAMPLEFORMAT to initial value #1467 (fixes #1466)
  [wiredfool]

- Fix handling of pathlib in Image.save #1464 (fixes #1460)
  [wiredfool]

- Make tests more robust #1469
  [hugovk]

- Use correctly sized pointers for windows handle types #1458
  [nu744]

3.0.0 (2015-10-01)
------------------

- Check flush method existence for file-like object #1398
  [mrTable, radarhere]

- Added PDF multipage saving #1445
  [radarhere]

- Removed deprecated code, Image.tostring, Image.fromstring, Image.offset, ImageDraw.setink, ImageDraw.setfill, ImageFileIO, ImageFont.FreeTypeFont and ImageFont.truetype `file` kwarg, ImagePalette private _make functions, ImageWin.fromstring and ImageWin.tostring #1343
  [radarhere]

- Load more broken images #1428
  [homm]

- Require zlib and libjpeg #1439
  [wiredfool]

- Preserve alpha when converting from a QImage to a Pillow Image by using png instead of ppm #1429
  [ericfrederich]

- Qt needs 32 bit aligned image data #1430
  [ericfrederich]

- Tiff ImageFileDirectory rewrite #1419
  [anntzer, wiredfool, homm]

- Removed spammy debug logging #1423
  [wiredfool]

- Save as GiF89a with support for animation parameters #1384
  [radarhere]

- Correct convert matrix docs #1426
  [wiredfool]

- Catch TypeError in _getexif #1414
  [radarhere, wiredfool]

- Fix for UnicodeDecodeError in TiffImagePlugin #1416
  [bogdan199, wiredfool]

- Dedup code in image.open #1415
  [wiredfool]

- Skip any number extraneous chars at the end of JPEG chunks #1337
  [homm]

- Single threaded build for pypy3, refactor #1413
  [wiredfool]

- Fix loading of truncated images with LOAD_TRUNCATED_IMAGES enabled #1366
  [homm]

- Documentation update for concepts: bands #1406
  [merriam]

- Add Solaris/SmartOS include and library directories #1356
  [njones11]

- Improved handling of getink color #1387
  [radarhere]

- Disable compiler optimizations for topalette and tobilevel functions for all msvc versions #1402 (fixes #1357)
  [cgohlke]

- Skip ImageFont_bitmap test if _imagingft C module is not installed #1409
  [homm]

- Add param documentation to ImagePalette #1381
  [bwrsandman]

- Corrected scripts path #1407
  [radarhere]

- Updated libtiff to 4.0.6 #1405, #1421
  [radarhere]

- Updated Platform Support for Yosemite #1403
  [radarhere]

- Fixed infinite loop on truncated file #1401
  [radarhere]

- Check that images are L mode in ImageMorph methods #1400
  [radarhere]

- In tutorial of pasting images, add to mask text #1389
  [merriam]

- Style/health fixes #1391, #1397, #1417, #1418
  [radarhere]

- Test on Python 3.5 dev and 3.6 nightly #1361
  [hugovk]

- Fix fast rotate operations #1373
  [radarhere]

- Added support for pathlib Path objects to open and save #1372
  [radarhere]

- Changed register calls to use format property #1333
  [radarhere]

- Added support for ImageGrab.grab to OS X #1367, #1443
  [radarhere, hugovk]

- Fixed PSDraw stdout Python 3 compatibility #1365
  [radarhere]

- Added Python 3.3 to AppVeyor #1363
  [radarhere]

- Treat MPO with unknown header as base JPEG file #1350
  [hugovk, radarhere]

- Added various tests #1330, #1344
  [radarhere]

- More ImageFont tests #1327
  [hugovk]

- Use logging instead of print #1207
  [anntzer]

2.9.0 (2015-07-01)
------------------

- Added test for GimpPaletteFile #1324
  [radarhere]

- Merged gifmaker script to allow saving of multi-frame GIF images #1320
  [radarhere]

- Added is_animated property to multi-frame formats #1319
  [radarhere]

- Fixed ValueError in Python 2.6 #1315 #1316
  [cgohlke, radarhere]

- Fixed tox test script path #1308
  [radarhere]

- Added width and height properties #1304
  [radarhere]

- Update tiff and tk tcl 8.5 versions #1303
  [radarhere, wiredfool]

- Add functions to convert: Image <-> QImage; Image <-> QPixmap #1217
  [radarhere, rominf]

- Remove duplicate code in gifmaker script #1294
  [radarhere]

- Multiline text in ImageDraw #1177
  [allo-, radarhere]

- Automated Windows CI/build support #1278
  [wiredfool]

- Removed support for Tk versions earlier than 8.4 #1288
  [radarhere]

- Fixed polygon edge drawing #1255 (fixes #1252)
  [radarhere]

- Check prefix length in _accept methods #1267
  [radarhere]

- Register MIME type for BMP #1277
  [coldmind]

- Adjusted ImageQt use of unicode() for 2/3 compatibility #1218
  [radarhere]

- Identify XBM file created with filename including underscore #1230 (fixes #1229)
  [hugovk]

- Copy image when saving in GifImagePlugin #1231 (fixes #718)
  [radarhere]

- Removed support for FreeType 2.0 #1247
  [radarhere]

- Added background saving to GifImagePlugin #1273
  [radarhere]

- Provide n_frames attribute to multi-frame formats #1261
  [anntzer, radarhere]

- Add duration and loop set to GifImagePlugin #1172, #1269
  [radarhere]

- Ico files are little endian #1232
  [wiredfool]

- Upgrade olefile from 0.30 to 0.42b #1226
  [radarhere, decalage2]

- Setting transparency value to 0 when the tRNS contains only null byte(s) #1239
  [juztin]

- Separated out feature checking from selftest #1233
  [radarhere]

- Style/health fixes
  [radarhere]

- Update WebP from 0.4.1 to 0.4.3 #1235
  [radarhere]

- Release GIL during image load (decode) #1224
  [lkesteloot]

- Added icns save #1185
  [radarhere]

- Fix putdata memory leak #1196
  [benoit-pierre]

- Keep user-specified ordering of icon sizes #1193
  [karimbahgat]

- Tiff: allow writing floating point tag values #1113
  [bpedersen2]

2.8.2 (2015-06-06)
------------------

- Bug fix: Fixed Tiff handling of bad EXIF data
  [radarhere]

2.8.1 (2015-04-02)
------------------

- Bug fix: Catch struct.error on invalid JPEG, fixes #1163
  [wiredfool, hugovk]

2.8.0 (2015-04-01)
------------------

- Fix 32-bit BMP loading (RGBA or RGBX) #1125
  [artscoop]

- Fix UnboundLocalError in ImageFile #1131
  [davarisg]

- Re-enable test image caching #982
  [hugovk, homm]

- Fix: Cannot identify EPS images #1152 (fixes #1104)
  [hugovk]

- Configure setuptools to run nosetests, fixes #729
  [aclark4life]

- Style/health fixes
  [radarhere, hugovk]

- Add support for HTTP response objects to Image.open() #1151
  [mfitzp]

- Improve reference docs for PIL.ImageDraw.Draw.pieslice() #1145
  [audreyr]

- Added copy method font_variant() and accessible properties to truetype() #1123
  [radarhere]

- Fix ImagingEffectNoise #1128
  [hugovk]

- Remove unreachable code #1126
  [hugovk]

- Let Python do the endian stuff + tests #1121
  [amoibos, radarhere]

- Fix webp decode memory leak #1114
  [benoit-pierre]

- Fast path for opaque pixels in RGBa unpacker #1088
  [bgilbert]

- Enable basic support for 'RGBa' raw encoding/decoding #1096
  [immerrr]

- Fix pickling L mode images with no palette, #1095
  [hugovk]

- iPython display hook #1091
  [wiredfool]

- Adjust buffer size when quality=keep #1079 (fixes #148 again)
  [wiredfool]

- Fix for corrupted bitmaps embedded in truetype fonts #1072
  [jackyyf, wiredfool]

2.7.0 (2015-01-01)
------------------

- Split Sane into a separate repo: https://github.com/python-pillow/Sane
  [hugovk]

- Look for OS X and Linux fonts in common places #1054
  [charleslaw]

- Fix CVE-2014-9601, potential PNG decompression DOS #1060
  [wiredfool]

- Use underscores, not spaces, in TIFF tag kwargs #1044, #1058
  [anntzer, hugovk]

- Update PSDraw for Python3, add tests #1055
  [hugovk]

- Use Bicubic filtering by default for thumbnails. Don't use Jpeg Draft mode for thumbnails #1029
  [homm]

- Fix MSVC compiler error: Use Py_ssize_t instead of ssize_t #1051
  [cgohlke]

- Fix compiler error: MSVC needs variables defined at the start of the block #1048
  [cgohlke]

- The GIF Palette optimization algorithm is only applicable to mode='P' or 'L' #993
  [moriyoshi]

- Use PySide as an alternative to PyQt4/5 #1024
  [holg]

- Replace affine-based im.resize implementation with convolution-based im.stretch #997
  [homm]

- Replace Gaussian Blur implementation with iterated fast box blur. #961  Note: Radius parameter is interpreted differently than before.
  [homm]

- Better docs explaining import _imaging failure #1016, build #1017, mode #1018, PyAccess, PixelAccess objects #1019 Image.quantize #1020 and Image.save #1021
  [wiredfool]

- Fix for saving TIFF image into an io.BytesIO buffer #1011
  [mfergie]

- Fix antialias compilation on debug versions of Python #1010
  [wiredfool]

- Fix for Image.putdata segfault #1009
  [wiredfool]

- Ico save, additional tests #1007
  [exherb]

- Use PyQt4 if it has already been imported, otherwise prefer PyQt5 #1003
  [AurelienBallier]

- Speedup resample implementation up to 2.5 times #977
  [homm]

- Speed up rotation by using cache aware loops, added transpose to rotations #994
  [homm]

- Fix Bicubic interpolation #970
  [homm]

- Support for 4-bit greyscale TIFF images #980
  [hugovk]

- Updated manifest #957
  [wiredfool]

- Fix PyPy 2.4 regression #952
  [wiredfool]

- Webp Metadata Skip Test comments #954
  [wiredfool]

- Fixes for things rpmlint complains about #942
  [manisandro]

2.6.2 (2015-01-01)
------------------

- Fix CVE-2014-9601, potential PNG decompression DOS #1060
  [wiredfool]

- Fix Regression in PyPy 2.4 in streamio  #958
  [wiredfool]

2.6.1 (2014-10-11)
------------------

- Fix SciPy regression in Image.resize #945
  [wiredfool]

- Fix manifest to include all test files.
  [aclark4life]

2.6.0 (2014-10-01)
------------------

- Relax precision of ImageDraw tests for x86, GimpGradient for PPC #930
  [wiredfool]

2.6.0-rc1 (2014-09-29)
----------------------

- Use redistributable image for testing #884
  [hugovk]

- Use redistributable ICC profiles for testing, skip if not available #923
  [wiredfool]

- Additional documentation for JPEG info and save options #890
  [wiredfool]

- Fix JPEG Encoding memory leak when exif or qtables were specified #921
  [wiredfool]

- Image.tobytes() and Image.tostring() documentation update #916 #917
  [mgedmin]

- On Windows, do not execute convert.exe without specifying path #912
  [cgohlke]

- Fix msvc build error #911
  [cgohlke]

- Fix for handling P + transparency -> RGBA conversions #904
  [wiredfool]

- Retain alpha in ImageEnhance operations #909
  [wiredfool]

- Jpeg2k Decode/encode memory leak fix #898
  [joshware, wiredfool]

- EpsFilePlugin Speed improvements #886
  [wiredfool, karstenw]

- Don't resize if already the right size #892
  [radarhere]

- Fix for reading multipage TIFFs #885
  [kostrom, wiredfool]

- Correctly handle saving gray and CMYK JPEGs with quality=keep #857
  [etienned]

- Correct duplicate Tiff Metadata and Exif tag values
  [hugovk]

- Windows fixes #871
  [wiredfool]

- Fix TGA files with image ID field #856
  [megabuz]

- Fixed wrong P-mode of small, unoptimized L-mode GIF #843
  [uvNikita]

- Fixed CVE-2014-3598, a DOS in the Jpeg2KImagePlugin
  [Andrew Drake]

- Fixed CVE-2014-3589, a DOS in the IcnsImagePlugin
  [Andrew Drake]

- setup.py: Close open file handle before deleting #844
  [divergentdave]

- Return Profile with Transformed Images #837
  [wiredfool]

- Changed docstring to refer to the correct function #836
  [MatMoore]

- Adding coverage support for C code tests #833
  [wiredfool]

- PyPy performance improvements #821
  [wiredfool]

- Added support for reading MPO files #822
  [Feneric]

- Added support for encoding and decoding iTXt chunks #818
  [dolda2000]

- HSV Support #816
  [wiredfool]

- Removed unusable ImagePalette.new()
  [hugovk]

- Fix Scrambled XPM #808
  [wiredfool]

- Doc cleanup
  [wiredfool]

- Fix `ImageStat` docs #796
  [akx]

- Added docs for ExifTags #794
  [Wintermute3]

- More tests for CurImagePlugin, DcxImagePlugin, Effects.c, GimpGradientFile, ImageFont, ImageMath, ImagePalette, IptcImagePlugin, SpiderImagePlugin, SgiImagePlugin, XpmImagePlugin and _util
  [hugovk]

- Fix return value of FreeTypeFont.textsize() does not include font offsets #784
  [tk0miya]

- Fix dispose calculations for animated GIFs #765
  [larsjsol]

- Added class checking to Image __eq__ function #775
  [radarhere, hugovk]

- Test PalmImagePlugin and method to skip known bad tests #776
  [hugovk, wiredfool]

2.5.3 (2014-08-18)
------------------

- Fixed CVE-2014-3598, a DOS in the Jpeg2KImagePlugin (backport)
  [Andrew Drake]


2.5.2 (2014-08-13)
------------------

- Fixed CVE-2014-3589, a DOS in the IcnsImagePlugin (backport)
  [Andrew Drake]

2.5.1 (2014-07-10)
------------------

- Fixed install issue if Multiprocessing.Pool is not available
  [wiredfool]

- 32bit mult overflow fix #782
  [wiredfool]

2.5.0 (2014-07-01)
------------------

- Imagedraw rewrite #737
  [terseus, wiredfool]

- Add support for multithreaded test execution #755
  [wiredfool]

- Prevent shell injection #748
  [mbrown1413, wiredfool]

- Support for Resolution in BMP files #734
  [gcq]

- Fix error in setup.py for Python 3 #744
  [matthew-brett]

- Pyroma fix and add Python 3.4 to setup metadata #742
  [wirefool]

- Top level flake8 fixes #741
  [aclark4life]

- Remove obsolete Animated Raster Graphics (ARG) support #736
  [hugovk]

- Fix test_imagedraw failures #727
  [cgohlke]

- Fix AttributeError: class Image has no attribute 'DEBUG' #726
  [cgohlke]

- Fix msvc warning: 'inline' : macro redefinition #725
  [cgohlke]

- Cleanup #654
  [dvska, hugovk, wiredfool]

- 16-bit monochrome support for JPEG2000 #730
  [videan42]

- Fixed ImagePalette.save
  [brightpisces]

- Support JPEG qtables #677
  [csinchok]

- Add binary morphology addon
  [dov, wiredfool]

- Decompression bomb protection #674
  [hugovk]

- Put images in a single directory #708
  [hugovk]

- Support OpenJpeg 2.1 #681
  [al45tair, wiredfool]

- Remove unistd.h #include for all platforms #704
  [wiredfool]

- Use unittest for tests
  [hugovk]

- ImageCms fixes
  [hugovk]

- Added more ImageDraw tests
  [hugovk]

- Added tests for Spider files
  [hugovk]

- Use libtiff to write any compressed tiff files #669
  [wiredfool]

- Support for pickling Image objects
  [hugovk]

- Fixed resolution handling for EPS thumbnails #619
  [eliempje]

- Fixed rendering of some binary EPS files (Issue #302)
  [eliempje]

- Rename variables not to use built-in function names #670
  [hugovk]

- Ignore junk JPEG markers
  [hugovk]

- Change default interpolation for Image.thumbnail to Image.ANTIALIAS
  [hugovk]

- Add tests and fixes for saving PDFs
  [hugovk]

- Remove transparency resource after P->RGBA conversion
  [hugovk]

- Clean up preprocessor cruft for Windows #652
  [CounterPillow]

- Adjust Homebrew freetype detection logic #656
  [jacknagel]

- Added Image.close, context manager support
  [wiredfool]

- Added support for 16 bit PGM files
  [wiredfool]

- Updated OleFileIO to version 0.30 from upstream #618
  [hugovk]

- Added support for additional TIFF floating point format
  [Hijackal]

- Have the tempfile use a suffix with a dot
  [wiredfool]

- Fix variable name used for transparency manipulations #604
  [nijel]

2.4.0 (2014-04-01)
------------------

- Indexed Transparency handled for conversions between L, RGB, and P modes #574 (fixes #510)
  [wiredfool]

- Conversions enabled from RGBA->P #574 (fixes #544)
  [wiredfool]

- Improved icns support #565
  [al45tair]

- Fix libtiff leaking open files #580 (fixes #526)
  [wiredfool]

- Fixes for Jpeg encoding in Python 3 #578 (fixes #577)
  [wiredfool]

- Added support for JPEG 2000 #547
  [al45tair]

- Add more detailed error messages to Image.py #566
  [larsmans]

- Avoid conflicting _expand functions in PIL & MINGW, fixes #538
  [aclark4life]

- Merge from Philippe Lagadec’s OleFileIO_PL fork #512
  [vadmium]

- Fix ImageColor.getcolor #534
  [homm]

- Make ICO files work with the ImageFile.Parser interface #525 (fixes #522)
  [wiredfool]

- Handle 32bit compiled python on 64bit architecture #521
  [choppsv1]

- Fix support for characters >128 using .pcf or .pil fonts in Py3k #517 (fixes #505)
  [wiredfool]

- Skip CFFI test earlier if it's not installed #516
  [wiredfool]

- Fixed opening and saving odd sized .pcx files #535 (fixes #523)
  [wiredfool]

- Fixed palette handling when converting from mode P->RGB->P
  [d-schmidt]

- Fixed saving mode P image as a PNG with transparency = palette color 0
  [d-schmidt]

- Improve heuristic used when saving progressive and optimized JPEGs with high quality values #504
  [e98cuenc]

- Fixed DOS with invalid palette size or invalid image size in BMP file
  [wiredfool]

- Added support for BMP version 4 and 5
  [eddwardo, wiredfool]

- Fix segfault in getfont when passed a memory resident font
  [wiredfool]

- Fix crash on Saving a PNG when icc-profile is None #496
  [brutasse]

- Cffi+Python implementation of the PixelAccess object
  [wiredfool]

- PixelAccess returns unsigned ints for I16 mode
  [wiredfool]

- Minor patch on booleans + Travis #474
  [sciunto]

- Look in multiarch paths in GNU platforms #511
  [pinotree]

- Add arch support for pcc64, s390, s390x, armv7l, aarch64 #475
  [manisandro]

- Add arch support for ppc
  [wiredfool]

- Correctly quote file names for WindowsViewer command
  [cgohlke]

- Prefer homebrew freetype over X11 freetype (but still allow both) #466
  [dmckeone]

2.3.2 (2014-08-13)
------------------

- Fixed CVE-2014-3589, a DOS in the IcnsImagePlugin (backport)
  [Andrew Drake]

2.3.1 (2014-03-14)
------------------

- Fix insecure use of tempfile.mktemp (CVE-2014-1932 CVE-2014-1933)
  [wiredfool]

2.3.0 (2014-01-01)
------------------

- Stop leaking filename parameter passed to getfont #459
  [jpharvey]

- Report availability of LIBTIFF during setup and selftest
  [cgohlke]

- Fix msvc build error C1189: "No Target Architecture" #460
  [cgohlke]

- Fix memory leak in font_getsize
  [wiredfool]

- Correctly prioritize include and library paths #442
  [ohanar]

- Image.point fixes for numpy.array and docs #441
  [wiredfool]

- Save the transparency header by default for PNGs #424
  [wiredfool]

- Support for PNG tRNS header when converting from RGB->RGBA #423
  [wiredfool]

- PyQT5 Support #418
  [wiredfool]

- Updates for saving color tiffs w/compression using libtiff #417
  [wiredfool]

- 2gigapix image fixes and redux
  [wiredfool]

- Save arbitrary tags in Tiff image files #369
  [wiredfool]

- Quote filenames and title before using on command line #398
  [tmccombs]

- Fixed Viewer.show to return properly #399
  [tmccombs]

- Documentation fixes
  [wiredfool]

- Fixed memory leak saving images as webp when webpmux is available #429
  [cezarsa]

- Fix compiling with FreeType 2.5.1 #427
  [stromnov]

- Adds directories for NetBSD #411
  [deepy]

- Support RGBA TIFF with missing ExtraSamples tag #393
  [cgohlke]

- Lossless WEBP Support #390
  [wiredfool]

- Take compression as an option in the save call for tiffs #389
  [wiredfool]

- Add support for saving lossless WebP. Just pass 'lossless=True' to save() #386
  [liftoff]

- LCMS support upgraded from version 1 to version 2 #380 (fixes #343)
  [wiredfool]

- Added more raw decoder 16 bit pixel formats #379
  [svanheulen]

- Document remaining Image* modules listed in PIL handbook
  [irksep]

- Document ImageEnhance, ImageFile, ImageFilter, ImageFont, ImageGrab, ImageMath, and ImageOps
  [irksep]

- Port and update docs for Image, ImageChops, ImageColor, and ImageDraw
  [irksep]

- Move or copy content from README.rst to docs/
  [irksep]

- Respect CFLAGS/LDFLAGS when searching for headers/libs
  [iElectric]

- Port PIL Handbook tutorial and appendices
  [irksep]

- Alpha Premultiplication support for transform and resize #364
  [wiredfool]

- Fixes to make Pypy 2.1.0 work on Ubuntu 12.04/64 #359
  [wiredfool]

2.2.2 (2013-12-11)
------------------

- Fix compiling with FreeType 2.5.1 #427
  [stromnov]

2.2.1 (2013-10-02)
------------------

- Error installing Pillow 2.2.0 on Mac OS X (due to hard dep on brew) #357 (fixes #356)
  [wiredfool]

2.2.0 (2013-10-02)
------------------

- Bug in image transformations resulting from uninitialized memory #348 (fixes #254)
  [nikmolnar]

- Fix for encoding of b_whitespace #346 (similar to closed issue #272)
  [mhogg]

- Add numpy array interface support for 16 and 32 bit integer modes #347 (fixes #273)
  [cgohlke]

- Partial fix for #290: Add preliminary support for TIFF tags.
  [wiredfool]

- Fix #251 and #326: circumvent classification of pngtest_bad.png as malware
  [cgohlke]

- Add typedef uint64_t for MSVC #339
  [cgohlke]

- setup.py: better support for C_INCLUDE_PATH, LD_RUN_PATH, etc. #336 (fixes #329)
  [nu774]

- _imagingcms.c: include windef.h to fix build issue on MSVC #335 (fixes #328)
  [nu774]

- Automatically discover homebrew include/ and lib/ paths on OS X #330
  [donspaulding]

- Fix bytes which should be bytearray #325
  [manisandro]

- Add respective paths for C_INCLUDE_PATH, LD_RUN_PATH (rpath) to build
  if specified as environment variables #324
  [seanupton]

- Fix #312 + gif optimize improvement
  [d-schmidt]

- Be more tolerant of tag read failures #320
  [ericbuehl]

- Catch truncated zTXt errors #321 (fixes #318)
  [vytisb]

- Fix IOError when saving progressive JPEGs #313
  [e98cuenc]

- Add RGBA support to ImageColor #309
  [yoavweiss]

- Test for `str`, not `"utf-8"` #306 (fixes #304)
  [mjpieters]

- Fix missing import os in _util.py #303
  [mnowotka]

- Added missing exif tags #300
  [freyes]

- Fail on all import errors #298, #299 (fixes #297)
  [macfreek, wiredfool]

- Fixed Windows fallback (wasn't using correct file in Windows fonts) #295
  [lmollea]

- Moved ImageFile and ImageFileIO comments to docstrings #293
  [freyes]

- Restore compatibility with ISO C #289
  [cgohlke]

- Use correct format character for C int type #288
  [cgohlke]

- Allocate enough memory to hold pointers in encode.c #287
  [cgohlke]

- Fillorder double shuffling bug when FillOrder ==2 and decoding using libtiff #284 (fixes #279)
  [wiredfool]

- Moved Image module comments to docstrings.
  [freyes]

- Add 16-bit TIFF support #277 (fixes #274)
  [wiredfool]

- Ignore high ascii characters in string.whitespace #276 (fixes #272)
  [wiredfool]

- Added clean/build to tox to make it behave like Travis #275
  [freyes]

- Adding support for metadata in webp images #271
  [heynemann]

2.1.0 (2013-07-02)
------------------

- Add /usr/bin/env python shebangs to all scripts in /Scripts #197
  [mgorny]

- Add several TIFF decoders and encoders #268
  [megabuz]

- Added support for alpha transparent webp images.

- Adding Python 3 support for StringIO.

- Adding Python3 basestring compatibility without changing basestring.

- Fix webp encode errors on win-amd64 #259
  [cgohlke]

- Better fix for ZeroDivisionError in ImageOps.fit for image.size height is 1 #267
  [chrispbailey]

- Better support for ICO images.

- Changed PY_VERSION_HEX #190 (fixes #166)

- Changes to put everything under the PIL namespace #191
  [wiredfool]

- Changing StringIO to BytesIO.

- Cleanup whitespace.
  [Arfrever]

- Don't skip 'import site' on initialization when running tests for inplace builds.
  [cgohlke]

- Enable warnings for test suite #227
  [wiredfool]

- Fix for ZeroDivisionError in ImageOps.fit for image.size == (1,1) #255
  [pterk]

- Fix for if isinstance(filter, collections.Callable) crash. Python bug #7624 on <2.6.6

- Remove double typedef declaration #194 (fixes #193)
  [evertrol]

- Fix msvc compile errors (#230).

- Fix rendered characters have been chipped for some TrueType fonts
  [tk0miya]

- Fix usage of pilfont.py script #184
  [fabiomcosta]

- Fresh start for docs, generated by sphinx-apidoc.

- Introduce --enable-x and fail if it is given and x is not available.

- Partial work to add a wrapper for WebPGetFeatures to correctly support #220 (fixes #204)

- Significant performance improvement of `alpha_composite` function #156
  [homm]

- Support explicitly disabling features via --disable-* options #240
  [mgorny]

- Support selftest.py --installed, fixes #263

- Transparent WebP Support #220 (fixes #204)
  [euangoddard, wiredfool]

- Use PyCapsule for py3.1 #238 (fixes #237)
  [wiredfool]

- Workaround for: http://bugs.python.org/issue16754 in 3.2.x < 3.2.4 and 3.3.0.

2.0.0 (2013-03-15)
------------------

.. Note:: Special thanks to Christoph Gohlke and Eric Soroos for assisting with a pre-PyCon 2013 release!

- Many other bug fixes and enhancements by many other people.

- Add Python 3 support. (Pillow >= 2.0.0 supports Python 2.6, 2.7, 3.2, 3.3. Pillow < 2.0.0 supports Python 2.4, 2.5, 2.6, 2.7.)
  [fluggo]

- Add PyPy support (experimental, please see #67)

- Add WebP support #96
  [lqs]

- Add Tiff G3/G4 support (experimental)
  [wiredfool]

- Backport PIL's PNG/Zip improvements #95, #97
  [olt]

- Various 64-bit and Windows fixes.
  [cgohlke]

- Add testing suite.
  [cgohlke, fluggo]

- Added support for PNG images with transparency palette.
  [d-schmidt]

1.7.8 (2012-11-01)
------------------

- Removed doctests.py that made tests of other packages fail.
  [thomasdesvenain]

- Fix opening psd files with RGBA layers when A mode is not of type 65535 but 3.
  Fixes #3
  [thomasdesvenain]


1.7.7 (2012-04-04)
------------------

- UNDEF more types before including windows headers
  [mattip]

1.7.6 (2012-01-20)
------------------

- Bug fix: freetype not found on Mac OS X with case-sensitive filesystem
  [gjo]

- Bug fix: Backport fix to split() after open() (regression introduced in PIL 1.1.7).
  [sfllaw]

1.7.5 (2011-09-07)
------------------

- Fix for sys.platform = "linux3"
  [blueyed]

- Package cleanup and additional documentation
  [aclark4life]

1.7.4 (2011-07-21)
------------------

- Fix brown bag release
  [aclark4life]

1.7.3 (2011-07-20)
------------------

- Fix : resize need int values, append int conversion in thumbnail method
  [harobed]

1.7.2 (2011-06-02)
------------------

- Bug fix: Python 2.4 compat
  [aclark4life]

1.7.1 (2011-05-31)
------------------

- More multi-arch support
  [SteveM, regebro, barry, aclark4life]

1.7.0 (2011-05-27)
------------------

- Add support for multi-arch library directory /usr/lib/x86_64-linux-gnu
  [aclark4life]

1.6 (12/01/2010)
----------------

- Bug fix: /usr/x11/include should be added to include_dirs not library_dirs
  [elro]

- Doc fixes
  [aclark4life]

1.5 (11/28/2010)
----------------

- Module and package fixes
  [aclark4life]

1.4 (11/28/2010)
----------------

- Doc fixes
  [aclark4life]

1.3 (11/28/2010)
----------------

- Add support for /lib64 and /usr/lib64 library directories on Linux
  [aclark4life]

- Doc fixes
  [aclark4life]

1.2 (08/02/2010)
----------------

- On OS X also check for freetype2 in the X11 path
  [jezdez]

- Doc fixes
  [aclark4life]

1.1 (07/31/2010)
----------------

- Removed setuptools_hg requirement
  [aclark4life]

- Doc fixes
  [aclark4life]

1.0 (07/30/2010)
----------------

- Remove support for ``import Image``, etc. from the standard namespace. ``from PIL import Image`` etc. now required.
- Forked PIL based on `Hanno Schlichting's re-packaging <http://dist.plone.org/thirdparty/PIL-1.1.7.tar.gz>`_
  [aclark4life]

Pre-fork
--------

0.2b5-1.1.7
+++++++++++

::

    -*- coding: utf-8 -*-

    The Python Imaging Library
    $Id$

    ACKNOWLEDGEMENTS: PIL wouldn't be what it is without the help of:
    David Ascher, Phil Austin, Douglas Bagnall, Larry Bates, Anthony
    Baxter, William Baxter, Denis Benoit, Jan Blom, Duncan Booth, Alexey
    Borzenkov, Jeff Breidenbach, Roger Burnham, Zac Burns, Gene Cash,
    Kevin Cazabon, Fred Clare, Greg Coats, Chris Cogdon, Greg Couch, Bill
    Crutchfield, Abel Deuring, Tim Docker, Fred Drake, Graham Dumpleton,
    Matthew Ellis, Eric Etheridge, Daniel Fetchinson, Robin Friedrich,
    Pier Paolo Glave, Federico Di Gregorio, Markus Gritsch, Daniel
    Haertle, Greg Hamilton, Mark Hammond, Bernhard Herzog, Rob Hooft, Bob
    Ippolito, Jack Jansen, Bill Janssen, Edward Jones, Richard Jones,
    Håkan Karlsson, Robert Kern, David Kirtley, Bob Klimek, Matthias
    Klose, Andrew Kuchling, Magnus Källström, Victor Lacina, Ben Last,
    Hamish Lawson, Cesare Leonardi, Andrew MacIntyre, Jan Matejek, Naveen
    Michaud-Agrawal, Gordon McMillan, Skip Montanaro, Fredrik Nehr,
    Russell Nelson, Luciano Nocera, Travis Oliphant, Piet van Oostrum,
    Richard Oudkerk, Paul Pharr, Andres Polit, Conrado Porto Lopes Gouvêa,
    Eric Raymond, Victor Reijs, Bertil Reinhammar, Nicholas Riley, Don
    Rozenberg, Toby Sargeant, Barry Scott, Les Schaffer, Joel Shprentz,
    Klamer Shutte, Gene Skonicki, Niki Spahiev, D. Alan Stewart, Perry
    Stoll, Paul Svensson, Ulrik Svensson, Miki Tebeka, Michael van
    Tellingen, Ivan Tkatchev, Dan Torop, Adam Twardoch, Rune Uhlin, Dmitry
    Vasiliev, Sasha Voynow, Charles Waldman, Collin Winter, Dan Wolfe,
    Ka-Ping Yee, and many others (if your name should be on this list, let
    me know.)

    *** Changes from release 1.1.6 to 1.1.7 ***

    This section may not be fully complete.  For changes since this file
    was last updated, see the repository revision history:

      https://bitbucket.org/effbot/pil-2009-raclette/commits/all

    (1.1.7 final)

    + Set GIF loop info property to the number of iterations if a NETSCAPE
      loop extension is present, instead of always setting it to 1 (from
      Valentino Volonghi).

    (1.1.7c1 released)

    + Improved PNG compression (from Alexey Borzenkov).

    + Read interlaced PNG files (from Conrado Porto Lopes Gouvêa)

    + Added various TGA improvements from Alexey Borzenkov, including
      support for specifying image orientation.

    + Bumped block threshold to 16 megabytes, made size estimation a bit
      more accurate.  This speeds up allocation of large images.

    + Fixed rounding error in ImagingDrawWideLine.

      "gormish" writes: ImagingDrawWideLine() in Draw.c has a bug in every
      version I've seen, which leads to different width lines depending on
      the order of the points in the line. This is especially bad at some
      angles where a 'width=2' line can completely disappear.

    + Added support for RGBA mode to the SGI module (based on code by
      Karsten Hiddemann).

    + Handle repeated IPTC tags (adapted from a patch by Eric Bruning).

      Eric writes: According to the specification, some IPTC tags can be
      repeated, e.g., tag 2:25 (keywords). PIL 1.1.6 only retained the last
      instance of that tag. Below is a patch to store all tags. If there are
      multiple tag instances, they are stored in a (python) list. Single tag
      instances remain as strings.

    + Fixed potential crash in ImageFilter for small target images
      (reported by Zac Burns and Daniel Fetchinson).

    + Use BMP instead of JPEG as temporary show format on Mac OS X.

    + Fixed putpixel/new for I;16 with colors > 255.

    + Added integer power support to ImagingMath.

    + Added limited support for I;16L mode (explicit little endian).

    + Moved WMF support into Image.core; enable WMF rendering by default
      if renderer is available.

    + Mark the ARG plugin as obsolete.

    + Added version query mechanism to ImageCms and ImageFont, for
      debugging.

    + Added (experimental) ImageCms function for fetching the ICC profile
      for the current display (currently Windows only).

      Added HWND/HDC support to ImageCms.get_display_profile().

    + Added WMF renderer (Windows only).

    + Added ImagePointHandler and ImageTransformHandler mixins; made
      ImageCmsTransform work with im.point.

    + Fixed potential endless loop in the XVThumbnail reader (from Nikolai
      Ugelvik).

    + Added Kevin Cazabon's pyCMS package.

      The C code has been moved to _imagingcms.c, the Python interface
      module is installed as PIL.ImageCMS.

      Added support for in-memory ICC profiles.

      Unified buildTransform and buildTransformFromOpenProfiles.

      The profile can now be either a filename, a profile object, or a
      file-like object containing an in-memory profile.

      Additional fixes from Florian Böch:

        Very nice - it just needs LCMS flags support so we can use black
        point compensation and softproofing :) See attached patches.  They
        also fix a naming issue which could cause confusion - display
        profile (ImageCms wording) actually means proof profile (lcms
        wording), so I changed variable names and docstrings where
        applicable. Patches are tested under Python 2.6.

    + Improved support for layer names in PSD files (from Sylvain Baubeau)

      Sylvain writes: I needed to be able to retrieve the names of the
      layers in a PSD files. But PsdImagePlugin.py didn't do the job so I
      wrote this very small patch.

    + Improved RGBA support for ImageTk for 8.4 and newer (from Con
      Radchenko).

      This replaces the slow run-length based encoding model with true
      compositing at the Tk level.

    + Added support for 16- and 32-bit images to McIdas loader.

      Based on file samples and stand-alone reader code provided by Craig
      Swank.

    + Added ImagePalette support to putpalette.

    + Fixed problem with incremental parsing of PNG files.

    + Make selftest.py report non-zero status on failure (from Mark
      Sienkiewicz)

    + Add big endian save support and multipage infrastructure to the TIFF
      writer (from Sebastian Haase).

    + Handle files with GPS IFD but no basic EXIF IFD (reported by Kurt
      Schwehr).

    + Added zTXT support (from Andrew Kuchling via Lowell Alleman).

    + Fixed potential infinite loop bug in ImageFont (from Guilherme Polo).

    + Added sample ICC profiles (from Kevin Cazabon)

    + Fixed array interface for I, F, and RGBA/RGBX images.

    + Added Chroma subsampling support for JPEG (from Justin Huff).

      Justin writes: Attached is a patch (against PIL 1.1.6) to provide
      control over the chroma subsampling done by the JPEG encoder.  This
      is often useful for reducing compression artifacts around edges of
      clipart and text.

    + Added USM/Gaussian Blur code from Kevin Cazabon.

    + Fixed bug w. uninitialized image data when cropping outside the
      source image.

    + Use ImageShow to implement the Image.show method.

      Most notably, this picks the 'display' utility when available.  It
      also allows application code to register new display utilities via
      the ImageShow registry.

    + Release the GIL in the PNG compressor (from Michael van Tellingen).

    + Revised JPEG CMYK handling.

      Always assume Adobe behaviour, both when reading and writing (based on
      a patch by Kevin Cazabon, and test data by Tim V. and Charlie Clark, and
      additional debugging by Michael van Tellingen).

    + Support for preserving ICC profiles (by Florian Böch via Tim Hatch).

      Florian writes:

      It's a beta, so still needs some testing, but should allow you to:
      - retain embedded ICC profiles when saving from/to JPEG, PNG, TIFF.
         Existing code doesn't need to be changed.
      - access embedded profiles in JPEG, PNG, PSD, TIFF.

      It also includes patches for TIFF to retain IPTC, Photoshop and XMP
      metadata when saving as TIFF again, read/write TIFF resolution
      information correctly, and to correct inverted CMYK JPEG files.

    + Fixed potential memory leak in median cut quantizer (from Evgeny Salmin).

    + Fixed OverflowError when reading upside-down BMP images.

    + Added resolution save option for PDF files.

      Andreas Kostyrka writes: I've included a patched PdfImagePlugin.py
      based on 1.1.6 as included in Ubuntu, that supports a "resolution"
      save option. Not great, but it makes the PDF saving more useful by
      allowing PDFs that are not exactly 72dpi.

    + Look for Tcl/Tk include files in version-specific include directory
      (from Encolpe Degoute).

    + Fixed grayscale rounding error in ImageColor.getcolor (from Tim
      Hatch).

    + Fixed calculation of mean value in ImageEnhance.Contrast (reported
      by "roop" and Scott David Daniels).

    + Fixed truetype positioning when first character has a negative left
      bearing (from Ned Batchelder):

      Ned writes: In PIL 1.1.6, ImageDraw.text will position the string
      incorrectly if the first character has a negative left bearing.  To
      see the problem, show a string like "///" in an italic font.  The
      first slash will be clipped at the left, and the string will be
      mis-positioned.

    + Fixed resolution unit bug in tiff reader/writer (based on code by
      Florian Höch, Gary Bloom, and others).

    + Added simple transparency support for RGB images (reported by
      Sebastian Spaeth).

    + Added support for Unicode filenames in ImageFont.truetype (from Donn
      Ingle).

    + Fixed potential crash in ImageFont.getname method (from Donn Ingle).

    + Fixed encoding issue in PIL/WalImageFile (from Santiago M. Mola).

    *** Changes from release 1.1.5 to 1.1.6 ***

    (1.1.6 released)

    + Fixed some 64-bit compatibility warnings for Python 2.5.

    + Added threading support for the Sane driver (from Abel Deuring).

    (1.1.6b2 released)

    + Added experimental "floodfill" function to the ImageDraw module
      (based on code by Eric Raymond).

    + The default arguments for "frombuffer" doesn't match "fromstring"
      and the documentation; this is a bug, and will most likely be fixed
      in a future version.  In this release, PIL prints a warning message
      instead.  To silence the warning, change any calls of the form
      "frombuffer(mode, size, data)" to

          frombuffer(mode, size, data, "raw", mode, 0, 1)

    + Added "fromarray" function, which takes an object implementing the
      NumPy array interface and creates a PIL Image from it. (from Travis
      Oliphant).

    + Added NumPy array interface support (__array_interface__) to the
      Image class (based on code by Travis Oliphant).

      This allows you to easily convert between PIL image memories and
      NumPy arrays:

        import numpy, Image

        im = Image.open('lena.jpg')

        a = numpy.asarray(im) # a is readonly

        im = Image.fromarray(a)

    + Fixed CMYK polarity for JPEG images, by treating all images as
      "Adobe CMYK" images. (thanks to Cesare Leonardi and Kevin Cazabon
      for samples, debugging, and patches).

    (1.1.6b1 released)

    + Added 'expand' option to the Image 'rotate' method.  If true, the
      output image is made large enough to hold the entire rotated image.

    + Changed the ImageDraw 'line' method to always draw the last pixel in
      a polyline, independent of line angle.

    + Fixed bearing calculation and clipping in the ImageFont truetype
      renderer; this could lead to clipped text, or crashes in the low-
      level _imagingft module.  (based on input from Adam Twardoch and
      others).

    + Added ImageQt wrapper module, for converting PIL Image objects to
      QImage objects in an efficient way.

    + Fixed 'getmodebands' to return the number of bands also for "PA"
      and "LA" modes.  Added 'getmodebandnames' helper that return the
      band names.

    (1.1.6a2 released)

    + Added float/double support to the TIFF loader (from Russell
      Nelson).

    + Fixed broken use of realloc() in path.c (from Jan Matejek)

    + Added save support for Spider images (from William Baxter).

    + Fixed broken 'paste' and 'resize' operations in pildriver
      (from Bill Janssen).

    + Added support for duplex scanning to the Sane interface (Abel
      Deuring).

    (1.1.6a1 released)

    + Fixed a memory leak in "convert(mode)", when converting from
      L to P.

    + Added pixel access object.  The "load" method now returns a
      access object that can be used to directly get and set pixel
      values, using ordinary [x, y] notation:

        pixel = im.load()
        v = pixel[x, y]
        pixel[x, y] = v

      If you're accessing more than a few pixels, this is a lot
      faster than using getpixel/putpixel.

    + Fixed building on Cygwin (from Miki Tebeka).

    + Fixed "point(callable)" on unloaded images (reported by Håkan
      Karlsson).

    + Fixed size bug in ImageWin.ImageWindow constructor (from Victor
      Reijs)

    + Fixed ImageMath float() and int() operations for Python 2.4
      (reported by Don Rozenberg).

    + Fixed "RuntimeError: encoder error -8 in tostring" problem for
      wide "RGB", "I", and "F" images.

    + Fixed line width calculation.

    (1.1.6a0 released)

    + Fixed byte order issue in Image.paste(ink) (from Ka-Ping Yee).

    + Fixed off-by-0.5 errors in the ANTIALIAS code (based on input
      from Douglas Bagnall).

    + Added buffer interface support to the Path constructor.  If
      a buffer is provided, it is assumed to contain a flat array
      of float coordinates (e.g. array.array('f', seq)).

    + Added new ImageMath module.

    + Fixed ImageOps.equalize when used with a small number of distinct
      values (reported by David Kirtley).

    + Fixed potential integer division in PSDraw.image (from Eric Etheridge).

    *** Changes from release 1.1 to 1.1.5 ***

    (1.1.5c2 and 1.1.5 final released)

    + Added experimental PERSPECTIVE transform method (from Jeff Breiden-
      bach).

    (1.1.5c1 released)

    + Make sure "thumbnail" never generates zero-wide or zero-high images
      (reported by Gene Skonicki)

    + Fixed a "getcolors" bug that could result in a zero count for some
      colors (reported by Richard Oudkerk).

    + Changed default "convert" palette to avoid "rounding errors" when
      round-tripping white source pixels (reported by Henryk Gerlach and
      Jeff Epler).

    (1.1.5b3 released)

    + Don't crash in "quantize" method if the number of colors requested
      is larger than 256.  This release raises a ValueError exception;
      future versions may return a mode "RGB" image instead (reported
      by Richard Oudkerk).

    + Added WBMP read/write support (based on code by Duncan Booth).

    (1.1.5b2 released)

    + Added DPI read/write support to the PNG codec.  The decoder sets
      the info["dpi"] attribute for PNG files with appropriate resolution
      settings.  The encoder uses the "dpi" option (based on code by Niki
      Spahiev).

    + Added limited support for "point" mappings from mode "I" to mode "L".
      Only 16-bit values are supported (other values are clipped), the lookup
      table must contain exactly 65536 entries, and the mode argument must be
      set to "L".

    + Added support for Mac OS X icns files (based on code by Bob Ippolito).

    + Added "ModeFilter" support to the ImageFilter module.

    + Added support for Spider images (from William Baxter).  See the
      comments in PIL/SpiderImagePlugin.py for more information on this
      format.

    (1.1.5b1 released)

    + Added new Sane release (from Ralph Heinkel).  See the Sane/README
      and Sane/CHANGES files for more information.

    + Added experimental PngInfo chunk container to the PngImageFile
      module.  This can be used to add arbitrary chunks to a PNG file.
      Create a PngInfo instance, use "add" or "add_text" to add chunks,
      and pass the instance as the "pnginfo" option when saving the
      file.

    + Added "getpalette" method.  This returns the palette as a list,
      or None if the image has no palette.  To modify the palette, use
      "getpalette" to fetch the current palette, modify the list, and
      put it back using "putpalette".

    + Added optional flattening to the ImagePath "tolist" method.
      tolist() or tolist(0) returns a list of 2-tuples, as before.
      tolist(1) returns a flattened list instead.

    (1.1.5a5 released)

    + Fixed BILINEAR/BICUBIC/ANTIALIAS filtering for mode "LA".

    + Added "getcolors()" method.  This is similar to the existing histo-
      gram method, but looks at color values instead of individual layers,
      and returns an unsorted list of (count, color) tuples.

      By default, the method returns None if finds more than 256 colors.
      If you need to look for more colors, you can pass in a limit (this
      is used to allocate internal tables, so you probably don't want to
      pass in too large values).

    + Build improvements: Fixed building under AIX, improved detection of
      FreeType2 and Mac OS X framework libraries, and more.  Many thanks
      to everyone who helped test the new "setup.py" script!

    (1.1.5a4 released)

    + The "save" method now looks for a file format driver before
      creating the file.

    + Don't use antialiased truetype fonts when drawing in mode "P", "I",
      and "F" images.

    + Rewrote the "setup.py" file.  The new version scans for available
      support libraries, and configures both the libImaging core library
      and the bindings in one step.

      To use specific versions of the libraries, edit the ROOT variables
      in the setup.py file.

    + Removed threaded "show" viewer; use the old "show" implementation
      instead (Windows).

    + Added deprecation warnings to Image.offset, ImageDraw.setink, and
      ImageDraw.setfill.

    + Added width option to ImageDraw.line().  The current implementation
      works best for straight lines; it does not support line joins, so
      polylines won't look good.

    + ImageDraw.Draw is now a factory function instead of a class.  If
      you need to create custom draw classes, inherit from the ImageDraw
      class.    All other code should use the factory function.

    + Fixed loading of certain PCX files (problem reported by Greg
      Hamilton, who also provided samples).

    + Changed _imagingft.c to require FreeType 2.1 or newer.  The
      module can still be built with earlier versions; see comments
      in _imagingft.c for details.

    (1.1.5a3 released)

    + Added 'getim' method, which returns a PyCObject wrapping an
      Imaging pointer.  The description string is set to IMAGING_MAGIC.
      See Imaging.h for pointer and string declarations.

    + Fixed reading of TIFF JPEG images (problem reported by Ulrik
      Svensson).

    + Made ImageColor work under Python 1.5.2

    + Fixed division by zero "equalize" on very small images (from
      Douglas Bagnall).

    (1.1.5a2 released)

    + The "paste" method now supports the alternative "paste(im, mask)"
      syntax (in this case, the box defaults to im's bounding box).

    + The "ImageFile.Parser" class now works also for PNG files with
      more than one IDAT block.

    + Added DPI read/write to the TIFF codec, and fixed writing of
      rational values.  The decoder sets the info["dpi"] attribute
      for TIFF files with appropriate resolution settings.  The
      encoder uses the "dpi" option.

    + Disable interlacing for small (or narrow) GIF images, to
      work around what appears to be a hard-to-find bug in PIL's
      GIF encoder.

    + Fixed writing of mode "P" PDF images.  Made mode "1" PDF
      images smaller.

    + Made the XBM reader a bit more robust; the file may now start
      with a few whitespace characters.

    + Added support for enhanced metafiles to the WMF driver.  The
      separate PILWMF kit lets you render both placeable WMF files
      and EMF files as raster images.  See

          http://effbot.org/downloads#pilwmf

    (1.1.5a1 released)

    + Replaced broken WMF driver with a WMF stub plugin (see below).

    + Fixed writing of mode "1", "L", and "CMYK" PDF images (based on
      input from Nicholas Riley and others).

    + Fixed adaptive palette conversion for zero-width or zero-height
      images (from Chris Cogdon)

    + Fixed reading of PNG images from QuickTime 6 (from Paul Pharr)

    + Added support for StubImageFile plugins, including stub plugins
      for BUFR, FITS, GRIB, and HDF5 files.  A stub plugin can identify
      a given file format, but relies on application code to open and
      save files in that format.

    + Added optional "encoding" argument to the ImageFont.truetype
      factory.  This argument can be used to specify non-Unicode character
      maps for fonts that support that.  For example, to draw text using
      the Microsoft Symbol font, use:

          font = ImageFont.truetype("symbol.ttf", 16, encoding="symb")
          draw.text((0, 0), unichr(0xF000 + 0xAA))

      (note that the symbol font uses characters in the 0xF000-0xF0FF
       range)

      Common encodings are "unic" (Unicode), "symb" (Microsoft Symbol),
      "ADOB" (Adobe Standard), "ADBE" (Adobe Expert), and "armn" (Apple
      Roman).  See the FreeType documentation for more information.

    + Made "putalpha" a bit more robust; you can now attach an alpha
      layer to a plain "L" or "RGB" image, and you can also specify
      constant alphas instead of alpha layers (using integers or colour
      names).

    + Added experimental "LA" mode support.

      An "LA" image is an "L" image with an attached transparency layer.
      Note that support for "LA" is not complete; some operations may
      fail or produce unexpected results.

    + Added "RankFilter", "MinFilter", "MedianFilter", and "MaxFilter"
      classes to the ImageFilter module.

    + Improved support for applications using multiple threads; PIL
      now releases the global interpreter lock for many CPU-intensive
      operations (based on work by Kevin Cazabon).

    + Ignore Unicode characters in the PCF loader (from Andres Polit)

    + Fixed typo in OleFileIO.loadfat, which could affect loading of
      FlashPix and Image Composer images (Daniel Haertle)

    + Fixed building on platforms that have Freetype but don't have
      Tcl/Tk (Jack Jansen, Luciano Nocera, Piet van Oostrum and others)

    + Added EXIF GPSInfo read support for JPEG files.  To extract
      GPSInfo information, open the file, extract the exif dictionary,
      and check for the key 0x8825 (GPSInfo).  If present, it contains
      a dictionary mapping GPS keys to GPS values.  For a list of keys,
      see the EXIF specification.

      The "ExifTags" module contains a GPSTAGS dictionary mapping GPS
      tags to tag names.

    + Added DPI read support to the PCX and DCX codecs (info["dpi"]).

    + The "show" methods now uses a built-in image viewer on Windows.
      This viewer creates an instance of the ImageWindow class (see
      below) and keeps it running in a separate thread.  NOTE: This
      was disabled in 1.1.5a4.

    + Added experimental "Window" and "ImageWindow" classes to the
      ImageWin module.  These classes allow you to create a WCK-style
      toplevel window, and use it to display raster data.

    + Fixed some Python 1.5.2 issues (to build under 1.5.2, use the
      Makefile.pre.in/Setup.in approach)

    + Added support for the TIFF FillOrder tag.  PIL can read mode "1",
      "L", "P" and "RGB" images with non-standard FillOrder (based on
      input from Jeff Breidenbach).

    (1.1.4 final released)

    + Fixed ImageTk build problem on Unix.

    (1.1.4b2 released)

    + Improved building on Mac OS X (from Jack Jansen).

    + Improved building on Windows with MinGW (from Klamer Shutte).

    + If no font is specified, ImageDraw now uses the embedded default
      font.  Use the "load" or "truetype" methods to load a real font.

    + Added embedded default font to the ImageFont module (currently
      an 8-pixel Courier font, taken from the X window distribution).

    (1.1.4b1 released)

    + Added experimental EXIF support for JPEG files.  To extract EXIF
      information from a JPEG file, open the file as usual, and call the
      "_getexif" method.  If successful, this method returns a dictionary
      mapping EXIF TIFF tags to values.  If the file does not contain EXIF
      data, the "_getexif" method returns None.

      The "ExifTags" module contains a dictionary mapping tags to tag
      names.

      This interface will most likely change in future versions.

    + Fixed a bug when using the "transparency" option with the GIF
      writer.

    + Added limited support for "bitfield compression" in BMP files
      and DIB buffers, for 15-bit, 16-bit, and 32-bit images.  This
      also fixes a problem with ImageGrab module when copying screen-
      dumps from the clipboard on 15/16/32-bit displays.

    + Added experimental WAL (Quake 2 textures) loader.  To use this
      loader, import WalImageFile and call the "open" method in that
      module.

    (1.1.4a4 released)

    + Added updated SANE driver (Andrew Kuchling, Abel Deuring)

    + Use Python's "mmap" module on non-Windows platforms to read some
      uncompressed formats using memory mapping.  Also added a "frombuffer"
      function that allows you to access the contents of an existing string
      or buffer object as if it were an image object.

    + Fixed a memory leak that could appear when processing mode "P"
      images (from Pier Paolo Glave)

    + Ignore Unicode characters in the BDF loader (from Graham Dumpleton)

    (1.1.4a3 released; windows only)

    + Added experimental RGBA-on-RGB drawing support.  To use RGBA
      colours on an RGB image, pass "RGBA" as the second string to
      the ImageDraw.Draw constructor.

    + Added support for non-ASCII strings (Latin-1) and Unicode
      to the truetype font renderer.

    + The ImageWin "Dib" object can now be constructed directly from
      an image object.

    + The ImageWin module now allows you use window handles as well
      as device contexts.  To use a window handle, wrap the handle in
      an ImageWin.HWND object, and pass in this object instead of the
      device context.

    (1.1.4a2 released)

    + Improved support for 16-bit unsigned integer images (mode "I;16").
      This includes TIFF reader support, and support for "getextrema"
      and "point" (from Klamer Shutte).

    + Made the BdfFontFile reader a bit more robust (from Kevin Cazabon
      and Dmitry Vasiliev)

    + Changed TIFF writer to always write Compression tag, even when
      using the default compression (from Greg Couch).

    + Added "show" support for Mac OS X (from Dan Wolfe).

    + Added clipboard support to the "ImageGrab" module (Windows only).
      The "grabclipboard" function returns an Image object, a list of
      filenames (not in 1.1.4), or None if neither was found.

    (1.1.4a1 released)

    + Improved support for drawing RGB data in palette images.  You can
      now use RGB tuples or colour names (see below) when drawing in a
      mode "P" image.  The drawing layer automatically assigns color
      indexes, as long as you don't use more than 256 unique colours.

    + Moved self test from MiniTest/test.py to ./selftest.py.

    + Added support for CSS3-style color strings to most places that
      accept colour codes/tuples.  This includes the "ImageDraw" module,
      the Image "new" function, and the Image "paste" method.

      Colour strings can use one of the following formats: "#f00",
      "#ff0000", "rgb(255,0,0)", "rgb(100%,0%,0%)", "hsl(0, 100%, 50%)",
      or "red" (most X11-style colour names are supported).  See the
      documentation for the "ImageColor" module for more information.

    + Fixed DCX decoder (based on input from Larry Bates)

    + Added "IptcImagePlugin.getiptcinfo" helper to extract IPTC/NAA
      newsphoto properties from JPEG, TIFF, or IPTC files.

    + Support for TrueType/OpenType fonts has been added to
      the standard distribution.  You need the freetype 2.0
      library.

    + Made the PCX reader a bit more robust when reading 2-bit
      and 4-bit PCX images with odd image sizes.

    + Added "Kernel" class to the ImageFilter module.  This class
      allows you to filter images with user-defined 3x3 and 5x5
      convolution kernels.

    + Added "putdata" support for mode "I", "F" and "RGB".

    + The GIF writer now supports the transparency option (from
      Denis Benoit).

    + A HTML version of the module documentation is now shipped
      with the source code distribution.  You'll find the files in
      the Doc subdirectory.

    + Added support for Palm pixmaps (from Bill Janssen).  This
      change was listed for 1.1.3, but the "PalmImagePlugin" driver
      didn't make it into the distribution.

    + Improved decoder error messages.

    (1.1.3 final released)

    + Made setup.py look for old versions of zlib.  For some back-
      ground, see: http://www.gzip.org/zlib/advisory-2002-03-11.txt

    (1.1.3c2 released)

    + Added setup.py file (tested on Unix and Windows).  You still
      need to build libImaging/imaging.lib in the traditional way,
      but the setup.py script takes care of the rest.

      The old Setup.in/Makefile.pre.in build method is still
      supported.

    + Fixed segmentation violation in ANTIALIAS filter (an internal
      buffer wasn't properly allocated).

    (1.1.3c1 released)

    + Added ANTIALIAS downsampling filter for high-quality "resize"
      and "thumbnail" operations.  Also added filter option to the
      "thumbnail" operation; the default value is NEAREST, but this
      will most likely change in future versions.

    + Fixed plugin loader to be more robust if the __file__
      variable isn't set.

    + Added seek/tell support (for layers) to the PhotoShop
      loader.  Layer 0 is the main image.

    + Added new (but experimental) "ImageOps" module, which provides
      shortcuts for commonly used operations on entire images.

    + Don't mess up when loading PNG images if the decoder leaves
      data in the output buffer.  This could cause internal errors
      on some PNG images, with some versions of ZLIB. (Bug report
      and patch provided by Bernhard Herzog.)

    + Don't mess up on Unicode filenames.

    + Don't mess up when drawing on big endian platforms.

    + Made the TIFF loader a bit more robust; it can now read some
      more slightly broken TIFF files (based on input from Ted Wright,
      Bob Klimek, and D. Alan Stewart)

    + Added OS/2 EMX build files (from Andrew MacIntyre)

    + Change "ImageFont" to reject image files if they don't have the
      right mode.  Older versions could leak memory for "P" images.
      (Bug reported by Markus Gritsch).

    + Renamed some internal functions to avoid potential build
      problem on Mac OS X.

    + Added DL_EXPORT where relevant (for Cygwin, based on input
      from Robert Yodlowski)

    + (re)moved bogus __init__ call in BdfFontFile (bug spotted
      by Fred Clare)

    + Added "ImageGrab" support (Windows only)

    + Added support for XBM hotspots (based on code contributed by
      Bernhard Herzog).

    + Added write support for more TIFF tags, namely the Artist,
      Copyright, DateTime, ResolutionUnit, Software, XResolution and
      YResolution tags (from Greg Couch)

    + Added TransposedFont wrapper to ImageFont module

    + Added "optimize" flag to GIF encoder.  If optimize is present
      and non-zero, PIL will work harder to create a small file.

    + Raise "EOFError" (not IndexError) when reading beyond the
      end of a TIFF sequence.

    + Support rewind ("seek(0)") for GIF and TIFF sequences.

    + Load grayscale GIF images as mode "L"

    + Added DPI read/write support to the JPEG codec.  The decoder
      sets the info["dpi"] attribute for JPEG files with JFIF dpi
      settings.  The encoder uses the "dpi" option:

          im = Image.open("file.jpg")
          dpi = im.info["dpi"] # raises KeyError if DPI not known
          im.save("out.jpg", dpi=dpi)

      Note that PIL doesn't always preserve the "info" attribute
      for normal image operations.

    (1.1.2c1 and 1.1.2 final released)

    + Adapted to Python 2.1.  Among other things, all uses of the
      "regex" module have been replaced with "re".

    + Fixed attribute error when reading large PNG files (this bug
      was introduced in maintenance code released after the 1.1.1
      release)

    + Ignore non-string objects in sys.path

    + Fixed Image.transform(EXTENT) for negative xoffsets

    + Fixed loading of image plugins if PIL is installed as a package.
      (The plugin loader now always looks in the directory where the
      Image.py module itself is found, even if that directory isn't on
      the standard search path)

    + The Png plugin has been added to the list of preloaded standard
      formats

    + Fixed bitmap/text drawing in fill mode.

    + Fixed "getextrema" to work also for multiband images.

    + Added transparency support for L and P images to the PNG codec.

    + Improved support for read-only images.  The "load" method now
      sets the "readonly" attribute for memory-mapped images.  Operations
      that modifies an image in place (such as "paste" and drawing operations)
      creates an in-memory copy of the image, if necessary.  (before this
      change, any attempt to modify a memory-mapped image resulted in a
      core dump...)

    + Added special cases for lists everywhere PIL expects a sequence.
      This should speed up things like "putdata" and drawing operations.

    + The Image.offset method is deprecated.  Use the ImageChops.offset
      function instead.

    + Changed ImageChops operators to copy palette and info dictionary
      from the first image argument.

    (1.1.1 released)

    + Additional fixes for Python 1.6/2.0, including TIFF "save" bug.

    + Changed "init" to properly load plugins when PIL is used as a
      package.

    + Fixed broken "show" method (on Unix)

    *** Changes from release 1.0 to 1.1 ***

    + Adapted to Python 1.6 ("append" and other method changes)

    + Fixed Image.paste when pasting with solid colour and matte
      layers ("L" or "RGBA" masks) (bug reported by Robert Kern)

    + To make it easier to distribute prebuilt versions of PIL,
      the tkinit binding stuff has been moved to a separate
      extension module, named "_imagingtk".

    *** Changes from release 0.3b2 to 1.0 final ***

    + If there's no 16-bit integer (like on a Cray T3E), set
      INT16 to the smallest integer available.  Most of the
      library works just fine anyway (from Bill Crutchfield)

    + Tweaks to make drawing work on big-endian platforms.

    (1.0c2 released)

    + If PIL is built with the WITH_TKINTER flag, ImageTk can
      automatically hook into a standard Tkinter build.  You
      no longer need to build your own Tkinter to use the
      ImageTk module.

      The old way still works, though.  For more information,
      see Tk/install.txt.

    + Some tweaks to ImageTk to support multiple Tk interpreters
      (from Greg Couch).

    + ImageFont "load_path" now scans directory mentioned in .pth
      files (from Richard Jones).

    (1.0c1 released)

    + The TIFF plugin has been rewritten.  The new plugin fully
      supports all major PIL image modes (including F and I).

    + The ImageFile module now includes a Parser class, which can
      be used to incrementally decode an image file (while down-
      loading it from the net, for example).  See the handbook for
      details.

    + "show" now converts non-standard modes to "L" or "RGB" (as
      appropriate), rather than writing weird things to disk for
      "xv" to choke upon. (bug reported by Les Schaffer).

    (1.0b2 released)

    + Major speedups for rotate, transform(EXTENT), and transform(AFFINE)
      when using nearest neighbour resampling.

    + Modified ImageDraw to be compatible with the Arrow graphics
      interface.  See the handbook for details.

    + PIL now automatically loads file codecs when used as a package
      (from The Dragon De Monsyne).  Also included an __init__.py file
      in the standard distribution.

    + The GIF encoder has been modified to produce much smaller files.

      PIL now uses a run-length encoding method to encode GIF files.
      On a random selection of GIF images grabbed from the web, this
      version makes the images about twice as large as the original
      LZW files, where the earlier version made them over 5 times
      larger.  YMMV, of course.

    + Added PCX write support (works with "1", "P", "L", and "RGB")

    + Added "bitmap" and "textsize" methods to ImageDraw.

    + Improved font rendering code.  Fixed a bug or two, and moved
      most of the time critical stuff to C.

    + Removed "bdf2pil.py".  Use "pilfont.py" instead!

    + Improved 16-bit support (still experimental, though).

      The following methods now support "I;16" and "I;16B" images:
      "getpixel", "copy", "convert" (to and from mode "I"), "resize",
      "rotate", and "transform" with nearest neighbour filters, and
      "save" using the IM format.  The "new" and "open" functions
      also work as expected.  On Windows, 16-bit files are memory
      mapped.

      NOTE: ALL other operations are still UNDEFINED on 16-bit images.

    + The "paste" method now supports constant sources.

      Just pass a colour value (a number or a tuple, depending on
      the target image mode) instead of the source image.

      This was in fact implemented in an inefficient way in
      earlier versions (the "paste" method generated a temporary
      source image if you passed it a colour instead of an image).
      In this version, this is handled on the C level instead.

    + Added experimental "RGBa" mode support.

      An "RGBa" image is an RGBA image where the colour components
      have have been premultiplied with the alpha value.  PIL allows
      you to convert an RGBA image to an RGBa image, and to paste
      RGBa images on top of RGB images.  Since this saves a bunch
      of multiplications and shifts, it is typically about twice
      as fast an ordinary RGBA paste.

    + Eliminated extra conversion step when pasting "RGBA" or "RGBa"
      images on top of "RGB" images.

    + Fixed Image.BICUBIC resampling for "RGB" images.

    + Fixed PCX image file handler to properly read 8-bit PCX
      files (bug introduced in 1.0b1, reported by Bernhard
      Herzog)

    + Fixed PSDraw "image" method to restore the coordinate
      system.

    + Fixed "blend" problem when applied to images that was
      not already loaded (reported by Edward C. Jones)

    + Fixed -f option to "pilconvert.py" (from Anthony Baxter)

    (1.0b1 released)

    + Added Toby J. Sargeant's quantization package.  To enable
      quantization, use the "palette" option to "convert":

        imOut = im.convert("P", palette=Image.ADAPTIVE)

      This can be used with "L", "P", and "RGB" images.  In this
      version, dithering cannot be used with adaptive palettes.

      Note: ADAPTIVE currently maps to median cut quantization
      with 256 colours.  The quantization package also contains
      a maximum coverage quantizer, which will be supported by
      future versions of PIL.

    + Added Eric S. Raymond's "pildriver" image calculator to the
      distribution.  See the docstring for more information.

    + The "offset" method no longer dumps core if given positive
      offsets (from Charles Waldman).

    + Fixed a resource leak that could cause ImageWin to run out of
      GDI resources (from Roger Burnham).

    + Added "arc", "chord", and "pieslice" methods to ImageDraw (inspired
      by code contributed by Richard Jones).

    + Added experimental 16-bit support, via modes "I;16" (little endian
      data) and "I;16B" (big endian).  Only a few methods properly support
      such images (see above).

    + Added XV thumbnail file handler (from Gene Cash).

    + Fixed BMP image file handler to handle palette images with small
      palettes (from Rob Hooft).

    + Fixed Sun raster file handler for palette images (from Charles
      Waldman).

    + Improved various internal error messages.

    + Fixed Path constructor to handle arbitrary sequence objects.  This
      also affects the ImageDraw class (from Richard Jones).

    + Fixed a bug in JpegDecode that caused PIL to report "decoder error
      -2" for some progressive JPEG files (reported by Magnus Källström,
      who also provided samples).

    + Fixed a bug in JpegImagePlugin that caused PIL to hang when loading
      JPEG files using 16-bit quantization tables.

    + The Image "transform" method now supports Image.QUAD transforms.
      The data argument is an 8-tuple giving the upper left, lower
      left, lower right, and upper right corner of the source quadri-
      lateral.  Also added Image.MESH transform which takes a list
      of quadrilaterals.

    + The Image "resize", "rotate", and "transform" methods now support
      Image.BILINEAR (2x2) and Image.BICUBIC (4x4) resampling filters.
      Filters can be used with all transform methods.

    + The ImageDraw "rectangle" method now includes both the right
      and the bottom edges when drawing filled rectangles.

    + The TGA decoder now works properly for runlength encoded images
      which have more than one byte per pixel.

    + "getbands" on an YCbCr image now returns ("Y", "Cb", "Cr")

    + Some file drivers didn't handle the optional "modify" argument
      to the load method.  This resulted in exceptions when you used
      "paste" (and other methods that modify an image in place) on a
      newly opened file.

    *** Changes from release 0.2 (b5) to 0.3 (b2) ***

    (0.3b2 released)

    The test suite includes 825 individual tests.

    + An Image "getbands" method has been added.  It returns a tuple
      containing the individual band names for this image.  To figure
      out how many bands an image has, use "len(im.getbands())".

    + An Image "putpixel" method has been added.

    + The Image "point" method can now be used to convert "L" images
      to any other format, via a lookup table.  That table should
      contain 256 values for each band in the output image.

    + Some file drivers (including FLI/FLC, GIF, and IM) accidently
      overwrote the offset method with an internal attribute.  All
      drivers have been updated to use private attributes where
      possible.

    + The Image "histogram" method now works for "I" and "F" images.
      For these modes, PIL divides the range between the min and
      max values used in the image into 256 bins.  You can also
      pass in your own min and max values via the "extrema" option:

        h = im.histogram(extrema=(0, 255))

    + An Image "getextrema" method has been added.  It returns the
      min and max values used in the image. In this release, this
      works for single band images only.

    + Changed the PNG driver to load and save mode "I" images as
      16-bit images.  When saving, values outside the range 0..65535
      are clipped.

    + Fixed ImageFont.py to work with the new "pilfont" compiler.

    + Added JPEG "save" and "draft" support for mode "YCbCr" images.
      Note that if you save an "YCbCr" image as a JPEG file and read
      it back, it is read as an RGB file.  To get around this, you
      can use the "draft" method:

        im = Image.open("color.jpg")
        im.draft("YCbCr", im.size)

    + Read "RGBA" TGA images.  Also fixed the orientation bug; all
      images should now come out the right way.

    + Changed mode name (and internal representation) from "YCrCb"
      to "YCbCr" (!)
      *** WARNING: MAY BREAK EXISTING CODE ***

    (0.3b1 released)

    The test suite includes 750 individual tests.

    + The "pilfont" package is now included in the standard PIL
      distribution.  The pilfont utility can be used to convert
      X BDF and PCF raster font files to a format understood by
      the ImageFont module.

    + GIF files are now interlaced by default.  To write a
      non-interlaced file, pass interlace=0 to the "save"
      method.

    + The default string format has changed for the "fromstring"
      and "tostring" methods.
      *** WARNING: MAY BREAK EXISTING CODE ***

      NOTE: If no extra arguments are given, the first line in
      the string buffer is the top line of the image, instead of
      the bottom line.  For RGB images, the string now contains
      3 bytes per pixel instead of 4.  These changes were made
      to make the methods compatible with the "fromstring"
      factory function.

      To get the old behaviour, use the following syntax:

        data = im.tostring("raw", "RGBX", 0, -1)
        im.fromstring(data, "raw", "RGBX", 0, -1)

    + "new" no longer gives a MemoryError if the width or height
      is zero (this only happened on platforms where malloc(0)
      or calloc(0) returns NULL).

    + "new" now adds a default palette object to "P" images.

    + You can now convert directly between all modes supported by
      PIL.  When converting colour images to "P", PIL defaults to
      a "web" palette and dithering.  When converting greyscale
      images to "1", PIL uses a thresholding and dithering.

    + Added a "dither" option to "convert".  By default, "convert"
      uses floyd-steinberg error diffusion for "P" and "1" targets,
      so this option is only used to *disable* dithering. Allowed
      values are NONE (no dithering) or FLOYDSTEINBERG (default).

        imOut = im.convert("P", dither=Image.NONE)

    + Added a full set of "I" decoders.  You can use "fromstring"
      (and file decoders) to read any standard integer type as an
      "I" image.

    + Added some support for "YCbCr" images (creation, conversion
      from/to "L" and "RGB", IM YCC load/save)

    + "getpixel" now works properly with fractional coordinates.

    + ImageDraw "setink" now works with "I", "F", "RGB", "RGBA",
      "RGBX", "CMYK", and "YCbCr" images.

    + ImImagePlugin no longer attaches palettes to "RGB" images.

    + Various minor fixes.

    (0.3a4 released)

    + Added experimental IPTC/NAA support.

    + Eliminated AttributeError exceptions after "crop" (from
      Skip Montanaro)

    + Reads some uncompressed formats via memory mapping (this
      is currently supported on Win32 only)

    + Fixed some last minute glitches in the last alpha release
      (Types instead of types in Image.py, version numbers, etc.)

    + Eliminated some more bogus compiler warnings.

    + Various fixes to make PIL compile and run smoother on Macs
      (from Jack Jansen).

    + Fixed "fromstring" and "tostring" for mode "I" images.

    (0.3a3 released)

    The test suite includes 530 individual tests.

    + Eliminated unexpected side-effect in "paste" with matte.  "paste"
      now works properly also if compiled with "gcc".

    + Adapted to Python 1.5 (build issues only)

    + Fixed the ImageDraw "point" method to draw also the last
      point (!).

    + Added "I" and "RGBX" support to Image.new.

    + The plugin path is now properly prepended to the module search
      path when a plugin module is imported.

    + Added "draw" method to the ImageWin.Dib class.  This is used by
      Topaz to print images on Windows printers.

    + "convert" now supports conversions from "P" to "1" and "F".

    + "paste" can now take a colour instead of an image as the first argument.
      The colour must match the colour argument given to the new function, and
      match the mode of the target image.

    + Fixed "paste" to allow a mask also for mode "F" images.

    + The BMP driver now saves mode "1" images.  When loading images, the mode
      is set to "L" for 8-bit files with greyscale palettes, and to "P" for
      other 8-bit files.

    + The IM driver now reads and saves "1" images (file modes "0 1" or "L 1").

    + The JPEG and GIF drivers now saves "1" images.  For JPEG, the image
      is saved as 8-bit greyscale (it will load as mode "L").  For GIF, the
      image will be loaded as a "P" image.

    + Fixed a potential buffer overrun in the GIF encoder.

    (0.3a2 released)

    The test suite includes 400 individual tests.

    + Improvements to the test suite revealed a number of minor bugs, which
      are all fixed.  Note that crop/paste, 32-bit ImageDraw, and ImageFont
      are still weak spots in this release.

    + Added "putpalette" method to the Image class.  You can use this
      to add or modify the palette for "P" and "L" images.  If a palette
      is added to an "L" image, it is automatically converted to a "P"
      image.

    + Fixed ImageDraw to properly handle 32-bit image memories
      ("RGB", "RGBA", "CMYK", "F")

    + Fixed "fromstring" and "tostring" not to mess up the mode attribute
      in default mode.

    + Changed ImPlatform.h to work on CRAY's (don't have one at home, so I
      haven't tried it).  The previous version assumed that either "short"
      or "int" were 16-bit wide. PIL still won't compile on platforms where
      neither "short", "int" nor "long" are 32-bit wide.

    + Added file= and data= keyword arguments to PhotoImage and BitmapImage.
      This allows you to use them as drop-in replacements for the corre-
      sponding Tkinter classes.

    + Removed bogus references to the crack coder (ImagingCrack).

    (0.3a1 released)

    + Make sure image is loaded in "tostring".

    + Added floating point packer (native 32-bit floats only).

    *** Changes from release 0.1b1 to 0.2 (b5) ***

    + Modified "fromstring" and "tostring" methods to use file codecs.
      Also added "fromstring" factory method to create an image directly
      from data in a string.

    + Added support for 32-bit floating point images (mode "F").  You
      can convert between "L" and "F" images, and apply a subset of the
      available image processing methods on the "F" image.  You can also
      read virtually any data format into a floating point image memory;
      see the section on "Decoding Floating Point Data" in the handbook
      for more information.

    (0.2b5 released; on windows only)

    + Fixed the tobitmap() method to work properly for small bitmaps.

    + Added RMS and standard deviation to the ImageStat.Stat class.  Also
      modified the constructor to take an optional feature mask, and also
      to accept either an image or a list containing the histogram data.

    + The BitmapImage code in ImageTk can now use a special bitmap
      decoder, which has to be patched into Tk.  See the "Tk/pilbitmap.txt"
      file for details.  If not installed, bitmaps are transferred to Tk as
      XBM strings.

    + The PhotoImage code in ImageTk now uses a Tcl command ("PyImagingPaste")
      instead of a special image type.  This gives somewhat better performance,
      and also allows PIL to support transparency.
      *** WARNING: TKAPPINIT MUST BE MODIFIED ***

    + ImageTk now honours the alpha layer in RGBA images.  Only fully
      transparent pixels are made transparent (that is, the alpha layer
      is treated as a mask).  To treat the alpha laters as a matte, you
      must paste the image on the background before handing it over to
      ImageTk.

    + Added McIdas reader (supports 8-bit images only).

    + PIL now preloads drivers for BMP, GIF, JPEG, PPM, and TIFF.  As
      long as you only load and save these formats, you don't have to
      wait for a full scan for drivers.  To force scanning, call the
      Image.init() function.

    + The "seek" and "tell" methods are now always available, also for
      single-frame images.

    + Added optional mask argument to histogram method.  The mask may
      be an "1" or "L" image with the same size as the original image.
      Only pixels where the mask is non-zero are included in the
      histogram.

    + The "paste" method now allows you to specify only the lower left
      corner (a 2-tuple), instead of the full region (a 4-tuple).

    + Reverted to old plugin scanning model; now scans all directory
      names in the path when looking for plugins.

    + Added PIXAR raster support.  Only uncompressed ("dumped") RGB
      images can currently be read (based on information provided
      by Greg Coats).

    + Added FlashPix (FPX) read support.  Reads all pixel formats, but
      only the highest resolution is read, and the viewing transform is
      currently ignored.

    + Made PNG encoding somewhat more efficient in "optimize" mode; a
      bug in 0.2b4 didn't enable all predictor filters when optimized
      storage were requested.

    + Added Microsoft Image Composer (MIC) read support.  When opened,
      the first sprite in the file is loaded.  You can use the seek method
      to load additional sprites from the file.

    + Properly reads "P" and "CMYK" PSD images.

    + "pilconvert" no longer optimizes by default; use the -o option to
      make the file as small as possible (at the expense of speed); use
      the -q option to set the quality when compressing to JPEG.

    + Fixed "crop" not to drop the palette for "P" images.

    + Added and verified FLC support.

    + Paste with "L" or "RGBA" alpha is now several times faster on most
      platforms.

    + Changed Image.new() to initialize the image to black, as described
      in the handbook.  To get an uninitialized image, use None as the
      colour.

    + Fixed the PDF encoder to produce a valid header; Acrobat no longer
      complains when you load PDF images created by PIL.

    + PIL only scans fully-qualified directory names in the path when
      looking for plugins.
      *** WARNING: MAY BREAK EXISTING CODE ***

    + Faster implementation of "save" used when filename is given,
      or when file object has "fileno" and "flush" methods.

    + Don't crash in "crop" if region extends outside the source image.

    + Eliminated a massive memory leak in the "save" function.

    + The GIF decoder doesn't crash if the code size is set to an illegal
      value.  This could happen since another bug didn't handle local
      palettes properly if they didn't have the same size as the
      global palette (not very common).

    + Added predictor support (TIFF 6.0 section 14) to the TIFF decoder.

    + Fixed palette and padding problems in BMP driver.  Now properly
      writes "1", "L", "P" and "RGB" images.

    + Fixed getpixel()/getdata() to return correct pixel values.

    + Added PSD (PhotoShop) read support.  Reads both uncompressed
      and compressed images of most types.

    + Added GIF write support (writes "uncompressed" GIF files only,
      due to unresolvable licensing issues).  The "gifmaker.py" script
      can be used to create GIF animations.

    + Reads 8-bit "L" and "P" TGA images.  Also reads 16-bit "RGB"
      images.

    + Added FLI read support.  This driver has only been tested
      on a few FLI samples.

    + Reads 2-bit and 4-bit PCX images.

    + Added MSP read and write support.  Both version 1 and 2 can be
      read, but only version 1 (uncompressed) files are written.

    + Fixed a bug in the FLI/FLC identification code that caused the
      driver to raise an exception when parsing valid FLI/FLC files.

    + Improved performance when loading file format plugins, and when
      opening files.

    + Added GIF animation support, via the "seek" and "tell" methods.
      You can use "player.py" to play an animated GIF file.

    + Removed MNG support, since the spec is changing faster than I
      can change the code.  I've added support for the experimental
      ARG format instead.  Contact me for more information on this
      format.

    + Added keyword options to the "save" method.  The following options
      are currently supported:

          format	option		description
          --------------------------------------------------------
          JPEG	optimize	minimize output file at the
                    expense of compression speed.

          JPEG	progressive	enable progressive output. the
                    option value is ignored.

          JPEG	quality		set compression quality (1-100).
                    the default value is 75.

          JPEG	smooth		smooth dithered images.  value
                    is strength (1-100).  default is
                    off (0).

          PNG	optimize	minimize output file at the
                    expense of compression speed.

      Expect more options in future releases.  Also note that
      file writers silently ignore unknown options.

    + Plugged memory leaks in the PNG and TIFF decoders.

    + Added PNG write support.

    + (internal) RGB unpackers and converters now set the pad byte
      to 255 (full opacity).

    + Properly handles the "transparency" property for GIF, PNG
      and XPM files.

    + Added a "putalpha" method, allowing you to attach a "1" or "L"
      image as the alpha layer to an "RGBA" image.

    + Various improvements to the sample scripts:

      "pilconvert"  Carries out some extra tricks in order to make
            the resulting file as small as possible.

      "explode"	(NEW) Split an image sequence into individual frames.

      "gifmaker"	(NEW) Convert a sequence file into a GIF animation.
            Note that the GIF encoder create "uncompressed" GIF
            files, so animations created by this script are
            rather large (typically 2-5 times the compressed
            sizes).

      "image2py"	(NEW) Convert a single image to a python module.  See
            comments in this script for details.

      "player"	If multiple images are given on the command line,
            they are interpreted as frames in a sequence.  The
            script assumes that they all have the same size.
            Also note that this script now can play FLI/FLC
            and GIF animations.

            This player can also execute embedded Python
            animation applets (ARG format only).

      "viewer"	Transparent images ("P" with transparency property,
            and "RGBA") are superimposed on the standard Tk back-
            ground.

    + Fixed colour argument to "new".  For multilayer images, pass a
      tuple: (Red, Green, Blue), (Red, Green, Blue, Alpha), or (Cyan,
      Magenta, Yellow, Black).

    + Added XPM (X pixmap) read support.

    (0.2b3 released)

    + Added MNG (multi-image network graphics) read support.  "Ming"
      is a proposed animation standard, based on the PNG file format.

      You can use the "player" sample script to display some flavours
      of this format.  The MNG standard is still under development,
      as is this driver.  More information, including sample files,
      can be found at <ftp://swrinde.nde.swri.edu/pub/mng>

    + Added a "verify" method to images loaded from file.  This method
      scans the file for errors, without actually decoding the image
      data, and raises a suitable exception if it finds any problems.
      Currently implemented for PNG and MNG files only.

    + Added support for interlaced GIF images.

    + Added PNG read support -- if linked with the ZLIB compression library,
      PIL reads all kinds of PNG images, except interlaced files.

    + Improved PNG identification support -- doesn't mess up on unknown
      chunks, identifies all possible PNG modes, and verifies checksum
      on PNG header chunks.

    + Added an experimental reader for placable Windows Meta Files (WMF).
      This reader is still very incomplete, but it illustrates how PIL's
      drawing capabilities can be used to render vector and metafile
      formats.

    + Added restricted drivers for images from Image Tools (greyscale
      only) and LabEye/IFUNC (common interchange modes only).

    + Some minor improvements to the sample scripts provided in the
      "Scripts" directory.

    + The test images have been moved to the "Images" directory.

    (0.2b2 released)
    (0.2b1 released; Windows only)

    + Fixed filling of complex polygons.  The ImageDraw "line" and
      "polygon" methods also accept Path objects.

    + The ImageTk "PhotoImage" object can now be constructed directly
      from an image.  You can also pass the object itself to Tkinter,
      instead of using the "image" attribute.  Finally, using "paste"
      on a displayed image automatically updates the display.

    + The ImageTk "BitmapImage" object allows you to create transparent
      overlays from 1-bit images.  You can pass the object itself to
      Tkinter.  The constructor takes the same arguments as the Tkinter
      BitmapImage class; use the "foreground" option to set the colour
      of the overlay.

    + Added a "putdata" method to the Image class.  This can be used to
      load a 1-layer image with data from a sequence object or a string.
      An optional floating point scale and offset can be used to adjust
      the data to fit into the 8-bit pixel range.  Also see the "getdata"
      method.

    + Added the EXTENT method to the Image "transform" method.  This can
      be used to quickly crop, stretch, shrink, or mirror a subregion
      from another image.

    + Adapted to Python 1.4.

    + Added a project makefile for Visual C++ 4.x.  This allows you to
      easily build a dynamically linked version of PIL for Windows 95
      and NT.

    + A Tk "booster" patch for Windows is available.  It gives dramatic
      performance improvements for some displays.  Has been tested with
      Tk 4.2 only, but is likely to work with Tk 4.1 as well.  See the Tk
      subdirectory for details.

    + You can now save 1-bit images in the XBM format.  In addition, the
      Image class now provides a "tobitmap" method which returns a string
      containing an XBM representation of the image.  Quite handy to use
      with Tk.

    + More conversions, including "RGB" to "1" and more.

    (0.2a1 released)

    + Where earlier versions accepted lists, this version accepts arbitrary
      Python sequences (including strings, in some cases).  A few resource
      leaks were plugged in the process.

    + The Image "paste" method now allows the box to extend outside
      the target image.  The size of the box, the image to be pasted,
      and the optional mask must still match.

    + The ImageDraw module now supports filled polygons, outlined and
      filled ellipses, and text.  Font support is rudimentary, though.

    + The Image "point" method now takes an optional mode argument,
      allowing you to convert the image while translating it.  Currently,
      this can only be used to convert "L" or "P" images to "1" images
      (creating thresholded images or "matte" masks).

    + An Image "getpixel" method has been added.  For single band images,
      it returns the pixel value at a given position as an integer.
      For n-band images, it returns an n-tuple of integers.

    + An Image "getdata" method has been added.  It returns a sequence
      object representing the image as a 1-dimensional array.  Only len()
      and [] can be used with this sequence.  This method returns a
      reference to the existing image data, so changes in the image
      will be immediately reflected in the sequence object.

    + Fixed alignment problems in the Windows BMP writer.

    + If converting an "RGB" image to "RGB" or "L", you can give a second
      argument containing a colour conversion matrix.

    + An Image "getbbox" method has been added.  It returns the bounding
      box of data in an image, considering the value 0 as background.

    + An Image "offset" method has been added.  It returns a new image
      where the contents of the image have been offset the given distance
      in X and/or Y direction.  Data wraps between edges.

    + Saves PDF images.  The driver creates a binary PDF 1.1 files, using
      JPEG compression for "L", "RGB", and "CMYK" images, and hex encoding
      (same as for PostScript) for other formats.

    + The "paste" method now accepts "1" masks.  Zero means transparent,
      any other pixel value means opaque.  This is faster than using an
      "L" transparency mask.

    + Properly writes EPS files (and properly prints images to postscript
      printers as well).

    + Reads 4-bit BMP files, as well as 4 and 8-bit Windows ICO and CUR
      files.  Cursor animations are not supported.

    + Fixed alignment problems in the Sun raster loader.

    + Added "draft" and "thumbnail" methods.  The draft method is used
      to optimize loading of JPEG and PCD files, the thumbnail method is
      used to create a thumbnail representation of an image.

    + Added Windows display support, via the ImageWin class (see the
      handbook for details).

    + Added raster conversion for EPS files.  This requires GNU or Aladdin
      Ghostscript, and probably works on UNIX only.

    + Reads PhotoCD (PCD) images.  The base resolution (768x512) can be
      read from a PhotoCD file.

    + Eliminated some compiler warnings.  Bindings now compile cleanly in C++
      mode.  Note that the Imaging library itself must be compiled in C mode.

    + Added "bdf2pil.py", which converts BDF fonts into images with associated
      metrics.  This is definitely work in progress.  For info, see description
      in script for details.

    + Fixed a bug in the "ImageEnhance.py" module.

    + Fixed a bug in the netpbm save hack in "GifImagePlugin.py"

    + Fixed 90 and 270 degree rotation of rectangular images.

    + Properly reads 8-bit TIFF palette-color images.

    + Reads plane separated RGB and CMYK TIFF images.

    + Added driver debug mode.  This is enabled by setting Image.DEBUG
      to a non-zero value.  Try the -D option to "pilfile.py" and see what
      happens.

    + Don't crash on "atend" constructs in PostScript files.

    + Only the Image module imports _imaging directly.  Other modules
      should refer to the binding module as "Image.core".

    *** Changes from release 0.0 to 0.1 (b1) ***

    + A handbook is available (distributed separately).

    + The coordinate system is changed so that (0,0) is now located
      in the upper left corner.  This is in compliancy with ISO 12087
      and 90% of all other image processing and graphics libraries.

    + Modes "1" (bilevel) and "P" (palette) have been introduced.  Note
      that bilevel images are stored with one byte per pixel.

    + The Image "crop" and "paste" methods now accepts None as the
      box argument, to refer to the full image (self, that is).

    + The Image "crop" method now works properly.

    + The Image "point" method is now available.  You can use either a
      lookup table or a function taking one argument.

    + The Image join function has been renamed to "merge".

    + An Image "composite" function has been added.  It is identical
      to copy() followed by paste(mask).

    + An Image "eval" function has been added.  It is currently identical
      to point(function); that is, only a single image can be processed.

    + A set of channel operations has been added.  See the "ImageChops"
      module, test_chops.py, and the handbook for details.

    + Added the "pilconvert" utility, which converts image files.  Note
      that the number of output formats are still quite restricted.

    + Added the "pilfile" utility, which quickly identifies image files
      (without loading them, in most cases).

    + Added the "pilprint" utility, which prints image files to Postscript
      printers.

    + Added a rudimentary version of the "pilview" utility, which is
      simple image viewer based on Tk.  Only File/Exit and Image/Next
      works properly.

    + An interface to Tk has been added.  See "Lib/ImageTk.py" and README
      for details.

    + An interface to Jack Jansen's Img library has been added (thanks to
      Jack).  This allows you to read images through the Img extensions file
      format handlers.  See the file "Lib/ImgExtImagePlugin.py" for details.

    + Postscript printing is provided through the PSDraw module.  See the
      handbook for details.
