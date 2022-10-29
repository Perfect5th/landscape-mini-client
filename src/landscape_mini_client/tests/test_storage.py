import os.path
import pickle
import tempfile
from unittest import TestCase

from .. import storage


class PutTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def test_put(self):
        """Tests that put creates a pickle file."""
        tempfile = os.path.join(self.tempdir.name, "test_put.pickle")
        self.assertFalse(os.path.exists(tempfile))

        storage.put({"test": "item"}, tempfile)

        self.assertTrue(os.path.exists(tempfile))

        with open(tempfile, "rb") as fp:
            self.assertEqual({"test": "item"}, pickle.load(fp))

    def test_put_exists_empty(self):
        """
        Tests that put adds items to an existing, empty pickle file.
        """
        tempfile = os.path.join(self.tempdir.name,
                                "test_put_exists_empty.pickle")

        with open(tempfile, "w"):
            pass

        self.assertTrue(os.path.exists(tempfile))

        storage.put({"test": "item"}, tempfile)

        with open(tempfile, "rb") as fp:
            self.assertEqual({"test": "item"}, pickle.load(fp))

    def test_put_exists(self):
        """
        Tests that put adds items to an existing, non-empty pickle file.
        """
        tempfile = os.path.join(self.tempdir.name, "test_put_exists.pickle")

        with open(tempfile, "wb") as fp:
            pickle.dump({"prexisting": "thing"}, fp)

        storage.put({"test": "item"}, tempfile)

        with open(tempfile, "rb") as fp:
            result = pickle.load(fp)

        self.assertEqual({"test": "item", "prexisting": "thing"}, result)


class GetTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

    def test_get(self):
        """
        Tests that get returns an item when it exists in the pickle
        file.
        """
        tempfile = os.path.join(self.tempdir.name, "test_get.pickle")

        with open(tempfile, "wb") as fp:
            pickle.dump({"test": "item"}, fp)

        result = storage.get("test", tempfile)

        self.assertEqual(result, "item")

    def test_get_not_in_file(self):
        """
        Tests that get returns None when the item does not exist in the
        pickle file.
        """
        tempfile = os.path.join(self.tempdir.name,
                                "test_get_not_in_file.pickle")

        with open(tempfile, "wb") as fp:
            pickle.dump({"test": "item"}, fp)

        result = storage.get("nonexistent", tempfile)

        self.assertIsNone(result)

    def test_get_no_file(self):
        """
        Tests that get returns None when the pickle file does not exist.
        """
        tempfile = os.path.join(self.tempdir.name, "test_get_no_file.pickle")
        
        result = storage.get("test", tempfile)

        self.assertIsNone(result)
