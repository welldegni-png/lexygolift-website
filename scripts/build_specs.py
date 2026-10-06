from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DATA = ROOT / "source-data.json"
OUTPUT = ROOT / "product_specs.json"


LABELS = {
    "品牌": "Manufacturer",
    "车型": "Model",
    "操作方式": "Operation mode",
    "额定载荷能力": "Rated load capacity",
    "门架类型": "Mast type",
    "提升高度": "Lift height",
    "最高点载重量": "Capacity at maximum lift height",
    "自重": "Service weight with battery",
    "载荷中心距": "Load center distance",
    "前悬距": "Axle center to fork face",
    "轴距": "Wheelbase",
    "控制器": "Controller",
    "轮胎类型": "Wheel material",
    "驱动轮尺寸": "Drive wheel size",
    "承载轮尺寸": "Load wheel size",
    "平衡轮尺寸": "Stabilizer wheel size",
    "驱动轮，平衡轮/承载轮数量": "Wheels, front/rear (x = driven)",
    "驱动轮，承载轮数量": "Wheels, front/rear (x = driven)",
    "最低门架高度": "Mast height, lowered",
    "门架最大高度": "Mast height, extended",
    "货叉最低高度": "Fork height, lowered",
    "整车长度": "Overall length",
    "车体长度": "Length to fork face",
    "整车宽度": "Overall width",
    "货叉尺寸": "Fork dimensions (thickness x width x length)",
    "货叉外宽": "Overall fork width",
    "轴距中心处离地间隙": "Ground clearance at center of wheelbase",
    "通道宽度：1000×1200托盘": "Aisle width with 1000 x 1200 mm pallet",
    "通道宽度：800×1200托盘": "Aisle width with 800 x 1200 mm pallet",
    "转弯半径": "Minimum turning radius",
    "前移距离": "Reach distance",
    "行走速度，满载/空载": "Travel speed, laden/unladen",
    "提升速度，满載/空载": "Lift speed, laden/unladen",
    "下降速度，满载/空载": "Lowering speed, laden/unladen",
    "最大爬坡度，满载/空载": "Gradeability, laden/unladen",
    "制动类型": "Service brake",
    "驱动电机功率": "Drive motor rating",
    "起升电机功率": "Lift motor rating",
    "蓄电池 根据DN": "Battery to DIN standard",
    "蓄电池电压/容量": "Battery voltage / rated capacity",
    "蓄电池重量": "Battery weight",
    "噪音水平": "Noise level at operator's ear",
    "转向类型": "Steering type",
}

SECTION_LABELS = {
    "特征": "Characteristics",
    "轮子": "Wheels",
    "尺寸": "Dimensions",
    "性能": "Performance",
    "电机和蓄电池": "Drive and battery",
    "其他": "Other",
}


def clean_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    replacements = {
        "φ": "Ø",
        "∅": "Ø",
        "≤": "<=",
        "≥": ">=",
        "×": " x ",
        "，": ", ",
        "（": " (",
        "）": ")",
        "步行式Pedestrian propelled": "Pedestrian",
        "步行式": "Pedestrian",
        "站驾式Standing driving": "Stand-on",
        "单门架Singel mast": "Single mast",
        "两级标准2-stage STD": "2-stage standard mast",
        "聚氨酯 (Polyurethane)": "Polyurethane (PU)",
        "电磁制动 (Electromagnetic brake)": "Electromagnetic brake",
        "机械转向 (Mechanical steering)": "Mechanical steering",
        "机械转向 (Electronic steering)": "Mechanical steering",
        "电子转向 (Electronic steering)": "Electronic steering",
        "24/120免维护 (Maintenance free)": "24 / 120, maintenance-free",
        "大能D2P (Daneng D2P)": "Daneng D2P",
        "LVM24S20 (前拓) (QEXPAND)": "QEXPAND LVM24S20",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"LVM24S20\s*\(前拓\)\s*\(QEXPAND\)", "QEXPAND LVM24S20", text)
    text = re.sub(r"WTBL4890MB-C4\s*\(天力\)\s*\(tianli\)", "Tianli WTBL4890MB-C4", text, flags=re.I)
    text = re.sub(r"Ø(\d+\s*x\s*\d+)橡胶\s*\(rubber\)", r"Ø\1 rubber", text, flags=re.I)
    text = re.sub(r"Ø(\d+\s*x\s*\d+)尼龙\s*\(nylon\)", r"Ø\1 nylon", text, flags=re.I)
    text = text.replace("迪鼎DiDing", "DiDing")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def english_label(row):
    chinese = str(row.get("B", "")).strip()
    for key, translated in LABELS.items():
        if chinese.startswith(key):
            return translated
    english = str(row.get("C", "")).strip()
    if re.search(r"[A-Za-z]{3}", english) and not re.fullmatch(r"[A-Za-z/().%\s]+", english):
        return clean_text(english)
    if re.search(r"[A-Za-z]{3}", english) and len(english.split()) > 1:
        fixes = {
            "Rated traction weight": "Rated load capacity",
            "Load centre": "Load center distance",
            "Travel spees,with/without load": "Travel speed, laden/unladen",
            "Fork Height,Lowered": "Fork height, lowered",
            "Min.Ground clearance": "Ground clearance at center of wheelbase",
            "Min.Turning radius": "Minimum turning radius",
            "Noise level at operator 'sear": "Noise level at operator's ear",
        }
        return fixes.get(english, clean_text(english))
    return clean_text(chinese)


