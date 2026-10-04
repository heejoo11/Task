"""
역행렬 계산 프로그램 (이산수학 리포트)

  방법 1) 행렬식(여인수 전개)과 수반행렬 :  A^-1 = adj(A) / det(A)
  방법 2) 가우스-조던 소거법            :  [A | I]  ->  [I | A^-1]

두 방법으로 각각 역행렬을 구해 출력하고, 결과가 같은지 비교한다.
표준 라이브러리만 사용한다. (fractions, time)
"""

from fractions import Fraction
import time

LINE = "-" * 60


class SingularMatrixError(Exception):
    """역행렬이 존재하지 않는 행렬(특이행렬)일 때 발생시키는 예외"""


# ============================================================
# 1. 행렬 입력
# ============================================================
def read_size():
    """정수 n(행렬의 크기)을 입력받는다. 잘못된 입력이면 다시 묻는다."""
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
    """n x n 정방행렬을 행 단위로 입력받아 2차원 리스트로 반환한다."""
    print(f"{n} x {n} 행렬을 한 행씩 입력하세요. (원소는 공백으로 구분)")
    matrix = []                                  # 2차원 리스트
    for i in range(n):
        while True:
            tokens = input(f"  {i + 1}행: ").split()
            if len(tokens) != n:
                print(f"  [입력 오류] 원소가 {n}개여야 합니다. "
                      f"(입력된 개수: {len(tokens)})")
                continue
            try:
                row = [Fraction(t) for t in tokens]   # 정수/소수/분수 허용
            except (ValueError, ZeroDivisionError):
                print("  [입력 오류] 숫자만 입력하세요. (예: 3  -1.5  2/3)")
                continue
            matrix.append(row)                   # 한 행을 리스트에 추가
            break
    return matrix


def ask_yes_no(message):
    """y 또는 n 으로 답할 때까지 다시 묻는다."""
    while True:
        answer = input(message).strip().lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("  [입력 오류] y 또는 n 으로 입력하세요.")


# ============================================================
# 공통 도구 (출력, 행렬 곱, 단위행렬)
# ============================================================
def format_rows(cells, bar=None):
    """문자열 2차원 리스트를 열 너비를 맞춘 줄 목록으로 바꾼다."""
    widths = [max(len(row[j]) for row in cells) for j in range(len(cells[0]))]
    lines = []
    for row in cells:
        parts = [row[j].rjust(widths[j]) for j in range(len(row))]
        if bar is not None:                      # 첨가행렬의 구분선 위치
            parts.insert(bar, "|")
        lines.append("[ " + "  ".join(parts) + " ]")
    return lines


def print_matrix(matrix, indent="    ", bar=None):
    """행렬을 분수 형태 그대로 출력한다. (예: -7/10)"""
    cells = [[str(x) for x in row] for row in matrix]
    for line in format_rows(cells, bar):
        print(indent + line)


def print_matrix_decimal(matrix, indent="    ", digits=4):
    """행렬을 소수 형태로 출력한다."""
    cells = [[f"{float(x):.{digits}f}" for x in row] for row in matrix]
    for line in format_rows(cells):
        print(indent + line)


def identity(n):
    """n x n 단위행렬"""
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def multiply(a, b):
    """행렬 곱 a x b"""
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)]
            for i in range(n)]


# ============================================================
# 2. 방법 1 : 행렬식을 이용한 역행렬
# ============================================================
def minor(matrix, row, col):
    """row행과 col열을 제거한 소행렬"""
    return [r[:col] + r[col + 1:] for i, r in enumerate(matrix) if i != row]


