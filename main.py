from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from tours import get_all_dates, get_categories, get_tour_by_name
from typing import List, Dict
from pydantic import BaseModel
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "https://inforestsbot-calendar.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
logger.info(f"Разрешенные источники CORS: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Явная обработка OPTIONS
@app.options("/tours/categories")
async def options_categories():
    logger.info("Получен запрос OPTIONS для /tours/categories")
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": allowed_origins_env,
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

@app.options("/tours/dates")
async def options_dates():
    logger.info("Получен запрос OPTIONS для /tours/dates")
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": allowed_origins_env,
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

class CalendarEvent(BaseModel):
    title: str
    start: str
    end: str
    extendedProps: Dict

@app.get("/tours/dates", response_model=List[CalendarEvent])
async def get_tour_dates(category: str = None):
    logger.info(f"Запрос /tours/dates с категорией: {category}")
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
    logger.info("Запрос /tours/categories")
    try:
        categories = get_categories()
        logger.info(f"Получено категорий: {len(categories)}, категории: {categories}")
        return categories
    except Exception as e:
        logger.error(f"Ошибка в /tours/categories: {e}")
        return []
