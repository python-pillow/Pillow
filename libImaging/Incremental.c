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

/* Additional complication: *Some* codecs need to seek; this is fine if
   there is a file descriptor, but if we're buffering data it becomes
   awkward.  The incremental adaptor now contains code to handle these
   two cases. */

#ifdef _WIN32
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
  ImagingIncrementalCodecEntry  entry;
  Imaging                       im;
  ImagingCodecState             state;
  struct {
    int    fd;
    UINT8 *buffer;      /* Base of buffer */
    UINT8 *ptr;         /* Current pointer in buffer */
    UINT8 *top;         /* Highest point in buffer we've used */
    UINT8 *end;         /* End of buffer */
  } stream;
  int                           read_or_write;
  int                           seekable;
  int                           started;
  int                           result;
};

static void flush_stream(ImagingIncrementalCodec codec);

#if _WIN32
static unsigned int __stdcall
codec_thread(void *ptr)
{
  ImagingIncrementalCodec codec = (ImagingIncrementalCodec)ptr;

  DEBUG("Entering thread\n");

  codec->result = codec->entry(codec->im, codec->state, codec);

  DEBUG("Leaving thread (%d)\n", codec->result);

  flush_stream(codec);

  SetEvent(codec->hCodecEvent);

  return 0;
}
#else
static void *
codec_thread(void *ptr)
{
  ImagingIncrementalCodec codec = (ImagingIncrementalCodec)ptr;

  DEBUG("Entering thread\n");

  codec->result = codec->entry(codec->im, codec->state, codec);

  DEBUG("Leaving thread (%d)\n", codec->result);

  flush_stream(codec);

  pthread_mutex_lock(&codec->codec_mutex);
  pthread_cond_signal(&codec->codec_cond);
  pthread_mutex_unlock(&codec->codec_mutex);

  return NULL;
}
#endif

static void
flush_stream(ImagingIncrementalCodec codec)
{
  UINT8 *buffer;
  size_t bytes;

  /* This is to flush data from the write buffer for a seekable write
     codec. */
  if (codec->read_or_write != INCREMENTAL_CODEC_WRITE
      || codec->state->errcode != IMAGING_CODEC_END
      || !codec->seekable
      || codec->stream.fd >= 0)
    return;

  DEBUG("flushing data\n");

  buffer = codec->stream.buffer;
  bytes = codec->stream.ptr - codec->stream.buffer;

  codec->state->errcode = 0;
  codec->seekable = INCREMENTAL_CODEC_NOT_SEEKABLE;
  codec->stream.buffer = codec->stream.ptr = codec->stream.end
    = codec->stream.top = NULL;

  ImagingIncrementalCodecWrite(codec, buffer, bytes);

  codec->state->errcode = IMAGING_CODEC_END;
  codec->result = (int)ImagingIncrementalCodecBytesInBuffer(codec);

  free(buffer);
}

/**
 * Create a new incremental codec */
ImagingIncrementalCodec
ImagingIncrementalCodecCreate(ImagingIncrementalCodecEntry codec_entry,
                              Imaging im,
                              ImagingCodecState state,
                              int read_or_write,
                              int seekable,
                              int fd)
{
  ImagingIncrementalCodec codec = (ImagingIncrementalCodec)malloc(sizeof(struct ImagingIncrementalCodecStruct));

  codec->entry = codec_entry;
  codec->im = im;
  codec->state = state;
  codec->result = 0;
  codec->stream.fd = fd;
  codec->stream.buffer = codec->stream.ptr = codec->stream.end
    = codec->stream.top = NULL;
  codec->started = 0;
  codec->seekable = seekable;
  codec->read_or_write = read_or_write;

  if (fd >= 0)
    lseek(fd, 0, SEEK_SET);

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

  if (codec->seekable && codec->stream.fd < 0)
    free (codec->stream.buffer);

  codec->stream.buffer = codec->stream.ptr = codec->stream.end
    = codec->stream.top = NULL;

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

    /* Wait for the thread to ask for data */
#ifdef _WIN32
    WaitForSingleObject(codec->hCodecEvent, INFINITE);
#else
    pthread_mutex_lock(&codec->codec_mutex);
    pthread_cond_wait(&codec->codec_cond, &codec->codec_mutex);
    pthread_mutex_unlock(&codec->codec_mutex);
#endif
    if (codec->result < 0) {
      DEBUG("got result %d\n", codec->result);

      return codec->result;
    }
  }

  /* Codecs using an fd don't need data, so when we get here, we're done */
  if (codec->stream.fd >= 0) {
    DEBUG("got result %d\n", codec->result);

    return codec->result;
  }

  DEBUG("providing %p, %d\n", buf, bytes);

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif

  if (codec->read_or_write == INCREMENTAL_CODEC_READ
      && codec->seekable && codec->stream.fd < 0) {
    /* In this specific case, we append to a buffer we allocate ourselves */
    size_t old_size = codec->stream.end - codec->stream.buffer;
    size_t new_size = codec->stream.end - codec->stream.buffer + bytes;
    UINT8 *new = (UINT8 *)realloc (codec->stream.buffer, new_size);

    if (!new) {
      codec->state->errcode = IMAGING_CODEC_MEMORY;
#ifndef _WIN32
      pthread_mutex_unlock(&codec->data_mutex);
#endif
      return -1;
    }

    codec->stream.ptr = codec->stream.ptr - codec->stream.buffer + new;
    codec->stream.end = new + new_size;
    codec->stream.buffer = new;

    memcpy(new + old_size, buf, bytes);
  } else {
    codec->stream.buffer = codec->stream.ptr = buf;
    codec->stream.end = buf + bytes;
  }

