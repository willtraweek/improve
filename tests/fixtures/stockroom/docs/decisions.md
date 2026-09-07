# Decisions

Zero-unit reservations intentionally return current stock without mutation.
The kiosk uses this as a preview operation. Keep that behavior.

The inventory belongs to one process and is not shared across threads. A
database, transaction layer, and HTTP API are outside the product's scope.
