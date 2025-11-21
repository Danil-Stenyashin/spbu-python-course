from collections.abc import MutableMapping
from multiprocessing import Manager
from typing import Any, Iterator


class ParallelHashTable(MutableMapping):
    """
    A parallel hash table implementation based on original HashTable from task 5.
    Uses separate chaining with fine-grained locking.
    """

    def __init__(self, volume: int = 8) -> None:
        """
        Initialize the parallel hash table.

        Args:
            volume: Number of buckets to create. Defaults to 8.
        """
        self.volume = volume
        self.manager = Manager()

        self.buckets = self.manager.list([self.manager.list() for _ in range(volume)])
        self.size = self.manager.Value("i", 0)

        self.locks = [self.manager.Lock() for _ in range(volume)]

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

        with self.locks[index]:
            bucket = self.buckets[index]

            # Оригинальная логика из твоей хэш-таблицы
            for i in range(len(bucket)):
                k, v = bucket[i]
                if k == key:
                    bucket[i] = (key, value)
                    return

            bucket.append((key, value))
            self.size.value += 1

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

        with self.locks[index]:
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

        with self.locks[index]:
            bucket = self.buckets[index]

            for i in range(len(bucket)):
                k, v = bucket[i]
                if k == key:
                    del bucket[i]
                    self.size.value -= 1
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

        with self.locks[index]:
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
        for lock in self.locks:
            lock.acquire()

        try:
            for bucket in self.buckets:
                for item in bucket:
                    k, v = item
                    yield k
        finally:
            for lock in self.locks:
                lock.release()

    def __len__(self) -> int:
        """
        Get the number of key-value pairs in the hash table.

        Returns:
            int: Number of elements
        """
        return self.size.value

    def clear(self) -> None:
        """
        Clear all key-value pairs from the hash table.
        """
        for i in range(self.volume):
            with self.locks[i]:
                self.buckets[i][:] = []
        self.size.value = 0
