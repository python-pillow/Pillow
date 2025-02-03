#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "avif/avif.h"

// Encoder type
typedef struct {
    PyObject_HEAD avifEncoder *encoder;
    avifImage *image;
    int frame_index;
} AvifEncoderObject;

static PyTypeObject AvifEncoder_Type;

// Decoder type
typedef struct {
    PyObject_HEAD avifDecoder *decoder;
    Py_buffer buffer;
    char *mode;
} AvifDecoderObject;

static PyTypeObject AvifDecoder_Type;

#if AVIF_VERSION < 1000000
static int
normalize_quantize_value(int qvalue) {
    if (qvalue < AVIF_QUANTIZER_BEST_QUALITY) {
        return AVIF_QUANTIZER_BEST_QUALITY;
    } else if (qvalue > AVIF_QUANTIZER_WORST_QUALITY) {
        return AVIF_QUANTIZER_WORST_QUALITY;
    } else {
        return qvalue;
    }
}
#endif

static int
normalize_tiles_log2(int value) {
    if (value < 0) {
        return 0;
    } else if (value > 6) {
        return 6;
    } else {
        return value;
    }
}

static PyObject *
exc_type_for_avif_result(avifResult result) {
    switch (result) {
        case AVIF_RESULT_INVALID_EXIF_PAYLOAD:
        case AVIF_RESULT_INVALID_CODEC_SPECIFIC_OPTION:
            return PyExc_ValueError;
        case AVIF_RESULT_INVALID_FTYP:
        case AVIF_RESULT_BMFF_PARSE_FAILED:
        case AVIF_RESULT_TRUNCATED_DATA:
        case AVIF_RESULT_NO_CONTENT:
            return PyExc_SyntaxError;
        default:
            return PyExc_RuntimeError;
    }
}

static uint8_t
irot_imir_to_exif_orientation(const avifImage *image) {
    uint8_t axis;
#if AVIF_VERSION_MAJOR >= 1
    axis = image->imir.axis;
#else
    axis = image->imir.mode;
#endif
    int imir = image->transformFlags & AVIF_TRANSFORM_IMIR;
    int irot = image->transformFlags & AVIF_TRANSFORM_IROT;
    if (irot) {
        uint8_t angle = image->irot.angle;
        if (angle == 1) {
            if (imir) {
                return axis ? 7   // 90 degrees anti-clockwise then swap left and right.
                            : 5;  // 90 degrees anti-clockwise then swap top and bottom.
            }
            return 6;  // 90 degrees anti-clockwise.
        }
        if (angle == 2) {
            if (imir) {
                return axis
                           ? 4   // 180 degrees anti-clockwise then swap left and right.
                           : 2;  // 180 degrees anti-clockwise then swap top and bottom.
            }
            return 3;  // 180 degrees anti-clockwise.
        }
        if (angle == 3) {
            if (imir) {
                return axis
                           ? 5   // 270 degrees anti-clockwise then swap left and right.
                           : 7;  // 270 degrees anti-clockwise then swap top and bottom.
            }
            return 8;  // 270 degrees anti-clockwise.
        }
    }
    if (imir) {
        return axis ? 2   // Swap left and right.
                    : 4;  // Swap top and bottom.
    }
    return 1;  // Default orientation ("top-left", no-op).
}

