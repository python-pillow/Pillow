/*
 * The Python Imaging Library
 * $Id$
 *
 * incremental decoding adaptor.
 *
 * Copyright (c) 2014 Coriolis Systems Limited
 * Copyright (c) 2014 Alastair Houghton
 *
 */

#include "Imaging.h"

/* The idea behind this interface is simple: the actual decoding proceeds in
   a thread, which is run in lock step with the main thread.  Whenever the
   ImagingIncrementalDecoderRead() call runs short on data, it suspends the
   decoding thread and wakes the main thread.  Conversely, the
   ImagingIncrementalDecodeData() call suspends the main thread and wakes
   the decoding thread, providing a buffer of data.

   The two threads are never running simultaneously, so there is no need for
   any addition synchronisation measures outside of this file.

   Note also that we start the thread suspended (on Windows), or make it
   immediately wait (other platforms), so that it's possible to initialise
   things before the thread starts running.

   This interface is useful to allow PIL to interact efficiently with any
   third-party imaging library that does not support suspendable reads;
   one example is OpenJPEG (which is used for J2K support).  The TIFF library
   might also benefit from using this code.

   Note that if using this module, you want to set handles_eof on your
   decoder to true.  Why?  Because otherwise ImageFile.load() will abort,
   thinking that the image is truncated, whereas generally you want it to
   pass the EOF condition (0 bytes to read) through to your code. */

#ifdef _WIN32
#include <windows.h>
#include <process.h>
#else
#include <pthread.h>
#endif

struct ImagingIncrementalStreamStruct {
  UINT8 *buffer;
  UINT8 *ptr;
  UINT8 *end;
};

struct ImagingIncrementalDecoderStruct {
#ifdef _WIN32
  HANDLE            hDecodeEvent;
  HANDLE            hDataEvent;
  HANDLE            hThread;
#else
  pthread_mutex_t   start_mutex;
  pthread_cond_t    start_cond;
  pthread_mutex_t   decode_mutex;
  pthread_cond_t    decode_cond;
  pthread_mutex_t   data_mutex;
  pthread_cond_t    data_cond;
  pthread_t         thread;
#endif
  ImagingIncrementalDecoderEntry        entry;
  Imaging                               im;
  ImagingCodecState                     state;
  struct {
    UINT8 *buffer;
    UINT8 *ptr;
    UINT8 *end;
  } stream;
  int                                   started;
  int                                   result;
};

#if _WIN32
static void __stdcall
incremental_thread(void *ptr)
{
  ImagingIncrementalDecoder decoder = (ImagingIncrementalDecoder)ptr;

  decoder->result = decoder->entry(decoder->im, decoder->state, decoder);

  SetEvent(decoder->hDecodeEvent);
}
#else
static void *
incremental_thread(void *ptr)
{
  ImagingIncrementalDecoder decoder = (ImagingIncrementalDecoder)ptr;

  decoder->result = decoder->entry(decoder->im, decoder->state, decoder);

  pthread_cond_signal(&decoder->decode_cond);

  return NULL;
}
#endif

/**
 * Create a new incremental decoder */
