# garminHelper.py
# data to calculate feedback on VO2 Max value - based on age and sex
vo2MaxRanges = {
    "MALE": {
        "20-29": [
            {
                "category": "Superior",
                "max": "",
                "min": "55.4"
            },
            {
                "category": "Excellent",
                "max": "55.4",
                "min": "51.1"
            },
            {
                "category": "Good",
                "max": "51.1",
                "min": "45.4"
            },
            {
                "category": "Fair",
                "max": "45.4",
                "min": "41.7"
            },
            {
                "category": "Poor",
                "max": "41.7",
                "min": ""
            }
        ],
        "30-39": [
            {
                "category": "Superior",
                "max": "",
                "min": "54"
            },
            {
                "category": "Excellent",
                "max": "54",
                "min": "48.3"
            },
            {
                "category": "Good",
                "max": "48.3",
                "min": "44"
            },
            {
                "category": "Fair",
                "max": "44",
                "min": "40.5"
            },
            {
                "category": "Poor",
                "max": "40.5",
                "min": ""
            }
        ],
        "40-49": [
            {
                "category": "Superior",
                "max": "",
                "min": "52.5"
            },
            {
                "category": "Excellent",
                "max": "52.5",
                "min": "46.4"
            },
            {
                "category": "Good",
                "max": "46.4",
                "min": "42.4"
            },
            {
                "category": "Fair",
                "max": "42.4",
                "min": "38.5"
            },
            {
                "category": "Poor",
                "max": "38.5",
                "min": ""
            }
        ],
        "50-59": [
            {
                "category": "Superior",
                "max": "",
                "min": "48.9"
            },
            {
                "category": "Excellent",
                "max": "48.9",
                "min": "43.4"
            },
            {
                "category": "Good",
                "max": "43.4",
                "min": "39.2"
            },
            {
                "category": "Fair",
                "max": "39.2",
                "min": "35.6"
            },
            {
                "category": "Poor",
                "max": "35.6",
                "min": ""
            }
        ],
        "60-69": [
            {
                "category": "Superior",
                "max": "",
                "min": "45.7"
            },
            {
                "category": "Excellent",
                "max": "45.7",
                "min": "39.5"
            },
            {
                "category": "Good",
                "max": "39.5",
                "min": "35.5"
            },
            {
                "category": "Fair",
                "max": "35.5",
                "min": "32.3"
            },
            {
                "category": "Poor",
                "max": "32.3",
                "min": ""
            }
        ],
        "70-79": [
            {
                "category": "Superior",
                "max": "",
                "min": "42.1"
            },
            {
                "category": "Excellent",
                "max": "42.1",
                "min": "36.7"
            },
            {
                "category": "Good",
                "max": "36.7",
                "min": "32.3"
            },
            {
                "category": "Fair",
                "max": "32.3",
                "min": "29.4"
            },
            {
                "category": "Poor",
                "max": "29.4",
                "min": ""
            }
        ]
    },
    "FEMALE": {
        "20-29": [
            {
                "category": "Superior",
                "max": "",
                "min": "49.6"
            },
            {
                "category": "Excellent",
                "max": "49.6",
                "min": "43.9"
            },
            {
                "category": "Good",
                "max": "43.9",
                "min": "39.5"
            },
            {
                "category": "Fair",
                "max": "39.5",
                "min": "36.1"
            },
            {
                "category": "Poor",
                "max": "36.1",
                "min": ""
            }
        ],
        "30-39": [
            {
                "category": "Superior",
                "max": "",
                "min": "47.4"
            },
            {
                "category": "Excellent",
                "max": "47.4",
                "min": "42.4"
            },
            {
                "category": "Good",
                "max": "42.4",
                "min": "37.8"
            },
            {
                "category": "Fair",
                "max": "37.8",
                "min": "34.4"
            },
            {
                "category": "Poor",
                "max": "34.4",
                "min": ""
            }
        ],
        "40-49": [
            {
                "category": "Superior",
                "max": "",
                "min": "45.3"
            },
            {
                "category": "Excellent",
                "max": "45.3",
                "min": "39.7"
            },
            {
                "category": "Good",
                "max": "39.7",
                "min": "36.3"
            },
            {
                "category": "Fair",
                "max": "36.3",
                "min": "33"
            },
            {
                "category": "Poor",
                "max": "33",
                "min": ""
            }
        ],
        "50-59": [
            {
                "category": "Superior",
                "max": "",
                "min": "41.1"
            },
            {
                "category": "Excellent",
                "max": "41.1",
                "min": "36.7"
            },
            {
                "category": "Good",
                "max": "36.7",
                "min": "33"
            },
            {
                "category": "Fair",
                "max": "33",
                "min": "30.1"
            },
            {
                "category": "Poor",
                "max": "30.1",
                "min": ""
            }
        ],
        "60-69": [
            {
                "category": "Superior",
                "max": "",
                "min": "37.8"
            },
            {
                "category": "Excellent",
                "max": "37.8",
                "min": "33"
            },
            {
                "category": "Good",
                "max": "33",
                "min": "30"
            },
            {
                "category": "Fair",
                "max": "30",
                "min": "27.5"
            },
            {
                "category": "Poor",
                "max": "27.5",
                "min": ""
            }
        ],
        "70-79": [
            {
                "category": "Superior",
                "max": "",
                "min": "36.7"
            },
            {
                "category": "Excellent",
                "max": "36.7",
                "min": "30.9"
            },
            {
                "category": "Good",
                "max": "30.9",
                "min": "28.1"
            },
            {
                "category": "Fair",
                "max": "28.1",
                "min": "25.9"
            },
            {
                "category": "Poor",
                "max": "25.9",
                "min": ""
            }
        ]
    }
}

def getVO2MaxFeedback(sex: str, age: int, vo2_max: float) -> str:
    sex = sex.upper()
    if sex not in vo2MaxRanges:
        return "Unknown"

    age_group = None
    if 20 <= age <= 29:
        age_group = "20-29"
    elif 30 <= age <= 39:
        age_group = "30-39"
    elif 40 <= age <= 49:
        age_group = "40-49"
    elif 50 <= age <= 59:
        age_group = "50-59"
    elif 60 <= age <= 69:
        age_group = "60-69"
    elif 70 <= age <= 79:
        age_group = "70-79"
    else:
        return "Unknown"

    print("age_group: ", age_group)

    if age_group not in vo2MaxRanges[sex]:
        return "Unknown"

    for range_info in vo2MaxRanges[sex][age_group]:
        min_val = float(range_info["min"]
                        ) if range_info["min"] else float('-inf')
        max_val = float(range_info["max"]
                        ) if range_info["max"] else float('inf')
        if min_val <= vo2_max <= max_val:
            return range_info["category"]

    return "Unknown"
