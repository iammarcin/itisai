import logging
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy.dialects.mysql import insert
from pydanticValidation.db_schemas import SleepData, UserSummary, BodyComposition, HRVData, TrainingReadiness, EnduranceScore, TrainingStatus, FitnessAge, TrainingData

from sqlalchemy import select

from db.dbHelper import to_dict
from db.garminHelper import getVO2MaxFeedback, get_latest_vo2max_before_date

import logconfig
import config as config
logger = logconfig.logger

# insert data - but if it's there already, update it
# important i added key in DB - so that it doesn't insert duplicate data
# ALTER TABLE `get_sleep_data`
# ADD UNIQUE KEY `unique_customer_date` (`customer_id`, `calendar_date`);
async def insert_sleep_data(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                mainSleepData = userInput["dailySleepDTO"]
                stmt = insert(SleepData).values(
                    customer_id=customerId,
                    calendar_date=mainSleepData.get("calendarDate"),
                    sleep_time_seconds=mainSleepData.get("sleepTimeSeconds"),
                    nap_time_seconds=mainSleepData.get("napTimeSeconds"),
                    deep_sleep_seconds=mainSleepData.get("deepSleepSeconds"),
                    light_sleep_seconds=mainSleepData.get("lightSleepSeconds"),
                    rem_sleep_seconds=mainSleepData.get("remSleepSeconds"),
                    awake_sleep_seconds=mainSleepData.get("awakeSleepSeconds"),
                    average_respiration_value=mainSleepData.get(
                        "averageRespirationValue"),
                    lowest_respiration_value=mainSleepData.get(
                        "lowestRespirationValue"),
                    highest_respiration_value=mainSleepData.get(
                        "highestRespirationValue"),
                    awake_count=mainSleepData.get("awakeCount"),
                    avg_sleep_stress=mainSleepData.get("avgSleepStress"),
                    sleep_score_feedback=mainSleepData.get(
                        "sleepScoreFeedback"),
                    sleep_score_insight=mainSleepData.get("sleepScoreInsight"),
                    sleep_score_personalized_insight=mainSleepData.get(
                        "sleepScorePersonalizedInsight"),
                    overall_score_value=mainSleepData.get(
                        'sleepScores', {}).get("overall", {}).get("value"),
                    overall_score_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "overall", {}).get("qualifierKey"),
                    rem_percentage_value=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("value"),
                    rem_percentage_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("qualifierKey"),
                    rem_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalStart"),
                    rem_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalEnd"),
                    restlessness_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "restlessness", {}).get("qualifierKey"),
                    restlessness_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalStart"),
                    restlessness_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalEnd"),
                    light_percentage_value=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("value"),
                    light_percentage_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("qualifierKey"),
                    light_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalStart"),
                    light_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalEnd"),
                    deep_percentage_value=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("value"),
                    deep_percentage_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("qualifierKey"),
                    deep_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalStart"),
                    deep_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalEnd"),
                    avg_overnight_hrv=userInput.get("avgOvernightHrv"),
                    resting_heart_rate=userInput.get("restingHeartRate"),
                    body_battery_change=userInput.get("bodyBatteryChange"),
                    restless_moments_count=userInput.get(
                        "restlessMomentsCount")
                ).on_duplicate_key_update(
                    sleep_time_seconds=mainSleepData.get("sleepTimeSeconds"),
                    nap_time_seconds=mainSleepData.get("napTimeSeconds"),
                    deep_sleep_seconds=mainSleepData.get("deepSleepSeconds"),
                    light_sleep_seconds=mainSleepData.get("lightSleepSeconds"),
                    rem_sleep_seconds=mainSleepData.get("remSleepSeconds"),
                    awake_sleep_seconds=mainSleepData.get("awakeSleepSeconds"),
                    average_respiration_value=mainSleepData.get(
                        "averageRespirationValue"),
                    lowest_respiration_value=mainSleepData.get(
                        "lowestRespirationValue"),
                    highest_respiration_value=mainSleepData.get(
                        "highestRespirationValue"),
                    awake_count=mainSleepData.get("awakeCount"),
                    avg_sleep_stress=mainSleepData.get("avgSleepStress"),
                    sleep_score_feedback=mainSleepData.get(
                        "sleepScoreFeedback"),
                    sleep_score_insight=mainSleepData.get("sleepScoreInsight"),
                    sleep_score_personalized_insight=mainSleepData.get(
                        "sleepScorePersonalizedInsight"),
                    overall_score_value=mainSleepData.get(
                        'sleepScores', {}).get("overall", {}).get("value"),
                    overall_score_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "overall", {}).get("qualifierKey"),
                    rem_percentage_value=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("value"),
                    rem_percentage_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("qualifierKey"),
                    rem_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalStart"),
                    rem_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalEnd"),
                    restlessness_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "restlessness", {}).get("qualifierKey"),
                    restlessness_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalStart"),
                    restlessness_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalEnd"),
                    light_percentage_value=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("value"),
                    light_percentage_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("qualifierKey"),
                    light_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalStart"),
                    light_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalEnd"),
                    deep_percentage_value=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("value"),
                    deep_percentage_qualifier=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("qualifierKey"),
                    deep_optimal_start=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalStart"),
                    deep_optimal_end=mainSleepData.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalEnd"),
                    avg_overnight_hrv=userInput.get("avgOvernightHrv"),
                    resting_heart_rate=userInput.get("restingHeartRate"),
                    body_battery_change=userInput.get("bodyBatteryChange"),
                    restless_moments_count=userInput.get(
                        "restlessMomentsCount")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Sleep data processed successfully for date: " + mainSleepData.get("calendarDate")})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_or_update_sleep_data: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_sleep_data")