ImagingIncrementalDecoder
ImagingIncrementalDecoderCreate(ImagingIncrementalDecoderEntry decoder_entry,
                                Imaging im,
                                ImagingCodecState state)
{
  ImagingIncrementalDecoder decoder = (ImagingIncrementalDecoder)malloc(sizeof(struct ImagingIncrementalDecoderStruct));

  decoder->entry = decoder_entry;
  decoder->im = im;
  decoder->state = state;
  decoder->result = 0;
  decoder->stream.buffer = decoder->stream.ptr = decoder->stream.end = NULL;
  decoder->started = 0;

  /* System specific set-up */
#if _WIN32
  decoder->hDecodeEvent = CreateEvent(NULL, FALSE, FALSE, NULL);

  if (!decoder->hDecodeEvent) {
    free(decoder);
    return NULL;
  }

  decoder->hDataEvent = CreateEvent(NULL, FALSE, FALSE, NULL);

  if (!decoder->hDataEvent) {
    CloseHandle(decoder->hDecodeEvent);
    free(decoder);
    return NULL;
  }

  decoder->hThread = _beginthreadex(NULL, 0, incremental_thread, decoder,
                                    CREATE_SUSPENDED, NULL);

  if (!decoder->hThread) {
    CloseHandle(decoder->hDecodeEvent);
    CloseHandle(decoder->hDataEvent);
    free(decoder);
    return NULL;
  }
#else
  if (pthread_mutex_init(&decoder->start_mutex, NULL)) {
    free (decoder);
    return NULL;
  }

  if (pthread_mutex_init(&decoder->decode_mutex, NULL)) {
    pthread_mutex_destroy(&decoder->start_mutex);
    free(decoder);
    return NULL;
  }

  if (pthread_mutex_init(&decoder->data_mutex, NULL)) {
    pthread_mutex_destroy(&decoder->start_mutex);
    pthread_mutex_destroy(&decoder->decode_mutex);
    free(decoder);
    return NULL;
  }

  if (pthread_cond_init(&decoder->start_cond, NULL)) {
    pthread_mutex_destroy(&decoder->start_mutex);
    pthread_mutex_destroy(&decoder->decode_mutex);
    pthread_mutex_destroy(&decoder->data_mutex);
    free(decoder);
    return NULL;
  }

  if (pthread_cond_init(&decoder->decode_cond, NULL)) {
    pthread_mutex_destroy(&decoder->start_mutex);
    pthread_mutex_destroy(&decoder->decode_mutex);
    pthread_mutex_destroy(&decoder->data_mutex);
    pthread_cond_destroy(&decoder->start_cond);
    free(decoder);
    return NULL;
  }

  if (pthread_cond_init(&decoder->data_cond, NULL)) {
    pthread_mutex_destroy(&decoder->start_mutex);
    pthread_mutex_destroy(&decoder->decode_mutex);
    pthread_mutex_destroy(&decoder->data_mutex);
    pthread_cond_destroy(&decoder->start_cond);
    pthread_cond_destroy(&decoder->decode_cond);
    free(decoder);
    return NULL;
  }

  if (pthread_create(&decoder->thread, NULL, incremental_thread, decoder)) {
    pthread_mutex_destroy(&decoder->start_mutex);
    pthread_mutex_destroy(&decoder->decode_mutex);
    pthread_mutex_destroy(&decoder->data_mutex);
    pthread_cond_destroy(&decoder->start_cond);
    pthread_cond_destroy(&decoder->decode_cond);
    pthread_cond_destroy(&decoder->data_cond);
    free(decoder);
    return NULL;
  }
#endif

  return decoder;
}

/**
 * Destroy an incremental decoder */
void
ImagingIncrementalDecoderDestroy(ImagingIncrementalDecoder decoder)
{
  if (!decoder->started) {
#ifdef _WIN32
    ResumeThread(decoder->hThread);
#else
    pthread_cond_signal(&decoder->start_cond);
#endif
    decoder->started = 1;
  }

#ifndef _WIN32
  pthread_mutex_lock(&decoder->data_mutex);
#endif

  decoder->stream.buffer = decoder->stream.ptr = decoder->stream.end = NULL;

#ifdef _WIN32
  SetEvent(decoder->hDataEvent);

  WaitForSingleObject(decoder->hThread, INFINITE);

  CloseHandle(decoder->hThread);
  CloseHandle(decoder->hDecodeEvent);
  CloseHandle(decoder->hDataEvent);
#else
  pthread_cond_signal(&decoder->data_cond);
  pthread_mutex_unlock(&decoder->data_mutex);

  pthread_join(decoder->thread, NULL);

  pthread_mutex_destroy(&decoder->start_mutex);
  pthread_mutex_destroy(&decoder->decode_mutex);
  pthread_mutex_destroy(&decoder->data_mutex);
  pthread_cond_destroy(&decoder->start_cond);
  pthread_cond_destroy(&decoder->decode_cond);
  pthread_cond_destroy(&decoder->data_cond);
#endif
  free (decoder);
}

