try:
  import unzip_requirements
except ImportError:
  pass
from pydantic import BaseModel
from typing import List

### Activities
# Transport
class TransportDetails(BaseModel):
    line: str
    stops: str
    time: str
    walk_to_station: str
class RecommendedTransport(BaseModel):
    type: str
    details: TransportDetails
    cost: str
class ConvenienceAnalysis(BaseModel):
    time_saved: str
    cost_vs_benefit: str
    recommendation_score: str
class AlternativeTransport(BaseModel):
    type: str
    details: TransportDetails
    cost: str
    convenience_analysis: ConvenienceAnalysis
class NextTransport(BaseModel):
    recommended: RecommendedTransport
    alternative: AlternativeTransport

# Time Window
class TimeWindow(BaseModel):
    recommended_start: str
    duration_min: int
    crowd_forecast: str

class Activity(BaseModel):
    type: str
    name: str
    description: str = ""
    cost_pp: float = 0.0
    time_window: TimeWindow
    coordinates: dict = {}
    pro_tip: str = ""
    need_booking: bool = False
    next_transport: NextTransport

### Meals
class Meal(BaseModel):
    name: str
    cuisine: str
    cost_pp: float
    time_window: str
    coordinates: dict = {}
    dietary: List[str]
    pro_tip: str

### Days
class Day(BaseModel):
    day_number: int
    theme: str
    activities: List[Activity]
    meals: List[Meal]

### Trip
class EstimatedCost(BaseModel):
    activities: float
    meals: float
    transport: float
class TripSummary(BaseModel):
    total_days: int
    estimated_cost_per_person: EstimatedCost
class Trip(BaseModel):
    trip_summary: TripSummary
    days: List[Day]