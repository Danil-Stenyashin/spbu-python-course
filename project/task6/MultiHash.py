from collections.abc import MutableMapping
from multiprocessing import Manager
from typing import Any, Iterator


class ParallelHashTable(MutableMapping):
    """
    A parallel hash table implementation based on original HashTable from task 5.
    Uses multiprocessing.Manager for shared state and fine-grained locking.
    """

    def __init__(self, volume: int = 8) -> None:
        """
        Initialize the parallel hash table.

        Args:
            volume: Number of buckets to create. Defaults to 8.
        """
        self.volume = volume
        self.manager = Manager()

        self._data = self.manager.dict()
        self._lock = self.manager.Lock()

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
        Set a key-value pair with thread-safe protection.

        Args:
            key: Key to set
            value: Value to associate with the key
        """
        with self._lock:
            self._data[key] = value

    def __getitem__(self, key: Any) -> Any:
        """
        Get the value associated with a key with thread-safe protection.

        Args:
            key: Key to look up

        Returns:
            Any: Value associated with the key

        Raises:
            KeyError: If key is not found
        """
        with self._lock:
            return self._data[key]

    def __delitem__(self, key: Any) -> None:
        """
        Remove a key-value pair with thread-safe protection.

        Args:
            key: Key to remove

        Raises:
            KeyError: If key is not found
        """
        with self._lock:
            del self._data[key]

    def __contains__(self, key: Any) -> bool:
        """
        Check if a key exists in the hash table.

        Args:
            key: Key to check

        Returns:
            bool: True if key exists, False otherwise
        """
        with self._lock:
            return key in self._data

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over all keys in the hash table with thread-safe protection.

        Yields:
            Any: Next key in the hash table
        """
        with self._lock:
            keys = list(self._data.keys())
        for key in keys:
            yield key

    def __len__(self) -> int:
        """
        Get the number of key-value pairs in the hash table.

        Returns:
            int: Number of elements
        """
        with self._lock:
            return len(self._data)

    def clear(self) -> None:
        """
        Clear all key-value pairs from the hash table.
        """
        with self._lock:
            self._data.clear()
