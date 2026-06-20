from pydantic import BaseModel, Field
class DayPlan(BaseModel): day: int; activities: list[str]
class TravelItinerary(BaseModel):
    city: str
    travelers: int = Field(ge=1)
    days: list[DayPlan]
    estimated_budget_inr: int = Field(ge=0)
    umbrella_advice: str
    caveats: list[str] = Field(default_factory=list)
