# technical_review

# Snapscale Technical Assignment

스냅스케일 기술 과제 제출 자료입니다.

본 저장소는 산업 엔지니어링 성과품을 대상으로 한 데이터 정합성 검증, 자연어 규칙 변환, 규칙 기반 검증 엔진 구현 과제를 수행한 결과물을 포함합니다.

---

# 프로젝트 개요

본 과제는 다음 3개의 주제로 구성됩니다.

## 과제 1

### P&ID(Process & Instrumentation Diagram) 분석

* 설비, 계장기기, 배관 관계 분석
* 공정 흐름 파악
* 제어 루프 해석
* 그래프 기반 구조화 방안 검토

---

## 과제 2

### 성과품 정합성 검증 미니 엔진

서로 다른 엔지니어가 작성한 성과품을 하나의 공통 스키마로 통합하고 정합성을 검증합니다.

#### 주요 기능

* Equipment_List
* Line_List

통합

* 속성명 매핑
* 단위 변환
* 공통 스키마 생성

검증

* 설계압력
* 운전압력
* 설계온도
* 운전온도
* 안전밸브 여부

READ_ME에 정의된 자연어 규칙 검증

---

## 과제 3

### 자연어 → 모듈 조합 변환

산업 규격 문장을 안전한 AST(Abstract Syntax Tree) 형태로 변환합니다.

#### 예시

자연어

> 모든 용기의 설계압력은 운전압력의 1.1배 이상이어야 한다.

변환 결과

```python
[
  "forEvery",
  ["allOf", "Vessel"],
  [
    "isAtLeast",
    ["prop", "x", "DesignPressure"],
    ["times", ["prop", "x", "OperatingPressure"], 1.1]
  ]
]
```

LLM 또는 규칙 기반 변환기가 생성한 결과는 Validator를 통해 검증됩니다.


---

# 과제 2 구현 내용

## 1. 공통 스키마 생성

Equipment_List

```text
Equipment Tag
Type
Operating Pressure
Design Pressure
Operating Temperature
Design Temperature
Material
Has Safety Valve
```

↓

공통 스키마

```python
{
    "Tag": "...",
    "ClassName": "...",
    "OperatingPressure": ...,
    "DesignPressure": ...,
    "OperatingTemperature": ...,
    "DesignTemperature": ...,
    "Material": ...,
    "HasSafetyValve": ...
}
```

---

## 2. 단위 변환

Line_List

```text
kPag → barg
K → degC
```

변환 수행

---

## 3. 정합성 검증

예시

```text
설계압력 >= 운전압력

설계온도 >= 운전온도
```

---

# 과제 3 구현 내용

## AST 구조

```python
("forEvery",
    ("allOf", "Vessel"),
    (
        "isAtLeast",
        ("prop", "x", "DesignPressure"),
        ("times",
            ("prop", "x", "OperatingPressure"),
            1.1
        )
    )
)
```

---

## Validator

Validator는 AST가 명세에 맞는지 검사합니다.

### 함수명 검증

허용 함수

```python
allOf
withSafetyValve
prop
isAtLeast
isAtMost
isEqual
exists
matchesPattern
times
plus
and
or
not
forEvery
```

### 속성명 검증

```python
DesignPressure
OperatingPressure
DesignTemperature
OperatingTemperature
Tag
Material
```

### 클래스명 검증

```python
Equipment
Vessel
Tank
Pump
HeatExchanger
Compressor
```

---

# 과제 2 + 과제 3 통합

추가 구현 사항입니다.

## 기존 구조

```text
과제2
↓
Excel 검증
```

```text
과제3
↓
AST 생성
```

서로 독립적으로 동작

---

## 통합 구조

```text
Excel
↓
equipment_data

MD
↓
rules

rules
↓
validator

valid_rules
↓
equipment_data 적용

↓
violation_report
```

즉, 자연어 규칙을 실제 데이터 검증에 적용하는 통합 파이프라인을 구현했습니다.

---

# LLM 확장안

추가 실험 버전입니다.

## 기존 방식

```text
자연어
↓
Rule Mapping
↓
AST
```

---

## LLM 방식

```text
자연어
↓
LLM
↓
AST 생성
↓
Validator
↓
실패
↓
피드백
↓
재생성
↓
Validator 통과
↓
실행
```

---

## Gate Loop 예시

LLM 출력

```python
["greaterThan", ...]
```

↓

Validator 실패

```text
명세에 없는 함수
```

↓

LLM 재생성

```python
["isAtLeast", ...]
```

↓

통과

---

# 기술 스택

* Python
* Pandas
* OpenPyXL
* Dataclass
* Regular Expression
* AST 기반 Rule Engine
* LLM (확장안)

---

# 실행 방법

## 과제 2

```bash
python task2.py
```

## 과제 3

```bash
python task3.py
```

## 통합 버전

```bash
python integration_pipeline.py
```

---

# 결과

* 공통 스키마 생성
* 단위 정규화
* 자연어 → AST 변환
* Validator 검증
* Rule Engine 실행
* 위반 리포트 생성

---

# 추가 구현

* 과제2 + 과제3 통합
* Gate Loop 구조
* LLM 기반 AST 생성 실험
* Validator 기반 안전성 확보

---
