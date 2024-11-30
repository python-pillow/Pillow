.. py:module:: PIL.ImageGrab
.. py:currentmodule:: PIL.ImageGrab

:py:mod:`~PIL.ImageGrab` Module
===============================

The :py:mod:`~PIL.ImageGrab` module can be used to copy the contents of the screen
or the clipboard to a PIL image memory.

.. versionadded:: 1.1.3

.. py:function:: grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay=None)

    Take a snapshot of the screen. The pixels inside the bounding box are returned as
    an "RGBA" on macOS, or an "RGB" image otherwise. If the bounding box is omitted,
    the entire screen is copied, and on macOS, it will be at 2x if on a Retina screen.

    On Linux, if ``xdisplay`` is ``None`` and the default X11 display does not return
    a snapshot of the screen, ``gnome-screenshot`` will be used as fallback if it is
    installed. To disable this behaviour, pass ``xdisplay=""`` instead.

    .. versionadded:: 1.1.3 (Windows), 3.0.0 (macOS), 7.1.0 (Linux)

    :param bbox: What region to copy. Default is the entire screen.
                 On macOS, this is not increased to 2x for Retina screens, so the full
                 width of a Retina screen would be 1440, not 2880.
                 On Windows, the top-left point may be negative if ``all_screens=True``
                 is used.
    :param include_layered_windows: Includes layered windows. Windows OS only.

        .. versionadded:: 6.1.0
    :param all_screens: Capture all monitors. Windows OS only.

        .. versionadded:: 6.2.0

    :param xdisplay:
        X11 Display address. Pass :data:`None` to grab the default system screen. Pass ``""`` to grab the default X11 screen on Windows or macOS.

        You can check X11 support using :py:func:`PIL.features.check_feature` with ``feature="xcb"``.

        .. versionadded:: 7.1.0
    :return: An image

.. py:function:: grabclipboard()

    Take a snapshot of the clipboard image, if any.

    On Linux, ``wl-paste`` or ``xclip`` is required.

    .. versionadded:: 1.1.4 (Windows), 3.3.0 (macOS), 9.4.0 (Linux)

    :return: On Windows, an image, a list of filenames,
             or None if the clipboard does not contain image data or filenames.
             Note that if a list is returned, the filenames may not represent image files.

             On Mac, an image,
             or None if the clipboard does not contain image data.

             On Linux, an image.