def normalize_unit(value):
    unit = clean_text(value)
    match = re.search(r"\(([^()]*)\)", unit)
    if match:
        unit = match.group(1)
    unit = re.sub(r"^[A-Za-z0-9]+\s*", "", unit).strip()
    fixes = {
        "Km/h": "km/h",
        "kw": "kW",
        "Mpa": "MPa",
        "dB (A)": "dB(A)",
    }
    return fixes.get(unit, unit)


def row_dict(cells):
    return {re.match(r"[A-Z]+", cell["cell"]).group(): cell["value"] for cell in cells}


def section_title(value):
    value = str(value or "")
    for key, title in SECTION_LABELS.items():
        if value.startswith(key):
            return title
    return None


def read_sheet(data, suffix, sheet_title):
    normalized_suffix = suffix.replace("/", "\\")
    for workbook in data["workbooks"]:
        if workbook["path"].endswith(normalized_suffix):
            for sheet in workbook["sheets"]:
                if sheet["title"] == sheet_title:
                    return [row_dict(row) for row in sheet["cells"]]
    raise KeyError(f"Missing sheet: {suffix} / {sheet_title}")


def extract_profile(rows, value_columns, fallback_columns=(), unit_column="D"):
    sections = []
    current = {"title": "Characteristics", "rows": []}
    sections.append(current)
    for row in rows:
        marker = str(row.get("A", ""))
        heading = section_title(row.get("B")) if not re.match(r"^\d+\.\d+", marker) else None
        if heading:
            current = {"title": heading, "rows": []}
            sections.append(current)
            continue
        if not re.match(r"^\d+\.\d+", marker):
            continue
        name = english_label(row)
        if name in {"Manufacturer", "Model", "Brand", ""}:
            continue
        values = [clean_text(row.get(column)) for column in value_columns]
        values = [value for value in values if value and value != "/"]
        if not values:
            values = [clean_text(row.get(column)) for column in fallback_columns]
            values = [value for value in values if value and value != "/"]
        if not values:
            continue
        if len(values) == 2 and values[0] != values[1]:
            value = f"Single mast: {values[0]}; 2-stage standard mast: {values[1]}"
        else:
            value = " / ".join(dict.fromkeys(values))
        unit = normalize_unit(row.get(unit_column, ""))
        current["rows"].append({"name": name, "unit": unit, "value": value})
    return [section for section in sections if section["rows"]]


def rows(*items):
    return [{"name": name, "unit": unit, "value": value} for name, unit, value in items]


