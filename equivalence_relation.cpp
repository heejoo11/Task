/*
 * Report 2 - 동치 관계 판별 프로그램
 * 집합 A = {1,2,3,4,5} 위의 관계를 5x5 관계행렬로 입력받아
 * 반사/대칭/추이 성질을 판별하고, 동치 관계이면 동치류를 출력한다.
 * 동치 관계가 아니면 각 성질의 폐포(closure)를 구해 다시 판별한다.
 *
 * [추가기능] 표시가 붙은 함수는 기본 구성 조건 외에 추가로 구현한 기능이다.
 *
 * 컴파일: g++ -std=c++17 -o equivalence equivalence_relation.cpp
 */
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#endif
using namespace std;

const int N = 5;                       // 집합 A의 원소 개수
const int A[N] = {1, 2, 3, 4, 5};      // 집합 A
typedef vector<vector<int>> Matrix;    // 관계행렬(2차원 배열)

/* ===================== 1. 관계 행렬 입력 기능 ===================== */

// [추가기능 1] 입력 검증: 한 줄이 0/1 값 5개로 이루어졌는지 검사한다.
bool parseRow(const string& line, vector<int>& row, string& err) {
    stringstream ss(line);
    string token;
    row.clear();
    while (ss >> token) {
        if (token != "0" && token != "1") {
            err = "'" + token + "' 는 0 또는 1이 아닙니다.";
            return false;
        }
        row.push_back(token[0] - '0');
    }
    if ((int)row.size() != N) {
        err = "값이 " + to_string(row.size()) + "개 입력되었습니다. (5개 필요)";
        return false;
    }
    return true;
}

// 사용자로부터 5x5 관계행렬을 행 단위로 입력받아 2차원 배열에 저장한다.
Matrix inputMatrix() {
    Matrix R(N, vector<int>(N, 0));
    cout << "\n관계 행렬을 행 단위로 입력하세요. (0 또는 1, 공백으로 구분)\n";
    for (int i = 0; i < N; i++) {
        while (true) {
            cout << "  " << A[i] << "행 입력: ";
            string line, err;
            if (!getline(cin, line)) exit(0);
            vector<int> row;
            if (parseRow(line, row, err)) {   // 올바른 행이면 저장
                R[i] = row;
                break;
            }
            cout << "  [입력 오류] " << err << " 다시 입력하세요.\n";
        }
    }
    return R;
}

// [추가기능 6] 미리 준비된 예제 관계행렬
Matrix sampleMatrix(int k) {
    if (k == 1) return {{1,1,0,0,0},{1,1,0,0,0},{0,0,1,0,0},{0,0,0,1,1},{0,0,0,1,1}};
    if (k == 2) return {{1,1,0,0,0},{0,1,1,0,0},{0,0,0,0,0},{0,0,0,1,0},{0,0,0,1,1}};
    return             {{1,1,0,0,0},{1,1,1,0,0},{0,1,1,0,0},{0,0,0,1,0},{0,0,0,0,1}};
}

/* ===================== 출력 보조 함수 ===================== */

// 관계행렬을 표 형태로 출력한다.
void printMatrix(const Matrix& R, const string& title) {
    cout << "\n[" << title << "]\n     ";
    for (int j = 0; j < N; j++) cout << A[j] << "  ";
    cout << "\n   +---------------\n";
    for (int i = 0; i < N; i++) {
        cout << " " << A[i] << " | ";
        for (int j = 0; j < N; j++) cout << R[i][j] << "  ";
        cout << "\n";
    }
}

// [추가기능 4] 변환 후 행렬을 출력하면서 새로 추가된 1 뒤에 '*' 를 표시한다.
void printMatrixDiff(const Matrix& before, const Matrix& after, const string& title) {
    cout << "\n[" << title << " (* : 새로 추가된 순서쌍)]\n     ";
    for (int j = 0; j < N; j++) cout << A[j] << "  ";
    cout << "\n   +---------------\n";
    for (int i = 0; i < N; i++) {
        cout << " " << A[i] << " | ";
        for (int j = 0; j < N; j++) {
            bool added = before[i][j] == 0 && after[i][j] == 1;
            cout << after[i][j] << (added ? "* " : "  ");
        }
        cout << "\n";
    }
}

