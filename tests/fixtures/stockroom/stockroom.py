class Inventory:
    def __init__(self, quantities):
        self._quantities = dict(quantities)

    def available(self, sku):
        return self._quantities[sku]

    def reserve(self, sku, quantity):
        current = self._quantities[sku]
        if quantity > current:
            raise ValueError("Insufficient stock")
        self._quantities[sku] = current - quantity
        return self._quantities[sku]