def manual_specs():
    return {
        "efl1200r3": [{"title": "Specifications", "rows": rows(
            ("Rated load capacity", "t", "1.2"),
            ("Service weight with battery", "kg", "1,940"),
            ("Mast height, lowered", "mm", "1,975"),
            ("Lift height", "mm", "3,000"),
            ("Overall length", "mm", "2,570"),
            ("Overall width", "mm", "922"),
            ("Fork dimensions (thickness x width x length)", "mm", "35 x 100 x 920"),
            ("Fork carriage width", "mm", "825"),
            ("Turning radius", "mm", "1,490"),
            ("Travel speed, laden/unladen", "km/h", "9 / 10"),
            ("Lift speed, laden/unladen", "m/s", "0.15 / 0.22"),
        )}],
        "efl2000r3": [{"title": "Specifications", "rows": rows(
            ("Power source", "", "Storage battery"),
            ("Rated load capacity", "kg", "2,000"),
            ("Service weight", "kg", "3,760"),
            ("Tire type, front/rear", "", "Solid tires"),
            ("Overall length, excluding forks", "mm", "2,105"),
            ("Overall width at frame", "mm", "1,100"),
            ("Overhead guard height", "mm", "2,055"),
            ("Lift height", "mm", "3,000"),
            ("Minimum turning radius", "mm", "1,690"),
            ("Maximum gradeability, laden", "%", "15"),
        )}],
        "r4efl1t": [
            {"title": "Dimensions and performance", "rows": rows(
                ("Rated load capacity", "kg", "1,200"), ("Lift height", "mm", "3,000"),
                ("Load center distance", "mm", "500"), ("Ground clearance under mast, lowered", "mm", "75"),
                ("Turning radius", "mm", "1,900"), ("Right-angle stacking aisle width", "mm", "3,200 (1,000 x 1,000 pallet; 200 clearance)"),
                ("Mast height, lowered", "mm", "2,050"), ("Overall length", "mm", "1,850"),
                ("Overall width", "mm", "970"), ("Overhead guard height", "mm", "1,860"),
                ("Maximum fork spread", "mm", "870"), ("Maximum height during operation", "mm", "3,900"),
                ("Fork dimensions (thickness x width x length)", "mm", "32 x 100 x 920"),
                ("Minimum fork spacing", "mm", "200"), ("Lift speed, laden/unladen", "mm/s", "230 / 250"),
                ("Travel speed, laden/unladen", "km/h", "10 / 12"), ("Gradeability, laden/unladen", "%", "10 / 15"),
                ("Mast tilt, forward/backward", "deg", "6 / 12"),
            )},
            {"title": "Powertrain and chassis", "rows": rows(
                ("Tire type", "", "Solid tires"), ("Front tire size", "", "16 x 6-8"),
                ("Rear tire size", "", "15 x 4 1/2-8"), ("Service weight with battery", "kg", "1,690"),
                ("Operator position", "", "Seated"), ("Wheelbase", "mm", "1,230"),
                ("Tread, front/rear", "mm", "820 / 810"), ("Charger input voltage", "V", "220"),
                ("Rated voltage", "V", "48"), ("Ground clearance at center of wheelbase", "mm", "100"),
                ("Lithium battery capacity", "Ah", "150"), ("Lift motor rating", "kW", "4.0"),
                ("Drive motor rating", "kW", "3.0"), ("Power source", "", "Lithium battery"),
                ("Steering", "", "Hydraulic power steering"), ("Counterweight", "", "One-piece cast"),
                ("Charging time", "h", "6 / 8"), ("Attachments", "", "Available to project requirements"),
            )},
        ],
        "r4efl3t": [
            {"title": "Dimensions and performance", "rows": rows(
                ("Rated load capacity", "kg", "3,000"), ("Lift height", "mm", "3,000"),
                ("Load center distance", "mm", "500"), ("Ground clearance under mast, lowered", "mm", "120"),
                ("Turning radius", "mm", "2,400"), ("Right-angle stacking aisle width", "mm", "4,664 (1,000 x 1,000 pallet; 200 clearance)"),
                ("Mast height, lowered", "mm", "2,090"), ("Overall length", "mm", "2,600"),
                ("Overall width", "mm", "1,240"), ("Overhead guard height", "mm", "2,100"),
                ("Maximum fork spread", "mm", "1,100"), ("Maximum height during operation", "mm", "4,255"),
                ("Fork dimensions (thickness x width x length)", "mm", "45 x 125 x 1,220"),
                ("Minimum fork spacing", "mm", "245"), ("Lift speed, laden/unladen", "mm/s", "230 / 250"),
                ("Travel speed, laden/unladen", "km/h", "10 / 12"), ("Gradeability, laden/unladen", "%", "10 / 15"),
                ("Mast tilt, forward/backward", "deg", "6 / 12"),
            )},
            {"title": "Powertrain and chassis", "rows": rows(
                ("Tire type", "", "Pneumatic tires"), ("Front tire size", "", "23 x 9-10"),
                ("Rear tire size", "", "18 x 7-8"), ("Service weight with battery", "kg", "4,300"),
                ("Operator position", "", "Seated"), ("Wheelbase", "mm", "1,640"),
                ("Tread, front/rear", "mm", "1,020 / 990"), ("Charger input voltage", "V", "220"),
                ("Rated voltage", "V", "72"), ("Ground clearance at center of wheelbase", "mm", "140"),
                ("Lead-acid battery capacity", "Ah", "500"), ("Lift motor rating", "kW", "15"),
                ("Drive motor rating", "kW", "11"), ("Power source", "", "Lead-acid traction battery"),
                ("Steering", "", "Hydraulic power steering"), ("Counterweight", "", "One-piece cast"),
                ("Charging time", "h", "8 / 10"), ("Attachments", "", "Available to project requirements"),
            )},
        ],
        "r4efl12t": [{"title": "Specifications", "rows": rows(
            ("Power source", "", "Storage battery"), ("Rated load capacity", "kg", "12,000"),
            ("Service weight", "kg", "15,800"), ("Tire type, front/rear", "", "Solid tires"),
            ("Overall length, excluding forks", "mm", "4,415"), ("Overall width at frame", "mm", "2,250"),
            ("Overhead guard height", "mm", "2,640"), ("Lift height", "mm", "3,000"),
            ("Minimum turning radius", "mm", "3,850"), ("Maximum gradeability, laden", "%", "10"),
        )}],
        "r4efl5t": [
            {"title": "Dimensions and performance", "rows": rows(
                ("Rated load capacity", "kg", "5,000"), ("Load center distance", "mm", "500"),
                ("Maximum lift height", "mm", "3,000"), ("Free lift height", "mm", "155"),
                ("Fork dimensions (length x width x thickness)", "mm", "1,070 x 150 x 50"),
                ("Mast tilt, forward/backward", "deg", "6 / 10"),
                ("Overall length to fork face", "mm", "3,005"), ("Overall width", "mm", "1,479"),
                ("Mast height, lowered", "mm", "2,245"), ("Mast height, extended", "mm", "4,066"),
                ("Overhead guard height", "mm", "2,353"), ("Minimum turning radius", "mm", "2,730"),
                ("Front overhang", "mm", "540"), ("Front wheel track", "mm", "1,228"),
                ("Rear wheel track", "mm", "1,130"), ("Minimum ground clearance, frame/mast", "mm", "150 / 175"),
                ("Wheelbase", "mm", "2,000"), ("Fork spread", "mm", "305 / 1,335"),
                ("Right-angle stacking aisle, 1,000 x 1,200 pallet", "mm", "4,540"),
                ("Right-angle stacking aisle, 800 x 1,200 pallet", "mm", "4,670"),
                ("Travel speed, unladen/laden", "km/h", "14.5 / 14"),
                ("Lift speed, unladen/laden", "mm/s", "400 / 250"),
                ("Maximum gradeability, laden", "%", "15"), ("Descent rate", "mm/s", "Laden <=600; unladen >=300"),
            )},
            {"title": "Powertrain and chassis", "rows": rows(
                ("Service weight", "kg", "7,320"), ("Front solid tire", "", "250-15"),
                ("Rear solid tire", "", "21 x 8-9"), ("Drive motor rating", "kW", "18"),
                ("Lift motor rating", "kW", "25"), ("Controller", "", "Fanji / Inmotion"),
                ("Battery voltage / capacity", "V/Ah", "80 / 700"), ("Working pressure", "MPa", "20"),
            )},
        ],
        "mpt5tn": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "5,000"), ("Minimum fork height", "mm", "85"),
            ("Maximum fork height", "mm", "185"), ("Maximum lift travel", "mm", "100"),
            ("Overall fork width", "mm", "540 / 685"), ("Inside fork spacing", "mm", "180 / 325"),
            ("Fork length", "mm", "1,150 / 1,220"), ("Single fork width", "mm", "180"),
            ("Fork thickness", "mm", "60"), ("Overall length", "mm", "1,670"),
            ("Overall height", "mm", "1,230"), ("Hydraulic piston rod diameter", "mm", "Ø45"),
            ("Tandem load wheel size", "mm", "Ø80 x 70"), ("Steering wheel size", "mm", "Ø180 x 50"),
            ("Wheel material", "", "PU / nylon / iron"), ("Service weight", "kg", "126"),
            ("Gross weight, 4 units per pallet", "kg", "517"),
            ("Packing size", "mm", "5T 685 x 1,220: 2,000 x 700 x 680"),
        )}],
        "mpjsc1500": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,500"), ("Minimum fork height", "mm", "85"),
            ("Maximum fork height", "mm", "800"), ("Maximum lift travel", "mm", ">=715"),
            ("Overall fork width", "mm", "540 / 680"), ("Inside fork spacing", "mm", "220 / 360"),
            ("Fork length", "mm", "1,150"), ("Single fork width", "mm", "160"),
            ("Fork thickness", "mm", "50"), ("Overall length", "mm", "1,540"),
            ("Overall height", "mm", "1,260"), ("Load wheel size", "mm", "Ø80 x 70"),
            ("Steering wheel size", "mm", "Ø180 x 50"), ("Minimum turning diameter", "mm", "1,260"),
            ("Wheel material", "", "PU / nylon"), ("Service weight", "kg", "122 / 128"),
            ("Gross weight, 4 units per pallet", "kg", "500 / 524"),
            ("Packing size", "mm", "ACHLT-D1.5T 680 x 1,150: 2,200 x 700 x 1,100"),
        )}],
        "mpjtsc1500": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,500"), ("Minimum fork height", "mm", "85"),
            ("Maximum fork height", "mm", "800"), ("Maximum lift travel", "mm", ">=715"),
            ("Overall fork width", "mm", "540 / 680"), ("Inside fork spacing", "mm", "220 / 360"),
            ("Fork length", "mm", "1,150"), ("Single fork width", "mm", "160"),
            ("Fork thickness", "mm", "50"), ("Overall length", "mm", "1,540"),
            ("Overall height", "mm", "1,260"), ("Load wheel size", "mm", "Ø80 x 70"),
            ("Steering wheel size", "mm", "Ø150 x 50"), ("Minimum turning diameter", "mm", "1,260"),
            ("Wheel material", "", "PU / nylon"), ("Service weight", "kg", "108 / 114"),
            ("Gross weight, 4 units per pallet", "kg", "448 / 472"),
            ("Packing size", "mm", "ACHLT-S1.5T 680 x 1,150: 1,920 x 700 x 800"),
        )}],
        "sc1016": [{"title": "Specifications", "rows": rows(
            ("Service weight", "kg", "200"), ("Lift height", "mm", "1,600; customizable"),
            ("Overall width", "mm", "860"), ("Overall length", "mm", "1,500"),
            ("Motor power", "W", "700"), ("Fork length", "mm", "1,150; customizable"),
            ("Fork width", "mm", "550"), ("Rated load capacity", "kg", "1,000"),
            ("Overall height", "mm", "1,800"), ("Battery", "", "48 V / 10 Ah LiFePO4"),
        )}],
        "qes12e": [{"title": "Specifications", "rows": rows(
            ("Drive type", "", "Horizontal drive unit"), ("Operation mode", "", "Pedestrian"),
            ("Rated load capacity", "kg", "1,200"), ("Load center distance", "mm", "600"),
            ("Wheelbase", "mm", "1,210"), ("Service weight without battery", "kg", "397"),
            ("Service weight with battery", "kg", "437"), ("Wheel material", "", "PU"),
            ("Front wheel size", "mm", "Ø80"), ("Drive wheel size", "mm", "Ø210"),
            ("Stabilizer wheel size", "mm", "152"), ("Number of wheels", "pcs", "4"),
            ("Mast height, lowered", "mm", "2,030"), ("Maximum vehicle height", "mm", "3,500"),
            ("Fork lift height", "mm", "3,000"), ("Overall length", "mm", "1,750"),
            ("Single fork width", "mm", "160"), ("Body width", "mm", "820"),
            ("Fork length", "mm", "1,125"), ("Overall fork width", "mm", "680"),
            ("Minimum fork height", "mm", "90"), ("Ground clearance", "mm", "35"),
            ("Turning radius, excluding handle", "mm", "1,385"), ("Body height", "mm", "810"),
        )}],
        "qes15e": [{"title": "Specifications", "rows": rows(
            ("Drive type", "", "Horizontal drive unit"), ("Operation mode", "", "Pedestrian"),
            ("Rated load capacity", "kg", "1,500"), ("Load center distance", "mm", "600"),
            ("Wheelbase", "mm", "1,235"), ("Service weight without battery", "kg", "450"),
            ("Service weight with battery", "kg", "490"), ("Wheel material", "", "PU"),
            ("Front wheel size", "mm", "Ø80"), ("Drive wheel size", "mm", "Ø210"),
            ("Stabilizer wheel size", "mm", "152"), ("Number of wheels", "pcs", "4"),
            ("Mast height, lowered", "mm", "2,030"), ("Maximum vehicle height", "mm", "3,500"),
            ("Fork lift height", "mm", "3,000"), ("Overall length", "mm", "1,750"),
            ("Single fork width", "mm", "160"), ("Body width", "mm", "800"),
            ("Fork length", "mm", "1,125"), ("Overall fork width", "mm", "680"),
            ("Minimum fork height", "mm", "90"), ("Ground clearance", "mm", "35"),
            ("Turning radius, excluding handle", "mm", "1,440"), ("Body height", "mm", "890"),
        )}],
        "qes15lie": [{"title": "Specifications", "rows": rows(
            ("Drive type", "", "Horizontal drive unit"), ("Operation mode", "", "Pedestrian"),
            ("Rated load capacity", "kg", "1,500"), ("Load center distance", "mm", "600"),
            ("Wheelbase", "mm", "1,235"), ("Service weight without battery", "kg", "450"),
            ("Service weight with battery", "kg", "470"), ("Wheel material", "", "PU"),
            ("Front wheel size", "mm", "Ø80"), ("Drive wheel size", "mm", "Ø210"),
            ("Stabilizer wheel size", "mm", "152"), ("Number of wheels", "pcs", "4"),
            ("Mast height, lowered", "mm", "2,030"), ("Maximum vehicle height", "mm", "3,500"),
            ("Fork lift height", "mm", "3,000"), ("Overall length", "mm", "1,750"),
            ("Single fork width", "mm", "160"), ("Body width", "mm", "800"),
            ("Fork length", "mm", "1,125"), ("Overall fork width", "mm", "680"),
            ("Minimum fork height", "mm", "90"), ("Ground clearance", "mm", "35"),
            ("Turning radius, excluding handle", "mm", "1,440"), ("Body height", "mm", "890"),
        )}],
        "qed1530": [{"title": "Specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,500"), ("Lift height", "mm", "3,000; customizable"),
            ("Power", "W", "2,200"), ("Operation mode", "", "Electric"),
            ("Travel speed, laden/unladen", "km/h", "3.5 / 4.0"),
            ("Lift motor power", "W", "750"), ("Lift speed, laden/unladen", "mm/s", "81 / 130"),
            ("Service brake", "", "Electromagnetic"), ("Battery", "", "24 V / 80 Ah; optional"),
        )}],
        "ept30": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "300"), ("Maximum table height", "mm", "880"),
            ("Minimum table height", "mm", "290"), ("Platform dimensions", "mm", "850 x 500"),
            ("Wheel size", "mm", "Ø125 x 40"), ("Overall length", "mm", "1,145"),
            ("Handle height", "mm", "920"), ("Lift speed, laden/unladen", "mm/s", "65 / 94"),
            ("Lowering speed, laden/unladen", "mm/s", "98 / 74"),
            ("Lifting cycles per full charge", "cycles", "120"),
            ("Battery configuration", "", "4 x 12 V / 15 Ah"), ("Lift stroke", "mm", "590"),
            ("Lift motor rating", "kW", "0.8"),
            ("Charging time with built-in 24 V / 3 A charger", "h", "8.5"),
            ("Approximate lifting time", "s", "10"), ("Net weight", "kg", "116"),
        )}],
        "ept50": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "500"), ("Maximum table height", "mm", "1,025"),
            ("Minimum table height", "mm", "440"), ("Platform dimensions", "mm", "1,010 x 520"),
            ("Wheel size", "mm", "Ø150 x 48"), ("Overall length", "mm", "1,305"),
            ("Handle height", "mm", "970"), ("Lift speed, laden/unladen", "mm/s", "65 / 94"),
            ("Lowering speed, laden/unladen", "mm/s", "98 / 74"),
            ("Lifting cycles per full charge", "cycles", "100"),
            ("Battery configuration", "", "2 x 12 V / 24 Ah"), ("Lift stroke", "mm", "585"),
            ("Lift motor rating", "kW", "0.8"),
            ("Charging time with built-in 24 V / 3 A charger", "h", "8.5"),
            ("Approximate lifting time", "s", "10"), ("Net weight", "kg", "157"),
        )}],
        "eptd35": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "350"), ("Maximum table height", "mm", "1,300"),
            ("Minimum table height", "mm", "370"), ("Platform dimensions", "mm", "910 x 500"),
            ("Wheel size", "mm", "Ø125 x 40"), ("Overall length", "mm", "1,210"),
            ("Handle height", "mm", "920"), ("Lift speed, laden/unladen", "mm/s", "90 / 110"),
            ("Lowering speed, laden/unladen", "mm/s", "100 / 90"),
            ("Lifting cycles per full charge", "cycles", "100"),
            ("Battery configuration", "", "4 x 12 V / 15 Ah"), ("Lift stroke", "mm", "930"),
            ("Lift motor rating", "kW", "0.8"),
            ("Charging time with built-in 24 V / 3 A charger", "h", "8.5"),
            ("Approximate lifting time", "s", "10"), ("Net weight", "kg", "142"),
        )}],
        "exl0412": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "400"), ("Overall height", "mm", "1,425"),
            ("Lift height", "mm", "1,115"), ("Platform height, lowered", "mm", "85"),
            ("Platform top height", "mm", "1,200"), ("Overall width", "mm", "600"),
            ("Platform length", "mm", "650"), ("Platform width", "mm", "576"),
            ("Steering wheel size", "mm", "Ø127 x 40"), ("Load wheel size", "mm", "Ø75 x 40"),
            ("Lift speed, unladen", "mm/s", "185"), ("Lowering speed, unladen", "mm/s", "0-75"),
            ("Lift speed, laden", "mm/s", "0-115"), ("Battery", "", "12 V / 60 Ah"),
            ("Lift motor", "", "12 V / 700 W"),
        )}],
        "exl0415": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "400"), ("Overall height", "mm", "1,725"),
            ("Lift height", "mm", "1,415"), ("Platform height, lowered", "mm", "85"),
            ("Platform top height", "mm", "1,500"), ("Overall width", "mm", "600"),
            ("Platform length", "mm", "650"), ("Platform width", "mm", "576"),
            ("Steering wheel size", "mm", "Ø127 x 40"), ("Load wheel size", "mm", "Ø75 x 40"),
            ("Lift speed, unladen", "mm/s", "185"), ("Lowering speed, unladen", "mm/s", "0-75"),
            ("Lift speed, laden", "mm/s", "0-115"), ("Battery", "", "12 V / 60 Ah"),
            ("Lift motor", "", "12 V / 700 W"),
        )}],
        "pt15": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "150"), ("Table height, lowered", "mm", "220"),
            ("Table height, raised", "mm", "720"), ("Platform dimensions", "mm", "700 x 450"),
            ("Wheel size", "mm", "Ø100 x 25"), ("Pump strokes to maximum height", "strokes", "<=28"),
            ("Service weight", "kg", "46"), ("Handle height", "mm", "950"),
        )}],
        "pt30": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "300"), ("Table height, lowered", "mm", "285"),
            ("Table height, raised", "mm", "880"), ("Platform dimensions", "mm", "815 x 500"),
            ("Wheel size", "mm", "Ø125 x 40"), ("Pump strokes to maximum height", "strokes", "<=27"),
            ("Service weight", "kg", "77"), ("Handle height", "mm", "990"),
        )}],
        "pt50": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "500"), ("Table height, lowered", "mm", "285"),
            ("Table height, raised", "mm", "880"), ("Platform dimensions", "mm", "815 x 500"),
            ("Wheel size", "mm", "Ø125 x 40"), ("Pump strokes to maximum height", "strokes", "<=27"),
            ("Service weight", "kg", "81"), ("Handle height", "mm", "990"),
        )}],
        "pt75": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "750"), ("Table height, lowered", "mm", "420"),
            ("Table height, raised", "mm", "1,000"), ("Platform dimensions", "mm", "1,000 x 510"),
            ("Wheel size", "mm", "Ø147 x 50"), ("Pump strokes to maximum height", "strokes", "<=45"),
            ("Service weight", "kg", "125"), ("Handle height", "mm", "990"),
        )}],
        "pt100": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,000"), ("Table height, lowered", "mm", "380"),
            ("Table height, raised", "mm", "1,000"), ("Platform dimensions", "mm", "1,016 x 510"),
            ("Wheel size", "mm", "Ø125 x 50"), ("Pump strokes to maximum height", "strokes", "<=82"),
            ("Service weight", "kg", "140"), ("Handle height", "mm", "980"),
        )}],
        "ptd35": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "350"), ("Table height, lowered", "mm", "355"),
            ("Table height, raised", "mm", "1,300"), ("Platform dimensions", "mm", "910 x 500"),
            ("Wheel size", "mm", "Ø125 x 40"), ("Pump strokes to maximum height", "strokes", "<=53"),
            ("Service weight", "kg", "110"), ("Handle height", "mm", "975"),
        )}],
        "ptd70": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "700"), ("Table height, lowered", "mm", "445"),
            ("Table height, raised", "mm", "1,500"), ("Platform dimensions", "mm", "1,220 x 610"),
            ("Wheel size", "mm", "Ø125 x 40"), ("Pump strokes to maximum height", "strokes", "<=97"),
            ("Service weight", "kg", "195"), ("Handle height", "mm", "980"),
        )}],
        "sl0485": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "400"), ("Overall height", "mm", "1,075"),
            ("Lift height", "mm", "765"), ("Platform height, lowered", "mm", "85"),
            ("Platform top height", "mm", "850"), ("Overall width", "mm", "600"),
            ("Platform length", "mm", "650"), ("Platform width", "mm", "576"),
            ("Fork dimensions", "mm", "650 x 110"), ("Steering wheel size", "mm", "Ø127 x 40"),
            ("Load wheel size", "mm", "Ø75 x 40"), ("Service weight", "kg", "75"),
        )}],
        "sl0412": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "400"), ("Overall height", "mm", "1,425"),
            ("Lift height", "mm", "1,115"), ("Platform height, lowered", "mm", "85"),
            ("Platform top height", "mm", "1,200"), ("Overall width", "mm", "600"),
            ("Platform length", "mm", "650"), ("Platform width", "mm", "576"),
            ("Fork dimensions", "mm", "650 x 110"), ("Steering wheel size", "mm", "Ø127 x 40"),
            ("Load wheel size", "mm", "Ø75 x 40"), ("Service weight", "kg", "81"),
        )}],
        "sl0415": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "400"), ("Overall height", "mm", "1,725"),
            ("Lift height", "mm", "1,415"), ("Platform height, lowered", "mm", "85"),
            ("Platform top height", "mm", "1,500"), ("Overall width", "mm", "600"),
            ("Platform length", "mm", "650"), ("Platform width", "mm", "576"),
            ("Fork dimensions", "mm", "650 x 110"), ("Steering wheel size", "mm", "Ø127 x 40"),
            ("Load wheel size", "mm", "Ø75 x 40"), ("Service weight", "kg", "91"),
        )}],
        "bed1016": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,000"), ("Overall length", "mm", "1,778"),
            ("Overall width", "mm", "777"), ("Mast height, lowered", "mm", "1,978"),
            ("Maximum mast height in operation", "mm", "1,978"), ("Lift height", "mm", "1,600"),
            ("Fork dimensions", "mm", "60 x 160 x 1,150"), ("Front wheel size", "mm", "Ø180 x 50"),
            ("Rear wheel size", "mm", "Ø74 x 70"), ("Service weight with battery", "kg", "305"),
            ("Battery weight", "kg", "35"), ("Lift motor rating, S3 10%", "kW", "1.6"),
            ("Battery voltage / capacity", "V/Ah", "12 / 150"),
        )}],
        "bed1025": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,000"), ("Overall length", "mm", "1,786"),
            ("Overall width", "mm", "777"), ("Mast height, lowered", "mm", "1,828"),
            ("Maximum mast height in operation", "mm", "3,066"), ("Lift height", "mm", "2,500"),
            ("Fork dimensions", "mm", "60 x 160 x 1,150"), ("Front wheel size", "mm", "Ø180 x 50"),
            ("Rear wheel size", "mm", "Ø74 x 70"), ("Service weight with battery", "kg", "364"),
            ("Battery weight", "kg", "35"), ("Lift motor rating, S3 10%", "kW", "1.6"),
            ("Battery voltage / capacity", "V/Ah", "12 / 150"),
        )}],
        "bed1030": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,000"), ("Overall length", "mm", "1,786"),
            ("Overall width", "mm", "777"), ("Mast height, lowered", "mm", "2,078"),
            ("Maximum mast height in operation", "mm", "3,566"), ("Lift height", "mm", "3,000"),
            ("Fork dimensions", "mm", "60 x 160 x 1,150"), ("Front wheel size", "mm", "Ø180 x 50"),
            ("Rear wheel size", "mm", "Ø74 x 70"), ("Service weight with battery", "kg", "380"),
            ("Battery weight", "kg", "35"), ("Lift motor rating, S3 10%", "kW", "1.6"),
            ("Battery voltage / capacity", "V/Ah", "12 / 150"),
        )}],
        "bed1516": [{"title": "Technical specifications", "rows": rows(
            ("Rated load capacity", "kg", "1,500"), ("Overall length", "mm", "1,778"),
            ("Overall width", "mm", "844"), ("Mast height, lowered", "mm", "1,978"),
            ("Maximum mast height in operation", "mm", "1,978"), ("Lift height", "mm", "1,600"),
            ("Fork dimensions", "mm", "60 x 182 x 1,150"), ("Front wheel size", "mm", "Ø180 x 50"),
            ("Rear wheel size", "mm", "Ø74 x 93"), ("Service weight with battery", "kg", "429"),
            ("Battery weight", "kg", "35"), ("Lift motor rating, S3 10%", "kW", "1.6"),
            ("Battery voltage / capacity", "V/Ah", "12 / 150"),
        )}],
    }


