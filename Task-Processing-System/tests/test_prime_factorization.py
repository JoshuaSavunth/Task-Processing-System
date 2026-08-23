import tasks

def test_prime_factorization_basic():
    assert tasks.prime_factorization(84) == [2, 2, 3, 7]

def test_prime_factorization_edge_cases():
    assert tasks.prime_factorization(1) == []
    assert tasks.prime_factorization(2) == [2]

def test_prime_factorization_composite():
    assert tasks.prime_factorization(99) == [3, 3, 11]
