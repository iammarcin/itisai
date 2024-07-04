# test_data.py
# those are real responses from garmin API
# separated to external file - because sometimes test data is huuuuuge

TEST_DATA = {
    "get_sleep_data": {
        "dailySleepDTO": {"id": 1717790546000, "userProfilePK": 9334852, "calendarDate": "2024-06-08", "sleepTimeSeconds": 26040, "napTimeSeconds": 0, "sleepWindowConfirmed": True, "sleepWindowConfirmationType": "enhanced_confirmed_final", "sleepStartTimestampGMT": 1717790546000, "sleepEndTimestampGMT": 1717817126000, "sleepStartTimestampLocal": 1717797746000, "sleepEndTimestampLocal": 1717824326000, "autoSleepStartTimestampGMT": None, "autoSleepEndTimestampGMT": None, "sleepQualityTypePK": None, "sleepResultTypePK": None, "unmeasurableSleepSeconds": 0, "deepSleepSeconds": 4020, "lightSleepSeconds": 17520, "remSleepSeconds": 4500, "awakeSleepSeconds": 540, "deviceRemCapable": True, "retro": False, "sleepFromDevice": True, "averageRespirationValue": 16.0, "lowestRespirationValue": 13.0, "highestRespirationValue": 21.0, "awakeCount": 1, "avgSleepStress": 14.0, "ageGroup": "ADULT", "sleepScoreFeedback": "POSITIVE_LONG_AND_CONTINUOUS", "sleepScoreInsight": "POSITIVE_RESTFUL_EVENING", "sleepScorePersonalizedInsight": "RHYTHM_POS_GOOD_SLEEP_EXCELLENT_TIMING", "sleepScores": {"totalDuration": {"qualifierKey": "GOOD", "optimalStart": 28200.0, "optimalEnd": 28200.0}, "stress": {"qualifierKey": "GOOD", "optimalStart": 0.0, "optimalEnd": 15.0}, "awakeCount": {"qualifierKey": "EXCELLENT", "optimalStart": 0.0, "optimalEnd": 1.0}, "overall": {"value": 84, "qualifierKey": "GOOD"}, "remPercentage": {"value": 17, "qualifierKey": "FAIR", "optimalStart": 21.0, "optimalEnd": 31.0, "idealStartInSeconds": 5468.4, "idealEndInSeconds": 8072.4}, "restlessness": {"qualifierKey": "GOOD", "optimalStart": 0.0, "optimalEnd": 5.0}, "lightPercentage": {"value": 67, "qualifierKey": "FAIR", "optimalStart": 30.0, "optimalEnd": 64.0, "idealStartInSeconds": 7812.0, "idealEndInSeconds": 16665.6}, "deepPercentage": {"value": 15, "qualifierKey": "FAIR", "optimalStart": 16.0, "optimalEnd": 33.0, "idealStartInSeconds": 4166.4, "idealEndInSeconds": 8593.2}}, "sleepVersion": 2, "sleepNeed": {"userProfilePk": 9334852, "calendarDate": "2024-06-08", "deviceId": 3423315346, "timestampGmt": "2024-06-07T04:28:27", "baseline": 470, "actual": 540, "feedback": "HIGHLY_INCREASED", "trainingFeedback": "NO_CHANGE", "sleepHistoryAdjustment": "INCREASING", "hrvAdjustment": "INCREASING", "napAdjustment": "NO_CHANGE", "displayedForTheDay": True, "preferredActivityTracker": True}, "nextSleepNeed": {"userProfilePk": 9334852, "calendarDate": "2024-06-09", "deviceId": 3423315346, "timestampGmt": "2024-06-08T04:28:56", "baseline": 470, "actual": 500, "feedback": "INCREASED", "trainingFeedback": "NO_CHANGE", "sleepHistoryAdjustment": "INCREASING", "hrvAdjustment": "INCREASING", "napAdjustment": "NO_CHANGE", "displayedForTheDay": True, "preferredActivityTracker": True}, "remSleepData": True, "restlessMomentsCount": 39, "avgOvernightHrv": 53.0, "hrvStatus": "UNBALANCED", "bodyBatteryChange": 0, "restingHeartRate": 45}
    },
    "get_user_summary":
        {'userProfileId': 9334852, 'totalKilocalories': 3940.0, 'activeKilocalories': 1720.0, 'bmrKilocalories': 2220.0, 'wellnessKilocalories': 3940.0, 'burnedKilocalories': None, 'consumedKilocalories': None, 'remainingKilocalories': 3940.0, 'totalSteps': 39709, 'netCalorieGoal': None, 'totalDistanceMeters': 32411, 'wellnessDistanceMeters': 32411, 'wellnessActiveKilocalories': 1720.0, 'netRemainingKilocalories': 1720.0, 'userDailySummaryId': 9334852, 'calendarDate': '2024-06-06', 'rule': {'typeId': 2, 'typeKey': 'private'}, 'uuid': '2d4838c0dc604d119c10f52aa3015275', 'dailyStepGoal': 13372, 'wellnessStartTimeGmt': '2024-06-05T22:00:00.0', 'wellnessStartTimeLocal': '2024-06-06T00:00:00.0', 'wellnessEndTimeGmt': '2024-06-06T22:00:00.0', 'wellnessEndTimeLocal': '2024-06-07T00:00:00.0', 'durationInMilliseconds': 86400000, 'wellnessDescription': None, 'highlyActiveSeconds': 643, 'activeSeconds': 24296, 'sedentarySeconds': 31572, 'sleepingSeconds': 29889, 'includesWellnessData': True, 'includesActivityData': True, 'includesCalorieConsumedData': False, 'privacyProtected': False, 'moderateIntensityMinutes': 162, 'vigorousIntensityMinutes': 36, 'floorsAscendedInMeters': 728.472, 'floorsDescendedInMeters': 754.52, 'floorsAscended': 239.0, 'floorsDescended': 247.54593, 'intensityMinutesGoal': 150, 'userFloorsAscendedGoal': 10, 'minHeartRate': 44, 'maxHeartRate': 143, 'restingHeartRate': 48, 'lastSevenDaysAvgRestingHeartRate': 47, 'source': 'GARMIN', 'averageStressLevel': 23, 'maxStressLevel': 99, 'stressDuration': 12480, 'restStressDuration': 27960, 'activityStressDuration': 28320, 'uncategorizedStressDuration': 16680, 'totalStressDuration': 85440, 'lowStressDuration': 11400, 'mediumStressDuration': 540, 'highStressDuration': 540, 'stressPercentage': 14.61, 'restStressPercentage': 32.72, 'activityStressPercentage': 33.15, 'uncategorizedStressPercentage': 19.52, 'lowStressPercentage': 13.34, 'mediumStressPercentage': 0.63, 'highStressPercentage': 0.63, 'stressQualifier': 'BALANCED', 'measurableAwakeDuration': 39000, 'measurableAsleepDuration': 29760, 'lastSyncTimestampGMT': None, 'minAvgHeartRate': 45, 'maxAvgHeartRate': 141, 'bodyBatteryChargedValue': 51, 'bodyBatteryDrainedValue': 35, 'bodyBatteryHighestValue': 65,
            'bodyBatteryLowestValue': 19, 'bodyBatteryMostRecentValue': 23, 'bodyBatteryDuringSleep': None, 'bodyBatteryVersion': 3.0, 'abnormalHeartRateAlertsCount': None, 'averageSpo2': None, 'lowestSpo2': None, 'latestSpo2': None, 'latestSpo2ReadingTimeGmt': None, 'latestSpo2ReadingTimeLocal': None, 'averageMonitoringEnvironmentAltitude': 118.0, 'restingCaloriesFromActivity': 489.0, 'bodyBatteryDynamicFeedbackEvent': {'eventTimestampGmt': '2024-06-06T18:35:00', 'bodyBatteryLevel': 'MODERATE', 'feedbackShortType': 'SLEEP_PREPARATION_NOT_STRESS_DATA_AND_EXERCISE', 'feedbackLongType': 'SLEEP_PREPARATION_NOT_STRESS_DATA_AND_EXERCISE'}, 'endOfDayBodyBatteryDynamicFeedbackEvent': {'eventTimestampGmt': '2024-06-06T21:53:13', 'bodyBatteryLevel': 'MODERATE', 'feedbackShortType': 'SLEEP_TIME_PASSED_NOT_STRESS_DATA_AND_EXERCISE', 'feedbackLongType': 'SLEEP_TIME_PASSED_NOT_STRESS_DATA_AND_EXERCISE'}, 'bodyBatteryActivityEventList': [{'eventType': 'SLEEP', 'eventStartTimeGmt': '2024-06-05T20:09:01', 'timezoneOffset': 7200000, 'durationInMilliseconds': 31440000, 'bodyBatteryImpact': 52, 'feedbackType': 'NONE', 'shortFeedback': 'NONE', 'deviceId': 3423315346, 'activityName': None, 'activityType': None, 'activityId': None, 'eventUpdateTimeGmt': '2024-06-06T05:28:34'}, {'eventType': 'RECOVERY', 'eventStartTimeGmt': '2024-06-06T06:50:24', 'timezoneOffset': 7200000, 'durationInMilliseconds': 2220000, 'bodyBatteryImpact': 0, 'feedbackType': 'RECOVERY_BODY_BATTERY_NOT_INCREASE', 'shortFeedback': 'RESTFUL_PERIOD', 'deviceId': 3423315346, 'activityName': None, 'activityType': None, 'activityId': None, 'eventUpdateTimeGmt': '2024-06-06T07:30:35'}, {'eventType': 'ACTIVITY', 'eventStartTimeGmt': '2024-06-06T08:01:54', 'timezoneOffset': 7200000, 'durationInMilliseconds': 26640000, 'bodyBatteryImpact': -28, 'feedbackType': 'EXERCISE_TRAINING_EFFECT_2', 'shortFeedback': 'MAINTAINING_AEROBIC_BASE', 'deviceId': 3423315346, 'activityName': "La Bisbal d'Empordà Hiking", 'activityType': 'hiking', 'activityId': 15774991090, 'eventUpdateTimeGmt': '2024-06-06T15:26:52'}], 'avgWakingRespirationValue': 14.0, 'highestRespirationValue': 21.0, 'lowestRespirationValue': 10.0, 'latestRespirationValue': 17.0, 'latestRespirationTimeGMT': '2024-06-06T22:00:00.0'},
    "get_body_composition":
        {'startDate': '2024-06-11', 'endDate': '2024-06-13', 'dateWeightList': [{'samplePk': 1718261884105, 'date': 1718267860000, 'calendarDate': '2024-06-13', 'weight': 85970.0, 'bmi': 24.299999237060547, 'bodyFat': 20.6, 'bodyWater': 52.1, 'boneMass': 3410, 'muscleMass': 64860, 'physiqueRating': None, 'visceralFat': None, 'metabolicAge': None, 'sourceType': 'INDEX_SCALE', 'timestampGMT': 1718260660000, 'weightDelta': None}, {'samplePk': 1718258360422, 'date': 1718109499000, 'calendarDate': '2024-06-11',
                                                                                                                                                                                                                                                                                                                                                                                                                                                'weight': 86440.0, 'bmi': 24.5, 'bodyFat': 19.8, 'bodyWater': 53.4, 'boneMass': 3460, 'muscleMass': 65889, 'physiqueRating': None, 'visceralFat': None, 'metabolicAge': None, 'sourceType': 'INDEX_SCALE', 'timestampGMT': 1718102299000, 'weightDelta': None}], 'totalAverage': {'from': 1718064000000, 'until': 1718323199999, 'weight': 86205.0, 'bmi': 24.399999618530273, 'bodyFat': 20.2, 'bodyWater': 52.8, 'boneMass': 3435, 'muscleMass': 65374, 'physiqueRating': None, 'visceralFat': None, 'metabolicAge': None}},
    "get_rhr_day": {

    },
    "get_training_readiness":
        [{'userProfilePK': 9334852, 'calendarDate': '2024-06-08', 'timestamp': '2024-06-08T03:30:50.0', 'timestampLocal': '2024-06-08T05:30:50.0', 'deviceId': 3423315346, 'level': 'MODERATE', 'feedbackLong': 'MOD_HRV_UNBALANCED', 'feedbackShort': 'TAKE_ON_THE_DAY', 'score': 59, 'sleepScore': 84, 'sleepScoreFactorPercent': 78, 'sleepScoreFactorFeedback': 'GOOD', 'recoveryTime': 1, 'recoveryTimeFactorPercent': 99,
            'recoveryTimeFactorFeedback': 'GOOD', 'acwrFactorPercent': 100, 'acwrFactorFeedback': 'VERY_GOOD', 'acuteLoad': 162, 'stressHistoryFactorPercent': 0, 'stressHistoryFactorFeedback': 'NONE', 'hrvFactorPercent': 59, 'hrvFactorFeedback': 'MODERATE', 'hrvWeeklyAverage': 42, 'sleepHistoryFactorPercent': 46, 'sleepHistoryFactorFeedback': 'MODERATE', 'validSleep': True, 'inputContext': None, 'recoveryTimeChangePhrase': 'NO_CHANGE_SLEEP'}],
    "get_endurance_score":
        {'userProfilePK': 9334852, 'startDate': '2024-06-11', 'endDate': '2024-06-13', 'avg': 5730, 'max': 5730, 'groupMap': {'2024-06-07': {'groupAverage': 5730, 'groupMax': 5730, 'enduranceContributorDTOList': [{'activityTypeId': 3, 'group': None, 'contribution': 77.496666}, {'activityTypeId': 160, 'group': None, 'contribution': 7.126667}, {'activityTypeId': 13, 'group': None, 'contribution': 14.240001}, {'activityTypeId': None, 'group': 8, 'contribution': 1.1366667}]}}, 'enduranceScoreDTO': {
            'userProfilePK': 9334852, 'deviceId': 3423315346, 'calendarDate': '2024-06-13', 'overallScore': 5730, 'classification': 2, 'feedbackPhrase': 30, 'primaryTrainingDevice': True, 'gaugeLowerLimit': 3570, 'classificationLowerLimitIntermediate': 5100, 'classificationLowerLimitTrained': 5800, 'classificationLowerLimitWellTrained': 6500, 'classificationLowerLimitExpert': 7200, 'classificationLowerLimitSuperior': 7900, 'classificationLowerLimitElite': 8600, 'gaugeUpperLimit': 10320, 'contributors': [{'activityTypeId': 3, 'group': None, 'contribution': 78.04}, {'activityTypeId': 13, 'group': None, 'contribution': 13.86}, {'activityTypeId': 160, 'group': None, 'contribution': 6.95}, {'activityTypeId': None, 'group': 8, 'contribution': 1.15}]}},
    "get_training_status":
        {'userId': 9334852, 'mostRecentVO2Max': {'userId': 9334852, 'generic': {'calendarDate': '2024-06-08', 'vo2MaxPreciseValue': 48.6, 'vo2MaxValue': 49.0, 'fitnessAge': None, 'fitnessAgeDescription': None, 'maxMetCategory': 0}, 'cycling': None, 'heatAltitudeAcclimation': {'calendarDate': '2024-06-13', 'altitudeAcclimationDate': '2024-06-12', 'previousAltitudeAcclimationDate': '2024-06-12', 'heatAcclimationDate': '2024-06-12', 'previousHeatAcclimationDate': '2024-06-12', 'altitudeAcclimation': 0, 'previousAltitudeAcclimation': 0, 'heatAcclimationPercentage': 19, 'previousHeatAcclimationPercentage': 22, 'heatTrend': 'DEACCLIMATIZING', 'altitudeTrend': None, 'currentAltitude': 0, 'previousAltitude': 0, 'acclimationPercentage': 0, 'previousAcclimationPercentage': 0, 'altitudeAcclimationLocalTimestamp': '2024-06-13T00:04:34.0'}}, 'mostRecentTrainingLoadBalance': {'userId': 9334852, 'metricsTrainingLoadBalanceDTOMap': {'3423315346': {'calendarDate': '2024-06-13', 'deviceId': 3423315346, 'monthlyLoadAerobicLow': 431.01794, 'monthlyLoadAerobicHigh': 0.0, 'monthlyLoadAnaerobic': 132.51617, 'monthlyLoadAerobicLowTargetMin': 142, 'monthlyLoadAerobicLowTargetMax': 353, 'monthlyLoadAerobicHighTargetMin': 244, 'monthlyLoadAerobicHighTargetMax': 456, 'monthlyLoadAnaerobicTargetMin': 0, 'monthlyLoadAnaerobicTargetMax': 211, 'trainingBalanceFeedbackPhrase':
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  'AEROBIC_HIGH_SHORTAGE', 'primaryTrainingDevice': True}}, 'recordedDevices': [{'deviceId': 3423315346, 'imageURL': 'https://static.garmincdn.com/en/products/010-02582-11/v/cf-sm-2x3-ac4d1374-c804-4a9d-afc5-865b69d339e8.png', 'deviceName': 'EPIX', 'category': 0}]}, 'mostRecentTrainingStatus': {'userId': 9334852, 'latestTrainingStatusData': {'3423315346': {'calendarDate': '2024-06-13', 'sinceDate': '2024-06-09', 'weeklyTrainingLoad': None, 'trainingStatus': 5, 'timestamp': 1718257412000, 'deviceId': 3423315346, 'loadTunnelMin': None, 'loadTunnelMax': None, 'loadLevelTrend': None, 'sport': None, 'subSport': None, 'fitnessTrendSport': 'NONE', 'fitnessTrend': 0, 'trainingStatusFeedbackPhrase': 'RECOVERY_1', 'trainingPaused': False, 'acuteTrainingLoadDTO': {'acwrPercent': 16, 'acwrStatus': 'LOW', 'acwrStatusFeedback': 'FEEDBACK_1', 'dailyTrainingLoadAcute': 107, 'maxTrainingLoadChronic': 328.5, 'minTrainingLoadChronic': 175.20000000000002, 'dailyTrainingLoadChronic': 219, 'dailyAcuteChronicWorkloadRatio': 0.4}, 'primaryTrainingDevice': True}}, 'recordedDevices': [{'deviceId': 3423315346, 'imageURL': 'https://static.garmincdn.com/en/products/010-02582-11/v/cf-sm-2x3-ac4d1374-c804-4a9d-afc5-865b69d339e8.png', 'deviceName': 'EPIX', 'category': 0}], 'showSelector': False, 'lastPrimarySyncDate': '2024-06-13'}, 'heatAltitudeAcclimationDTO': None},
}
