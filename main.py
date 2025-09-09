from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tours import get_all_dates, get_categories, get_tour_by_name  # Исправлено
from typing import List, Dict
from pydantic import BaseModel
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "https://inforestsbot-calendar.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalendarEvent(BaseModel):
    title: str
    start: str
    end: str
    extendedProps: Dict

@app.get("/tours/dates", response_model=List[CalendarEvent])
async def get_tour_dates(category: str = None):
    try:
        dates = get_all_dates()
        logger.info(f"Получено дат: {len(dates)}")
        if category:
            dates = [date for date in dates if date["category"] == category]
            logger.info(f"Фильтрация по категории '{category}': {len(dates)} дат")
       
        events = []
        for date in dates:
            tour_name = date["tour_name"]
            shift = date["shift"]
            date_range = date["date"].split(" to ")
            if len(date_range) != 2:
                logger.warning(f"Некорректный формат даты: {date['date']}")
                continue
            start_date, end_date = date_range
            events.append({
                "title": tour_name,
                "start": start_date,
                "end": end_date,
                "extendedProps": {
                    "shift": shift,
                    "category": date["category"],
                    "price": date["price"],
                    "places": date["places"]
                }
            })
        logger.info(f"Создано событий: {len(events)}")
        events.sort(key=lambda x: x["start"])
        return events
    except Exception as e:
        logger.error(f"Ошибка в /tours/dates: {e}")
        return []

@app.get("/tours/categories", response_model=List[str])
async def get_tour_categories():
    try:
        categories = get_categories()
        logger.info(f"Получено категорий: {len(categories)}")
        return categories
    except Exception as e:
        logger.error(f"Ошибка в /tours/categories: {e}")
        return []
