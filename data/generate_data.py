"""
EduPilot — Synthetic college data generator.
Generates data/colleges.json with 50 realistic Indian engineering colleges.
Run: python data/generate_data.py
"""

import json
import random
from pathlib import Path

random.seed(42)

# ── Data pools ────────────────────────────────────────────────

BRANCHES = ["CSE", "ECE", "Mech", "Civil", "EE", "Chemical", "AI/ML", "IT", "Biotech"]

IITS = [
    {"name": "IIT Bombay",   "city": "Mumbai",       "state": "Maharashtra",     "nirf_rank": 3,  "type": "IIT", "tuition_fee": 100000,  "avg_package": 21.0, "highest_package": 80, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Delhi",    "city": "New Delhi",     "state": "Delhi",           "nirf_rank": 2,  "type": "IIT", "tuition_fee": 100000,  "avg_package": 22.0, "highest_package": 90, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Madras",   "city": "Chennai",       "state": "Tamil Nadu",      "nirf_rank": 1,  "type": "IIT", "tuition_fee": 100000,  "avg_package": 20.5, "highest_package": 85, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Kanpur",   "city": "Kanpur",        "state": "Uttar Pradesh",   "nirf_rank": 4,  "type": "IIT", "tuition_fee": 100000,  "avg_package": 19.0, "highest_package": 70, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Kharagpur","city": "Kharagpur",     "state": "West Bengal",     "nirf_rank": 5,  "type": "IIT", "tuition_fee": 110000,  "avg_package": 18.5, "highest_package": 65, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Roorkee",  "city": "Roorkee",       "state": "Uttarakhand",     "nirf_rank": 6,  "type": "IIT", "tuition_fee": 110000,  "avg_package": 17.0, "highest_package": 60, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Guwahati", "city": "Guwahati",      "state": "Assam",           "nirf_rank": 7,  "type": "IIT", "tuition_fee": 100000,  "avg_package": 15.5, "highest_package": 55, "exams": ["JEE Advanced"], "status": "Closed"},
    {"name": "IIT Hyderabad","city": "Hyderabad",     "state": "Telangana",       "nirf_rank": 8,  "type": "IIT", "tuition_fee": 112000,  "avg_package": 15.0, "highest_package": 50, "exams": ["JEE Advanced"], "status": "Upcoming"},
    {"name": "IIT Indore",   "city": "Indore",        "state": "Madhya Pradesh",  "nirf_rank": 13, "type": "IIT", "tuition_fee": 115000,  "avg_package": 14.0, "highest_package": 45, "exams": ["JEE Advanced"], "status": "Upcoming"},
    {"name": "IIT Gandhinagar","city": "Gandhinagar", "state": "Gujarat",         "nirf_rank": 14, "type": "IIT", "tuition_fee": 115000,  "avg_package": 13.5, "highest_package": 42, "exams": ["JEE Advanced"], "status": "Upcoming"},
]

