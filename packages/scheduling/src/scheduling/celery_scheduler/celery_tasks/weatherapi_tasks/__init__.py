from __future__ import annotations

from .adhoc_tasks import task_adhoc_current_weather, task_adhoc_weather_forecast
from .scheduled_tasks import (
    SCHEDULED_TASK_15m_weatherapi_current_weather,
    SCHEDULED_TASK_30m_weatherapi_weather_forecast,
    SCHEDULED_TASK_test_minutely_weatherapi_current_weather,
    SCHEDULED_TASK_test_minutely_weatherapi_weather_forecast
)
from .tasks import task_current_weather, task_weather_forecast
