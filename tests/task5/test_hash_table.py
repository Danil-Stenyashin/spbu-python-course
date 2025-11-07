from project.task5.hash_table import HashTable


def test_basic_operations():
    """Test basic dictionary operations"""
    ht = HashTable()

    ht["key1"] = "value1"
    ht["key2"] = "value2"

    assert ht["key1"] == "value1"
    assert ht["key2"] == "value2"
    assert len(ht) == 2


def test_key_error():
    """Test KeyError for non-existent keys"""
    ht = HashTable()

    try:
        _ = ht["nonexistent"]
        assert False, "Should raise KeyError"
    except KeyError:
        pass


def test_update_value():
    """Test updating existing key"""
    ht = HashTable()

    ht["key"] = "value1"
    assert ht["key"] == "value1"

    ht["key"] = "value2"
    assert ht["key"] == "value2"
    assert len(ht) == 1


def test_contains():
    """Test 'in' operator"""
    ht = HashTable()

    ht["key1"] = "value1"

    assert "key1" in ht
    assert "key2" not in ht


def test_delete():
    """Test item deletion"""
    ht = HashTable()

    ht["key1"] = "value1"
    ht["key2"] = "value2"

    del ht["key1"]
    assert "key1" not in ht
    assert len(ht) == 1
    assert ht["key2"] == "value2"


def test_delete_key_error():
    """Test KeyError when deleting non-existent key"""
    ht = HashTable()

    try:
        del ht["nonexistent"]
        assert False, "Should raise KeyError"
    except KeyError:
        pass


def test_iteration():
    """Test iteration over keys"""
    ht = HashTable()

    keys = ["a", "b", "c"]
    for key in keys:
        ht[key] = f"value_{key}"

    iterated_keys = list(ht)
    for key in keys:
        assert key in iterated_keys

    assert len(iterated_keys) == len(keys)


def test_collision_handling():
    """Test that collisions are handled correctly"""
    ht = HashTable(volume=2)

    ht["a"] = 1
    ht["b"] = 2
    ht["c"] = 3

    assert ht["a"] == 1
    assert ht["b"] == 2
    assert ht["c"] == 3
    assert len(ht) == 3