// [추가기능 3] 관계를 순서쌍 집합으로 출력한다.
void printPairs(const Matrix& R) {
    cout << "R = { ";
    bool first = true;
    int cnt = 0;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            if (R[i][j]) {
                cout << (first ? "" : ", ") << "(" << A[i] << "," << A[j] << ")";
                first = false;
                cnt++;
            }
    cout << " }  (순서쌍 " << cnt << "개)\n";
}

string setToString(const vector<int>& v) {
    string s = "{";
    for (size_t i = 0; i < v.size(); i++) s += (i ? ", " : "") + to_string(v[i]);
    return s + "}";
}

/* ===================== 2. 동치 관계 판별 기능 ===================== */

// 반사 관계: 모든 a에 대해 (a,a) ∈ R
bool isReflexive(const Matrix& R) {
    for (int i = 0; i < N; i++)
        if (R[i][i] == 0) return false;
    return true;
}

// 대칭 관계: (a,b) ∈ R 이면 (b,a) ∈ R
bool isSymmetric(const Matrix& R) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            if (R[i][j] == 1 && R[j][i] == 0) return false;
    return true;
}

// 추이 관계: (a,b) ∈ R 이고 (b,c) ∈ R 이면 (a,c) ∈ R
bool isTransitive(const Matrix& R) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            for (int k = 0; k < N; k++)
                if (R[i][j] == 1 && R[j][k] == 1 && R[i][k] == 0) return false;
    return true;
}

// [추가기능 2] 성질을 깨뜨리는 순서쌍을 찾아 출력한다. (type: 'r' 반사, 's' 대칭, 't' 추이)
void printViolations(const Matrix& R, char type) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            if (type == 'r' && i == j && R[i][i] == 0)
                cout << "     - (" << A[i] << "," << A[i] << ") 가 없음\n";
            if (type == 's' && R[i][j] == 1 && R[j][i] == 0)
                cout << "     - (" << A[i] << "," << A[j] << ") 는 있으나 ("
                     << A[j] << "," << A[i] << ") 가 없음\n";
            if (type == 't')
                for (int k = 0; k < N; k++)
                    if (R[i][j] == 1 && R[j][k] == 1 && R[i][k] == 0)
                        cout << "     - (" << A[i] << "," << A[j] << "), (" << A[j] << "," << A[k]
                             << ") 는 있으나 (" << A[i] << "," << A[k] << ") 가 없음\n";
        }
}

// 세 성질을 판별해 결과 메시지를 출력하고 동치 관계 여부를 반환한다.
// detail 이 true 이면 [추가기능 2] 위반 순서쌍도 함께 출력한다.
bool checkEquivalence(const Matrix& R, bool detail = true) {
    bool r = isReflexive(R), s = isSymmetric(R), t = isTransitive(R);
    cout << "\n<성질 판별 결과>\n";
    cout << "  반사 관계 : " << (r ? "O (만족)" : "X (불만족)") << "\n";
    if (!r && detail) printViolations(R, 'r');
    cout << "  대칭 관계 : " << (s ? "O (만족)" : "X (불만족)") << "\n";
    if (!s && detail) printViolations(R, 's');
    cout << "  추이 관계 : " << (t ? "O (만족)" : "X (불만족)") << "\n";
    if (!t && detail) printViolations(R, 't');

    if (r && s && t) {
        cout << "  ▶ 반사·대칭·추이를 모두 만족하므로 동치 관계입니다.\n";
        return true;
    }
    cout << "  ▶ 만족하지 않는 성질이 있으므로 동치 관계가 아닙니다.\n";
    return false;
}

/* ===================== 3. 동치류 출력 기능 ===================== */

// 원소 A[idx]의 동치류 [a] = { b | (a,b) ∈ R }
vector<int> equivalenceClass(const Matrix& R, int idx) {
    vector<int> cls;
    for (int j = 0; j < N; j++)
        if (R[idx][j] == 1) cls.push_back(A[j]);
    return cls;
}

// [추가기능 5] 서로 다른 동치류만 모아 분할 A/R 을 출력한다.
void printPartition(const Matrix& R) {
    vector<vector<int>> partition;
    for (int i = 0; i < N; i++) {
        vector<int> cls = equivalenceClass(R, i);
        bool exists = false;
        for (auto& p : partition) if (p == cls) exists = true;
        if (!exists) partition.push_back(cls);
    }
    cout << "  분할 A/R = { ";
    for (size_t i = 0; i < partition.size(); i++)
        cout << (i ? ", " : "") << setToString(partition[i]);
    cout << " }  (서로 다른 동치류 " << partition.size() << "개)\n";
}

