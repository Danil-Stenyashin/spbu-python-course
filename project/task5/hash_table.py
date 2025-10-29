from collections.abc import MutableMapping
from typing import Any, Iterator, List, Tuple


class HashTable(MutableMapping):
    """
    A hash table implementation using separate chaining for collision resolution.
    """

    def __init__(self, volume: int = 8) -> None:
        """
        Initialize the hash table.

        Args:
            volume: Number of buckets to create. Defaults to 8.
        """
        self.volume = volume
        self.size = 0
        self.buckets: List[List[Tuple[Any, Any]]] = [[] for _ in range(volume)]

    def _hash(self, key: Any) -> int:
        """
        Compute the bucket index for a given key.

        Args:
            key: Key to hash

        Returns:
            int: Bucket index between 0 and volume-1
        """
        return hash(key) % self.volume

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set a key-value pair in the hash table.

        Args:
            key: Key to set
            value: Value to associate with the key
        """
        index = self._hash(key)
        bucket = self.buckets[index]

        for i in range(len(bucket)):
            k, v = bucket[i]
            if k == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.size += 1

    def __getitem__(self, key: Any) -> Any:
        """
        Get the value associated with a key.

        Args:
            key: Key to look up

        Returns:
            Any: Value associated with the key

        Raises:
            KeyError: If key is not found
        """
        index = self._hash(key)
        bucket = self.buckets[index]

        for item in bucket:
            k, v = item
            if k == key:
                return v

        raise KeyError("Key not found: {0}".format(key))

    def __delitem__(self, key: Any) -> None:
        """
        Remove a key-value pair from the hash table.

        Args:
            key: Key to remove

        Raises:
            KeyError: If key is not found
        """
        index = self._hash(key)
        bucket = self.buckets[index]

        for i in range(len(bucket)):
            k, v = bucket[i]
            if k == key:
                del bucket[i]
                self.size -= 1
                return

        raise KeyError("Key not found: {0}".format(key))

    def __contains__(self, key: Any) -> bool:
        """
        Check if a key exists in the hash table.

        Args:
            key: Key to check

        Returns:
            bool: True if key exists, False otherwise
        """
        index = self._hash(key)
        bucket = self.buckets[index]

        for item in bucket:
            k, v = item
            if k == key:
                return True
        return False

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over all keys in the hash table.

        Yields:
            Any: Next key in the hash table
        """
        for bucket in self.buckets:
            for item in bucket:
                k, v = item
                yield k

    def __len__(self) -> int:
        """
        Get the number of key-value pairs in the hash table.

        Returns:
            int: Number of elements
        """
        return self.size
