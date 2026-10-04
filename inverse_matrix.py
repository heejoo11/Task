from fractions import Fraction
import time

LINE = "-" * 60


class SingularMatrixError(Exception):
    pass


def read_size():
    while True:
        text = input("행렬의 크기 n을 입력하세요 (n x n): ").strip()
        try:
            n = int(text)
        except ValueError:
            print("  [입력 오류] n은 정수여야 합니다. 다시 입력하세요.")
            continue
        if n < 1:
            print("  [입력 오류] n은 1 이상이어야 합니다. 다시 입력하세요.")
            continue
        return n


def read_matrix(n):
    print(f"{n} x {n} 행렬을 한 행씩 입력하세요. (원소는 공백으로 구분)")
    matrix = []
    for i in range(n):
        while True:
            tokens = input(f"  {i + 1}행: ").split()
            if len(tokens) != n:
                print(f"  [입력 오류] 원소가 {n}개여야 합니다. "
                      f"(입력된 개수: {len(tokens)})")
                continue
            try:
                row = [Fraction(t) for t in tokens]
            except (ValueError, ZeroDivisionError):
                print("  [입력 오류] 숫자만 입력하세요. (예: 3  -1.5  2/3)")
                continue
            matrix.append(row)
            break
    return matrix


def ask_yes_no(message):
    while True:
        answer = input(message).strip().lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("  [입력 오류] y 또는 n 으로 입력하세요.")


def format_rows(cells, bar=None):
    widths = [max(len(row[j]) for row in cells) for j in range(len(cells[0]))]
    lines = []
    for row in cells:
        parts = [row[j].rjust(widths[j]) for j in range(len(row))]
        if bar is not None:
            parts.insert(bar, "|")
        lines.append("[ " + "  ".join(parts) + " ]")
    return lines


def print_matrix(matrix, indent="    ", bar=None):
    cells = [[str(x) for x in row] for row in matrix]
    for line in format_rows(cells, bar):
        print(indent + line)


def print_matrix_decimal(matrix, indent="    ", digits=4):
    cells = [[f"{float(x):.{digits}f}" for x in row] for row in matrix]
    for line in format_rows(cells):
        print(indent + line)


def identity(n):
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def multiply(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
            for i in range(n)]


def minor(matrix, row, col):
    return [r[:col] + r[col + 1:] for i, r in enumerate(matrix) if i != row]


def determinant(matrix):
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = Fraction(0)
    for j in range(n):
        if matrix[0][j] != 0:
            sign = (-1) ** j
            det += sign * matrix[0][j] * determinant(minor(matrix, 0, j))
    return det


def inverse_by_determinant(matrix):
    n = len(matrix)
    det = determinant(matrix)
    if det == 0:
        raise SingularMatrixError(
            "행렬식이 0이므로 역행렬이 존재하지 않습니다.")
    if n == 1:
        return [[1 / det]]
    cofactors = [[(-1) ** (i + j) * determinant(minor(matrix, i, j))
                  for j in range(n)] for i in range(n)]
    return [[cofactors[j][i] / det for j in range(n)] for i in range(n)]


def print_operations(col, ops):
    head = f"  [{col + 1}열 정리] "
    if not ops:
        print(head + "연산 없음")
    for k in range(0, len(ops), 2):
        print((head if k == 0 else " " * 13) + ",  ".join(ops[k:k + 2]))


