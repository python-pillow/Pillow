#!/usr/bin/env python
"""PILdriver, an image-processing calculator using PIL.

An instance of class PILDriver is essentially a software stack machine
(Polish-notation interpreter) for sequencing PIL image
transformations.  The state of the instance is the interpreter stack.

The only method one will normally invoke after initialization is the
`execute' method.  This takes an argument list of tokens, pushes them
onto the instance's stack, and then tries to clear the stack by
successive evaluation of PILdriver operators.  Any part of the stack
not cleaned off persists and is part of the evaluation context for
the next call of the execute method.

PILDriver doesn't catch any exceptions, on the theory that these
are actually diagnostic information that should be interpreted by
the calling code.

When called as a script, the command-line arguments are passed to
a PILDriver instance.  If there are no command-line arguments, the
module runs an interactive interpreter, each line of which is split into
space-separated tokens and passed to the execute method.

In the method descriptions below, a first line beginning with the string
`usage:' means this method can be invoked with the token that follows
it.  Following <>-enclosed arguments describe how the method interprets
the entries on the stack.  Each argument specification begins with a
type specification: either `int', `float', `string', or `image'.

All operations consume their arguments off the stack (use `dup' to
keep copies around).  Use `verbose 1' to see the stack state displayed
before each operation.

Usage examples:

    `show crop 0 0 200 300 open test.png' loads test.png, crops out a portion
of its upper-left-hand corner and displays the cropped portion.

    `save rotated.png rotate 30 open test.tiff' loads test.tiff, rotates it
30 degrees, and saves the result as rotated.png (in PNG format).
"""
# by Eric S. Raymond <esr@thyrsus.com>
# $Id$

# TO DO:
# 1. Add PILFont capabilities, once that's documented.
# 2. Add PILDraw operations.
# 3. Add support for composing and decomposing multiple-image files.
#

from __future__ import print_function

from PIL import Image

