#!/usr/bin/python3
"""Contains the TestDBStorageDocs and TestDBStorage classes"""
from datetime import datetime
import inspect
import models
from models.engine import db_storage
from models.amenity import Amenity
from models.base_model import BaseModel
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
import json
import os
import pep8  # type: ignore
import unittest
DBStorage = db_storage.DBStorage
classes = {"Amenity": Amenity, "City": City, "Place": Place,
           "Review": Review, "State": State, "User": User}


class TestDBStorageDocs(unittest.TestCase):
    """Tests to check the documentation and style of DBStorage class"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.dbs_f = inspect.getmembers(DBStorage, inspect.isfunction)

    def test_pep8_conformance_db_storage(self):
        """Test that models/engine/db_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['models/engine/db_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_db_storage(self):
        """Test tests/test_models/test_db_storage.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['tests/test_models/test_engine/\
test_db_storage.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_db_storage_module_docstring(self):
        """Test for the db_storage.py module docstring"""
        self.assertIsNot(db_storage.__doc__, None,
                         "db_storage.py needs a docstring")
        self.assertTrue(len(db_storage.__doc__) >= 1,
                        "db_storage.py needs a docstring")

    def test_db_storage_class_docstring(self):
        """Test for the DBStorage class docstring"""
        self.assertIsNot(DBStorage.__doc__, None,
                         "DBStorage class needs a docstring")
        self.assertTrue(len(DBStorage.__doc__) >= 1,
                        "DBStorage class needs a docstring")

    def test_dbs_func_docstrings(self):
        """Test for the presence of docstrings in DBStorage methods"""
        for func in self.dbs_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestDBStorage(unittest.TestCase):
    """Test the FileStorage class"""
    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_all_returns_dict(self):
        """Test that all returns a dictionaty"""
        self.assertIs(type(models.storage.all()), dict)

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_all_no_class(self):
        """Test that all returns all rows when no class is passed"""
        storage = DBStorage()
        initial_count = len(storage.all())
        new_state = State(name="California")
        storage.new(new_state)
        storage.save()
        self.assertEqual(len(storage.all()), initial_count + 1)
        storage.delete(new_state)
        storage.save()

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_new(self):
        """test that new adds an object to the database"""
        storage = DBStorage()
        new_state = State(name="California")
        storage.new(new_state)
        self.assertIn(new_state, storage.all().values())

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_save(self):
        """Test that save properly saves objects to file.json"""
        storage = DBStorage()
        new_state = State(name="California")
        storage.new(new_state)
        storage.save()
        storage.reload()
        self.assertIn(new_state.id, [obj.id for obj in storage.all(State).values()])
        storage.delete(new_state)
        storage.save()

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_delete(self):
        """Test that delete removes an object from the database"""
        storage = DBStorage()
        new_state = State(name="California")
        storage.new(new_state)
        storage.save()
        storage.delete(new_state)
        storage.save()
        self.assertIsNone(storage.get(State, new_state.id))

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_reload(self):
        """Test that reload loads objects from the database"""
        storage = DBStorage()
        storage.reload()
        all_objs = storage.all()
        self.assertIsInstance(all_objs, dict)

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_close(self):
        """Test that close removes the session"""
        storage = DBStorage()
        storage.reload()
        storage.close()
        self.assertIsNone(storage._DBStorage__session.registry().session())

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_get(self):
        """Test that get returns the correct object or None"""
        storage = DBStorage()
        new_state = State(name="California")
        storage.new(new_state)
        storage.save()
        self.assertEqual(storage.get(State, new_state.id), new_state)
        self.assertIsNone(storage.get(State, "nonexistent_id"))
        storage.delete(new_state)
        storage.save()

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_count(self):
        """Test that count returns the correct number of objects"""
        storage = DBStorage()
        initial_count = storage.count(State)
        new_state1 = State(name="California")
        new_state2 = State(name="Nevada")
        storage.new(new_state1)
        storage.new(new_state2)
        storage.save()
        self.assertEqual(storage.count(State), initial_count + 2)
        self.assertEqual(storage.count(City), 0)
        storage.delete(new_state1)
        storage.delete(new_state2)
        storage.save()

    @unittest.skipIf(models.storage_t != 'db', "not testing db storage")
    def test_count_all(self):
        """Test that count returns the correct total number of objects"""
        storage = DBStorage()
        initial_count = storage.count()
        new_state1 = State(name="California")
        new_city = City(name="San Francisco", state_id=new_state1.id)
        storage.new(new_state1)
        storage.new(new_city)
        storage.save()
        self.assertEqual(storage.count(), initial_count + 2)
        storage.delete(new_state1)
        storage.delete(new_city)
        storage.save()
