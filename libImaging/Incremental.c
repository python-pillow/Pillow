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
   ImagingIncrementalCodecRead() call runs short on data, it suspends the
   decoding thread and wakes the main thread.  Conversely, the
   ImagingIncrementalCodecPushBuffer() call suspends the main thread and wakes
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

#define DEBUG_INCREMENTAL 0

#if DEBUG_INCREMENTAL
#define DEBUG(...) printf(__VA_ARGS__)
#else
#define DEBUG(...)
#endif

struct ImagingIncrementalCodecStruct {
#ifdef _WIN32
  HANDLE            hCodecEvent;
  HANDLE            hDataEvent;
  HANDLE            hThread;
#else
  pthread_mutex_t   start_mutex;
  pthread_cond_t    start_cond;
  pthread_mutex_t   codec_mutex;
  pthread_cond_t    codec_cond;
  pthread_mutex_t   data_mutex;
  pthread_cond_t    data_cond;
  pthread_t         thread;
#endif
  ImagingIncrementalCodecEntry        entry;
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
codec_thread(void *ptr)
{
  ImagingIncrementalCodec codec = (ImagingIncrementalCodec)ptr;

  codec->result = codec->entry(codec->im, codec->state, codec);

  SetEvent(codec->hCodecEvent);
}
#else
static void *
codec_thread(void *ptr)
{
  ImagingIncrementalCodec codec = (ImagingIncrementalCodec)ptr;

  codec->result = codec->entry(codec->im, codec->state, codec);

  pthread_cond_signal(&codec->codec_cond);

  return NULL;
}
#endif

/**
 * Create a new incremental codec */
ImagingIncrementalCodec
ImagingIncrementalCodecCreate(ImagingIncrementalCodecEntry codec_entry,
                              Imaging im,
                              ImagingCodecState state)
{
  ImagingIncrementalCodec codec = (ImagingIncrementalCodec)malloc(sizeof(struct ImagingIncrementalCodecStruct));

  codec->entry = codec_entry;
  codec->im = im;
  codec->state = state;
  codec->result = 0;
  codec->stream.buffer = codec->stream.ptr = codec->stream.end = NULL;
  codec->started = 0;

  /* System specific set-up */
#if _WIN32
  codec->hCodecEvent = CreateEvent(NULL, FALSE, FALSE, NULL);

  if (!codec->hCodecEvent) {
    free(codec);
    return NULL;
  }

  codec->hDataEvent = CreateEvent(NULL, FALSE, FALSE, NULL);

  if (!codec->hDataEvent) {
    CloseHandle(codec->hCodecEvent);
    free(codec);
    return NULL;
  }

  codec->hThread = _beginthreadex(NULL, 0, codec_thread, codec,
                                    CREATE_SUSPENDED, NULL);

  if (!codec->hThread) {
    CloseHandle(codec->hCodecEvent);
    CloseHandle(codec->hDataEvent);
    free(codec);
    return NULL;
  }
#else
  if (pthread_mutex_init(&codec->start_mutex, NULL)) {
    free (codec);
    return NULL;
  }

  if (pthread_mutex_init(&codec->codec_mutex, NULL)) {
    pthread_mutex_destroy(&codec->start_mutex);
    free(codec);
    return NULL;
  }

  if (pthread_mutex_init(&codec->data_mutex, NULL)) {
    pthread_mutex_destroy(&codec->start_mutex);
    pthread_mutex_destroy(&codec->codec_mutex);
    free(codec);
    return NULL;
  }

  if (pthread_cond_init(&codec->start_cond, NULL)) {
    pthread_mutex_destroy(&codec->start_mutex);
    pthread_mutex_destroy(&codec->codec_mutex);
    pthread_mutex_destroy(&codec->data_mutex);
    free(codec);
    return NULL;
  }

  if (pthread_cond_init(&codec->codec_cond, NULL)) {
    pthread_mutex_destroy(&codec->start_mutex);
    pthread_mutex_destroy(&codec->codec_mutex);
    pthread_mutex_destroy(&codec->data_mutex);
    pthread_cond_destroy(&codec->start_cond);
    free(codec);
    return NULL;
  }

  if (pthread_cond_init(&codec->data_cond, NULL)) {
    pthread_mutex_destroy(&codec->start_mutex);
    pthread_mutex_destroy(&codec->codec_mutex);
    pthread_mutex_destroy(&codec->data_mutex);
    pthread_cond_destroy(&codec->start_cond);
    pthread_cond_destroy(&codec->codec_cond);
    free(codec);
    return NULL;
  }

  if (pthread_create(&codec->thread, NULL, codec_thread, codec)) {
    pthread_mutex_destroy(&codec->start_mutex);
    pthread_mutex_destroy(&codec->codec_mutex);
    pthread_mutex_destroy(&codec->data_mutex);
    pthread_cond_destroy(&codec->start_cond);
    pthread_cond_destroy(&codec->codec_cond);
    pthread_cond_destroy(&codec->data_cond);
    free(codec);
    return NULL;
  }
#endif

  return codec;
}

/**
 * Destroy an incremental codec */
void
ImagingIncrementalCodecDestroy(ImagingIncrementalCodec codec)
{
  DEBUG("destroying\n");

  if (!codec->started) {
#ifdef _WIN32
    ResumeThread(codec->hThread);
#else
    pthread_cond_signal(&codec->start_cond);
#endif
    codec->started = 1;
  }

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif

  codec->stream.buffer = codec->stream.ptr = codec->stream.end = NULL;

#ifdef _WIN32
  SetEvent(codec->hDataEvent);

  WaitForSingleObject(codec->hThread, INFINITE);

  CloseHandle(codec->hThread);
  CloseHandle(codec->hCodecEvent);
  CloseHandle(codec->hDataEvent);
#else
  pthread_cond_signal(&codec->data_cond);
  pthread_mutex_unlock(&codec->data_mutex);

  pthread_join(codec->thread, NULL);

  pthread_mutex_destroy(&codec->start_mutex);
  pthread_mutex_destroy(&codec->codec_mutex);
  pthread_mutex_destroy(&codec->data_mutex);
  pthread_cond_destroy(&codec->start_cond);
  pthread_cond_destroy(&codec->codec_cond);
  pthread_cond_destroy(&codec->data_cond);
#endif
  free (codec);
}

/**
 * Push a data buffer for an incremental codec */
int
ImagingIncrementalCodecPushBuffer(ImagingIncrementalCodec codec,
                                  UINT8 *buf, int bytes)
{
  if (!codec->started) {
    DEBUG("starting\n");

#ifdef _WIN32
    ResumeThread(codec->hThread);
#else
    pthread_cond_signal(&codec->start_cond);
#endif
    codec->started = 1;
  }

  DEBUG("providing %p, %d\n", buf, bytes);

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif

  codec->stream.buffer = codec->stream.ptr = buf;
  codec->stream.end = buf + bytes;

#ifdef _WIN32
  SetEvent(codec->hDataEvent);
  WaitForSingleObject(codec->hCodecEvent);
#else
  pthread_cond_signal(&codec->data_cond);
  pthread_mutex_unlock(&codec->data_mutex);

  pthread_mutex_lock(&codec->codec_mutex);
  pthread_cond_wait(&codec->codec_cond, &codec->codec_mutex);
  pthread_mutex_unlock(&codec->codec_mutex);
#endif

  DEBUG("got result %d\n", codec->result);

  return codec->result;
}

size_t
ImagingIncrementalCodecBytesInBuffer(ImagingIncrementalCodec codec)
{
  return codec->stream.ptr - codec->stream.buffer;
}

size_t
ImagingIncrementalCodecRead(ImagingIncrementalCodec codec,
                             void *buffer, size_t bytes)
{
  UINT8 *ptr = (UINT8 *)buffer;
  size_t done = 0;

  DEBUG("reading (want %llu bytes)\n", (unsigned long long)bytes);

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif
  while (bytes) {
    size_t todo = bytes;
    size_t remaining = codec->stream.end - codec->stream.ptr;

    if (!remaining) {
      DEBUG("waiting for data\n");

#ifndef _WIN32
      pthread_mutex_lock(&codec->codec_mutex);
#endif
      codec->result = (int)(codec->stream.ptr - codec->stream.buffer);
#if _WIN32
      SetEvent(codec->hCodecEvent);
      WaitForSingleObject(codec->hDataEvent);
#else
      pthread_cond_signal(&codec->codec_cond);
      pthread_mutex_unlock(&codec->codec_mutex);
      pthread_cond_wait(&codec->data_cond, &codec->data_mutex);
#endif

      remaining = codec->stream.end - codec->stream.ptr;

      DEBUG("got %llu bytes\n", (unsigned long long)remaining);
    }
    if (todo > remaining)
      todo = remaining;

    if (!todo)
      break;

    memcpy (ptr, codec->stream.ptr, todo);
    codec->stream.ptr += todo;
    bytes -= todo;
    done += todo;
    ptr += todo;
  }
#ifndef _WIN32
  pthread_mutex_unlock(&codec->data_mutex);
#endif

  DEBUG("read total %llu bytes\n", (unsigned long long)done);

  return done;
}

off_t
ImagingIncrementalCodecSkip(ImagingIncrementalCodec codec,
                              off_t bytes)
{
  off_t done = 0;

  DEBUG("skipping (want %llu bytes)\n", (unsigned long long)bytes);

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif
  while (bytes) {
    off_t todo = bytes;
    off_t remaining = codec->stream.end - codec->stream.ptr;

    if (!remaining) {
      DEBUG("waiting for data\n");

#ifndef _WIN32
      pthread_mutex_lock(&codec->codec_mutex);
#endif
      codec->result = (int)(codec->stream.ptr - codec->stream.buffer);
#if _WIN32
      SetEvent(codec->hCodecEvent);
      WaitForSingleObject(codec->hDataEvent);
#else
      pthread_cond_signal(&codec->codec_cond);
      pthread_mutex_unlock(&codec->codec_mutex);
      pthread_cond_wait(&codec->data_cond, &codec->data_mutex);
#endif

      remaining = codec->stream.end - codec->stream.ptr;
    }
    if (todo > remaining)
      todo = remaining;

    if (!todo)
      break;

    codec->stream.ptr += todo;
    bytes -= todo;
    done += todo;
  }
#ifndef _WIN32
  pthread_mutex_unlock(&codec->data_mutex);
#endif

  DEBUG("skipped total %llu bytes\n", (unsigned long long)done);

  return done;
}

size_t
ImagingIncrementalCodecWrite(ImagingIncrementalCodec codec,
                             const void *buffer, size_t bytes)
{
  const UINT8 *ptr = (const UINT8 *)buffer;
  size_t done = 0;

  DEBUG("write (have %llu bytes)\n", (unsigned long long)bytes);

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif
  while (bytes) {
    size_t todo = bytes;
    size_t remaining = codec->stream.end - codec->stream.ptr;

    if (!remaining) {
      DEBUG("waiting for space\n");

#ifndef _WIN32
      pthread_mutex_lock(&codec->codec_mutex);
#endif
      codec->result = (int)(codec->stream.ptr - codec->stream.buffer);
#if _WIN32
      SetEvent(codec->hCodecEvent);
      WaitForSingleObject(codec->hDataEvent);
#else
      pthread_cond_signal(&codec->codec_cond);
      pthread_mutex_unlock(&codec->codec_mutex);
      pthread_cond_wait(&codec->data_cond, &codec->data_mutex);
#endif

      remaining = codec->stream.end - codec->stream.ptr;

      DEBUG("got %llu bytes\n", (unsigned long long)remaining);
    }
    if (todo > remaining)
      todo = remaining;

    if (!todo)
      break;

    memcpy (codec->stream.ptr, ptr, todo);
    codec->stream.ptr += todo;
    bytes -= todo;
    done += todo;
    ptr += todo;
  }
#ifndef _WIN32
  pthread_mutex_unlock(&codec->data_mutex);
#endif

  DEBUG("wrote total %llu bytes\n", (unsigned long long)done);

  return done;
}
