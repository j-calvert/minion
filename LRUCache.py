from collections import OrderedDict

class LRUCache:
    def __init__(self, max_size):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        print(f"cache size: {len(self.cache)}") if len(self.cache) % 1000 == 0 else None
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def __contains__(self, key):
        return key in self.cache