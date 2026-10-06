from pathlib import Path


SOURCE_ROOT = Path(
    "F:/business and work/sale detail/\u957f\u5174\u5723\u529b/LEXYGO/"
    "CODEX\u62d3\u5c55\u4e1a\u52a1/\u53c9\u8f66+\u5806\u9ad8\u8f66/\u5806\u9ad8\u8f66\u5ba3\u4f20\u518c\u5236\u4f5c/WEB"
)

COMPANY = {
    "brand": "LEXYGO",
    "display_name": "LEXYGO Material Handling Equipment",
    "legal_name": "Zhejiang Changxing Shengli Intelligent Machinery Co., Ltd.",
    "email": "info@lexygolift.com",
    "telephone": "+86-159 6826 3134",
    "telephone_href": "+8615968263134",
    "whatsapp": "+63-915-0522-944",
    "whatsapp_href": "639150522944",
    "address": "No. 4 Workshop, No. 188 Baixi Road, Changxing Development Zone, Huzhou, Zhejiang, China",
    "location": "Huzhou, Zhejiang, China",
    "website": "www.lexygolift.com",
    "domain": "https://www.lexygolift.com",
}

CATEGORIES = {
    "electric-pallet-trucks": {
        "name": "Electric Pallet Trucks",
        "short": "Move palletized loads efficiently across warehouses, docks, and mixed surfaces.",
        "answer": "Choose a walkie truck for compact indoor routes, a rider truck for longer travel, or an all-terrain model for uneven surfaces.",
        "image": "wep20j.png",
    },
    "electric-pallet-stackers": {
        "name": "Electric Pallet Stackers",
        "short": "Lift, place, and retrieve pallets in low- to medium-height storage areas.",
        "answer": "Select by rated load, lift height, aisle width, load overhang, and whether the operator walks or rides.",
        "image": "wes1500a.png",
    },
    "electric-forklifts": {
        "name": "Electric Forklifts",
        "short": "Electric counterbalanced forklifts for indoor logistics and industrial handling.",
        "answer": "Three-wheel models prioritize maneuverability. Four-wheel models prioritize stability and broader capacity options.",
        "image": "r4efl3t.png",
    },
    "manual-pallet-trucks": {
        "name": "Manual Pallet Trucks",
        "short": "Simple, dependable pallet movement and manual high-lift handling.",
        "answer": "Use a standard pallet truck for horizontal movement or a high-lift model when ergonomic working height is required.",
        "image": "mpt5tn.png",
    },
    "warehouse-equipment": {
        "name": "Warehouse Equipment",
        "short": "Compact lifting tables, platform trucks, and support equipment for material flow.",
        "answer": "Match platform size, lifting range, mobility, and duty cycle to the workstation and load.",
        "image": "sc1016.png",
    },
}


def product(slug, model, name, category, image, capacity, lift, operation, best_for, specs=None, note=None):
    return {
        "slug": slug,
        "model": model,
        "name": name,
        "category": category,
        "image": image,
        "capacity": capacity,
        "lift": lift,
        "operation": operation,
        "best_for": best_for,
        "specs": specs or {},
        "note": note or "Final configuration, dimensions, battery, mast, and compliance documentation are confirmed in the quotation.",
    }


