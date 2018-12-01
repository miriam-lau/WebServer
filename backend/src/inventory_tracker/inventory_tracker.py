from typing import Dict, List
import psycopg2


class InventoryTracker:
    def __init__(self, database):
        self._database = database
