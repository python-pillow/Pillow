from __future__ import division, print_function

import sys

from helper import unittest, PillowTestCase
from PIL import Image


is_pypy = hasattr(sys, 'pypy_version_info')


class TestCoreStats(PillowTestCase):
    def test_get_stats(self):
        # Create at least one image
        Image.new('RGB', (10, 10))

        stats = Image.core.get_stats()
        self.assertIn('new_count', stats)
        self.assertIn('reused_blocks', stats)
        self.assertIn('freed_blocks', stats)
        self.assertIn('allocated_blocks', stats)
        self.assertIn('reallocated_blocks', stats)
        self.assertIn('blocks_cached', stats)

    def test_reset_stats(self):
        Image.core.reset_stats()

        stats = Image.core.get_stats()
        self.assertEqual(stats['new_count'], 0)
        self.assertEqual(stats['reused_blocks'], 0)
        self.assertEqual(stats['freed_blocks'], 0)
        self.assertEqual(stats['allocated_blocks'], 0)
        self.assertEqual(stats['reallocated_blocks'], 0)
        self.assertEqual(stats['blocks_cached'], 0)


class TestCoreMemory(PillowTestCase):
    def tearDown(self):
        # Restore default values
        Image.core.set_alignment(1)
        Image.core.set_block_size(1024*1024)
        Image.core.set_blocks_max(0)
        Image.core.clear_cache()

    def test_get_alignment(self):
        alignment = Image.core.get_alignment()

        self.assertGreater(alignment, 0)

    def test_set_alignment(self):
        for i in [1, 2, 4, 8, 16, 32]:
            Image.core.set_alignment(i)
            alignment = Image.core.get_alignment()
            self.assertEqual(alignment, i)

            # Try to construct new image
            Image.new('RGB', (10, 10))

        self.assertRaises(ValueError, Image.core.set_alignment, 0)
        self.assertRaises(ValueError, Image.core.set_alignment, -1)
        self.assertRaises(ValueError, Image.core.set_alignment, 3)

    def test_get_block_size(self):
        block_size = Image.core.get_block_size()

        self.assertGreaterEqual(block_size, 4096)

    def test_set_block_size(self):
        for i in [4096, 2*4096, 3*4096]:
            Image.core.set_block_size(i)
            block_size = Image.core.get_block_size()
            self.assertEqual(block_size, i)

            # Try to construct new image
            Image.new('RGB', (10, 10))

        self.assertRaises(ValueError, Image.core.set_block_size, 0)
        self.assertRaises(ValueError, Image.core.set_block_size, -1)
        self.assertRaises(ValueError, Image.core.set_block_size, 4000)

    def test_set_block_size_stats(self):
        Image.core.reset_stats()
        Image.core.set_blocks_max(0)
        Image.core.set_block_size(4096)
        Image.new('RGB', (256, 256))

        stats = Image.core.get_stats()
        self.assertGreaterEqual(stats['new_count'], 1)
        self.assertGreaterEqual(stats['allocated_blocks'], 64)
        if not is_pypy:
            self.assertGreaterEqual(stats['freed_blocks'], 64)

    def test_get_blocks_max(self):
        blocks_max = Image.core.get_blocks_max()

        self.assertGreaterEqual(blocks_max, 0)

    def test_set_blocks_max(self):
        for i in [0, 1, 10]:
            Image.core.set_blocks_max(i)
            blocks_max = Image.core.get_blocks_max()
            self.assertEqual(blocks_max, i)

            # Try to construct new image
            Image.new('RGB', (10, 10))

        self.assertRaises(ValueError, Image.core.set_blocks_max, -1)

    @unittest.skipIf(is_pypy, "images are not collected")
    def test_set_blocks_max_stats(self):
        Image.core.reset_stats()
        Image.core.set_blocks_max(128)
        Image.core.set_block_size(4096)
        Image.new('RGB', (256, 256))
        Image.new('RGB', (256, 256))

        stats = Image.core.get_stats()
        self.assertGreaterEqual(stats['new_count'], 2)
        self.assertGreaterEqual(stats['allocated_blocks'], 64)
        self.assertGreaterEqual(stats['reused_blocks'], 64)
        self.assertEqual(stats['freed_blocks'], 0)
        self.assertEqual(stats['blocks_cached'], 64)

    @unittest.skipIf(is_pypy, "images are not collected")
    def test_clear_cache_stats(self):
        Image.core.reset_stats()
        Image.core.clear_cache()
        Image.core.set_blocks_max(128)
        Image.core.set_block_size(4096)
        Image.new('RGB', (256, 256))
        Image.new('RGB', (256, 256))
        # Keep 16 blocks in cache
        Image.core.clear_cache(16)

        stats = Image.core.get_stats()
        self.assertGreaterEqual(stats['new_count'], 2)
        self.assertGreaterEqual(stats['allocated_blocks'], 64)
        self.assertGreaterEqual(stats['reused_blocks'], 64)
        self.assertGreaterEqual(stats['freed_blocks'], 48)
        self.assertEqual(stats['blocks_cached'], 16)

    def test_large_images(self):
        Image.core.reset_stats()
        Image.core.set_blocks_max(0)
        Image.core.set_block_size(4096)
        Image.new('RGB', (2048, 16))
        Image.core.clear_cache()

        stats = Image.core.get_stats()
        self.assertGreaterEqual(stats['new_count'], 1)
        self.assertGreaterEqual(stats['allocated_blocks'], 16)
        self.assertGreaterEqual(stats['reused_blocks'], 0)
        self.assertEqual(stats['blocks_cached'], 0)
        if not is_pypy:
            self.assertGreaterEqual(stats['freed_blocks'], 16)


class TestEnvVars(PillowTestCase):
    def tearDown(self):
        # Restore default values
        Image.core.set_alignment(1)
        Image.core.set_block_size(1024*1024)
        Image.core.set_blocks_max(0)
        Image.core.clear_cache()

    def test_units(self):
        Image._apply_env_variables({'PILLOW_BLOCKS_MAX': '2K'})
        self.assertEqual(Image.core.get_blocks_max(), 2*1024)
        Image._apply_env_variables({'PILLOW_BLOCK_SIZE': '2m'})
        self.assertEqual(Image.core.get_block_size(), 2*1024*1024)

    def test_warnings(self):
        self.assert_warning(
            UserWarning, Image._apply_env_variables,
            {'PILLOW_ALIGNMENT': '15'})
        self.assert_warning(
            UserWarning, Image._apply_env_variables,
            {'PILLOW_BLOCK_SIZE': '1024'})
        self.assert_warning(
            UserWarning, Image._apply_env_variables,
            {'PILLOW_BLOCKS_MAX': 'wat'})
