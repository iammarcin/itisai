import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.dialects.mysql import insert
from pydanticValidation.db_schemas import SleepData, UserSummary, BodyComposition, HRVData, TrainingReadiness

from sqlalchemy import select

from db.dbHelper import to_dict

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
                summaryData = userInput["result"]
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
                compositionDataList = userInput["message"]["result"]["dateWeightList"]
                for compositionData in compositionDataList:
                    stmt = insert(BodyComposition).values(
                        customer_id=customerId,
                        calendar_date=compositionData.get("calendarDate"),
                        weight=compositionData.get("weight"),
                        bmi=compositionData.get("bmi"),
                        body_fat=compositionData.get("bodyFat"),
                        body_water=compositionData.get("bodyWater"),
                        bone_mass=compositionData.get("boneMass"),
                        muscle_mass=compositionData.get("muscleMass"),
                        visceral_fat=compositionData.get("visceralFat")
                    ).on_duplicate_key_update(
                        weight=compositionData.get("weight"),
                        bmi=compositionData.get("bmi"),
                        body_fat=compositionData.get("bodyFat"),
                        body_water=compositionData.get("bodyWater"),
                        bone_mass=compositionData.get("boneMass"),
                        muscle_mass=compositionData.get("muscleMass"),
                        visceral_fat=compositionData.get("visceralFat")
                    )
                    await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Body composition data processed successfully for date range: " + userInput["message"]["result"]["startDate"] + " to " + userInput["message"]["result"]["endDate"]})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_body_composition: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_body_composition")


async def insert_hrv_data(AsyncSessionLocal, userInput: dict, customerId):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                hrvSummary = userInput["message"]["result"]["hrvSummary"]
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
                readinessData = userInput["result"][0]
                stmt = insert(TrainingReadiness).values(
                    customer_id=customerId,
                    calendar_date=readinessData.get("calendarDate"),
                    level=readinessData.get("level"),
                    score=readinessData.get("score"),
                    sleep_score=readinessData.get("sleepScore"),
                    sleep_score_factor_feedback=readinessData.get("sleepScoreFactorFeedback"),
                    recovery_time_factor_feedback=readinessData.get("recoveryTimeFactorFeedback"),
                    recovery_time=readinessData.get("recoveryTime"),
                    acute_load=readinessData.get("acuteLoad"),
                    hrv_weekly_average=readinessData.get("hrvWeeklyAverage"),
                    hrv_factor_feedback=readinessData.get("hrvFactorFeedback"),
                    stress_history_factor_feedback=readinessData.get("stressHistoryFactorFeedback"),
                    sleep_history_factor_feedback=readinessData.get("sleepHistoryFactorFeedback")
                ).on_duplicate_key_update(
                    level=readinessData.get("level"),
                    score=readinessData.get("score"),
                    sleep_score=readinessData.get("sleepScore"),
                    sleep_score_factor_feedback=readinessData.get("sleepScoreFactorFeedback"),
                    recovery_time_factor_feedback=readinessData.get("recoveryTimeFactorFeedback"),
                    recovery_time=readinessData.get("recoveryTime"),
                    acute_load=readinessData.get("acuteLoad"),
                    hrv_weekly_average=readinessData.get("hrvWeeklyAverage"),
                    hrv_factor_feedback=readinessData.get("hrvFactorFeedback"),
                    stress_history_factor_feedback=readinessData.get("stressHistoryFactorFeedback"),
                    sleep_history_factor_feedback=readinessData.get("sleepHistoryFactorFeedback")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Training readiness data processed successfully for date: " + readinessData.get("calendarDate")})
            except Exception as e:
                logger.error("Error in DB! insert_training_readiness: %s", str(e))
                raise HTTPException(status_code=500, detail="Error in DB! insert_training_readiness")

async def get_garmin_data(AsyncSessionLocal, userInput: dict, customerId):
    start_date = userInput.get("start_date", None)
    end_date = userInput.get("end_date", None)
    sort_type = userInput.get("sort_type", "asc")
    offset = userInput.get("offset", 0)
    limit = userInput.get("limit", None)
    table = userInput.get("table", None)

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

            query = query.offset(offset)

            result = await session.execute(query)

            data = result.scalars().all()
            data_list = [to_dict(day_data) for day_data in data]

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": data_list}}, status_code=200)
        except Exception as e:
            logger.error("Error in DB! get_garmin_data: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error in DB! get_garmin_data")
