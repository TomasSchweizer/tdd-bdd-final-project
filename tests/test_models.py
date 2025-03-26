# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a Product"""
        # Create a fake product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Read the product
        read_product = Product.find(product.id)
        self.assertIsNotNone(read_product)
        for attr in vars(read_product):
            self.assertEqual(getattr(read_product, attr), getattr(product, attr))

    def test_update_a_product(self):
        """It should update a Product"""

        # Create a fake product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Update description property
        product.description = "This is an updated description."
        product.update()

        # Fetch product and check if updated
        updated_product = Product.find(product.id)
        self.assertIsNotNone(updated_product)
        for attr in vars(updated_product):
            self.assertEqual(getattr(updated_product, attr), getattr(product, attr))

        # Fetch all products and check if only one product
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)
        for attr in vars(all_products[0]):
            self.assertEqual(getattr(all_products[0], attr), getattr(product, attr))

    def test_update_empty_id(self):
        """It should not update a Product with empty id"""
        # Create a fake product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should delete a Product"""
        # Create a fake product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Fetch all products and check if only one product
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)

        # Delete the product
        product.delete()

        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

    def test_list_all_products(self):
        """It should list all products"""

        # Check that there are no products
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)
        self.assertEqual(all_products, [])

        # Add five products
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        # Check if there are five products
        all_products = Product.all()
        self.assertEqual(len(all_products), 5)

    def test_find_by_name(self):
        """It should return all Products with a given name"""

        # Create 5 fake products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        # Find name of first product
        first_product_name = products[0].name

        # Count the len of the number of different products with this name
        product_count = len([product for product in products if product.name == first_product_name])

        # Find products with the name of the first product
        found_products = Product.find_by_name(first_product_name)

        self.assertEqual(found_products.count(), product_count)
        for product in found_products:
            self.assertEqual(product.name, first_product_name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        price = products[0].price
        found_products = Product.find_by_price(price)
        for attr in vars(products[0]):
            self.assertEqual(getattr(found_products[0], attr), getattr(products[0], attr))

    def test_serialize(self):
        """It should serialize a Product into a dict"""
        # Create a fake product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Create dict
        product_dict = product.serialize()

        # Check dict vs product
        for key, values in product_dict.items():
            attr = getattr(product, key)
            if key == "price":
                attr = str(attr)
            if key == "category":
                attr = product.category.name

            self.assertEqual(product_dict[key], attr)

    def test_deserialize_available(self):
        """It should not deserialize if available is not bool"""

        product_dict = dict(name="Fedora",
                            description="A red hat",
                            price=12.50,
                            available="true",
                            category=Category.CLOTHS)

        prodcut = Product()
        with self.assertRaises(DataValidationError):
            prodcut.deserialize(product_dict)