def main():
    data = json.loads(SOURCE_DATA.read_text(encoding="utf-8"))
    specs = manual_specs()
    profiles = [
        ("WEP20J.xlsx", "WEP20J", [("wep20j", ("E",), (), "D")]),
        ("REP3000E.xlsx", "CBDE", [("rep3000e", ("E",), (), "D")]),
        ("ATEP3000Y.xlsx", "CBDY", [("atep3000y", ("E", "F"), (), "D")]),
        ("WES1500A & WES1600A.xlsx", "CDDA", [("wes1500a", ("E", "F"), (), "D"), ("wes1600a", ("G", "H"), ("E",), "D")]),
        ("WES1500JP.xlsx", "WES1500JP", [("wes1500jp", ("E", "F"), (), "D")]),
        ("WES2000A.xlsx", "CDD20A", [("wes2000a", ("D", "E"), (), "C")]),
        ("RES1500D & RES2000D.xlsx", "CDDD", [("res1500d", ("E", "F"), (), "D"), ("res2000d", ("G", "H"), ("E",), "D")]),
        ("RES1500E & RES2000E.xlsx", "CDDE", [("res1500e", ("E", "F"), (), "D"), ("res2000e", ("G", "H"), ("E",), "D")]),
        ("RES1500G.xlsx", "CDDG", [("res1500g", ("E", "F"), (), "D")]),
        ("参数表合集.xlsx", "JWCES500J", [("wces500j", ("D", "E"), (), "C")]),
        ("参数表合集.xlsx", "WCES1000J", [("wces1000j", ("E", "F"), (), "D")]),
        ("参数表合集.xlsx", "WCES1300J", [("wces1300j", ("E", "F"), (), "D")]),
        ("参数表合集.xlsx", "WCES1500J", [("wces1500j", ("D", "E"), (), "C")]),
        ("RCES1000B&RCES1500E&RCES2000E.xlsx", "RCES1000B", [("rces1000b", ("E", "F"), (), "D")]),
        ("RCES1000B&RCES1500E&RCES2000E.xlsx", "RCES1500E & RCES2000E", [("rces1500e", ("E", "F"), (), "D"), ("rces2000e", ("G", "H"), ("E",), "D")]),
        ("HES1500A & HES2000A.xlsx", "CQDA", [("hes1500a", ("D", "E"), (), "C"), ("hes2000a", ("F", "G"), ("D",), "C")]),
    ]
    for suffix, sheet, models in profiles:
        source_rows = read_sheet(data, suffix, sheet)
        for slug, value_columns, fallback_columns, unit_column in models:
            specs[slug] = extract_profile(source_rows, value_columns, fallback_columns, unit_column)
    OUTPUT.write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote English specification tables for {len(specs)} products to {OUTPUT}")


if __name__ == "__main__":
    main()
