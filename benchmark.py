import random
from fractions import Fraction

from inverse_matrix import (determinant, inverse_by_determinant,
                            inverse_by_gauss_jordan, measure_time)

random.seed(3)
print(" n | 행렬식(ms) | 가우스-조던(ms) |   배율")
print("---+------------+-----------------+--------")
for n in range(2, 8):
    while True:
        a = [[Fraction(random.randint(-5, 5)) for _ in range(n)]
             for _ in range(n)]
        if determinant(a) != 0:
            break
    repeat = 20 if n <= 5 else 3
    t_det = measure_time(inverse_by_determinant, a, repeat)
    t_gj = measure_time(inverse_by_gauss_jordan, a, repeat)
    print(f"{n:2d} | {t_det:10.3f} | {t_gj:15.3f} | {t_det / t_gj:5.1f}배")
