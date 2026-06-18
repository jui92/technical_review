import pandas as pd
import numpy as np
import re


# 1.엑셀 파일 읽기
file_path = "./consistency_check.xlsx"

equipment_raw = pd.read_excel(file_path, sheet_name="Equipment_List")
line_raw = pd.read_excel(file_path, sheet_name="Line_List")
readme = pd.read_excel(file_path, sheet_name="READ_ME", header=8)



# 2.실제 파일 컬럼명을 반영한 컬럼 매핑 정의
equipment = equipment_raw.rename(columns={
    "Equipment Tag": "equipment_tag",
    "Type": "equipment_type",
    "Operating Pressure (barg)": "operating_pressure_barg",
    "Design Pressure (barg)": "design_pressure_barg",
    "Operating Temp (degC)": "operating_temp_degC",
    "Design Temp (degC)": "design_temp_degC",
    "Material": "material",
    "Has Safety Valve": "has_safety_valve"
}).copy()

line = line_raw.rename(columns={
    "배관 번호": "line_no",
    "From 장비": "from_equipment",
    "To 장비": "to_equipment",
    "설계압력 [kPag]": "design_pressure_kPag",
    "운전온도 [K]": "operating_temp_K",
    "보온 여부": "insulation"
}).copy()



# 3.단위 환산
line["design_pressure_barg"] = line["design_pressure_kPag"] / 100
line["operating_temp_degC"] = line["operating_temp_K"] - 273.15



# 4.위반 결과를 저장할 DataFrame 생성 함수
def make_report(df, rule_id, item_type, id_col, reason_col):
    """
    조건에 걸린 DataFrame을 위반 리포트 형식으로 바꾸는 함수.
    """
    return pd.DataFrame({
        "rule_id": rule_id,
        "item_type": item_type,
        "item_id": df[id_col],
        "reason": df[reason_col]
    })

reports = []


### 4-1.모든 장비의 설계압력은 운전압력의 1.1배 이상이어야 한다.
r1 = equipment.copy()

r1["r1_reason"] = np.select(
    [r1["operating_pressure_barg"].isna(),
     r1["design_pressure_barg"].isna(),
     r1["design_pressure_barg"] < r1["operating_pressure_barg"] * 1.1],
    ["운전압력이 공란임",
     "설계압력이 공란임",
     "설계압력이 운전압력의 1.1배보다 작음"],
    default=None)

r1_violation = r1[r1["r1_reason"].notna()]
reports.append(make_report(r1_violation, "R1", "Equipment", "equipment_tag", "r1_reason"))


### 4-2.Line_List의 From/To 장비는 Equipment_List에 존재해야 한다.
equipment_tags = set(equipment["equipment_tag"])

r2_from = line[~line["from_equipment"].isin(equipment_tags)].copy()
r2_from["r2_reason"] = ("From 장비 '" + r2_from["from_equipment"].astype(str) + "'가 Equipment_List에 존재하지 않음")
reports.append(make_report(r2_from, "R2", "Line", "line_no", "r2_reason"))

r2_to = line[~line["to_equipment"].isin(equipment_tags)].copy()
r2_to["r2_reason"] = ("To 장비 '" + r2_to["to_equipment"].astype(str) + "'가 Equipment_List에 존재하지 않음")
reports.append(make_report(r2_to, "R2", "Line", "line_no", "r2_reason"))


### 4-3.모든 장비의 설계온도는 운전온도보다 30℃ 이상 높아야 한다.
r3 = equipment.copy()

r3["r3_reason"] = np.select(
    [r3["operating_temp_degC"].isna(),
     r3["design_temp_degC"].isna(),
     r3["design_temp_degC"] < r3["operating_temp_degC"] + 30],
    ["운전온도가 공란임",
     "설계온도가 공란임",
     "설계온도가 운전온도 + 30℃ 기준보다 낮음"],
    default=None)

r3_violation = r3[r3["r3_reason"].notna()]
reports.append(make_report(r3_violation, "R3", "Equipment", "equipment_tag", "r3_reason"))


### 4-4.안전밸브가 있는 장비는 설계압력이 반드시 정의되어 있어야 한다.
r4 = equipment[(equipment["has_safety_valve"] == "Y") & (equipment["design_pressure_barg"].isna())].copy()
r4["r4_reason"] = "안전밸브가 있는 장비인데 설계압력이 공란임"

reports.append(make_report(r4, "R4", "Equipment", "equipment_tag", "r4_reason"))


### 4-5.장비 태그 패턴 검증
tag_pattern = r"^[A-Za-z]+-\d{3}[A-Za-z]?$"

r5 = equipment[~equipment["equipment_tag"].astype(str).str.match(tag_pattern)].copy()
r5["r5_reason"] = "장비 태그 형식이 규칙에 맞지 않음"

reports.append(make_report(r5, "R5", "Equipment", "equipment_tag", "r5_reason"))



# 5.최종 위반 리포트 생성 및 저장
violation_report = pd.concat(reports, ignore_index=True)
violation_report = violation_report.sort_values(by=["rule_id", "item_type", "item_id"]).reset_index(drop=True)

violation_report.to_excel("violation_report_vectorized.xlsx", index=False)