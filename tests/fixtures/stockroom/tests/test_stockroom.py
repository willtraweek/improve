import unittest

from stockroom import Inventory


class InventoryTests(unittest.TestCase):
    def test_reserves_stock(self):
        inventory = Inventory({"tea": 5})
        self.assertEqual(inventory.reserve("tea", 2), 3)

    def test_insufficient_stock_does_not_mutate_inventory(self):
        inventory = Inventory({"tea": 5})
        with self.assertRaises(ValueError):
            inventory.reserve("tea", 6)
        self.assertEqual(inventory.available("tea"), 5)

    def test_preview_does_not_mutate_inventory(self):
        inventory = Inventory({"tea": 5})
        self.assertEqual(inventory.reserve("tea", 0), 5)
        self.assertEqual(inventory.available("tea"), 5)