#ifdef _WIN32
  SetEvent(codec->hDataEvent);
  WaitForSingleObject(codec->hCodecEvent, INFINITE);
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

Py_ssize_t
ImagingIncrementalCodecRead(ImagingIncrementalCodec codec,
                             void *buffer, size_t bytes)
{
  UINT8 *ptr = (UINT8 *)buffer;
  size_t done = 0;

  if (codec->read_or_write == INCREMENTAL_CODEC_WRITE) {
    DEBUG("attempt to read from write codec\n");
    return -1;
  }

  DEBUG("reading (want %llu bytes)\n", (unsigned long long)bytes);

  if (codec->stream.fd >= 0) {
    Py_ssize_t ret = read(codec->stream.fd, buffer, bytes);
    DEBUG("read %lld bytes from fd\n", (long long)ret);
    return ret;
  }

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
      WaitForSingleObject(codec->hDataEvent, INFINITE);
#else
      pthread_cond_signal(&codec->codec_cond);
      pthread_mutex_unlock(&codec->codec_mutex);
      pthread_cond_wait(&codec->data_cond, &codec->data_mutex);
#endif

      remaining = codec->stream.end - codec->stream.ptr;
      codec->stream.top = codec->stream.end;

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

  /* In write mode, explicitly fill with zeroes */
  if (codec->read_or_write == INCREMENTAL_CODEC_WRITE) {
    static const UINT8 zeroes[256] = { 0 };
    off_t done = 0;
    while (bytes) {
      size_t todo = (size_t)(bytes > 256 ? 256 : bytes);
      Py_ssize_t written = ImagingIncrementalCodecWrite(codec, zeroes, todo);
      if (written <= 0)
        break;
      done += written;
      bytes -= written;
    }
    return done;
  }

  if (codec->stream.fd >= 0)
    return lseek(codec->stream.fd, bytes, SEEK_CUR);

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
      WaitForSingleObject(codec->hDataEvent, INFINITE);
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

Py_ssize_t
ImagingIncrementalCodecWrite(ImagingIncrementalCodec codec,
                             const void *buffer, size_t bytes)
{
  const UINT8 *ptr = (const UINT8 *)buffer;
  size_t done = 0;

  if (codec->read_or_write == INCREMENTAL_CODEC_READ) {
    DEBUG("attempt to write from read codec\n");
    return -1;
  }

  DEBUG("write (have %llu bytes)\n", (unsigned long long)bytes);

  if (codec->stream.fd >= 0)
    return write(codec->stream.fd, buffer, bytes);

#ifndef _WIN32
  pthread_mutex_lock(&codec->data_mutex);
#endif
  while (bytes) {
    size_t todo = bytes;
    size_t remaining = codec->stream.end - codec->stream.ptr;

    if (!remaining) {
      if (codec->seekable && codec->stream.fd < 0) {
        /* In this case, we maintain the stream buffer ourselves */
        size_t old_size = codec->stream.top - codec->stream.buffer;
        size_t new_size = (old_size + bytes + 65535) & ~65535;
        UINT8 *new = (UINT8 *)realloc(codec->stream.buffer, new_size);

        if (!new) {
          codec->state->errcode = IMAGING_CODEC_MEMORY;
#ifndef _WIN32
          pthread_mutex_unlock(&codec->data_mutex);
#endif
          return done == 0 ? -1 : done;
        }

        codec->stream.ptr = codec->stream.ptr - codec->stream.buffer + new;
        codec->stream.buffer = new;
        codec->stream.end = new + new_size;
        codec->stream.top = new + old_size;
      } else {
        DEBUG("waiting for space\n");

#ifndef _WIN32
        pthread_mutex_lock(&codec->codec_mutex);
#endif
        codec->result = (int)(codec->stream.ptr - codec->stream.buffer);
#if _WIN32
        SetEvent(codec->hCodecEvent);
        WaitForSingleObject(codec->hDataEvent, INFINITE);
#else
        pthread_cond_signal(&codec->codec_cond);
        pthread_mutex_unlock(&codec->codec_mutex);
        pthread_cond_wait(&codec->data_cond, &codec->data_mutex);
#endif
      }

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

  if (codec->stream.ptr > codec->stream.top)
    codec->stream.top = codec->stream.ptr;

#ifndef _WIN32
  pthread_mutex_unlock(&codec->data_mutex);
#endif

  DEBUG("wrote total %llu bytes\n", (unsigned long long)done);

  return done;
}

off_t
ImagingIncrementalCodecSeek(ImagingIncrementalCodec codec,
                            off_t bytes)
{
  off_t buffered;

  DEBUG("seeking (going to %llu bytes)\n", (unsigned long long)bytes);

  if (codec->stream.fd >= 0)
    return lseek(codec->stream.fd, bytes, SEEK_SET);

  if (!codec->seekable) {
    DEBUG("attempt to seek non-seekable stream\n");
    return -1;
  }

  if (bytes < 0) {
    DEBUG("attempt to seek before stream start\n");
    return -1;
  }
    
  buffered = codec->stream.top - codec->stream.buffer;

  if (bytes <= buffered) {
    DEBUG("seek within buffer\n");
    codec->stream.ptr = codec->stream.buffer + bytes;
    return bytes;
  }

  return buffered + ImagingIncrementalCodecSkip(codec, bytes - buffered);
}
