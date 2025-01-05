from __future__ import annotations

from celery.schedules import crontab
from weather_client.apis import api_weatherapi

SCHEDULED_TASK_15m_weatherapi_current_weather = {
    "15m_weaterapi_current_weather": {
        "task": "request_current_weather",
        "schedule": crontab(minute="*/15"),
        "args": [
            api_weatherapi.location_name,
        ]
    }
}

SCHEDULED_TASK_30m_weatherapi_weather_forecast = {
    "30m_weatherapi_weather_forecast": {
        "task": "request_weather_forecast",
        "schedule": crontab(hour="*/30"),
        "args": [
            api_weatherapi.location_name,
        ]
    }
}

SCHEDULED_TASK_test_minutely_weatherapi_current_weather = {
    "test_minutely_weatherapi_current_weather": {
        "task": "request_current_weather",
        "schedule": crontab(minute="*"),
        "args": [
            api_weatherapi.location_name,
        ]
    }
}

SCHEDULED_TASK_test_minutely_weatherapi_weather_forecast = {
    "test_minutely_weatherapi_weather_forecast": {
        "task": "request_weather_forecast",
        "schedule": crontab(minute="*"),
        "args": [
            api_weatherapi.location_name,
        ]
    }
}