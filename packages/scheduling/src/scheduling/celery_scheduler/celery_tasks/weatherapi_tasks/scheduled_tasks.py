from celery.schedules import crontab

SCHEDULED_TASK_15m_weatherapi_current_weather = {
    "15m_weaterapi_current_weather": {
        "task": "request_current_weather",
        "schedule": crontab(minute="*/15"),
    }
}

# SCHEDULED_TASK_30m_weatherapi_weather_forecast = {
#     "30m_weatherapi_weather_forecast": {
#         "task": ""
#     }
# }