static void
exif_orientation_to_irot_imir(avifImage *image, int orientation) {
    // Mapping from Exif orientation as defined in JEITA CP-3451C section 4.6.4.A
    // Orientation to irot and imir boxes as defined in HEIF ISO/IEC 28002-12:2021
    // sections 6.5.10 and 6.5.12.
    switch (orientation) {
        case 2:  // The 0th row is at the visual top of the image, and the 0th column is
                 // the visual right-hand side.
            image->transformFlags |= AVIF_TRANSFORM_IMIR;
#if AVIF_VERSION_MAJOR >= 1
            image->imir.axis = 1;
#else
            image->imir.mode = 1;
#endif
            break;
        case 3:  // The 0th row is at the visual bottom of the image, and the 0th column
                 // is the visual right-hand side.
            image->transformFlags |= AVIF_TRANSFORM_IROT;
            image->irot.angle = 2;
            break;
        case 4:  // The 0th row is at the visual bottom of the image, and the 0th column
                 // is the visual left-hand side.
            image->transformFlags |= AVIF_TRANSFORM_IMIR;
            break;
        case 5:  // The 0th row is the visual left-hand side of the image, and the 0th
                 // column is the visual top.
            image->transformFlags |= AVIF_TRANSFORM_IROT | AVIF_TRANSFORM_IMIR;
            image->irot.angle = 1;  // applied before imir according to MIAF spec
                                    // ISO/IEC 28002-12:2021 - section 7.3.6.7
            break;
        case 6:  // The 0th row is the visual right-hand side of the image, and the 0th
                 // column is the visual top.
            image->transformFlags |= AVIF_TRANSFORM_IROT;
            image->irot.angle = 3;
            break;
        case 7:  // The 0th row is the visual right-hand side of the image, and the 0th
                 // column is the visual bottom.
            image->transformFlags |= AVIF_TRANSFORM_IROT | AVIF_TRANSFORM_IMIR;
            image->irot.angle = 3;  // applied before imir according to MIAF spec
                                    // ISO/IEC 28002-12:2021 - section 7.3.6.7
            break;
        case 8:  // The 0th row is the visual left-hand side of the image, and the 0th
                 // column is the visual bottom.
            image->transformFlags |= AVIF_TRANSFORM_IROT;
            image->irot.angle = 1;
            break;
    }
}

static int
_codec_available(const char *name, uint32_t flags) {
    avifCodecChoice codec = avifCodecChoiceFromName(name);
    if (codec == AVIF_CODEC_CHOICE_AUTO) {
        return 0;
    }
    const char *codec_name = avifCodecName(codec, flags);
    return (codec_name == NULL) ? 0 : 1;
}

PyObject *
_decoder_codec_available(PyObject *self, PyObject *args) {
    char *codec_name;
    if (!PyArg_ParseTuple(args, "s", &codec_name)) {
        return NULL;
    }
    int is_available = _codec_available(codec_name, AVIF_CODEC_FLAG_CAN_DECODE);
    return PyBool_FromLong(is_available);
}

PyObject *
_encoder_codec_available(PyObject *self, PyObject *args) {
    char *codec_name;
    if (!PyArg_ParseTuple(args, "s", &codec_name)) {
        return NULL;
    }
    int is_available = _codec_available(codec_name, AVIF_CODEC_FLAG_CAN_ENCODE);
    return PyBool_FromLong(is_available);
}

static int
_add_codec_specific_options(avifEncoder *encoder, PyObject *opts) {
    Py_ssize_t i, size;
    PyObject *keyval, *py_key, *py_val;
    if (!PyTuple_Check(opts)) {
        PyErr_SetString(PyExc_ValueError, "Invalid advanced codec options");
        return 1;
    }
    size = PyTuple_GET_SIZE(opts);

    for (i = 0; i < size; i++) {
        keyval = PyTuple_GetItem(opts, i);
        if (!PyTuple_Check(keyval) || PyTuple_GET_SIZE(keyval) != 2) {
            PyErr_SetString(PyExc_ValueError, "Invalid advanced codec options");
            return 1;
        }
        py_key = PyTuple_GetItem(keyval, 0);
        py_val = PyTuple_GetItem(keyval, 1);
        if (!PyUnicode_Check(py_key) || !PyUnicode_Check(py_val)) {
            PyErr_SetString(PyExc_ValueError, "Invalid advanced codec options");
            return 1;
        }
        const char *key = PyUnicode_AsUTF8(py_key);
        const char *val = PyUnicode_AsUTF8(py_val);
        if (key == NULL || val == NULL) {
            PyErr_SetString(PyExc_ValueError, "Invalid advanced codec options");
            return 1;
        }

        avifResult result = avifEncoderSetCodecSpecificOption(encoder, key, val);
        if (result != AVIF_RESULT_OK) {
            PyErr_Format(
                exc_type_for_avif_result(result),
                "Setting advanced codec options failed: %s",
                avifResultToString(result)
            );
            return 1;
        }
    }
    return 0;
}

// Encoder functions
PyObject *
AvifEncoderNew(PyObject *self_, PyObject *args) {
    unsigned int width, height;
    AvifEncoderObject *self = NULL;
    avifEncoder *encoder;

    char *subsampling;
    int quality;
    int speed;
    int exif_orientation;
    int max_threads;
    Py_buffer icc_buffer;
    Py_buffer exif_buffer;
    Py_buffer xmp_buffer;
    PyObject *alpha_premultiplied;
    PyObject *autotiling;
    int tile_rows_log2;
    int tile_cols_log2;

    char *codec;
    char *range;

    PyObject *advanced;

    if (!PyArg_ParseTuple(
            args,
            "IIsiiissiiOOy*y*iy*O",
            &width,
            &height,
            &subsampling,
            &quality,
            &speed,
            &max_threads,
            &codec,
            &range,
            &tile_rows_log2,
            &tile_cols_log2,
            &alpha_premultiplied,
            &autotiling,
            &icc_buffer,
            &exif_buffer,
            &exif_orientation,
            &xmp_buffer,
            &advanced
        )) {
        return NULL;
    }

    // Create a new animation encoder and picture frame
    avifImage *image = avifImageCreateEmpty();

    // Set these in advance so any upcoming RGB -> YUV use the proper coefficients
    if (strcmp(range, "full") == 0) {
        image->yuvRange = AVIF_RANGE_FULL;
    } else if (strcmp(range, "limited") == 0) {
        image->yuvRange = AVIF_RANGE_LIMITED;
    } else {
        PyErr_SetString(PyExc_ValueError, "Invalid range");
        avifImageDestroy(image);
        return NULL;
    }
    if (strcmp(subsampling, "4:0:0") == 0) {
        image->yuvFormat = AVIF_PIXEL_FORMAT_YUV400;
    } else if (strcmp(subsampling, "4:2:0") == 0) {
        image->yuvFormat = AVIF_PIXEL_FORMAT_YUV420;
    } else if (strcmp(subsampling, "4:2:2") == 0) {
        image->yuvFormat = AVIF_PIXEL_FORMAT_YUV422;
    } else if (strcmp(subsampling, "4:4:4") == 0) {
        image->yuvFormat = AVIF_PIXEL_FORMAT_YUV444;
    } else {
        PyErr_Format(PyExc_ValueError, "Invalid subsampling: %s", subsampling);
        avifImageDestroy(image);
        return NULL;
    }

    // Validate canvas dimensions
    if (width <= 0 || height <= 0) {
        PyErr_SetString(PyExc_ValueError, "invalid canvas dimensions");
        avifImageDestroy(image);
        return NULL;
    }
    image->width = width;
    image->height = height;

    image->depth = 8;
#if AVIF_VERSION >= 90000
    image->alphaPremultiplied = alpha_premultiplied == Py_True ? AVIF_TRUE : AVIF_FALSE;
#endif

    encoder = avifEncoderCreate();

    int is_aom_encode = strcmp(codec, "aom") == 0 ||
                        (strcmp(codec, "auto") == 0 &&
                         _codec_available("aom", AVIF_CODEC_FLAG_CAN_ENCODE));
    encoder->maxThreads = is_aom_encode && max_threads > 64 ? 64 : max_threads;

#if AVIF_VERSION >= 1000000
    encoder->quality = quality;
#else
    encoder->minQuantizer = normalize_quantize_value(64 - quality);
    encoder->maxQuantizer = normalize_quantize_value(100 - quality);
#endif

    if (strcmp(codec, "auto") == 0) {
        encoder->codecChoice = AVIF_CODEC_CHOICE_AUTO;
    } else {
        encoder->codecChoice = avifCodecChoiceFromName(codec);
    }
    if (speed < AVIF_SPEED_SLOWEST) {
        speed = AVIF_SPEED_SLOWEST;
    } else if (speed > AVIF_SPEED_FASTEST) {
        speed = AVIF_SPEED_FASTEST;
    }
    encoder->speed = speed;
    encoder->timescale = (uint64_t)1000;
    encoder->tileRowsLog2 = normalize_tiles_log2(tile_rows_log2);
    encoder->tileColsLog2 = normalize_tiles_log2(tile_cols_log2);

#if AVIF_VERSION >= 110000
    encoder->autoTiling = autotiling == Py_True ? AVIF_TRUE : AVIF_FALSE;
#endif

    if (advanced != Py_None) {
#if AVIF_VERSION >= 80200
        if (_add_codec_specific_options(encoder, advanced)) {
            avifImageDestroy(image);
            avifEncoderDestroy(encoder);
            return NULL;
        }
#else
        PyErr_SetString(
            PyExc_ValueError, "Advanced codec options require libavif >= 0.8.2"
        );
        avifImageDestroy(image);
        avifEncoderDestroy(encoder);
        return NULL;
#endif
    }

    self = PyObject_New(AvifEncoderObject, &AvifEncoder_Type);
    if (!self) {
        PyErr_SetString(PyExc_RuntimeError, "could not create encoder object");
        avifImageDestroy(image);
        avifEncoderDestroy(encoder);
        return NULL;
    }
    self->frame_index = -1;

    avifResult result;
    if (icc_buffer.len) {
        result = avifImageSetProfileICC(image, icc_buffer.buf, icc_buffer.len);
        if (result != AVIF_RESULT_OK) {
            PyErr_Format(
                exc_type_for_avif_result(result),
                "Setting ICC profile failed: %s",
                avifResultToString(result)
            );
            avifImageDestroy(image);
            avifEncoderDestroy(encoder);
            PyBuffer_Release(&icc_buffer);
            PyBuffer_Release(&exif_buffer);
            PyBuffer_Release(&xmp_buffer);
            PyObject_Del(self);
            return NULL;
        }
        // colorPrimaries and transferCharacteristics are ignored when an ICC
        // profile is present, so set them to UNSPECIFIED.
        image->colorPrimaries = AVIF_COLOR_PRIMARIES_UNSPECIFIED;
        image->transferCharacteristics = AVIF_TRANSFER_CHARACTERISTICS_UNSPECIFIED;
    } else {
        image->colorPrimaries = AVIF_COLOR_PRIMARIES_BT709;
        image->transferCharacteristics = AVIF_TRANSFER_CHARACTERISTICS_SRGB;
    }
    image->matrixCoefficients = AVIF_MATRIX_COEFFICIENTS_BT601;
    PyBuffer_Release(&icc_buffer);

    if (exif_buffer.len) {
        result = avifImageSetMetadataExif(image, exif_buffer.buf, exif_buffer.len);
        if (result != AVIF_RESULT_OK) {
            PyErr_Format(
                exc_type_for_avif_result(result),
                "Setting EXIF data failed: %s",
                avifResultToString(result)
            );
            avifImageDestroy(image);
            avifEncoderDestroy(encoder);
            PyBuffer_Release(&exif_buffer);
            PyBuffer_Release(&xmp_buffer);
            PyObject_Del(self);
            return NULL;
        }
    }
    PyBuffer_Release(&exif_buffer);

    if (xmp_buffer.len) {
        result = avifImageSetMetadataXMP(image, xmp_buffer.buf, xmp_buffer.len);
        if (result != AVIF_RESULT_OK) {
            PyErr_Format(
                exc_type_for_avif_result(result),
                "Setting XMP data failed: %s",
                avifResultToString(result)
            );
            avifImageDestroy(image);
            avifEncoderDestroy(encoder);
            PyBuffer_Release(&xmp_buffer);
            PyObject_Del(self);
            return NULL;
        }
    }
    PyBuffer_Release(&xmp_buffer);

    if (exif_orientation > 1) {
        exif_orientation_to_irot_imir(image, exif_orientation);
    }

    self->image = image;
    self->encoder = encoder;

    return (PyObject *)self;
}

PyObject *
_encoder_dealloc(AvifEncoderObject *self) {
    if (self->encoder) {
        avifEncoderDestroy(self->encoder);
    }
    if (self->image) {
        avifImageDestroy(self->image);
    }
    Py_RETURN_NONE;
}

PyObject *
_encoder_add(AvifEncoderObject *self, PyObject *args) {
    uint8_t *rgb_bytes;
    Py_ssize_t size;
    unsigned int duration;
    unsigned int width;
    unsigned int height;
    char *mode;
    PyObject *is_single_frame = NULL;
    PyObject *ret = Py_None;

    int is_first_frame;
    avifRGBImage rgb;
    avifResult result;

    avifEncoder *encoder = self->encoder;
    avifImage *image = self->image;
    avifImage *frame = NULL;

    if (!PyArg_ParseTuple(
            args,
            "z#IIIsO",
            (char **)&rgb_bytes,
            &size,
            &duration,
            &width,
            &height,
            &mode,
            &is_single_frame
        )) {
        return NULL;
    }

    is_first_frame = self->frame_index == -1;

    if (image->width != width || image->height != height) {
        PyErr_Format(
            PyExc_ValueError,
            "Image sequence dimensions mismatch, %ux%u != %ux%u",
            image->width,
            image->height,
            width,
            height
        );
        return NULL;
    }

    if (is_first_frame) {
        // If we don't have an image populated with yuv planes, this is the first frame
        frame = image;
    } else {
        frame = avifImageCreateEmpty();

        frame->colorPrimaries = image->colorPrimaries;
        frame->transferCharacteristics = image->transferCharacteristics;
        frame->matrixCoefficients = image->matrixCoefficients;
        frame->yuvRange = image->yuvRange;
        frame->yuvFormat = image->yuvFormat;
        frame->depth = image->depth;
#if AVIF_VERSION >= 90000
        frame->alphaPremultiplied = image->alphaPremultiplied;
#endif
    }

    frame->width = width;
    frame->height = height;

    memset(&rgb, 0, sizeof(avifRGBImage));

    avifRGBImageSetDefaults(&rgb, frame);
    rgb.depth = 8;

    if (strcmp(mode, "RGBA") == 0) {
        rgb.format = AVIF_RGB_FORMAT_RGBA;
    } else {
        rgb.format = AVIF_RGB_FORMAT_RGB;
    }

    result = avifRGBImageAllocatePixels(&rgb);
    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Pixel allocation failed: %s",
            avifResultToString(result)
        );
        return NULL;
    }

    if (rgb.rowBytes * rgb.height != size) {
        PyErr_Format(
            PyExc_RuntimeError,
            "rgb data is incorrect size: %u * %u (%u) != %u",
            rgb.rowBytes,
            rgb.height,
            rgb.rowBytes * rgb.height,
            size
        );
        ret = NULL;
        goto end;
    }

    // rgb.pixels is safe for writes
    memcpy(rgb.pixels, rgb_bytes, size);

    Py_BEGIN_ALLOW_THREADS;
    result = avifImageRGBToYUV(frame, &rgb);
    Py_END_ALLOW_THREADS;

    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Conversion to YUV failed: %s",
            avifResultToString(result)
        );
        ret = NULL;
        goto end;
    }

    uint32_t addImageFlags = AVIF_ADD_IMAGE_FLAG_NONE;
    if (PyObject_IsTrue(is_single_frame)) {
        addImageFlags |= AVIF_ADD_IMAGE_FLAG_SINGLE;
    }

    Py_BEGIN_ALLOW_THREADS;
    result = avifEncoderAddImage(encoder, frame, duration, addImageFlags);
    Py_END_ALLOW_THREADS;

    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Failed to encode image: %s",
            avifResultToString(result)
        );
        ret = NULL;
        goto end;
    }

end:
    avifRGBImageFreePixels(&rgb);
    if (!is_first_frame) {
        avifImageDestroy(frame);
    }

    if (ret == Py_None) {
        self->frame_index++;
        Py_RETURN_NONE;
    } else {
        return ret;
    }
}

PyObject *
_encoder_finish(AvifEncoderObject *self) {
    avifEncoder *encoder = self->encoder;

    avifRWData raw = AVIF_DATA_EMPTY;
    avifResult result;
    PyObject *ret = NULL;

    Py_BEGIN_ALLOW_THREADS;
    result = avifEncoderFinish(encoder, &raw);
    Py_END_ALLOW_THREADS;

    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Failed to finish encoding: %s",
            avifResultToString(result)
        );
        avifRWDataFree(&raw);
        return NULL;
    }

    ret = PyBytes_FromStringAndSize((char *)raw.data, raw.size);

    avifRWDataFree(&raw);

    return ret;
}

// Decoder functions
PyObject *
AvifDecoderNew(PyObject *self_, PyObject *args) {
    Py_buffer buffer;
    AvifDecoderObject *self = NULL;
    avifDecoder *decoder;

    char *codec_str;
    avifCodecChoice codec;
    int max_threads;

    avifResult result;

    if (!PyArg_ParseTuple(args, "y*si", &buffer, &codec_str, &max_threads)) {
        return NULL;
    }

    if (strcmp(codec_str, "auto") == 0) {
        codec = AVIF_CODEC_CHOICE_AUTO;
    } else {
        codec = avifCodecChoiceFromName(codec_str);
    }

    self = PyObject_New(AvifDecoderObject, &AvifDecoder_Type);
    if (!self) {
        PyErr_SetString(PyExc_RuntimeError, "could not create decoder object");
        PyBuffer_Release(&buffer);
        return NULL;
    }

    decoder = avifDecoderCreate();
#if AVIF_VERSION >= 80400
    decoder->maxThreads = max_threads;
#endif
#if AVIF_VERSION >= 90200
    // Turn off libavif's 'clap' (clean aperture) property validation.
    decoder->strictFlags &= ~AVIF_STRICT_CLAP_VALID;
    // Allow the PixelInformationProperty ('pixi') to be missing in AV1 image
    // items. libheif v1.11.0 and older does not add the 'pixi' item property to
    // AV1 image items.
    decoder->strictFlags &= ~AVIF_STRICT_PIXI_REQUIRED;
#endif
    decoder->codecChoice = codec;

    result = avifDecoderSetIOMemory(decoder, buffer.buf, buffer.len);
    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Setting IO memory failed: %s",
            avifResultToString(result)
        );
        avifDecoderDestroy(decoder);
        PyBuffer_Release(&buffer);
        PyObject_Del(self);
        return NULL;
    }

    result = avifDecoderParse(decoder);
    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Failed to decode image: %s",
            avifResultToString(result)
        );
        avifDecoderDestroy(decoder);
        PyBuffer_Release(&buffer);
        PyObject_Del(self);
        return NULL;
    }

    if (decoder->alphaPresent) {
        self->mode = "RGBA";
    } else {
        self->mode = "RGB";
    }

    self->decoder = decoder;
    self->buffer = buffer;

    return (PyObject *)self;
}

PyObject *
_decoder_dealloc(AvifDecoderObject *self) {
    if (self->decoder) {
        avifDecoderDestroy(self->decoder);
    }
    PyBuffer_Release(&self->buffer);
    Py_RETURN_NONE;
}

PyObject *
_decoder_get_info(AvifDecoderObject *self) {
    avifDecoder *decoder = self->decoder;
    avifImage *image = decoder->image;

    PyObject *icc = NULL;
    PyObject *exif = NULL;
    PyObject *xmp = NULL;
    PyObject *ret = NULL;

    if (image->xmp.size) {
        xmp = PyBytes_FromStringAndSize((const char *)image->xmp.data, image->xmp.size);
    }

    if (image->exif.size) {
        exif =
            PyBytes_FromStringAndSize((const char *)image->exif.data, image->exif.size);
    }

    if (image->icc.size) {
        icc = PyBytes_FromStringAndSize((const char *)image->icc.data, image->icc.size);
    }

    ret = Py_BuildValue(
        "IIIsSSIS",
        image->width,
        image->height,
        decoder->imageCount,
        self->mode,
        NULL == icc ? Py_None : icc,
        NULL == exif ? Py_None : exif,
        irot_imir_to_exif_orientation(image),
        NULL == xmp ? Py_None : xmp
    );

    Py_XDECREF(xmp);
    Py_XDECREF(exif);
    Py_XDECREF(icc);

    return ret;
}

PyObject *
_decoder_get_frame(AvifDecoderObject *self, PyObject *args) {
    PyObject *bytes;
    PyObject *ret;
    Py_ssize_t size;
    avifResult result;
    avifRGBImage rgb;
    avifDecoder *decoder;
    avifImage *image;
    uint32_t frame_index;

    decoder = self->decoder;

    if (!PyArg_ParseTuple(args, "I", &frame_index)) {
        return NULL;
    }

    result = avifDecoderNthImage(decoder, frame_index);
    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Failed to decode frame %u: %s",
            decoder->imageIndex + 1,
            avifResultToString(result)
        );
        return NULL;
    }

    image = decoder->image;

    memset(&rgb, 0, sizeof(rgb));
    avifRGBImageSetDefaults(&rgb, image);

    rgb.depth = 8;

    if (decoder->alphaPresent) {
        rgb.format = AVIF_RGB_FORMAT_RGBA;
    } else {
        rgb.format = AVIF_RGB_FORMAT_RGB;
        rgb.ignoreAlpha = AVIF_TRUE;
    }

    result = avifRGBImageAllocatePixels(&rgb);
    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Pixel allocation failed: %s",
            avifResultToString(result)
        );
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;
    result = avifImageYUVToRGB(image, &rgb);
    Py_END_ALLOW_THREADS;

    if (result != AVIF_RESULT_OK) {
        PyErr_Format(
            exc_type_for_avif_result(result),
            "Conversion from YUV failed: %s",
            avifResultToString(result)
        );
        avifRGBImageFreePixels(&rgb);
        return NULL;
    }

    if (rgb.height > PY_SSIZE_T_MAX / rgb.rowBytes) {
        PyErr_SetString(PyExc_MemoryError, "Integer overflow in pixel size");
        return NULL;
    }

    size = rgb.rowBytes * rgb.height;

    bytes = PyBytes_FromStringAndSize((char *)rgb.pixels, size);
    avifRGBImageFreePixels(&rgb);

    ret = Py_BuildValue(
        "SKKK",
        bytes,
        decoder->timescale,
        decoder->imageTiming.ptsInTimescales,
        decoder->imageTiming.durationInTimescales
    );

    Py_DECREF(bytes);

    return ret;
}

/* -------------------------------------------------------------------- */
/* Type Definitions                                                     */
/* -------------------------------------------------------------------- */

// AvifEncoder methods
static struct PyMethodDef _encoder_methods[] = {
    {"add", (PyCFunction)_encoder_add, METH_VARARGS},
    {"finish", (PyCFunction)_encoder_finish, METH_NOARGS},
    {NULL, NULL} /* sentinel */
};

// AvifEncoder type definition
static PyTypeObject AvifEncoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "AvifEncoder",
    .tp_basicsize = sizeof(AvifEncoderObject),
    .tp_dealloc = (destructor)_encoder_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = _encoder_methods,
};

// AvifDecoder methods
static struct PyMethodDef _decoder_methods[] = {
    {"get_info", (PyCFunction)_decoder_get_info, METH_NOARGS},
    {"get_frame", (PyCFunction)_decoder_get_frame, METH_VARARGS},
    {NULL, NULL} /* sentinel */
};

// AvifDecoder type definition
static PyTypeObject AvifDecoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "AvifDecoder",
    .tp_basicsize = sizeof(AvifDecoderObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)_decoder_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = _decoder_methods,
};

/* -------------------------------------------------------------------- */
/* Module Setup                                                         */
/* -------------------------------------------------------------------- */

static PyMethodDef avifMethods[] = {
    {"AvifDecoder", AvifDecoderNew, METH_VARARGS},
    {"AvifEncoder", AvifEncoderNew, METH_VARARGS},
    {"decoder_codec_available", _decoder_codec_available, METH_VARARGS},
    {"encoder_codec_available", _encoder_codec_available, METH_VARARGS},
    {NULL, NULL}
};

static int
setup_module(PyObject *m) {
    if (PyType_Ready(&AvifDecoder_Type) < 0 || PyType_Ready(&AvifEncoder_Type) < 0) {
        return -1;
    }

    PyObject *d = PyModule_GetDict(m);
    PyObject *v = PyUnicode_FromString(avifVersion());
    PyDict_SetItemString(d, "libavif_version", v ? v : Py_None);
    Py_XDECREF(v);

    return 0;
}

PyMODINIT_FUNC
PyInit__avif(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_avif",
        .m_size = -1,
        .m_methods = avifMethods,
    };

    m = PyModule_Create(&module_def);
    if (setup_module(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
