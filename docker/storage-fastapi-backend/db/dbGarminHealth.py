from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.dialects.mysql import insert
from pydanticValidation.db_schemas import SleepData

import logconfig
import config as config
logger = logconfig.logger


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
                )
                await session.execute(stmt)

                return JSONResponse(status_code=200, content={"message": "Sleep data inserted successfully for date: " + userInput.get("calendarDate")})
            except Exception as e:
                logger.error(
                    "Error in DB! insert_sleep_data: %s", str(e))
                # return JSONResponse(content={"success": False, "code": 500, "message": {"status": "fail", "detail": str(e), "result": "Error in DB! edit_chat_message_for_user"}}, status_code=500)
                raise HTTPException(
                    status_code=500, detail="Error in DB! db_edit_message")
