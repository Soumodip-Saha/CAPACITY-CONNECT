class UniversalRow:
    def __init__(self, values_list, columns_map):
        self._values = list(values_list)
        self._map = {col.lower(): i for i, col in enumerate(columns_map)}
        self._columns = list(columns_map)

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._values[key]
        if isinstance(key, str):
            idx = self._map.get(key.lower())
            if idx is not None:
                return self._values[idx]
            raise KeyError(key)
        raise TypeError(f"Row indices must be integers or strings, not {type(key)}")

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def keys(self):
        return self._columns

    def items(self):
        return zip(self._columns, self._values)

    def __iter__(self):
        return iter(self._columns)

    def __len__(self):
        return len(self._values)

row = UniversalRow([5, "test@imd.gov.in"], ["count", "email"])
print("row[0]:", row[0])
print("row['count']:", row["count"])
print("dict(row):", dict(row))
print("dict(row.items()):", dict(row.items()))