async def insert_user_summary(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                summaryData = userInput
                stmt = insert(UserSummary).values(
                    customer_id=customerId,
                    calendar_date=summaryData.get("calendarDate"),
                    total_kilocalories=summaryData.get("totalKilocalories"),
                    active_kilocalories=summaryData.get("activeKilocalories"),
                    bmr_kilocalories=summaryData.get("bmrKilocalories"),
                    total_steps=summaryData.get("totalSteps"),
                    total_distance_meters=summaryData.get(
                        "totalDistanceMeters"),
                    min_heart_rate=summaryData.get("minHeartRate"),
                    max_heart_rate=summaryData.get("maxHeartRate"),
                    resting_heart_rate=summaryData.get("restingHeartRate"),
                    last_seven_days_avg_resting_heart_rate=summaryData.get(
                        "lastSevenDaysAvgRestingHeartRate"),
                    vigorous_intensity_minutes=summaryData.get(
                        "vigorousIntensityMinutes"),
                    moderate_intensity_minutes=summaryData.get(
                        "moderateIntensityMinutes"),
                    rest_stress_duration=summaryData.get("restStressDuration"),
                    low_stress_duration=summaryData.get("lowStressDuration"),
                    activity_stress_duration=summaryData.get(
                        "activityStressDuration"),
                    medium_stress_duration=summaryData.get(
                        "mediumStressDuration"),
                    high_stress_duration=summaryData.get("highStressDuration"),
                    stress_qualifier=summaryData.get("stressQualifier"),
                    body_battery_charged_value=summaryData.get(
                        "bodyBatteryChargedValue"),
                    body_battery_drained_value=summaryData.get(
                        "bodyBatteryDrainedValue"),
                    body_battery_highest_value=summaryData.get(
                        "bodyBatteryHighestValue"),
                    body_battery_lowest_value=summaryData.get(
                        "bodyBatteryLowestValue"),
                    body_battery_most_recent_value=summaryData.get(
                        "bodyBatteryMostRecentValue"),
                    avg_waking_respiration_value=summaryData.get(
                        "avgWakingRespirationValue"),
                    highest_respiration_value=summaryData.get(
                        "highestRespirationValue"),
                    lowest_respiration_value=summaryData.get(
                        "lowestRespirationValue"),
                    latest_respiration_value=summaryData.get(
                        "latestRespirationValue")
                ).on_duplicate_key_update(
                    total_kilocalories=summaryData.get("totalKilocalories"),
                    active_kilocalories=summaryData.get("activeKilocalories"),
                    bmr_kilocalories=summaryData.get("bmrKilocalories"),
                    total_steps=summaryData.get("totalSteps"),
                    total_distance_meters=summaryData.get(
                        "totalDistanceMeters"),
                    min_heart_rate=summaryData.get("minHeartRate"),
                    max_heart_rate=summaryData.get("maxHeartRate"),
                    resting_heart_rate=summaryData.get("restingHeartRate"),
                    last_seven_days_avg_resting_heart_rate=summaryData.get(
                        "lastSevenDaysAvgRestingHeartRate"),
                    vigorous_intensity_minutes=summaryData.get(
                        "vigorousIntensityMinutes"),
                    moderate_intensity_minutes=summaryData.get(
                        "moderateIntensityMinutes"),
                    rest_stress_duration=summaryData.get("restStressDuration"),
                    low_stress_duration=summaryData.get("lowStressDuration"),
                    activity_stress_duration=summaryData.get(
                        "activityStressDuration"),
                    medium_stress_duration=summaryData.get(
                        "mediumStressDuration"),
                    high_stress_duration=summaryData.get("highStressDuration"),
                    stress_qualifier=summaryData.get("stressQualifier"),
                    body_battery_charged_value=summaryData.get(
                        "bodyBatteryChargedValue"),
                    body_battery_drained_value=summaryData.get(
                        "bodyBatteryDrainedValue"),
                    body_battery_highest_value=summaryData.get(
                        "bodyBatteryHighestValue"),
                    body_battery_lowest_value=summaryData.get(
                        "bodyBatteryLowestValue"),
                    body_battery_most_recent_value=summaryData.get(
                        "bodyBatteryMostRecentValue"),
                    avg_waking_respiration_value=summaryData.get(
                        "avgWakingRespirationValue"),
                    highest_respiration_value=summaryData.get(
                        "highestRespirationValue"),
                    lowest_respiration_value=summaryData.get(
                        "lowestRespirationValue"),
                    latest_respiration_value=summaryData.get(
                        "latestRespirationValue")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "User summary data processed successfully for date: " + summaryData.get("calendarDate")})
            except Exception as e:
                logger.error("Error in DB! insert_user_summary: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_user_summary")