/**
 * Decode data using an incremental decoder */
int
ImagingIncrementalDecodeData(ImagingIncrementalDecoder decoder,
                             UINT8 *buf, int bytes)
{
  if (!decoder->started) {
#ifdef _WIN32
    ResumeThread(decoder->hThread);
#else
    pthread_cond_signal(&decoder->start_cond);
#endif
    decoder->started = 1;
  }

#ifndef _WIN32
  pthread_mutex_lock(&decoder->data_mutex);
#endif

  decoder->stream.buffer = decoder->stream.ptr = buf;
  decoder->stream.end = buf + bytes;

#ifdef _WIN32
  SetEvent(decoder->hDataEvent);
  WaitForSingleObject(decoder->hDecodeEvent);
#else
  pthread_cond_signal(&decoder->data_cond);
  pthread_mutex_unlock(&decoder->data_mutex);

  pthread_mutex_lock(&decoder->decode_mutex);
  pthread_cond_wait(&decoder->decode_cond, &decoder->decode_mutex);
  pthread_mutex_unlock(&decoder->decode_mutex);
#endif

  return decoder->result;
}

size_t
ImagingIncrementalDecoderRead(ImagingIncrementalDecoder decoder,
                             void *buffer, size_t bytes)
{
  UINT8 *ptr = (UINT8 *)buffer;
  size_t done = 0;

  pthread_mutex_lock(&decoder->data_mutex);
  while (bytes) {
    size_t todo = bytes;
    size_t remaining = decoder->stream.end - decoder->stream.ptr;

    if (!remaining) {
#ifndef _WIN32
      pthread_mutex_lock(&decoder->decode_mutex);
#endif
      decoder->result = (int)(decoder->stream.ptr - decoder->stream.buffer);
#if _WIN32
      SetEvent(decoder->hDecodeEvent);
      WaitForSingleObject(decoder->hDataEvent);
#else
      pthread_cond_signal(&decoder->decode_cond);
      pthread_mutex_unlock(&decoder->decode_mutex);
      pthread_cond_wait(&decoder->data_cond, &decoder->data_mutex);
#endif

      remaining = decoder->stream.end - decoder->stream.ptr;
    }
    if (todo > remaining)
      todo = remaining;

    if (!todo)
      break;

    memcpy (ptr, decoder->stream.ptr, todo);
    decoder->stream.ptr += todo;
    bytes -= todo;
    done += todo;
    ptr += todo;
  }
  pthread_mutex_unlock(&decoder->data_mutex);

  return done;
}

off_t
ImagingIncrementalDecoderSkip(ImagingIncrementalDecoder decoder,
                              off_t bytes)
{
  off_t done = 0;

  while (bytes) {
    off_t todo = bytes;
    off_t remaining = decoder->stream.end - decoder->stream.ptr;

    if (!remaining) {
      decoder->result = (int)(decoder->stream.ptr - decoder->stream.buffer);
#if _WIN32
      SetEvent(decoder->hDecodeEvent);
      WaitForSingleObject(decoder->hDataEvent);
#else
      pthread_cond_signal(&decoder->decode_cond);
      pthread_mutex_lock(&decoder->data_mutex);
      pthread_cond_wait(&decoder->data_cond, &decoder->data_mutex);
#endif

      remaining = decoder->stream.end - decoder->stream.ptr;
    }
    if (todo > remaining)
      todo = remaining;

    if (!todo)
      break;

    decoder->stream.ptr += todo;
    bytes -= todo;
    done += todo;
  }

  return done;
}

