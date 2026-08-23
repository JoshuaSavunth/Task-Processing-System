def prime_factorization(n: int) -> list[int]:
    if n < 2:
        raise ValueError("n must be at least 2")
    factors: list[int] = []
    divisor = 2
    remaining = n
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.append(divisor)
            remaining //= divisor
        divisor += 1 if divisor == 2 else 2
    if remaining > 1:
        factors.append(remaining)
    return factors