async def insert_body_composition(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                compositionData = userInput
                stmt = insert(BodyComposition).values(
                    customer_id=customerId,
                    calendar_date=compositionData.get("calendar_date"),
                    weight=compositionData.get("weight"),
                    bmi=compositionData.get("bmi"),
                    body_fat_mass=compositionData.get("body_fat_mass"),
                    body_fat_percentage=compositionData.get(
                        "body_fat_percentage"),
                    body_water_mass=compositionData.get("body_water_mass"),
                    body_water_percentage=compositionData.get(
                        "body_water_percentage"),
                    bone_mass=compositionData.get("bone_mass"),
                    bone_mass_percentage=compositionData.get(
                        "bone_mass_percentage"),
                    muscle_mass=compositionData.get("muscle_mass"),
                    muscle_mass_percentage=compositionData.get(
                        "muscle_mass_percentage"),
                    visceral_fat=compositionData.get("visceral_fat"),
                    basal_metabolic_rate=compositionData.get(
                        "basal_metabolic_rate")
                ).on_duplicate_key_update(
                    weight=compositionData.get("weight"),
                    bmi=compositionData.get("bmi"),
                    body_fat_mass=compositionData.get("body_fat_mass"),
                    body_fat_percentage=compositionData.get(
                        "body_fat_percentage"),
                    body_water_mass=compositionData.get("body_water_mass"),
                    body_water_percentage=compositionData.get(
                        "body_water_percentage"),
                    bone_mass=compositionData.get("bone_mass"),
                    bone_mass_percentage=compositionData.get(
                        "bone_mass_percentage"),
                    muscle_mass=compositionData.get("muscle_mass"),
                    muscle_mass_percentage=compositionData.get(
                        "muscle_mass_percentage"),
                    visceral_fat=compositionData.get("visceral_fat"),
                    basal_metabolic_rate=compositionData.get(
                        "basal_metabolic_rate")
                )
                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Body composition data processed successfully for date %s " % compositionData.get("calendar_date")})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_body_composition: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_body_composition")


