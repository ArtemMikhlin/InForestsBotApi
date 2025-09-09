from typing import List, Dict, Optional
from pydantic import BaseModel
import os
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic-модели для валидации JSON
class Shift(BaseModel):
    shift: str
    date: str
    price: int
    places: int

class Tour(BaseModel):
    id: str
    category: str
    name: str
    description: str
    dates: List[Shift]
    start_location: str
    contact: str
    photos: List[str]
    videos: List[str]

# Чтение туров из папки tours/
def get_tours() -> List[Dict]:
    tours = []
    tours_dir = "tours"
    if not os.path.exists(tours_dir):
        logger.error(f"Папка {tours_dir} не существует")
        return tours
    
    for filename in os.listdir(tours_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(tours_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    tour = Tour(**data).dict()
                    tours.append(tour)
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {file_path}: {e}")
    return tours

# Получение уникальных категорий
def get_categories() -> List[str]:
    tours = get_tours()
    return list(set(tour["category"] for tour in tours))

# Получение туров по категории
def get_tours_by_category(category: str) -> List[Dict]:
    return [tour for tour in get_tours() if tour["category"] == category]

# Получение дат по туру
def get_dates_by_tour(tour_name: str) -> List[Dict]:
    for tour in get_tours():
        if tour["name"] == tour_name:
            return tour["dates"]
    return []

# Получение тура по имени
def get_tour_by_name(tour_name: str) -> Optional[Dict]:
    for tour in get_tours():
        if tour["name"] == tour_name:
            return tour
    return None

# Получение всех дат с привязкой к турам
def get_all_dates() -> List[Dict]:
    dates = []
    for tour in get_tours():
        for date in tour["dates"]:
            dates.append({
                "tour_name": tour["name"],
                "shift": date["shift"],
                "date": date["date"],
                "price": date["price"],
                "places": date["places"],
                "category": tour["category"]  # Добавляем категорию для фильтрации
            })
    return dates