PRODUCTS = [
    product(
        "wep20j", "WEP20J", "2.0 t Walkie Electric Pallet Truck", "electric-pallet-trucks", "wep20j.png",
        "2,000 kg", "205 mm", "Walk-behind", "Short and medium indoor pallet routes",
        {"Load center": "600 mm", "Wheel material": "PU", "Travel mode": "Walkie"},
    ),
    product(
        "rep3000e", "REP3000E", "3.0 t Rider Electric Pallet Truck", "electric-pallet-trucks", "rep3000e.png",
        "3,000 kg", "205 mm", "Ride-on", "Longer routes and frequent dock-to-storage travel",
        {"Load center": "600 mm", "Service weight": "670 kg", "Travel mode": "Rider"},
    ),
    product(
        "atep3000y", "ATEP3000Y", "3.0 t All-Terrain Electric Pallet Truck", "electric-pallet-trucks", "atep3000y.png",
        "3,000 kg", "205 mm", "Walk-behind", "Uneven yards, construction supply, and mixed surfaces",
        {"Load center": "600 mm", "Service weight": "268 kg", "Drive/load wheels": "Rubber / nylon"},
    ),
    product(
        "wes1500a", "WES1500A", "1.5 t Walkie Electric Stacker", "electric-pallet-stackers", "wes1500a.png",
        "1,500 kg", "1,600-3,500 mm", "Walk-behind", "Compact pallet stacking in narrow work areas",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Travel mode": "Walkie"},
    ),
    product(
        "wes1600a", "WES1600A", "1.6 t Walkie Electric Stacker", "electric-pallet-stackers", "wes1600a.png",
        "1,600 kg", "1,600-3,500 mm", "Walk-behind", "Indoor stacking where extra rated capacity is needed",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Travel mode": "Walkie"},
    ),
    product(
        "wes1500jp", "WES1500JP", "1.5 t Walkie Electric Stacker", "electric-pallet-stackers", "wes1500jp.png",
        "1,500 kg", "1,600-3,500 mm", "Walk-behind", "Routine pallet placement and retrieval",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Travel mode": "Walkie"},
    ),
    product(
        "wes2000a", "WES2000A", "2.0 t Walkie Electric Stacker", "electric-pallet-stackers", "wes2000a.png",
        "2,000 kg", "1,600-3,500 mm", "Walk-behind", "Heavier pallet stacking on level indoor floors",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Travel mode": "Walkie"},
    ),
    product(
        "res1500d", "RES1500D", "1.5 t Rider Electric Stacker", "electric-pallet-stackers", "res1500d.png",
        "1,500 kg", "1,600-3,500 mm", "Stand-on", "Frequent stacking with longer travel distances",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Operator position": "Stand-on"},
    ),
    product(
        "res2000d", "RES2000D", "2.0 t Rider Electric Stacker", "electric-pallet-stackers", "res2000d.png",
        "2,000 kg", "1,600-3,500 mm", "Stand-on", "High-throughput pallet movement and stacking",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Operator position": "Stand-on"},
    ),
    product(
        "res1500e", "RES1500E", "1.5 t Rider Electric Stacker", "electric-pallet-stackers", "res1500e.png",
        "1,500 kg", "1,600-3,500 mm", "Stand-on", "Distribution centers with repeated travel and lift cycles",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Operator position": "Stand-on"},
    ),
    product(
        "res2000e", "RES2000E", "2.0 t Rider Electric Stacker", "electric-pallet-stackers", "res2000e.png",
        "2,000 kg", "1,600-3,500 mm", "Stand-on", "Heavier distribution and warehouse stacking",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Operator position": "Stand-on"},
    ),
    product(
        "res1500g", "RES1500G", "1.5 t Rider Electric Stacker", "electric-pallet-stackers", "res1500g.png",
        "1,500 kg", "1,600-3,000 mm", "Stand-on", "Fast internal movement with moderate lift heights",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 mm", "Operator position": "Stand-on"},
    ),
    product(
        "wces500j", "WCES500J", "0.5 t Walkie Counterbalanced Stacker", "electric-pallet-stackers", "wces500j.png",
        "500 kg", "1,600-3,500 mm", "Walk-behind", "Closed pallets, molds, and loads without fork access underneath",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Mast type": "Counterbalanced"},
    ),
    product(
        "wces1000j", "WCES1000J", "1.0 t Walkie Counterbalanced Stacker", "electric-pallet-stackers", "wces1000j.png",
        "1,000 kg", "1,600-3,500 mm", "Walk-behind", "Closed pallets and general industrial loads",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Mast type": "Counterbalanced"},
    ),
    product(
        "wces1300j", "WCES1300J", "1.3 t Walkie Counterbalanced Stacker", "electric-pallet-stackers", "wces1300j.png",
        "1,300 kg", "1,600-3,500 mm", "Walk-behind", "Industrial handling where straddle legs cannot be used",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Mast type": "Counterbalanced"},
    ),
    product(
        "wces1500j", "WCES1500J", "1.5 t Walkie Counterbalanced Stacker", "electric-pallet-stackers", "wces1500j.png",
        "1,500 kg", "1,600-3,500 mm", "Walk-behind", "Heavier closed-pallet and machine-side handling",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Mast type": "Counterbalanced"},
    ),
    product(
        "rces1000b", "RCES1000B", "1.0 t Rider Counterbalanced Stacker", "electric-pallet-stackers", "rces1000b.png",
        "1,000 kg", "Configuration based", "Stand-on", "Frequent closed-pallet handling over longer routes",
        {"Operator position": "Stand-on", "Mast type": "Counterbalanced"},
    ),
    product(
        "rces1500e", "RCES1500E", "1.5 t Rider Counterbalanced Stacker", "electric-pallet-stackers", "rces1500e.png",
        "1,500 kg", "Configuration based", "Stand-on", "Industrial handling with limited pallet under-clearance",
        {"Operator position": "Stand-on", "Mast type": "Counterbalanced"},
    ),
    product(
        "rces2000e", "RCES2000E", "2.0 t Rider Counterbalanced Stacker", "electric-pallet-stackers", "rces2000e.png",
        "2,000 kg", "Configuration based", "Stand-on", "High-capacity closed-pallet and fixture handling",
        {"Operator position": "Stand-on", "Mast type": "Counterbalanced"},
    ),
    product(
        "hes1500a", "HES1500A", "1.5 t Reach Electric Stacker", "electric-pallet-stackers", "hes1500a.png",
        "1,500 kg", "3,000 mm", "Stand-on", "Narrower aisles and deeper pallet placement",
        {"Operator position": "Stand-on", "Mast type": "Reach"},
    ),
    product(
        "hes2000a", "HES2000A", "2.0 t Reach Electric Stacker", "electric-pallet-stackers", "hes2000a.png",
        "2,000 kg", "1,600-3,500 mm", "Stand-on", "Heavier pallets in space-efficient storage layouts",
        {"Lift options": "1,600 / 2,000 / 2,500 / 3,000 / 3,500 mm", "Mast type": "Reach"},
    ),
    product(
        "efl1200r3", "EFL1200R3", "1.2 t Three-Wheel Electric Forklift", "electric-forklifts", "efl1200r3.png",
        "1,200 kg", "3,000 mm", "Seated", "Compact indoor handling and tight turning areas",
        {"Overall width": "922 mm", "Turning radius": "1,490 mm", "Travel speed": "9 / 10 km/h"},
    ),
    product(
        "efl2000r3", "EFL2000R3", "2.0 t Three-Wheel Electric Forklift", "electric-forklifts", "efl2000r3.png",
        "2,000 kg", "3,000 mm", "Seated", "Maneuverable warehouse and production logistics",
        {"Overall width": "1,100 mm", "Turning radius": "1,690 mm", "Tires": "Solid"},
    ),
    product(
        "r4efl1t", "R4EFL1T", "1.2 t Four-Wheel Electric Forklift", "electric-forklifts", "r4efl1t.png",
        "1,200 kg", "3,000 mm", "Seated", "Stable indoor transport and loading",
        {"Load center": "500 mm", "Battery": "48 V / 150 Ah lithium", "Drive / lift motor": "3.0 / 4.0 kW"},
    ),
    product(
        "r4efl3t", "R4EFL3T", "3.0 t Four-Wheel Electric Forklift", "electric-forklifts", "r4efl3t.png",
        "3,000 kg", "3,000 mm", "Seated", "General industrial and warehouse handling",
        {"Load center": "500 mm", "Battery": "72 V / 500 Ah lead-acid", "Turning radius": "2,400 mm"},
    ),
    product(
        "r4efl5t", "R4EFL5T", "5.0 t Four-Wheel Electric Forklift", "electric-forklifts", "r4efl5t.png",
        "5,000 kg", "3,000 mm", "Seated", "Heavy industrial handling on prepared surfaces",
        {"Load center": "500 mm", "Fork size": "1,070 x 150 x 50 mm", "Wheel arrangement": "Four-wheel"},
    ),
    product(
        "r4efl12t", "R4EFL12T", "Heavy-Duty Four-Wheel Electric Forklift", "electric-forklifts", "r4efl12t.png",
        "12,000 kg", "3,000 mm", "Seated", "High-capacity industrial applications",
        {"Overall width": "2,250 mm", "Turning radius": "3,850 mm", "Power": "Storage battery"},
    ),
    product(
        "mpt5tn", "MPT5TN", "5.0 t Manual Pallet Truck", "manual-pallet-trucks", "mpt5tn.png",
        "5,000 kg", "85-185 mm fork height", "Manual", "Heavy horizontal pallet movement over short distances",
        {"Fork length": "1,150 / 1,220 mm", "Overall length": "1,670 mm", "Drive": "Manual"},
    ),
    product(
        "mpjsc1500", "MPJSC1500", "1.5 t Single-Cylinder High-Lift Pallet Jack", "manual-pallet-trucks", "mpjsc1500.png",
        "1,500 kg", "85-800 mm fork height", "Manual", "Ergonomic loading, feeding, and workstation positioning",
        {"Cylinder": "Single-stage", "Fork length": "1,150 mm", "Drive": "Manual"},
    ),
    product(
        "mpjtsc1500", "MPJTSC1500", "1.5 t Two-Stage High-Lift Pallet Jack", "manual-pallet-trucks", "mpjtsc1500.png",
        "1,500 kg", "85-800 mm fork height", "Manual", "Higher manual positioning and occasional stacking tasks",
        {"Cylinder": "Two-stage", "Fork length": "1,150 mm", "Drive": "Manual"},
    ),
    product(
        "sc1016", "SC1016", "1.0 t Self-Loading Pallet Stacker", "warehouse-equipment", "sc1016.png",
        "1,000 kg", "1,600 mm configurable", "Manual travel / electric lift", "Vehicle loading, delivery support, and compact warehouse lifting",
        {"Overall width": "860 mm", "Overall length": "1,500 mm", "Battery": "48 V / 10 Ah LiFePO4"},
    ),
    product(
        "qes12e", "QES12E", "1.2 t Offset-Tiller Walkie Electric Stacker", "electric-pallet-stackers", "qes12e.png",
        "1,200 kg", "3,000 mm", "Walk-behind", "Compact electric pallet stacking and internal handling",
        {"Load center": "600 mm", "Overall width": "820 mm", "Turning radius": "1,385 mm"},
    ),
    product(
        "qes15e", "QES15E", "1.5 t Offset-Tiller Walkie Electric Stacker", "electric-pallet-stackers", "qes15e.png",
        "1,500 kg", "3,000 mm", "Walk-behind", "General warehouse pallet stacking on level floors",
        {"Load center": "600 mm", "Overall width": "800 mm", "Turning radius": "1,440 mm"},
    ),
    product(
        "qes15lie", "QES15LION", "1.5 t Lithium Offset-Tiller Walkie Electric Stacker", "electric-pallet-stackers", "qes15lion.png",
        "1,500 kg", "3,000 mm", "Walk-behind", "Lithium-powered pallet stacking and frequent indoor use",
        {"Load center": "600 mm", "Service weight": "470 kg", "Overall width": "800 mm"},
    ),
    product(
        "qed1530", "QED1530", "1.5 t Walkie Electric Pallet Stacker", "electric-pallet-stackers", "qed1530.png",
        "1,500 kg", "3,000 mm configurable", "Electric", "Warehouse pallet lifting with customizable lift height",
        {"Drive power": "2,200 W", "Lift motor": "750 W", "Battery": "24 V / 80 Ah optional"},
    ),
    product(
        "ept30", "EPT30", "300 kg Electric Hydraulic Lift Table Cart", "warehouse-equipment", "ept30.png",
        "300 kg", "290-880 mm", "Electric lift / manual travel", "Ergonomic load positioning and workstation feeding",
        {"Platform": "850 x 500 mm", "Lift stroke": "590 mm", "Motor": "0.8 kW"},
    ),
    product(
        "ept50", "EPT50", "500 kg Electric Hydraulic Lift Table Cart", "warehouse-equipment", "ept50.png",
        "500 kg", "440-1,025 mm", "Electric lift / manual travel", "Heavier workstation feeding and ergonomic load positioning",
        {"Platform": "1,010 x 520 mm", "Lift stroke": "585 mm", "Motor": "0.8 kW"},
    ),
    product(
        "eptd35", "EPTD35", "350 kg Double-Scissor Electric Lift Table Cart", "warehouse-equipment", "eptd35.png",
        "350 kg", "370-1,300 mm", "Electric lift / manual travel", "Higher workstation feeding and ergonomic load positioning",
        {"Platform": "910 x 500 mm", "Lift stroke": "930 mm", "Motor": "0.8 kW"},
    ),
    product(
        "exl0412", "EXL0412", "400 kg Electric Platform Stacker", "warehouse-equipment", "exl0412.png",
        "400 kg", "1,115 mm", "Electric lift / manual travel", "Platform lifting for luggage, parcels, and non-palletized loads",
        {"Platform": "650 x 576 mm", "Platform top height": "1,200 mm", "Motor": "12 V / 700 W"},
    ),
    product(
        "exl0415", "EXL0415", "400 kg Electric Platform Stacker", "warehouse-equipment", "exl0415.png",
        "400 kg", "1,415 mm", "Electric lift / manual travel", "Higher platform lifting for luggage, parcels, and non-palletized loads",
        {"Platform": "650 x 576 mm", "Platform top height": "1,500 mm", "Motor": "12 V / 700 W"},
    ),
    product(
        "pt15", "PT15", "150 kg Manual Hydraulic Lift Table Cart", "warehouse-equipment", "pt15.png",
        "150 kg", "220-720 mm", "Manual hydraulic", "Light workstation feeding and ergonomic load positioning",
        {"Platform": "700 x 450 mm", "Pump strokes": "<=28", "Service weight": "46 kg"},
    ),
    product(
        "pt30", "PT30", "300 kg Manual Hydraulic Lift Table Cart", "warehouse-equipment", "pt30.png",
        "300 kg", "285-880 mm", "Manual hydraulic", "Workstation feeding and ergonomic load positioning",
        {"Platform": "815 x 500 mm", "Pump strokes": "<=27", "Service weight": "77 kg"},
    ),
    product(
        "pt50", "PT50", "500 kg Manual Hydraulic Lift Table Cart", "warehouse-equipment", "pt50.png",
        "500 kg", "285-880 mm", "Manual hydraulic", "Medium-duty workstation feeding and load positioning",
        {"Platform": "815 x 500 mm", "Pump strokes": "<=27", "Service weight": "81 kg"},
    ),
    product(
        "pt75", "PT75", "750 kg Manual Hydraulic Lift Table Cart", "warehouse-equipment", "pt75.png",
        "750 kg", "420-1,000 mm", "Manual hydraulic", "Heavy workstation feeding and ergonomic load positioning",
        {"Platform": "1,000 x 510 mm", "Pump strokes": "<=45", "Service weight": "125 kg"},
    ),
    product(
        "pt100", "PT100", "1.0 t Manual Hydraulic Lift Table Cart", "warehouse-equipment", "pt100.png",
        "1,000 kg", "380-1,000 mm", "Manual hydraulic", "High-capacity workstation feeding and load positioning",
        {"Platform": "1,016 x 510 mm", "Pump strokes": "<=82", "Service weight": "140 kg"},
    ),
    product(
        "ptd35", "PTD35", "350 kg Double-Scissor Manual Lift Table Cart", "warehouse-equipment", "ptd35.png",
        "350 kg", "355-1,300 mm", "Manual hydraulic", "Higher ergonomic positioning for lighter loads",
        {"Platform": "910 x 500 mm", "Pump strokes": "<=53", "Service weight": "110 kg"},
    ),
    product(
        "ptd70", "PTD70", "700 kg Double-Scissor Manual Lift Table Cart", "warehouse-equipment", "ptd70.png",
        "700 kg", "445-1,500 mm", "Manual hydraulic", "High-lift ergonomic positioning for heavier loads",
        {"Platform": "1,220 x 610 mm", "Pump strokes": "<=97", "Service weight": "195 kg"},
    ),
    product(
        "sl0485", "SL0485", "400 kg Manual Platform Stacker", "warehouse-equipment", "sl0485.png",
        "400 kg", "765 mm", "Manual hydraulic", "Low-height platform lifting for luggage, parcels, and loose loads",
        {"Platform": "650 x 576 mm", "Platform top height": "850 mm", "Service weight": "75 kg"},
    ),
    product(
        "sl0412", "SL0412", "400 kg Manual Platform Stacker", "warehouse-equipment", "sl0412.png",
        "400 kg", "1,115 mm", "Manual hydraulic", "Platform lifting for luggage, parcels, and loose loads",
        {"Platform": "650 x 576 mm", "Platform top height": "1,200 mm", "Service weight": "81 kg"},
    ),
    product(
        "sl0415", "SL0415", "400 kg Manual Platform Stacker", "warehouse-equipment", "sl0415.png",
        "400 kg", "1,415 mm", "Manual hydraulic", "Higher platform lifting for luggage, parcels, and loose loads",
        {"Platform": "650 x 576 mm", "Platform top height": "1,500 mm", "Service weight": "91 kg"},
    ),
    product(
        "bed1016", "BED1016", "1.0 t Semi-Electric Pallet Stacker", "warehouse-equipment", "bed1016.png",
        "1,000 kg", "1,600 mm", "Manual travel / electric lift", "Light warehouse pallet lifting on level floors",
        {"Overall width": "777 mm", "Forks": "60 x 160 x 1,150 mm", "Battery": "12 V / 150 Ah"},
    ),
    product(
        "bed1025", "BED1025", "1.0 t Semi-Electric Pallet Stacker", "warehouse-equipment", "bed1025.png",
        "1,000 kg", "2,500 mm", "Manual travel / electric lift", "Medium-height warehouse pallet lifting on level floors",
        {"Overall width": "777 mm", "Forks": "60 x 160 x 1,150 mm", "Battery": "12 V / 150 Ah"},
    ),
    product(
        "bed1030", "BED1030", "1.0 t Semi-Electric Pallet Stacker", "warehouse-equipment", "bed1030.png",
        "1,000 kg", "3,000 mm", "Manual travel / electric lift", "Higher warehouse pallet lifting on level floors",
        {"Overall width": "777 mm", "Forks": "60 x 160 x 1,150 mm", "Battery": "12 V / 150 Ah"},
    ),
    product(
        "bed1516", "BED1516", "1.5 t Semi-Electric Pallet Stacker", "warehouse-equipment", "bed1516.png",
        "1,500 kg", "1,600 mm", "Manual travel / electric lift", "Higher-capacity pallet lifting on level floors",
        {"Overall width": "844 mm", "Forks": "60 x 182 x 1,150 mm", "Battery": "12 V / 150 Ah"},
    ),
]


GUIDES = [
    {
        "slug": "how-to-choose-an-electric-pallet-truck",
        "title": "How to Choose an Electric Pallet Truck",
        "summary": "A practical checklist for load, route length, floor condition, turning space, battery, and duty cycle.",
    },
    {
        "slug": "pallet-truck-vs-stacker",
        "title": "Pallet Truck vs. Pallet Stacker",
        "summary": "Use a pallet truck to move loads horizontally and a stacker when the task includes lifting into storage positions.",
    },
    {
        "slug": "forklift-capacity-and-aisle-width",
        "title": "Forklift Capacity, Lift Height, and Aisle Width",
        "summary": "Why rated capacity alone is not enough when selecting an electric forklift.",
    },
]