async def insert_hrv_data(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                hrvSummary = userInput["hrvSummary"]
                stmt = insert(HRVData).values(
                    customer_id=customerId,
                    calendar_date=hrvSummary.get("calendarDate"),
                    weekly_avg=hrvSummary.get("weeklyAvg"),
                    last_night_avg=hrvSummary.get("lastNightAvg"),
                    status=hrvSummary.get("status"),
                    baseline_balanced_low=hrvSummary.get(
                        "baseline", {}).get("balancedLow"),
                    baseline_balanced_upper=hrvSummary.get(
                        "baseline", {}).get("balancedUpper")
                ).on_duplicate_key_update(
                    weekly_avg=hrvSummary.get("weeklyAvg"),
                    last_night_avg=hrvSummary.get("lastNightAvg"),
                    status=hrvSummary.get("status"),
                    baseline_balanced_low=hrvSummary.get(
                        "baseline", {}).get("balancedLow"),
                    baseline_balanced_upper=hrvSummary.get(
                        "baseline", {}).get("balancedUpper")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "HRV data processed successfully for date: " + hrvSummary.get("calendarDate")})
            except Exception as e:
                logger.error("Error in DB! insert_hrv_data: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_hrv_data")

async def insert_training_readiness(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                readinessData = userInput
                stmt = insert(TrainingReadiness).values(
                    customer_id=customerId,
                    calendar_date=readinessData.get("calendarDate"),
                    level=readinessData.get("level"),
                    score=readinessData.get("score"),
                    sleep_score=readinessData.get("sleepScore"),
                    sleep_score_factor_feedback=readinessData.get(
                        "sleepScoreFactorFeedback"),
                    recovery_time_factor_feedback=readinessData.get(
                        "recoveryTimeFactorFeedback"),
                    recovery_time=readinessData.get("recoveryTime"),
                    acute_load=readinessData.get("acuteLoad"),
                    hrv_weekly_average=readinessData.get("hrvWeeklyAverage"),
                    hrv_factor_feedback=readinessData.get("hrvFactorFeedback"),
                    stress_history_factor_feedback=readinessData.get(
                        "stressHistoryFactorFeedback"),
                    sleep_history_factor_feedback=readinessData.get(
                        "sleepHistoryFactorFeedback")
                ).on_duplicate_key_update(
                    level=readinessData.get("level"),
                    score=readinessData.get("score"),
                    sleep_score=readinessData.get("sleepScore"),
                    sleep_score_factor_feedback=readinessData.get(
                        "sleepScoreFactorFeedback"),
                    recovery_time_factor_feedback=readinessData.get(
                        "recoveryTimeFactorFeedback"),
                    recovery_time=readinessData.get("recoveryTime"),
                    acute_load=readinessData.get("acuteLoad"),
                    hrv_weekly_average=readinessData.get("hrvWeeklyAverage"),
                    hrv_factor_feedback=readinessData.get("hrvFactorFeedback"),
                    stress_history_factor_feedback=readinessData.get(
                        "stressHistoryFactorFeedback"),
                    sleep_history_factor_feedback=readinessData.get(
                        "sleepHistoryFactorFeedback")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Training readiness data processed successfully for date: " + readinessData.get("calendarDate")})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_training_readiness: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_training_readiness")

async def insert_endurance_score(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                scoreData = userInput
                stmt = insert(EnduranceScore).values(
                    customer_id=customerId,
                    calendar_date=scoreData.get("calendarDate"),
                    overall_score=scoreData.get("overallScore"),
                    classification=scoreData.get("classification"),
                    classification_lower_limit_intermediate=scoreData.get(
                        "classificationLowerLimitIntermediate"),
                    classification_lower_limit_trained=scoreData.get(
                        "classificationLowerLimitTrained"),
                    classification_lower_limit_well_trained=scoreData.get(
                        "classificationLowerLimitWellTrained"),
                    classification_lower_limit_expert=scoreData.get(
                        "classificationLowerLimitExpert"),
                    classification_lower_limit_superior=scoreData.get(
                        "classificationLowerLimitSuperior"),
                    classification_lower_limit_elite=scoreData.get(
                        "classificationLowerLimitElite"),
                    contributors=scoreData.get("contributors")
                ).on_duplicate_key_update(
                    overall_score=scoreData.get("overallScore"),
                    classification=scoreData.get("classification"),
                    classification_lower_limit_intermediate=scoreData.get(
                        "classificationLowerLimitIntermediate"),
                    classification_lower_limit_trained=scoreData.get(
                        "classificationLowerLimitTrained"),
                    classification_lower_limit_well_trained=scoreData.get(
                        "classificationLowerLimitWellTrained"),
                    classification_lower_limit_expert=scoreData.get(
                        "classificationLowerLimitExpert"),
                    classification_lower_limit_superior=scoreData.get(
                        "classificationLowerLimitSuperior"),
                    classification_lower_limit_elite=scoreData.get(
                        "classificationLowerLimitElite"),
                    contributors=scoreData.get("contributors")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Endurance score data processed successfully for date: " + scoreData.get("calendarDate")})
            except Exception as e:
                logger.error("Error in DB! insert_endurance_score: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_endurance_score")

async def insert_training_status(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                latest_training_status_data = userInput["latestTrainingStatusData"]
                # on next level (key?) under latestTrainingStatusData - there is number (id) - which can vary
                data = next(iter(latest_training_status_data.values()))

                stmt = insert(TrainingStatus).values(
                    customer_id=customerId,
                    calendar_date=data.get("calendarDate"),
                    daily_training_load_acute=data["acuteTrainingLoadDTO"].get(
                        "dailyTrainingLoadAcute"),
                    daily_training_load_acute_feedback=data["acuteTrainingLoadDTO"].get(
                        "acwrStatus"),
                    daily_training_load_chronic=data["acuteTrainingLoadDTO"].get(
                        "dailyTrainingLoadChronic"),
                    min_training_load_chronic=data["acuteTrainingLoadDTO"].get(
                        "minTrainingLoadChronic"),
                    max_training_load_chronic=data["acuteTrainingLoadDTO"].get(
                        "maxTrainingLoadChronic")
                ).on_duplicate_key_update(
                    daily_training_load_acute=data["acuteTrainingLoadDTO"].get(
                        "dailyTrainingLoadAcute"),
                    daily_training_load_acute_feedback=data["acuteTrainingLoadDTO"].get(
                        "acwrStatus"),
                    daily_training_load_chronic=data["acuteTrainingLoadDTO"].get(
                        "dailyTrainingLoadChronic"),
                    min_training_load_chronic=data["acuteTrainingLoadDTO"].get(
                        "minTrainingLoadChronic"),
                    max_training_load_chronic=data["acuteTrainingLoadDTO"].get(
                        "maxTrainingLoadChronic")
                )
                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Training status data processed successfully for day: " + data.get("calendarDate")})
            except Exception as e:
                logger.error("Error in DB! insert_training_status: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_training_status")

# here we really get vo2max value only (and get the feedback per age)
# it's little bit more complex then other functions because the data is set around monthly
# so we get this data and save every day the same value - based on monthly value from garmin
async def insert_max_metrics(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                target_date_str = userInput.get("date")
                if not target_date_str:
                    return JSONResponse(status_code=400, content={"message": "Target date is required"})

                target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

                # Get the latest vo2MaxPreciseValue before the target_date
                latest_entry = await get_latest_vo2max_before_date(userInput, target_date_str)
                if not latest_entry:
                    return JSONResponse(status_code=404, content={"message": "No valid VO2 max data found before the target date"})

                data = latest_entry["generic"]
                vo2_max_precise_value = data.get("vo2MaxPreciseValue")

                # Calculate custom feedback based on garminHelper json with ranges
                age = userInput.get("age", datetime.now().year - 1981)
                sex = userInput.get("sex", "male").upper()
                vo2_max_feedback = getVO2MaxFeedback(
                    sex, age, vo2_max_precise_value)

                # Prepare the statement for insertion or update
                stmt = insert(TrainingStatus).values(
                    customer_id=customerId,
                    calendar_date=target_date.strftime("%Y-%m-%d"),
                    vo2_max_precise_value=vo2_max_precise_value,
                    vo2_max_feedback=vo2_max_feedback,
                ).on_duplicate_key_update(
                    vo2_max_precise_value=vo2_max_precise_value,
                    vo2_max_feedback=vo2_max_feedback,
                )

                # Execute the statement
                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Max metrics data processed successfully for day: " + target_date.strftime("%Y-%m-%d")})

            except Exception as e:
                logger.error("Error in DB! insert_max_metrics: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_max_metrics")

async def insert_training_load_balance(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                metrics_data = userInput["metricsTrainingLoadBalanceDTOMap"]

                # on next level (key?) under metricsTrainingLoadBalanceDTOMap - there is number (id) - which can vary
                data = next(iter(metrics_data.values()))

                stmt = insert(TrainingStatus).values(
                    customer_id=customerId,
                    calendar_date=data.get("calendarDate"),
                    monthly_load_anaerobic=data.get(
                        "monthlyLoadAnaerobic"),
                    monthly_load_aerobic_high=data.get(
                        "monthlyLoadAerobicHigh"),
                    monthly_load_aerobic_low=data.get(
                        "monthlyLoadAerobicLow"),
                    monthly_load_aerobic_low_target_min=data.get(
                        "monthlyLoadAerobicLowTargetMin"),
                    monthly_load_aerobic_low_target_max=data.get(
                        "monthlyLoadAerobicLowTargetMax"),
                    monthly_load_aerobic_high_target_min=data.get(
                        "monthlyLoadAerobicHighTargetMin"),
                    monthly_load_aerobic_high_target_max=data.get(
                        "monthlyLoadAerobicHighTargetMax"),
                    monthly_load_anaerobic_target_min=data.get(
                        "monthlyLoadAnaerobicTargetMin"),
                    monthly_load_anaerobic_target_max=data.get(
                        "monthlyLoadAnaerobicTargetMax"),
                    training_balance_feedback_phrase=data.get(
                        "trainingBalanceFeedbackPhrase")
                ).on_duplicate_key_update(
                    monthly_load_anaerobic=data.get(
                        "monthlyLoadAnaerobic"),
                    monthly_load_aerobic_high=data.get(
                        "monthlyLoadAerobicHigh"),
                    monthly_load_aerobic_low=data.get(
                        "monthlyLoadAerobicLow"),
                    monthly_load_aerobic_low_target_min=data.get(
                        "monthlyLoadAerobicLowTargetMin"),
                    monthly_load_aerobic_low_target_max=data.get(
                        "monthlyLoadAerobicLowTargetMax"),
                    monthly_load_aerobic_high_target_min=data.get(
                        "monthlyLoadAerobicHighTargetMin"),
                    monthly_load_aerobic_high_target_max=data.get(
                        "monthlyLoadAerobicHighTargetMax"),
                    monthly_load_anaerobic_target_min=data.get(
                        "monthlyLoadAnaerobicTargetMin"),
                    monthly_load_anaerobic_target_max=data.get(
                        "monthlyLoadAnaerobicTargetMax"),
                    training_balance_feedback_phrase=data.get(
                        "trainingBalanceFeedbackPhrase")
                )
                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Training load balance data processed successfully for day: " + data.get("calendarDate")})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_training_load_balance: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_training_load_balance")

async def insert_fitness_age(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                fitnessData = userInput
                stmt = insert(FitnessAge).values(
                    customer_id=customerId,
                    calendar_date=fitnessData.get("lastUpdated"),
                    chronological_age=fitnessData.get("chronologicalAge"),
                    fitness_age=fitnessData.get("fitnessAge"),
                    body_fat_value=fitnessData.get("components", {}).get(
                        "bodyFat", {}).get("value"),
                    vigorous_days_avg_value=fitnessData.get(
                        "components", {}).get("vigorousDaysAvg", {}).get("value"),
                    rhr_value=fitnessData.get("components", {}).get(
                        "rhr", {}).get("value"),
                    vigorous_minutes_avg_value=fitnessData.get(
                        "components", {}).get("vigorousMinutesAvg", {}).get("value")
                ).on_duplicate_key_update(
                    chronological_age=fitnessData.get("chronologicalAge"),
                    fitness_age=fitnessData.get("fitnessAge"),
                    body_fat_value=fitnessData.get("components", {}).get(
                        "bodyFat", {}).get("value"),
                    vigorous_days_avg_value=fitnessData.get(
                        "components", {}).get("vigorousDaysAvg", {}).get("value"),
                    rhr_value=fitnessData.get("components", {}).get(
                        "rhr", {}).get("value"),
                    vigorous_minutes_avg_value=fitnessData.get(
                        "components", {}).get("vigorousMinutesAvg", {}).get("value")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Fitness age data processed successfully for date: " + fitnessData.get("lastUpdated")})
            except Exception as e:
                logger.error("Error in DB! insert_fitness_age: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_fitness_age")

async def insert_activity_data(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                activity = userInput

                # Extracting secsInZone data
                secs_in_zone = {
                    f"secs_in_zone{zone['zoneNumber']}": zone["secsInZone"] for zone in activity.get("zones", [])}

                stmt = insert(TrainingData).values(
                    customer_id=customerId,
                    calendar_date=activity.get("startTimeLocal").split(" ")[0],
                    activity_id=activity.get("activityId"),
                    activity_type=activity.get(
                        "activityType", {}).get("typeKey"),
                    distance=activity.get("distance"),
                    duration=activity.get("duration"),
                    elevation_gain=activity.get("elevationGain"),
                    elevation_loss=activity.get("elevationLoss"),
                    min_elevation=activity.get("minElevation"),
                    max_elevation=activity.get("maxElevation"),
                    calories=activity.get("calories"),
                    bmr_calories=activity.get("bmrCalories"),
                    steps=activity.get("steps"),
                    aerobic_training_effect=activity.get(
                        "aerobicTrainingEffect"),
                    anaerobic_training_effect=activity.get(
                        "anaerobicTrainingEffect"),
                    activity_training_load=activity.get(
                        "activityTrainingLoad"),
                    training_effect_label=activity.get("trainingEffectLabel"),
                    aerobic_training_effect_message=activity.get(
                        "aerobicTrainingEffectMessage"),
                    anaerobic_training_effect_message=activity.get(
                        "anaerobicTrainingEffectMessage"),
                    moderate_intensity_minutes=activity.get(
                        "moderateIntensityMinutes"),
                    vigorous_intensity_minutes=activity.get(
                        "vigorousIntensityMinutes"),
                    difference_body_battery=activity.get(
                        "differenceBodyBattery"),
                    secs_in_zone1=secs_in_zone.get("secs_in_zone1"),
                    secs_in_zone2=secs_in_zone.get("secs_in_zone2"),
                    secs_in_zone3=secs_in_zone.get("secs_in_zone3"),
                    secs_in_zone4=secs_in_zone.get("secs_in_zone4"),
                    secs_in_zone5=secs_in_zone.get("secs_in_zone5")
                ).on_duplicate_key_update(
                    activity_type=activity.get(
                        "activityType", {}).get("typeKey"),
                    distance=activity.get("distance"),
                    duration=activity.get("duration"),
                    elevation_gain=activity.get("elevationGain"),
                    elevation_loss=activity.get("elevationLoss"),
                    min_elevation=activity.get("minElevation"),
                    max_elevation=activity.get("maxElevation"),
                    calories=activity.get("calories"),
                    bmr_calories=activity.get("bmrCalories"),
                    steps=activity.get("steps"),
                    aerobic_training_effect=activity.get(
                        "aerobicTrainingEffect"),
                    anaerobic_training_effect=activity.get(
                        "anaerobicTrainingEffect"),
                    activity_training_load=activity.get(
                        "activityTrainingLoad"),
                    training_effect_label=activity.get("trainingEffectLabel"),
                    aerobic_training_effect_message=activity.get(
                        "aerobicTrainingEffectMessage"),
                    anaerobic_training_effect_message=activity.get(
                        "anaerobicTrainingEffectMessage"),
                    moderate_intensity_minutes=activity.get(
                        "moderateIntensityMinutes"),
                    vigorous_intensity_minutes=activity.get(
                        "vigorousIntensityMinutes"),
                    difference_body_battery=activity.get(
                        "differenceBodyBattery"),
                    secs_in_zone1=secs_in_zone.get("secs_in_zone1"),
                    secs_in_zone2=secs_in_zone.get("secs_in_zone2"),
                    secs_in_zone3=secs_in_zone.get("secs_in_zone3"),
                    secs_in_zone4=secs_in_zone.get("secs_in_zone4"),
                    secs_in_zone5=secs_in_zone.get("secs_in_zone5")
                )

                await session.execute(stmt)
                await session.commit()

                return JSONResponse(status_code=200, content={"message": "Activity processed. Date: %s , activity_id: %s" % (activity.get("startTimeLocal").split(" ")[0], activity.get("activityId"))})
            except Exception as e:
                logger.error("Error in DB! insert_activity_data: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_activity_data")


async def get_garmin_data(AsyncSessionLocal, userInput: dict, customerId):
    start_date = userInput.get("start_date", None)
    end_date = userInput.get("end_date", None)
    sort_type = userInput.get("sort_type", "asc")
    offset = userInput.get("offset", 0)
    limit = userInput.get("limit", None)
    table = userInput.get("table", None)
    # these flags (by default False) - will filter out null values for vo2max and training load (explained in garminHelper get_latest_data)
    ignore_null_vo2max = userInput.get("ignore_null_vo2max", False)
    ignore_null_training_load_data = userInput.get(
        "ignore_null_training_load_data", False)

    if table == "get_sleep_data":
        model = SleepData
    elif table == "get_user_summary":
        model = UserSummary
    elif table == "get_body_composition":
        model = BodyComposition
    elif table == "get_hrv_data":
        model = HRVData
    elif table == "get_training_readiness":
        model = TrainingReadiness
    elif table == "get_endurance_score":
        model = EnduranceScore
    elif table == "get_training_status":
        model = TrainingStatus
    elif table == "get_fitness_age":
        model = FitnessAge
    elif table == "get_activities":
        model = TrainingData
    else:
        raise HTTPException(status_code=400, detail="Invalid table name")

    sort_order = model.calendar_date.asc(
    ) if sort_type == "asc" else model.calendar_date.desc()

    async with AsyncSessionLocal() as session:
        try:
            query = select(model).where(model.customer_id == customerId)

            if start_date:
                query = query.where(model.calendar_date >= start_date)
            if end_date:
                query = query.where(model.calendar_date <= end_date)

            query = query.order_by(sort_order)

            if limit is not None:
                query = query.limit(limit)

            if ignore_null_vo2max:
                query = query.where(model.vo2_max_precise_value != None)

            if ignore_null_training_load_data:
                query = query.where(model.monthly_load_anaerobic != None)

            query = query.offset(offset)

            result = await session.execute(query)

            data = result.scalars().all()
            data_list = [to_dict(day_data) for day_data in data]

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": data_list}}, status_code=200)
        except Exception as e:
            logger.error("Error in DB! get_garmin_data: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error in DB! get_garmin_data")
