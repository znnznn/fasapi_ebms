import calendar
from datetime import datetime

from fastapi import HTTPException


class DateValidator:
    @staticmethod
    def validate_year(year: int):
        if year < 2021 or year > 2100:
            raise HTTPException(status_code=404, detail="Year must be between 2021 and 2030")

    @staticmethod
    def validate_month(month: int):
        if month < 1 or month > 12:
            raise HTTPException(status_code=404, detail="Month must be between 1 and 12")

    @staticmethod
    def validate_calendar_date(year: int, month: int):
        DateValidator.validate_year(year)
        DateValidator.validate_month(month)

    @staticmethod
    def get_month_days(year: int, month: int) -> list[str]:
        return [datetime(year, month, day).strftime('%Y-%m-%d') for day in range(1, calendar.monthrange(year, month)[1] + 1)]