def determinant(matrix):
    """1행에 대한 여인수 전개(재귀)로 행렬식을 구한다."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = Fraction(0)
    for j in range(n):
        if matrix[0][j] != 0:                    # 0인 항은 건너뛴다
            sign = (-1) ** j
            det += sign * matrix[0][j] * determinant(minor(matrix, 0, j))
    return det


def inverse_by_determinant(matrix):
    """A^-1 = adj(A) / det(A).  det(A) = 0 이면 예외를 발생시킨다."""
    n = len(matrix)
    det = determinant(matrix)
    if det == 0:
        raise SingularMatrixError(
            "행렬식이 0이므로 역행렬이 존재하지 않습니다.")
    if n == 1:
        return [[1 / det]]
    # 여인수 행렬  C[i][j] = (-1)^(i+j) * det(M_ij)
    cofactors = [[(-1) ** (i + j) * determinant(minor(matrix, i, j))
                  for j in range(n)] for i in range(n)]
    # 수반행렬 adj(A)는 여인수 행렬의 전치 -> 각 원소를 det(A)로 나눈다
    return [[cofactors[j][i] / det for j in range(n)] for i in range(n)]


# ============================================================
# 3. 방법 2 : 가우스-조던 소거법을 이용한 역행렬
# ============================================================
def print_operations(col, ops):
    """col열에서 수행한 기본 행 연산을 한 줄에 2개씩 출력한다."""
    head = f"  [{col + 1}열 정리] "
    if not ops:
        print(head + "연산 없음")
    for k in range(0, len(ops), 2):
        print((head if k == 0 else " " * 13) + ",  ".join(ops[k:k + 2]))


def inverse_by_gauss_jordan(matrix, trace=False):
    """[A | I] 를 [I | A^-1] 로 바꾼다. trace=True 이면 과정을 출력한다."""
    n = len(matrix)
    aug = [list(matrix[i]) + identity(n)[i] for i in range(n)]   # [A | I]
    if trace:
        print("  [초기] 첨가행렬 [A | I]")
        print_matrix(aug, bar=n)

    for col in range(n):
        ops = []                                 # 이번 열에서 한 행 연산
        # (1) col열에서 0이 아닌 피벗을 가진 행을 찾는다
        pivot_row = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot_row is None:
            raise SingularMatrixError(
                f"{col + 1}열에서 피벗을 찾을 수 없어 "
                "역행렬이 존재하지 않습니다.")
        # (2) 필요하면 행을 교환한다
        if pivot_row != col:
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            ops.append(f"R{col + 1} <-> R{pivot_row + 1}")
        # (3) 피벗을 1로 만든다
        pivot = aug[col][col]
        if pivot != 1:
            aug[col] = [x / pivot for x in aug[col]]
            ops.append(f"R{col + 1} <- R{col + 1} / ({pivot})")
        # (4) 피벗 열의 나머지 원소를 0으로 만든다
        for r in range(n):
            factor = aug[r][col]
            if r != col and factor != 0:
                aug[r] = [x - factor * p for x, p in zip(aug[r], aug[col])]
                ops.append(f"R{r + 1} <- R{r + 1} - ({factor})*R{col + 1}")
        if trace:
            print_operations(col, ops)
            print_matrix(aug, bar=n)

    return [row[n:] for row in aug]              # 오른쪽 절반이 A^-1


# ============================================================
# 4. 결과 비교 / 5. 추가 기능 (검산, 실행 시간)
# ============================================================
def is_same_matrix(a, b):
    """두 행렬의 모든 원소가 같은지 비교한다."""
    n = len(a)
    return all(a[i][j] == b[i][j] for i in range(n) for j in range(n))


def verify_inverse(matrix, inverse):
    """검산: A x A^-1 이 단위행렬인지 확인한다."""
    return is_same_matrix(multiply(matrix, inverse), identity(len(matrix)))


def measure_time(func, matrix, repeat):
    """func(matrix)를 repeat번 실행한 평균 시간(ms)"""
    start = time.perf_counter()
    for _ in range(repeat):
        func(matrix)
    return (time.perf_counter() - start) / repeat * 1000


def solve(matrix, trace):
    """두 방법으로 역행렬을 구해 출력하고 비교한다."""
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