NITS = [
    {"name": "NIT Trichy",          "city": "Tiruchirappalli", "state": "Tamil Nadu",    "nirf_rank": 9,  "type": "NIT", "tuition_fee": 150000, "avg_package": 12.0, "highest_package": 40, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Warangal",        "city": "Warangal",        "state": "Telangana",     "nirf_rank": 10, "type": "NIT", "tuition_fee": 150000, "avg_package": 11.5, "highest_package": 38, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Surathkal",       "city": "Surathkal",       "state": "Karnataka",     "nirf_rank": 11, "type": "NIT", "tuition_fee": 148000, "avg_package": 11.0, "highest_package": 36, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Calicut",         "city": "Calicut",         "state": "Kerala",        "nirf_rank": 16, "type": "NIT", "tuition_fee": 148000, "avg_package": 10.5, "highest_package": 32, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Rourkela",        "city": "Rourkela",        "state": "Odisha",        "nirf_rank": 17, "type": "NIT", "tuition_fee": 150000, "avg_package": 10.0, "highest_package": 30, "exams": ["JEE Main"], "status": "Open"},
    {"name": "MNIT Jaipur",         "city": "Jaipur",          "state": "Rajasthan",     "nirf_rank": 22, "type": "NIT", "tuition_fee": 145000, "avg_package": 9.5,  "highest_package": 28, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Kurukshetra",     "city": "Kurukshetra",     "state": "Haryana",       "nirf_rank": 26, "type": "NIT", "tuition_fee": 143000, "avg_package": 9.0,  "highest_package": 25, "exams": ["JEE Main"], "status": "Open"},
    {"name": "VNIT Nagpur",         "city": "Nagpur",          "state": "Maharashtra",   "nirf_rank": 25, "type": "NIT", "tuition_fee": 143000, "avg_package": 9.0,  "highest_package": 26, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Silchar",         "city": "Silchar",         "state": "Assam",         "nirf_rank": 37, "type": "NIT", "tuition_fee": 138000, "avg_package": 7.5,  "highest_package": 20, "exams": ["JEE Main"], "status": "Open"},
    {"name": "NIT Raipur",          "city": "Raipur",          "state": "Chhattisgarh",  "nirf_rank": 45, "type": "NIT", "tuition_fee": 132000, "avg_package": 7.0,  "highest_package": 18, "exams": ["JEE Main"], "status": "Open"},
]

PRIVATE = [
    {"name": "VIT Vellore",          "city": "Vellore",       "state": "Tamil Nadu",   "nirf_rank": 15, "type": "Private", "tuition_fee": 195000, "avg_package": 7.8, "highest_package": 43, "exams": ["VITEEE"],          "status": "Open",    "deadline": "2025-04-10"},
    {"name": "VIT Chennai",          "city": "Chennai",       "state": "Tamil Nadu",   "nirf_rank": 28, "type": "Private", "tuition_fee": 195000, "avg_package": 7.5, "highest_package": 42, "exams": ["VITEEE"],          "status": "Open",    "deadline": "2025-04-10"},
    {"name": "Manipal Institute of Technology","city": "Manipal","state": "Karnataka", "nirf_rank": 20, "type": "Private", "tuition_fee": 220000, "avg_package": 8.2, "highest_package": 44, "exams": ["MET", "JEE Main"], "status": "Open",    "deadline": "2025-04-20"},
    {"name": "SRM Institute of Science and Technology","city": "Chennai","state": "Tamil Nadu","nirf_rank": 32,"type": "Private","tuition_fee": 225000,"avg_package": 6.5,"highest_package": 38,"exams": ["SRMJEEE", "JEE Main"],"status": "Open","deadline": "2025-03-31"},
    {"name": "BITS Pilani",          "city": "Pilani",        "state": "Rajasthan",    "nirf_rank": 27, "type": "Deemed",  "tuition_fee": 215000, "avg_package": 15.0,"highest_package": 60, "exams": ["BITSAT"],          "status": "Open",    "deadline": "2025-05-15"},
    {"name": "BITS Goa",             "city": "Vasco da Gama", "state": "Goa",          "nirf_rank": 35, "type": "Deemed",  "tuition_fee": 215000, "avg_package": 14.0,"highest_package": 58, "exams": ["BITSAT"],          "status": "Open",    "deadline": "2025-05-15"},
    {"name": "BITS Hyderabad",       "city": "Hyderabad",     "state": "Telangana",    "nirf_rank": 38, "type": "Deemed",  "tuition_fee": 215000, "avg_package": 13.5,"highest_package": 55, "exams": ["BITSAT"],          "status": "Open",    "deadline": "2025-05-15"},
    {"name": "Thapar Institute",     "city": "Patiala",       "state": "Punjab",       "nirf_rank": 29, "type": "Deemed",  "tuition_fee": 185000, "avg_package": 9.0, "highest_package": 32, "exams": ["JEE Main"],        "status": "Open",    "deadline": "2025-06-10"},
    {"name": "Amrita Vishwa Vidyapeetham","city": "Coimbatore","state": "Tamil Nadu",  "nirf_rank": 19, "type": "Deemed",  "tuition_fee": 175000, "avg_package": 7.0, "highest_package": 25, "exams": ["AEEE", "JEE Main"],"status": "Open",   "deadline": "2025-04-30"},
    {"name": "PSG College of Technology","city": "Coimbatore","state": "Tamil Nadu",   "nirf_rank": 46, "type": "Private", "tuition_fee": 120000, "avg_package": 6.5, "highest_package": 22, "exams": ["TNEA"],            "status": "Upcoming","deadline": "2025-07-01"},
    {"name": "Hindustan Institute of Technology","city": "Chennai","state": "Tamil Nadu","nirf_rank": 61,"type": "Private","tuition_fee": 140000,"avg_package": 5.5,"highest_package": 18,"exams": ["HICAT", "JEE Main"],"status": "Open","deadline": "2025-05-20"},
    {"name": "Kalasalingam University","city": "Krishnankoil","state": "Tamil Nadu",   "nirf_rank": 55, "type": "Deemed",  "tuition_fee": 90000,  "avg_package": 5.0, "highest_package": 15, "exams": ["JEE Main"],        "status": "Open",    "deadline": "2025-06-15"},
    {"name": "SSN College of Engineering","city": "Chennai","state": "Tamil Nadu",     "nirf_rank": 49, "type": "Private", "tuition_fee": 110000, "avg_package": 6.8, "highest_package": 24, "exams": ["TNEA"],            "status": "Upcoming","deadline": "2025-07-01"},
    {"name": "PES University",        "city": "Bangalore",     "state": "Karnataka",   "nirf_rank": 52, "type": "Private", "tuition_fee": 255000, "avg_package": 8.5, "highest_package": 30, "exams": ["PESSAT", "JEE Main"],"status": "Open", "deadline": "2025-04-15"},
    {"name": "RV College of Engineering","city": "Bangalore",  "state": "Karnataka",   "nirf_rank": 56, "type": "Private", "tuition_fee": 195000, "avg_package": 7.5, "highest_package": 28, "exams": ["KCET", "COMEDK"],  "status": "Open",    "deadline": "2025-06-20"},
    {"name": "BMS College of Engineering","city": "Bangalore", "state": "Karnataka",   "nirf_rank": 58, "type": "Private", "tuition_fee": 185000, "avg_package": 7.0, "highest_package": 25, "exams": ["KCET", "COMEDK"],  "status": "Open",    "deadline": "2025-06-20"},
    {"name": "MSRIT Bangalore",       "city": "Bangalore",     "state": "Karnataka",   "nirf_rank": 63, "type": "Private", "tuition_fee": 180000, "avg_package": 6.5, "highest_package": 22, "exams": ["KCET", "COMEDK"],  "status": "Open",    "deadline": "2025-06-20"},
    {"name": "College of Engineering Pune","city": "Pune",     "state": "Maharashtra", "nirf_rank": 36, "type": "Government","tuition_fee": 75000, "avg_package": 8.0, "highest_package": 30, "exams": ["MHT-CET", "JEE Main"],"status": "Open","deadline": "2025-07-15"},
    {"name": "VJTI Mumbai",           "city": "Mumbai",        "state": "Maharashtra", "nirf_rank": 43, "type": "Government","tuition_fee": 70000, "avg_package": 7.5, "highest_package": 28, "exams": ["MHT-CET"],         "status": "Open",    "deadline": "2025-07-15"},
    {"name": "PICT Pune",             "city": "Pune",          "state": "Maharashtra", "nirf_rank": 67, "type": "Private", "tuition_fee": 165000, "avg_package": 6.0, "highest_package": 20, "exams": ["MHT-CET"],         "status": "Open",    "deadline": "2025-07-20"},
    {"name": "Dhirubhai Ambani Institute","city": "Gandhinagar","state": "Gujarat",    "nirf_rank": 31, "type": "Private", "tuition_fee": 290000, "avg_package": 11.0,"highest_package": 45, "exams": ["JEE Main", "DAT"],  "status": "Open",    "deadline": "2025-05-30"},
    {"name": "Nirma University",       "city": "Ahmedabad",    "state": "Gujarat",     "nirf_rank": 40, "type": "Deemed",  "tuition_fee": 200000, "avg_package": 7.8, "highest_package": 28, "exams": ["JEE Main"],        "status": "Open",    "deadline": "2025-06-01"},
    {"name": "Symbiosis Institute of Technology","city": "Pune","state": "Maharashtra","nirf_rank": 60,"type": "Deemed",  "tuition_fee": 240000, "avg_package": 6.5, "highest_package": 22, "exams": ["SET", "JEE Main"], "status": "Open",    "deadline": "2025-05-10"},
    {"name": "Lovely Professional University","city": "Phagwara","state": "Punjab",    "nirf_rank": 33, "type": "Private", "tuition_fee": 130000, "avg_package": 5.8, "highest_package": 25, "exams": ["JEE Main", "LPUNEST"],"status": "Open", "deadline": "2025-05-31"},
    {"name": "Chandigarh University", "city": "Chandigarh",    "state": "Punjab",      "nirf_rank": 41, "type": "Private", "tuition_fee": 145000, "avg_package": 6.0, "highest_package": 24, "exams": ["JEE Main", "CUCET"],"status": "Open",  "deadline": "2025-06-15"},
    {"name": "Jamia Millia Islamia",  "city": "New Delhi",     "state": "Delhi",       "nirf_rank": 30, "type": "Central", "tuition_fee": 45000,  "avg_package": 7.0, "highest_package": 24, "exams": ["JMI Entrance"],    "status": "Upcoming","deadline": "2025-05-01"},
    {"name": "Delhi Technological University","city": "New Delhi","state": "Delhi",    "nirf_rank": 34, "type": "Government","tuition_fee": 88000, "avg_package": 10.0,"highest_package": 40, "exams": ["JEE Main"],        "status": "Open",    "deadline": "2025-07-01"},
    {"name": "Netaji Subhas University of Technology","city": "New Delhi","state": "Delhi","nirf_rank": 42,"type": "Government","tuition_fee": 82000,"avg_package": 9.5,"highest_package": 38,"exams": ["JEE Main"],"status": "Open","deadline": "2025-07-01"},
    {"name": "IIIT Hyderabad",        "city": "Hyderabad",     "state": "Telangana",   "nirf_rank": 21, "type": "IIIT",    "tuition_fee": 175000, "avg_package": 17.5,"highest_package": 65, "exams": ["UGEE", "JEE Main"], "status": "Open",   "deadline": "2025-04-30"},
    {"name": "IIIT Delhi",            "city": "New Delhi",     "state": "Delhi",       "nirf_rank": 24, "type": "IIIT",    "tuition_fee": 165000, "avg_package": 15.0,"highest_package": 55, "exams": ["JEE Main"],        "status": "Open",    "deadline": "2025-06-15"},
]

ALL_COLLEGES = IITS + NITS + PRIVATE


def _build_cutoffs(college: dict) -> dict:
    """Generate realistic cutoff ranks for each exam/category/quota combo."""
    cutoffs = {}
    college_type = college.get("type", "Private")
    nirf = college["nirf_rank"]

    for exam in college.get("exams", []):
        # Realistic base ranks based on type and NIRF
        if college_type == "IIT":
            # IITs: JEE Advanced rank 200 (IIT Bombay) to 3000 (IIT Indore)
            base = int(200 + (nirf - 1) * 220)
        elif college_type == "NIT":
            # NITs: JEE Main rank 5000 (NIT Trichy) to 60000 (NIT Raipur)
            base = int(5000 + (nirf - 9) * 2800)
        elif college_type in ("IIIT", "Central"):
            base = int(3000 + (nirf - 20) * 1200)
        elif college_type == "Deemed":
            # BITS: score-based (higher = better), map to rank proxy
            base = int(15000 + (nirf - 15) * 1500)
        else:
            # Government / Private
            base = int(40000 + (nirf - 30) * 2000)

        base = max(base, 500)  # floor

        cutoffs[exam] = {
            "General": {
                "All_India":   base,
                "Home_State":  int(base * 1.3),
            },
            "OBC": {
                "All_India":   int(base * 1.8),
                "Home_State":  int(base * 2.2),
            },
            "EWS": {
                "All_India":   int(base * 1.6),
                "Home_State":  int(base * 2.0),
            },
            "SC": {
                "All_India":   int(base * 3.5),
                "Home_State":  int(base * 4.0),
            },
            "ST": {
                "All_India":   int(base * 5.0),
                "Home_State":  int(base * 6.0),
            },
        }
    return cutoffs


def _build_scholarships(college: dict) -> list:
    """Generate merit-based scholarship tiers."""
    base = int(10_000 / max(college["nirf_rank"], 1) * 300)
    return [
        {"percent": 100, "rank_below": int(base * 0.2)},
        {"percent": 50,  "rank_below": int(base * 0.5)},
        {"percent": 25,  "rank_below": int(base * 0.8)},
    ]


def _build_branches(college: dict) -> list:
    """Return branch list. IITs/NITs have all; private varies."""
    if college["type"] in ("IIT", "NIT", "Central"):
        return BRANCHES
    return random.sample(BRANCHES, k=random.randint(4, 7))


def _build_description(college: dict) -> str:
    typename = college["type"]
    nirf = college["nirf_rank"]
    fee = college["tuition_fee"]
    pkg = college["avg_package"]
    status = college["status"]
    deadline = college.get("deadline", "July 2025")
    return (
        f"{college['name']} is a prestigious {typename} institution ranked NIRF #{nirf} "
        f"in {college['city']}, {college['state']}. Annual tuition is ₹{fee:,}. "
        f"Average placement package is {pkg} LPA. "
        f"Admission status: {status}. Application deadline: {deadline}."
    )


def generate_colleges() -> list[dict]:
    colleges = []
    for c in ALL_COLLEGES:
        entry = dict(c)
        entry["branches"]     = _build_branches(c)
        entry["cutoffs"]      = _build_cutoffs(c)
        entry["scholarships"] = _build_scholarships(c)
        entry["description"]  = _build_description(c)
        if "deadline" not in entry:
            # NITs / IITs use JoSAA counselling
            entry["deadline"] = "JoSAA 2025 counselling (June–July 2025)"
        colleges.append(entry)
    return colleges


def main():
    output_path = Path(__file__).parent / "colleges.json"
    colleges = generate_colleges()
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(colleges, f, indent=2, ensure_ascii=False)
    print(f"✅  Generated {len(colleges)} colleges → {output_path}")


if __name__ == "__main__":
    main()