def inverse_by_gauss_jordan(matrix, trace=False):
    n = len(matrix)
    aug = [list(matrix[i]) + identity(n)[i] for i in range(n)]
    if trace:
        print("  [초기] 첨가행렬 [A | I]")
        print_matrix(aug, bar=n)

    for col in range(n):
        ops = []
        pivot_row = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot_row is None:
            raise SingularMatrixError(
                f"{col + 1}열에서 피벗을 찾을 수 없어 "
                "역행렬이 존재하지 않습니다.")
        if pivot_row != col:
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            ops.append(f"R{col + 1} <-> R{pivot_row + 1}")
        pivot = aug[col][col]
        if pivot != 1:
            aug[col] = [x / pivot for x in aug[col]]
            ops.append(f"R{col + 1} <- R{col + 1} / ({pivot})")
        for r in range(n):
            factor = aug[r][col]
            if r != col and factor != 0:
                aug[r] = [x - factor * p for x, p in zip(aug[r], aug[col])]
                ops.append(f"R{r + 1} <- R{r + 1} - ({factor})*R{col + 1}")
        if trace:
            print_operations(col, ops)
            print_matrix(aug, bar=n)

    return [row[n:] for row in aug]


def is_same_matrix(a, b):
    n = len(a)
    return all(a[i][j] == b[i][j] for i in range(n) for j in range(n))


def verify_inverse(matrix, inverse):
    return is_same_matrix(multiply(matrix, inverse), identity(len(matrix)))


def measure_time(func, matrix, repeat):
    start = time.perf_counter()
    for _ in range(repeat):
        func(matrix)
    return (time.perf_counter() - start) / repeat * 1000


def solve(matrix, trace):
    n = len(matrix)

    print(LINE)
    print("[방법 1] 행렬식 이용 :  A^-1 = adj(A) / det(A)")
    print(f"  det(A) = {determinant(matrix)}")
    try:
        inv_det = inverse_by_determinant(matrix)
        print("  A^-1 =")
        print_matrix(inv_det)
    except SingularMatrixError as error:
        inv_det = None
        print(f"  [오류] {error}")

    print(LINE)
    print("[방법 2] 가우스-조던 소거법 :  [A | I] -> [I | A^-1]")
    try:
        inv_gj = inverse_by_gauss_jordan(matrix, trace)
        print("  A^-1 =")
        print_matrix(inv_gj)
    except SingularMatrixError as error:
        inv_gj = None
        print(f"  [오류] {error}")

    print(LINE)
    if inv_det is None and inv_gj is None:
        print("[비교 결과] 두 방법 모두 '역행렬 없음'으로 판정했습니다. (일치)")
        return
    if inv_det is None or inv_gj is None:
        print("[비교 결과] 두 방법의 판정이 서로 다릅니다. (불일치)")
        return
    if is_same_matrix(inv_det, inv_gj):
        print("[비교 결과] 두 방법으로 구한 역행렬이 동일합니다. (일치)")
    else:
        print("[비교 결과] 두 방법으로 구한 역행렬이 서로 다릅니다. (불일치)")

    print("[소수 표현] 소수점 넷째 자리까지")
    print_matrix_decimal(inv_gj)

    ok = verify_inverse(matrix, inv_det) and verify_inverse(matrix, inv_gj)
    print("[검산] A x A^-1 = I  ->", "성립" if ok else "성립하지 않음")

    repeat = 20 if n <= 5 else 1
    t_det = measure_time(inverse_by_determinant, matrix, repeat)
    t_gj = measure_time(inverse_by_gauss_jordan, matrix, repeat)
    print(f"[실행 시간] 행렬식 {t_det:.4f} ms / "
          f"가우스-조던 {t_gj:.4f} ms ({repeat}회 평균)")


def main():
    print("=" * 60)
    print("  역행렬 계산 프로그램  (행렬식 / 가우스-조던 소거법)")
    print("=" * 60)
    while True:
        n = read_size()
        matrix = read_matrix(n)
        print()
        print("[입력 행렬 A]")
        print_matrix(matrix)
        trace = ask_yes_no("가우스-조던 소거 과정을 출력할까요? (y/n): ")
        solve(matrix, trace)
        print(LINE)
        if not ask_yes_no("다른 행렬을 계산하시겠습니까? (y/n): "):
            print("프로그램을 종료합니다.")
            break
        print()


if __name__ == "__main__":
    main()
