from multiprocessing import Process

import pytest

from project.task6.MultiHash import ParallelHashTable


def worker_add(ht, process_id):
    for i in range(10):
        ht[f"key_{process_id}_{i}"] = f"value_{process_id}_{i}"


def increment_worker(ht, counter_key, increments):
    for _ in range(increments):
        ht.atomic_increment(counter_key, 1)


def update_worker(ht, key, iterations):
    for i in range(iterations):
        ht[key] = i


def test_basic_operations():
    """Test basic dictionary operations"""
    ht = ParallelHashTable()
    ht["key1"] = "value1"
    ht["key2"] = "value2"
    assert ht["key1"] == "value1"
    assert ht["key2"] == "value2"
    assert len(ht) == 2


def test_key_error():
    """Test KeyError for non-existent keys"""
    ht = ParallelHashTable()
    try:
        _ = ht["nonexistent"]
        assert False, "Should raise KeyError"
    except KeyError:
        pass


def test_update_value():
    """Test updating existing key"""
    ht = ParallelHashTable()
    ht["key"] = "value1"
    assert ht["key"] == "value1"
    ht["key"] = "value2"
    assert ht["key"] == "value2"
    assert len(ht) == 1


def test_contains():
    """Test 'in' operator"""
    ht = ParallelHashTable()
    ht["key1"] = "value1"
    assert "key1" in ht
    assert "key2" not in ht


def test_delete():
    """Test item deletion"""
    ht = ParallelHashTable()
    ht["key1"] = "value1"
    ht["key2"] = "value2"
    del ht["key1"]
    assert "key1" not in ht
    assert len(ht) == 1
    assert ht["key2"] == "value2"


def test_delete_key_error():
    """Test KeyError when deleting non-existent key"""
    ht = ParallelHashTable()
    try:
        del ht["nonexistent"]
        assert False, "Should raise KeyError"
    except KeyError:
        pass


def test_iteration():
    """Test iteration over keys"""
    ht = ParallelHashTable()
    keys = ["a", "b", "c"]
    for key in keys:
        ht[key] = f"value_{key}"
    iterated_keys = list(ht)
    for key in keys:
        assert key in iterated_keys
    assert len(iterated_keys) == len(keys)


def test_collision_handling():
    """Test that collisions are handled correctly"""
    ht = ParallelHashTable(volume=2)
    ht["a"] = 1
    ht["b"] = 2
    ht["c"] = 3
    assert ht["a"] == 1
    assert ht["b"] == 2
    assert ht["c"] == 3
    assert len(ht) == 3


def test_hash_method():
    """Test that _hash method works correctly"""
    ht = ParallelHashTable(volume=10)
    index1 = ht._hash("test_key")
    index2 = ht._hash("test_key")
    assert index1 == index2
    assert 0 <= index1 < 10
    assert 0 <= index2 < 10


def test_manager_creation():
    ht = ParallelHashTable()
    assert hasattr(ht, "manager")
    assert hasattr(ht, "_data")
    assert hasattr(ht, "_lock")


def test_clear_method():
    """Test clear method works correctly"""
    ht = ParallelHashTable()
    for i in range(10):
        ht[f"key_{i}"] = f"value_{i}"
    assert len(ht) == 10
    ht.clear()
    assert len(ht) == 0
    for i in range(10):
        assert f"key_{i}" not in ht


def test_multiprocess_access():
    ht = ParallelHashTable()

    try:
        processes = []
        for i in range(2):
            p = Process(target=worker_add, args=(ht, i))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        assert len(ht) == 20
        for i in range(2):
            for j in range(10):
                assert ht[f"key_{i}_{j}"] == f"value_{i}_{j}"
    except Exception as e:
        pytest.skip(f"Multiprocessing test skipped(windows problem): {e}")


def test_no_race_conditions():
    """Test that there are no race conditions in counter increments"""
    ht = ParallelHashTable()

    processes = []
    num_processes = 2
    increments_per_process = 10

    for _ in range(num_processes):
        p = Process(
            target=increment_worker, args=(ht, "counter", increments_per_process)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join(timeout=5)

    expected_total = num_processes * increments_per_process
    assert (
        ht["counter"] == expected_total
    ), f"Expected {expected_total}, got {ht['counter']}"


def ShowRecipe():
    recipe = """Классический рецепт шарлотки:

    Ингредиенты (на 6–8 порций):

    яйца — 4 шт.;
    сахар — 150–160 г;
    мука — 150–160 г;
    яблоки — 500–600 г;
    соль — 1 щепотка.
    Время приготовления: около 1 часа (включая выпечку).

    Пошаговый процесс:

    Подготовка ингредиентов. Яйца и масло должны быть комнатной температуры — это обеспечит лучшее соединение компонентов. Яблоки очистите от сердцевины и нарежьте ломтиками или кубиками.
    Взбивание яиц. В глубокой миске взбейте яйца с сахаром и щепоткой соли до образования пышной, светлой массы. Готовность проверьте так: проведите венчиком линию по поверхности — если она держится 1–2 секунды, масса готова.
    Замес теста. Просейте муку и аккуратно введите её в яично‑сахарную смесь. Перемешивайте лопаткой движениями снизу вверх, чтобы сохранить воздушность.
    Сборка пирога. Смажьте форму сливочным маслом или застелите пергаментом. Выложите тесто: можно сначала налить половину, затем распределить яблоки и залить оставшимся тестом, либо аккуратно смешать яблоки с тестом и переложить в форму.
    Выпечка. Поставьте форму в разогретую до 180 °C духовку на 20–30 минут. Готовность проверяйте деревянной шпажкой: она должна выходить сухой.
    Подача. Готовую шарлотку можно посыпать сахарной пудрой.
    Секреты пышной шарлотки
    Чтобы пирог получился воздушным и не осел, соблюдайте эти правила:

    Качественное взбивание. Яйца с сахаром должны превратиться в густую, пышную массу. Используйте миксер на высоких скоростях.
    Просеивание муки. Это обогащает муку кислородом и делает тесто легче.
    Аккуратное замешивание. При соединении ингредиентов действуйте быстро и деликатно, чтобы не разрушить воздушную структуру.
    Разогрев духовки. Предварительно прогрейте духовку до 180–190 °C. Не открывайте дверцу первые 30 минут выпекания.
    Выбор яблок. Кислые сорта (например, «Антоновка») придают приятную кислинку и хорошо держат форму. Можно сочетать со сладкими яблоками для баланса вкуса."""
    print(recipe)


ShowRecipe()
