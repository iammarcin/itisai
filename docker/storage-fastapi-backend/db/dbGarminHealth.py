from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.dialects.mysql import insert
from pydanticValidation.db_schemas import SleepData

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
                stmt = insert(SleepData).values(
                    customer_id=customerId,
                    calendar_date=userInput.get("calendarDate"),
                    sleep_time_seconds=userInput.get("sleepTimeSeconds"),
                    nap_time_seconds=userInput.get("napTimeSeconds"),
                    deep_sleep_seconds=userInput.get("deepSleepSeconds"),
                    light_sleep_seconds=userInput.get("lightSleepSeconds"),
                    rem_sleep_seconds=userInput.get("remSleepSeconds"),
                    awake_sleep_seconds=userInput.get("awakeSleepSeconds"),
                    average_respiration_value=userInput.get(
                        "averageRespirationValue"),
                    lowest_respiration_value=userInput.get(
                        "lowestRespirationValue"),
                    highest_respiration_value=userInput.get(
                        "highestRespirationValue"),
                    awake_count=userInput.get("awakeCount"),
                    avg_sleep_stress=userInput.get("avgSleepStress"),
                    sleep_score_feedback=userInput.get("sleepScoreFeedback"),
                    sleep_score_insight=userInput.get("sleepScoreInsight"),
                    sleep_score_personalized_insight=userInput.get(
                        "sleepScorePersonalizedInsight"),
                    overall_score_value=userInput.get(
                        'sleepScores', {}).get("overall", {}).get("value"),
                    overall_score_qualifier=userInput.get('sleepScores', {}).get(
                        "overall", {}).get("qualifierKey"),
                    rem_percentage_value=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("value"),
                    rem_percentage_qualifier=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("qualifierKey"),
                    rem_optimal_start=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalStart"),
                    rem_optimal_end=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalEnd"),
                    restlessness_qualifier=userInput.get('sleepScores', {}).get(
                        "restlessness", {}).get("qualifierKey"),
                    restlessness_optimal_start=userInput.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalStart"),
                    restlessness_optimal_end=userInput.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalEnd"),
                    light_percentage_value=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("value"),
                    light_percentage_qualifier=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("qualifierKey"),
                    light_optimal_start=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalStart"),
                    light_optimal_end=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalEnd"),
                    deep_percentage_value=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("value"),
                    deep_percentage_qualifier=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("qualifierKey"),
                    deep_optimal_start=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalStart"),
                    deep_optimal_end=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalEnd"),
                    avg_overnight_hrv=userInput.get("avgOvernightHrv"),
                    resting_heart_rate=userInput.get("restingHeartRate"),
                    body_battery_change=userInput.get("bodyBatteryChange"),
                    restless_moments_count=userInput.get(
                        "restlessMomentsCount")
                ).on_duplicate_key_update(
                    sleep_time_seconds=userInput.get("sleepTimeSeconds"),
                    nap_time_seconds=userInput.get("napTimeSeconds"),
                    deep_sleep_seconds=userInput.get("deepSleepSeconds"),
                    light_sleep_seconds=userInput.get("lightSleepSeconds"),
                    rem_sleep_seconds=userInput.get("remSleepSeconds"),
                    awake_sleep_seconds=userInput.get("awakeSleepSeconds"),
                    average_respiration_value=userInput.get(
                        "averageRespirationValue"),
                    lowest_respiration_value=userInput.get(
                        "lowestRespirationValue"),
                    highest_respiration_value=userInput.get(
                        "highestRespirationValue"),
                    awake_count=userInput.get("awakeCount"),
                    avg_sleep_stress=userInput.get("avgSleepStress"),
                    sleep_score_feedback=userInput.get("sleepScoreFeedback"),
                    sleep_score_insight=userInput.get("sleepScoreInsight"),
                    sleep_score_personalized_insight=userInput.get(
                        "sleepScorePersonalizedInsight"),
                    overall_score_value=userInput.get(
                        'sleepScores', {}).get("overall", {}).get("value"),
                    overall_score_qualifier=userInput.get('sleepScores', {}).get(
                        "overall", {}).get("qualifierKey"),
                    rem_percentage_value=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("value"),
                    rem_percentage_qualifier=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("qualifierKey"),
                    rem_optimal_start=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalStart"),
                    rem_optimal_end=userInput.get('sleepScores', {}).get(
                        "remPercentage", {}).get("optimalEnd"),
                    restlessness_qualifier=userInput.get('sleepScores', {}).get(
                        "restlessness", {}).get("qualifierKey"),
                    restlessness_optimal_start=userInput.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalStart"),
                    restlessness_optimal_end=userInput.get('sleepScores', {}).get(
                        "restlessness", {}).get("optimalEnd"),
                    light_percentage_value=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("value"),
                    light_percentage_qualifier=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("qualifierKey"),
                    light_optimal_start=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalStart"),
                    light_optimal_end=userInput.get('sleepScores', {}).get(
                        "lightPercentage", {}).get("optimalEnd"),
                    deep_percentage_value=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("value"),
                    deep_percentage_qualifier=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("qualifierKey"),
                    deep_optimal_start=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalStart"),
                    deep_optimal_end=userInput.get('sleepScores', {}).get(
                        "deepPercentage", {}).get("optimalEnd"),
                    avg_overnight_hrv=userInput.get("avgOvernightHrv"),
                    resting_heart_rate=userInput.get("restingHeartRate"),
                    body_battery_change=userInput.get("bodyBatteryChange"),
                    restless_moments_count=userInput.get(
                        "restlessMomentsCount")
                )

                await session.execute(stmt)
                return JSONResponse(status_code=200, content={"message": "Sleep data processed successfully for date: " + userInput.get("calendarDate")})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_or_update_sleep_data: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error in DB! insert_sleep_data")

async def get_sleep_data(AsyncSessionLocal, userInput: dict, customerId):
    start_date = userInput.get("start_date", None)
    end_date = userInput.get("end_date", None)
    sort_type = userInput.get("sort_type", "asc")
    offset = userInput.get("offset", 0)
    limit = userInput.get("limit", None)

    sort_order = SleepData.calendar_date.asc(
    ) if sort_type == "asc" else SleepData.calendar_date.desc()

    async with AsyncSessionLocal() as session:
        try:
            query = select(SleepData).where(
                SleepData.customer_id == customerId)

            if start_date:
                query = query.where(SleepData.calendar_date >= start_date)
            if end_date:
                query = query.where(SleepData.calendar_date <= end_date)

            query = query.order_by(sort_order)

            if limit is not None:
                query = query.limit(limit)

            query = query.offset(offset)

            print(query)

            result = await session.execute(query)

            data = result.scalars().all()
            data_list = [to_dict(day_data) for day_data in data]

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": data_list}}, status_code=200)
        except Exception as e:
            logger.error(
                "Error in DB! get_sleep_data: %s", str(e))
            # return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! get_all_chat_sessions_for_user"}}, status_code=500)
            raise HTTPException(
                status_code=500, detail="Error in DB! get_sleep_data")