class PILDriver:

    verbose = 0

    def do_verbose(self):
        """usage: verbose <int:num>

        Set verbosity flag from top of stack.
        """
        self.verbose = int(self.do_pop())

    # The evaluation stack (internal only)

    stack = []          # Stack of pending operations

    def push(self, item):
        "Push an argument onto the evaluation stack."
        self.stack = [item] + self.stack

    def top(self):
        "Return the top-of-stack element."
        return self.stack[0]

    # Stack manipulation (callable)

    def do_clear(self):
        """usage: clear

        Clear the stack.
        """
        self.stack = []

    def do_pop(self):
        """usage: pop

        Discard the top element on the stack.
        """
        top = self.stack[0]
        self.stack = self.stack[1:]
        return top

    def do_dup(self):
        """usage: dup

        Duplicate the top-of-stack item.
        """
        if hasattr(self, 'format'):     # If it's an image, do a real copy
            dup = self.stack[0].copy()
        else:
            dup = self.stack[0]
        self.stack = [dup] + self.stack

    def do_swap(self):
        """usage: swap

        Swap the top-of-stack item with the next one down.
        """
        self.stack = [self.stack[1], self.stack[0]] + self.stack[2:]

    # Image module functions (callable)

    def do_new(self):
        """usage: new <int:xsize> <int:ysize> <int:color>:

        Create and push a greyscale image of given size and color.
        """
        xsize = int(self.do_pop())
        ysize = int(self.do_pop())
        color = int(self.do_pop())
        self.push(Image.new("L", (xsize, ysize), color))

    def do_open(self):
        """usage: open <string:filename>

        Open the indicated image, read it, push the image on the stack.
        """
        self.push(Image.open(self.do_pop()))

    def do_blend(self):
        """usage: blend <image:pic1> <image:pic2> <float:alpha>

        Replace two images and an alpha with the blended image.
        """
        image1 = self.do_pop()
        image2 = self.do_pop()
        alpha = float(self.do_pop())
        self.push(Image.blend(image1, image2, alpha))

    def do_composite(self):
        """usage: composite <image:pic1> <image:pic2> <image:mask>

        Replace two images and a mask with their composite.
        """
        image1 = self.do_pop()
        image2 = self.do_pop()
        mask = self.do_pop()
        self.push(Image.composite(image1, image2, mask))

    def do_merge(self):
        """usage: merge <string:mode> <image:pic1> [<image:pic2> [<image:pic3> [<image:pic4>]]]

        Merge top-of stack images in a way described by the mode.
        """
        mode = self.do_pop()
        bandlist = []
        for band in mode:
            bandlist.append(self.do_pop())
        self.push(Image.merge(mode, bandlist))

    # Image class methods

    def do_convert(self):
        """usage: convert <string:mode> <image:pic1>

        Convert the top image to the given mode.
        """
        mode = self.do_pop()
        image = self.do_pop()
        self.push(image.convert(mode))

    def do_copy(self):
        """usage: copy <image:pic1>

        Make and push a true copy of the top image.
        """
        self.dup()

    def do_crop(self):
        """usage: crop <int:left> <int:upper> <int:right> <int:lower> <image:pic1>

        Crop and push a rectangular region from the current image.
        """
        left = int(self.do_pop())
        upper = int(self.do_pop())
        right = int(self.do_pop())
        lower = int(self.do_pop())
        image = self.do_pop()
        self.push(image.crop((left, upper, right, lower)))

    def do_draft(self):
        """usage: draft <string:mode> <int:xsize> <int:ysize>

        Configure the loader for a given mode and size.
        """
        mode = self.do_pop()
        xsize = int(self.do_pop())
        ysize = int(self.do_pop())
        self.push(self.draft(mode, (xsize, ysize)))

    def do_filter(self):
        """usage: filter <string:filtername> <image:pic1>

        Process the top image with the given filter.
        """
        from PIL import ImageFilter
        filter = eval("ImageFilter." + self.do_pop().upper())
        image = self.do_pop()
        self.push(image.filter(filter))

    def do_getbbox(self):
        """usage: getbbox

        Push left, upper, right, and lower pixel coordinates of the top image.
        """
        bounding_box = self.do_pop().getbbox()
        self.push(bounding_box[3])
        self.push(bounding_box[2])
        self.push(bounding_box[1])
        self.push(bounding_box[0])

    def do_getextrema(self):
        """usage: extrema

        Push minimum and maximum pixel values of the top image.
        """
        extrema = self.do_pop().extrema()
        self.push(extrema[1])
        self.push(extrema[0])

    def do_offset(self):
        """usage: offset <int:xoffset> <int:yoffset> <image:pic1>

        Offset the pixels in the top image.
        """
        xoff = int(self.do_pop())
        yoff = int(self.do_pop())
        image = self.do_pop()
        self.push(image.offset(xoff, yoff))

    def do_paste(self):
        """usage: paste <image:figure> <int:xoffset> <int:yoffset> <image:ground>

        Paste figure image into ground with upper left at given offsets.
        """
        figure = self.do_pop()
        xoff = int(self.do_pop())
        yoff = int(self.do_pop())
        ground = self.do_pop()
        if figure.mode == "RGBA":
            ground.paste(figure, (xoff, yoff), figure)
        else:
            ground.paste(figure, (xoff, yoff))
        self.push(ground)

    def do_resize(self):
        """usage: resize <int:xsize> <int:ysize> <image:pic1>

        Resize the top image.
        """
        ysize = int(self.do_pop())
        xsize = int(self.do_pop())
        image = self.do_pop()
        self.push(image.resize((xsize, ysize)))

    def do_rotate(self):
        """usage: rotate <int:angle> <image:pic1>

        Rotate image through a given angle
        """
        angle = int(self.do_pop())
        image = self.do_pop()
        self.push(image.rotate(angle))

    def do_save(self):
        """usage: save <string:filename> <image:pic1>

        Save image with default options.
        """
        filename = self.do_pop()
        image = self.do_pop()
        image.save(filename)

    def do_save2(self):
        """usage: save2 <string:filename> <string:options> <image:pic1>

        Save image with specified options.
        """
        filename = self.do_pop()
        options = self.do_pop()
        image = self.do_pop()
        image.save(filename, None, options)

    def do_show(self):
        """usage: show <image:pic1>

        Display and pop the top image.
        """
        self.do_pop().show()

    def do_thumbnail(self):
        """usage: thumbnail <int:xsize> <int:ysize> <image:pic1>

        Modify the top image in the stack to contain a thumbnail of itself.
        """
        ysize = int(self.do_pop())
        xsize = int(self.do_pop())
        self.top().thumbnail((xsize, ysize))

    def do_transpose(self):
        """usage: transpose <string:operator> <image:pic1>

        Transpose the top image.
        """
        transpose = self.do_pop().upper()
        image = self.do_pop()
        self.push(image.transpose(transpose))

    # Image attributes

    def do_format(self):
        """usage: format <image:pic1>

        Push the format of the top image onto the stack.
        """
        self.push(self.do_pop().format)

    def do_mode(self):
        """usage: mode <image:pic1>

        Push the mode of the top image onto the stack.
        """
        self.push(self.do_pop().mode)

    def do_size(self):
        """usage: size <image:pic1>

        Push the image size on the stack as (y, x).
        """
        size = self.do_pop().size
        self.push(size[0])
        self.push(size[1])

    # ImageChops operations

    def do_invert(self):
        """usage: invert <image:pic1>

        Invert the top image.
        """
        from PIL import ImageChops
        self.push(ImageChops.invert(self.do_pop()))

    def do_lighter(self):
        """usage: lighter <image:pic1> <image:pic2>

        Pop the two top images, push an image of the lighter pixels of both.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.lighter(image1, image2))

    def do_darker(self):
        """usage: darker <image:pic1> <image:pic2>

        Pop the two top images, push an image of the darker pixels of both.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.darker(image1, image2))

    def do_difference(self):
        """usage: difference <image:pic1> <image:pic2>

        Pop the two top images, push the difference image
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.difference(image1, image2))

    def do_multiply(self):
        """usage: multiply <image:pic1> <image:pic2>

        Pop the two top images, push the multiplication image.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        self.push(ImageChops.multiply(image1, image2))

    def do_screen(self):
        """usage: screen <image:pic1> <image:pic2>

        Pop the two top images, superimpose their inverted versions.
        """
        from PIL import ImageChops
        image2 = self.do_pop()
        image1 = self.do_pop()
        self.push(ImageChops.screen(image1, image2))

    def do_add(self):
        """usage: add <image:pic1> <image:pic2> <int:offset> <float:scale>

        Pop the two top images, produce the scaled sum with offset.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        scale = float(self.do_pop())
        offset = int(self.do_pop())
        self.push(ImageChops.add(image1, image2, scale, offset))

    def do_subtract(self):
        """usage: subtract <image:pic1> <image:pic2> <int:offset> <float:scale>

        Pop the two top images, produce the scaled difference with offset.
        """
        from PIL import ImageChops
        image1 = self.do_pop()
        image2 = self.do_pop()
        scale = float(self.do_pop())
        offset = int(self.do_pop())
        self.push(ImageChops.subtract(image1, image2, scale, offset))

    # ImageEnhance classes

    def do_color(self):
        """usage: color <image:pic1>

        Enhance color in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Color(image)
        self.push(enhancer.enhance(factor))

    def do_contrast(self):
        """usage: contrast <image:pic1>

        Enhance contrast in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Contrast(image)
        self.push(enhancer.enhance(factor))

    def do_brightness(self):
        """usage: brightness <image:pic1>

        Enhance brightness in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Brightness(image)
        self.push(enhancer.enhance(factor))

    def do_sharpness(self):
        """usage: sharpness <image:pic1>

        Enhance sharpness in the top image.
        """
        from PIL import ImageEnhance
        factor = float(self.do_pop())
        image = self.do_pop()
        enhancer = ImageEnhance.Sharpness(image)
        self.push(enhancer.enhance(factor))

    # The interpreter loop

    def execute(self, list):
        "Interpret a list of PILDriver commands."
        list.reverse()
        while len(list) > 0:
            self.push(list[0])
            list = list[1:]
            if self.verbose:
                print("Stack: " + repr(self.stack))
            top = self.top()
            if not isinstance(top, str):
                continue;
            funcname = "do_" + top
            if not hasattr(self, funcname):
                continue
            else:
                self.do_pop()
                func = getattr(self, funcname)
                func()

if __name__ == '__main__':
    import sys
    try:
        import readline
    except ImportError:
        pass # not available on all platforms

    # If we see command-line arguments, interpret them as a stack state
    # and execute.  Otherwise go interactive.

    driver = PILDriver()
    if len(sys.argv[1:]) > 0:
        driver.execute(sys.argv[1:])
    else:
        print("PILDriver says hello.")
        while True:
            try:
                if sys.version_info[0] >= 3:
                    line = input('pildriver> ');
                else:
                    line = raw_input('pildriver> ');
            except EOFError:
                print("\nPILDriver says goodbye.")
                break
            driver.execute(line.split())
            print(driver.stack)

# The following sets edit modes for GNU EMACS
# Local Variables:
# mode:python
# End:
