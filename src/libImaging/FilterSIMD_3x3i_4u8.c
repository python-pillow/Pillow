void
ImagingFilter3x3i_4u8(Imaging imOut, Imaging im, const INT16* kernel,
                      INT32 offset)
{
    int x, y;

    offset += 1 << (PRECISION_BITS-1);

    memcpy(imOut->image32[0], im->image32[0], im->linesize);

    for (y = 1; y < im->ysize-1; y++) {
        INT32* in_1 = im->image32[y-1];
        INT32* in0 = im->image32[y];
        INT32* in1 = im->image32[y+1];
        INT32* out = imOut->image32[y];

#if defined(__AVX2__)

    #define MM_KERNEL_LOAD(x) \
        source = _mm256_castsi128_si256(_mm_shuffle_epi8(_mm_loadu_si128((__m128i*) &in1[x]), shuffle)); \
        source = _mm256_inserti128_si256(source, _mm256_castsi256_si128(source), 1); \
        pix00 = _mm256_unpacklo_epi8(source, _mm256_setzero_si256()); \
        pix01 = _mm256_unpackhi_epi8(source, _mm256_setzero_si256()); \
        source = _mm256_castsi128_si256(_mm_shuffle_epi8(_mm_loadu_si128((__m128i*) &in0[x]), shuffle)); \
        source = _mm256_inserti128_si256(source, _mm256_castsi256_si128(source), 1); \
        pix10 = _mm256_unpacklo_epi8(source, _mm256_setzero_si256()); \
        pix11 = _mm256_unpackhi_epi8(source, _mm256_setzero_si256()); \
        source = _mm256_castsi128_si256(_mm_shuffle_epi8(_mm_loadu_si128((__m128i*) &in_1[x]), shuffle)); \
        source = _mm256_inserti128_si256(source, _mm256_castsi256_si128(source), 1); \
        pix20 = _mm256_unpacklo_epi8(source, _mm256_setzero_si256()); \
        pix21 = _mm256_unpackhi_epi8(source, _mm256_setzero_si256());

    #define MM_KERNEL_SUM(ss, row, kctl) \
        ss = _mm256_add_epi32(ss, _mm256_madd_epi16( \
            pix0##row, _mm256_shuffle_epi32(kernel00, kctl))); \
        ss = _mm256_add_epi32(ss, _mm256_madd_epi16( \
            pix1##row, _mm256_shuffle_epi32(kernel10, kctl))); \
        ss = _mm256_add_epi32(ss, _mm256_madd_epi16( \
            pix2##row, _mm256_shuffle_epi32(kernel20, kctl)));

        __m128i shuffle = _mm_set_epi8(15,11,14,10,13,9,12,8, 7,3,6,2,5,1,4,0);
        __m256i kernel00 = _mm256_set_epi16(
            0, 0, 0, 0, kernel[2], kernel[1], kernel[0], 0,
            0, 0, 0, 0, 0, kernel[2], kernel[1], kernel[0]);
        __m256i kernel10 = _mm256_set_epi16(
            0, 0, 0, 0, kernel[5], kernel[4], kernel[3], 0,
            0, 0, 0, 0, 0, kernel[5], kernel[4], kernel[3]);
        __m256i kernel20 = _mm256_set_epi16(
            0, 0, 0, 0, kernel[8], kernel[7], kernel[6], 0,
            0, 0, 0, 0, 0, kernel[8], kernel[7], kernel[6]);
        __m256i pix00, pix10, pix20;
        __m256i pix01, pix11, pix21;
        __m256i source;

        out[0] = in0[0];
        x = 1;
        if (im->xsize >= 4) {
            MM_KERNEL_LOAD(0);
        }
        // Last loaded pixel: x+3 + 3 (wide load)
        // Last x should be < im->xsize-6
        for (; x < im->xsize-1-5; x += 4) {
            __m256i ss0, ss2;
            __m128i ssout;

            ss0 = _mm256_set1_epi32(offset);
            MM_KERNEL_SUM(ss0, 0, 0x00);
            MM_KERNEL_SUM(ss0, 1, 0x55);
            ss0 = _mm256_srai_epi32(ss0, PRECISION_BITS);

            ss2 = _mm256_set1_epi32(offset);
            MM_KERNEL_SUM(ss2, 1, 0x00);
            MM_KERNEL_LOAD(x+3);
            MM_KERNEL_SUM(ss2, 0, 0x55);
            ss2 = _mm256_srai_epi32(ss2, PRECISION_BITS);
            
            ss0 = _mm256_packs_epi32(ss0, ss2);
            ssout = _mm_packus_epi16(
                _mm256_extracti128_si256(ss0, 0),
                _mm256_extracti128_si256(ss0, 1));
            ssout = _mm_shuffle_epi32(ssout, 0xd8);
            _mm_storeu_si128((__m128i*) &out[x], ssout);
        }
        for (; x < im->xsize-1; x++) {
            __m256i ss = _mm256_set1_epi32(offset);

            source = _mm256_castsi128_si256(_mm_shuffle_epi8(_mm_or_si128(
                _mm_slli_si128(_mm_cvtsi32_si128(*(INT32*) &in1[x+1]), 8),
                _mm_loadl_epi64((__m128i*) &in1[x-1])), shuffle));
            source = _mm256_inserti128_si256(source, _mm256_castsi256_si128(source), 1);
            pix00 = _mm256_unpacklo_epi8(source, _mm256_setzero_si256());
            pix01 = _mm256_unpackhi_epi8(source, _mm256_setzero_si256());
            source = _mm256_castsi128_si256(_mm_shuffle_epi8(_mm_or_si128(
                _mm_slli_si128(_mm_cvtsi32_si128(*(INT32*) &in0[x+1]), 8),
                _mm_loadl_epi64((__m128i*) &in0[x-1])), shuffle));
            source = _mm256_inserti128_si256(source, _mm256_castsi256_si128(source), 1);
            pix10 = _mm256_unpacklo_epi8(source, _mm256_setzero_si256());
            pix11 = _mm256_unpackhi_epi8(source, _mm256_setzero_si256());
            source = _mm256_castsi128_si256(_mm_shuffle_epi8(_mm_or_si128(
                _mm_slli_si128(_mm_cvtsi32_si128(*(INT32*) &in_1[x+1]), 8),
                _mm_loadl_epi64((__m128i*) &in_1[x-1])), shuffle));
            source = _mm256_inserti128_si256(source, _mm256_castsi256_si128(source), 1);
            pix20 = _mm256_unpacklo_epi8(source, _mm256_setzero_si256());
            pix21 = _mm256_unpackhi_epi8(source, _mm256_setzero_si256());

            MM_KERNEL_SUM(ss, 0, 0x00);
            MM_KERNEL_SUM(ss, 1, 0x55);

            ss = _mm256_srai_epi32(ss, PRECISION_BITS);
            
            ss = _mm256_packs_epi32(ss, ss);
            ss = _mm256_packus_epi16(ss, ss);
            out[x] = _mm_cvtsi128_si32(_mm256_castsi256_si128(ss));
        }
        out[x] = in0[x];
    #undef MM_KERNEL_LOAD
    #undef MM_KERNEL_SUM

#else

    #define MM_KERNEL_LOAD(x) \
        source = _mm_shuffle_epi8(_mm_loadu_si128((__m128i*) &in1[x]), shuffle); \
        pix00 = _mm_unpacklo_epi8(source, _mm_setzero_si128()); \
        pix01 = _mm_unpackhi_epi8(source, _mm_setzero_si128()); \
        source = _mm_shuffle_epi8(_mm_loadu_si128((__m128i*) &in0[x]), shuffle); \
        pix10 = _mm_unpacklo_epi8(source, _mm_setzero_si128()); \
        pix11 = _mm_unpackhi_epi8(source, _mm_setzero_si128()); \
        source = _mm_shuffle_epi8(_mm_loadu_si128((__m128i*) &in_1[x]), shuffle); \
        pix20 = _mm_unpacklo_epi8(source, _mm_setzero_si128()); \
        pix21 = _mm_unpackhi_epi8(source, _mm_setzero_si128());

    #define MM_KERNEL_SUM(ss, row, kctl) \
        ss = _mm_add_epi32(ss, _mm_madd_epi16( \
            pix0##row, _mm_shuffle_epi32(kernel00, kctl))); \
        ss = _mm_add_epi32(ss, _mm_madd_epi16( \
            pix1##row, _mm_shuffle_epi32(kernel10, kctl))); \
        ss = _mm_add_epi32(ss, _mm_madd_epi16( \
            pix2##row, _mm_shuffle_epi32(kernel20, kctl)));

        __m128i shuffle = _mm_set_epi8(15,11,14,10,13,9,12,8, 7,3,6,2,5,1,4,0);
        __m128i kernel00 = _mm_set_epi16(
            kernel[2], kernel[1], kernel[0], 0,
            0, kernel[2], kernel[1], kernel[0]);
        __m128i kernel10 = _mm_set_epi16(
            kernel[5], kernel[4], kernel[3], 0,
            0, kernel[5], kernel[4], kernel[3]);
        __m128i kernel20 = _mm_set_epi16(
            kernel[8], kernel[7], kernel[6], 0,
            0, kernel[8], kernel[7], kernel[6]);
        __m128i pix00, pix10, pix20;
        __m128i pix01, pix11, pix21;
        __m128i source;

        out[0] = in0[0];
        x = 1;
        if (im->xsize >= 4) {
            MM_KERNEL_LOAD(0);
        }
        // Last loaded pixel: x+3 + 3 (wide load)
        // Last x should be < im->xsize-6
        for (; x < im->xsize-1-5; x += 4) {
            __m128i ss0 = _mm_set1_epi32(offset);
            __m128i ss1 = _mm_set1_epi32(offset);
            __m128i ss2 = _mm_set1_epi32(offset);
            __m128i ss3 = _mm_set1_epi32(offset);

            MM_KERNEL_SUM(ss0, 0, 0x00);
            MM_KERNEL_SUM(ss0, 1, 0x55);
            ss0 = _mm_srai_epi32(ss0, PRECISION_BITS);

            MM_KERNEL_SUM(ss1, 0, 0xaa);
            MM_KERNEL_SUM(ss1, 1, 0xff);
            ss1 = _mm_srai_epi32(ss1, PRECISION_BITS);

            MM_KERNEL_SUM(ss2, 1, 0x00);
            MM_KERNEL_SUM(ss3, 1, 0xaa);

            MM_KERNEL_LOAD(x+3);

            MM_KERNEL_SUM(ss2, 0, 0x55);
            MM_KERNEL_SUM(ss3, 0, 0xff);
            ss2 = _mm_srai_epi32(ss2, PRECISION_BITS);
            ss3 = _mm_srai_epi32(ss3, PRECISION_BITS);
            
            ss0 = _mm_packs_epi32(ss0, ss1);
            ss2 = _mm_packs_epi32(ss2, ss3);
            ss0 = _mm_packus_epi16(ss0, ss2);
            _mm_storeu_si128((__m128i*) &out[x], ss0);
        }
        for (; x < im->xsize-1; x++) {
            __m128i ss = _mm_set1_epi32(offset);

            source = _mm_shuffle_epi8(_mm_loadl_epi64((__m128i*) &in1[x-1]), shuffle);
            pix00 = _mm_unpacklo_epi8(source, _mm_setzero_si128());
            source = _mm_shuffle_epi8(_mm_cvtsi32_si128(*(int*) &in1[x+1]), shuffle);
            pix01 = _mm_unpacklo_epi8(source, _mm_setzero_si128());
            source = _mm_shuffle_epi8(_mm_loadl_epi64((__m128i*) &in0[x-1]), shuffle);
            pix10 = _mm_unpacklo_epi8(source, _mm_setzero_si128());
            source = _mm_shuffle_epi8(_mm_cvtsi32_si128(*(int*) &in0[x+1]), shuffle);
            pix11 = _mm_unpacklo_epi8(source, _mm_setzero_si128());
            source = _mm_shuffle_epi8(_mm_loadl_epi64((__m128i*) &in_1[x-1]), shuffle);
            pix20 = _mm_unpacklo_epi8(source, _mm_setzero_si128());
            source = _mm_shuffle_epi8(_mm_cvtsi32_si128(*(int*) &in_1[x+1]), shuffle);
            pix21 = _mm_unpacklo_epi8(source, _mm_setzero_si128());

            MM_KERNEL_SUM(ss, 0, 0x00);
            MM_KERNEL_SUM(ss, 1, 0x55);

            ss = _mm_srai_epi32(ss, PRECISION_BITS);
            
            ss = _mm_packs_epi32(ss, ss);
            ss = _mm_packus_epi16(ss, ss);
            out[x] = _mm_cvtsi128_si32(ss);
        }
        out[x] = in0[x];
    #undef MM_KERNEL_LOAD
    #undef MM_KERNEL_SUM

#endif
    }
    memcpy(imOut->image32[y], im->image32[y], im->linesize);
}