// 집합의 각 원소에 대한 동치류를 출력한다.
void printEquivalenceClasses(const Matrix& R) {
    cout << "\n<동치류>\n";
    for (int i = 0; i < N; i++)
        cout << "  [" << A[i] << "] = " << setToString(equivalenceClass(R, i)) << "\n";
    printPartition(R);   // [추가기능 5]
}

/* ===================== 4. 폐포 구현 기능 ===================== */

// 반사 폐포: 대각 원소를 모두 1로
Matrix reflexiveClosure(Matrix R) {
    for (int i = 0; i < N; i++) R[i][i] = 1;
    return R;
}

// 대칭 폐포: R ∪ R^(-1)
Matrix symmetricClosure(Matrix R) {
    Matrix S = R;
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            if (R[i][j] == 1) S[j][i] = 1;
    return S;
}

// 추이 폐포: Warshall 알고리즘
Matrix transitiveClosure(Matrix R) {
    for (int k = 0; k < N; k++)
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                if (R[i][k] && R[k][j]) R[i][j] = 1;
    return R;
}

// 폐포 변환 전/후를 출력하고 동치 관계를 다시 판별한다.
void showClosure(const Matrix& R, const string& name, Matrix (*closure)(Matrix)) {
    cout << "\n------------------------------------------------\n";
    cout << " " << name << " 폐포 변환\n";
    cout << "------------------------------------------------";
    Matrix C = closure(R);
    printMatrix(R, "변환 전");
    printMatrixDiff(R, C, "변환 후");          // [추가기능 4]
    if (checkEquivalence(C, false)) printEquivalenceClasses(C);
}

// [추가기능 5] 동치 폐포 t(s(r(R))) : R을 포함하는 가장 작은 동치 관계
void showEquivalenceClosure(const Matrix& R) {
    cout << "\n================ [추가] 동치 폐포 ================\n";
    cout << "t(s(r(R))) : 반사 → 대칭 → 추이 폐포를 차례로 적용";
    Matrix E = transitiveClosure(symmetricClosure(reflexiveClosure(R)));
    printMatrixDiff(R, E, "동치 폐포");
    if (checkEquivalence(E, false)) printEquivalenceClasses(E);
}

// 만족하지 않는 성질마다 폐포를 구해 출력한다.
void processClosures(const Matrix& R) {
    cout << "\n================ 폐포 구현 ================\n";
    bool r = isReflexive(R), s = isSymmetric(R), t = isTransitive(R);
    if (r && s && t) {
        cout << "반사·대칭·추이를 모두 만족하므로 폐포 변환이 필요하지 않습니다.\n";
        return;
    }
    if (!r) showClosure(R, "반사", reflexiveClosure);
    if (!s) showClosure(R, "대칭", symmetricClosure);
    if (!t) showClosure(R, "추이", transitiveClosure);
    showEquivalenceClosure(R);                 // [추가기능 5]
}

/* ===================== 메인 ===================== */

void analyze(const Matrix& R) {
    printMatrix(R, "입력된 관계 행렬");
    printPairs(R);                             // [추가기능 3]
    if (checkEquivalence(R)) printEquivalenceClasses(R);
    processClosures(R);
}

int main() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    while (true) {
        cout << "\n==========================================\n";
        cout << "   동치 관계 판별 프로그램  A = {1,2,3,4,5}\n";
        cout << "==========================================\n";
        cout << " 1. 관계 행렬 직접 입력\n";
        cout << " 2. 예제 관계 행렬 사용\n";
        cout << " 0. 종료\n";
        cout << "선택: ";
        string sel;
        if (!getline(cin, sel)) break;

        if (sel == "0") {
            cout << "프로그램을 종료합니다.\n";
            break;
        } else if (sel == "1") {
            analyze(inputMatrix());
        } else if (sel == "2") {                  // [추가기능 6] 예제 메뉴
            cout << " 예제 1) 동치 관계   예제 2) 세 성질 모두 불만족   예제 3) 추이만 불만족\n";
            cout << "예제 번호: ";
            string k;
            if (!getline(cin, k)) break;
            if (k == "1" || k == "2" || k == "3") analyze(sampleMatrix(stoi(k)));
            else cout << "[입력 오류] 1~3 중에서 선택하세요.\n";
        } else {                                  // [추가기능 1] 메뉴 번호 검증
            cout << "[입력 오류] 0, 1, 2 중에서 선택하세요.\n";
        }
    }
    return 0;
}
