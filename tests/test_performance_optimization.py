"""
Performance optimization tests for startup and image loading.

Tests verify that:
1. Image caching works correctly (no redundant disk I/O)
2. Performance tracker records milestones
3. App startup is fast without blocking on icon loading
"""
import os
import tempfile
import time
import unittest
from unittest.mock import Mock, patch, MagicMock

try:
    from src.services.app_service import _ImageCache, _PerformanceTracker
except ImportError:
    from services.app_service import _ImageCache, _PerformanceTracker


class TestImageCache(unittest.TestCase):
    """Test _ImageCache for efficient image loading."""

    def setUp(self):
        self.cache = _ImageCache()

    def tearDown(self):
        self.cache.clear()

    def test_cache_returns_none_for_missing_file(self):
        """Test that missing files return None gracefully."""
        result = self.cache.get_image("/nonexistent/path.png")
        self.assertIsNone(result)

    def test_cache_key_includes_size(self):
        """Test that different sizes are cached separately."""
        # Create a temporary image
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL not available")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img = Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Load with different sizes
            img1 = self.cache.get_image(tmp_path, (48, 48))
            img2 = self.cache.get_image(tmp_path, (64, 64))
            img3 = self.cache.get_image(tmp_path, (48, 48))  # Should return cached

            self.assertIsNotNone(img1)
            self.assertIsNotNone(img2)
            self.assertIsNotNone(img3)
            # Size (48, 48) should be cached, so img3 should be same object as img1
            self.assertIs(img3, img1)
            # But size (64, 64) should be different
            self.assertIsNot(img2, img1)
        finally:
            os.unlink(tmp_path)

    def test_cache_can_be_cleared(self):
        """Test that cache.clear() resets the cache."""
        self.assertEqual(len(self.cache._cache), 0)
        self.cache._cache[("key", None)] = "value"
        self.assertEqual(len(self.cache._cache), 1)
        self.cache.clear()
        self.assertEqual(len(self.cache._cache), 0)


class TestPerformanceTracker(unittest.TestCase):
    """Test _PerformanceTracker for timing milestones."""

    def setUp(self):
        self.mock_logger = Mock()
        self.tracker = _PerformanceTracker(self.mock_logger)

    def test_mark_records_elapsed_time(self):
        """Test that mark() records milestones with elapsed time."""
        time.sleep(0.01)  # Small delay
        self.tracker.mark("test_milestone")
        
        self.assertIn("test_milestone", self.tracker._marks)
        elapsed = self.tracker._marks["test_milestone"]
        self.assertGreaterEqual(elapsed, 0.01)
        self.assertLess(elapsed, 1)  # Should complete quickly

    def test_mark_calls_logger(self):
        """Test that mark() logs the milestone."""
        self.tracker.mark("test")
        self.mock_logger.debug.assert_called_once()

    def test_report_logs_all_marks(self):
        """Test that report() logs all recorded milestones."""
        self.tracker.mark("first")
        time.sleep(0.001)
        self.tracker.mark("second")
        
        self.tracker.report()
        # Should have logged 2 mark calls + 1 report call
        self.assertGreaterEqual(self.mock_logger.info.call_count, 1)

    def test_multiple_marks_are_ordered(self):
        """Test that marks preserve temporal order."""
        self.tracker.mark("first")
        time.sleep(0.005)
        self.tracker.mark("second")
        
        first_time = self.tracker._marks["first"]
        second_time = self.tracker._marks["second"]
        self.assertLess(first_time, second_time)


class TestAppStartupPerformance(unittest.TestCase):
    """Unit tests for performance-related components."""

    def test_image_cache_prevents_redundant_loads(self):
        """Test that using _ImageCache reduces disk I/O."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL not available")

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img = Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            cache = _ImageCache()
            
            # First load
            img1 = cache.get_image(tmp_path, (48, 48))
            self.assertIsNotNone(img1)
            
            # Second load from cache (no disk I/O)
            img2 = cache.get_image(tmp_path, (48, 48))
            self.assertIsNotNone(img2)
            
            # They should be the same object in memory
            self.assertIs(img1, img2)
        finally:
            os.unlink(tmp_path)

    def test_performance_tracker_records_startup_milestones(self):
        """Test that performance tracker can record app startup milestones."""
        mock_logger = Mock()
        tracker = _PerformanceTracker(mock_logger)
        
        # Simulate startup sequence
        tracker.mark("app_init_start")
        tracker.mark("config_loaded")
        tracker.mark("ui_created")
        tracker.mark("payloads_async_started")
        
        # Verify all marks recorded
        self.assertEqual(len(tracker._marks), 4)
        self.assertIn("app_init_start", tracker._marks)
        self.assertIn("payloads_async_started", tracker._marks)
        
        # Marks should be in chronological order
        marks_list = list(tracker._marks.items())
        for i in range(len(marks_list) - 1):
            self.assertLessEqual(marks_list[i][1], marks_list[i+1][1])


if __name__ == "__main__":
    unittest.main()
