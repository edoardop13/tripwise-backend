try:
  import unzip_requirements
except ImportError:
  pass
import instructor
import json
import google.generativeai as genai
from shared.utils import Trip

genai.configure(api_key= "AIzaSyD3x1WpBzgZMxbtPzLypVzyz04tBF5UVDs")  #os.environ["API_KEY"]) # right way to get the API key

def search(event, context):

    query_params = event.get('queryStringParameters', {})
    city = query_params.get('city')
    month = query_params.get('month')
    days = query_params.get('days')
    number_of_people = query_params.get('people', 1)
    withKids = query_params.get('withKids', False)

    missing_params = []
    if not city:
        missing_params.append("city")
    if not days:
        missing_params.append("days")
    if not month:
        missing_params.append("month")

    if missing_params:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Missing required parameter(s)",
                "missing_params": missing_params
            })
        }

    prompt = f"""
    Create a comprehensive {days}-day itinerary for exploring {city} for {number_of_people} people in the month of {month}. 
    Each day should include a rich selection of activities, meals, and considerations to make the experience memorable and practical. 
    Ensure the itinerary balances iconic landmarks, cultural experiences, and hidden gems, with plenty of activities for each day.
    {"This trip is for a family with children, so please include family-friendly activities and meals." if withKids else "This trip is for people without children."}
    Ensure each day includes a mix of experiences, such as: Historical landmarks, Art and culture, Nature and parks, Shopping and local life.
    Requirements:
    Activity Requirements:
    1. Time Management:
    - Time windows with queue buffer: "recommended_start" + "duration_min";
    - Include typical crowd levels (Low/Med/High) for each attraction;
    - Incorporate small breaks between activities to account for relaxation or unexpected delays.
    3. Meals:
    - Include one lunch and one dinner location per day;
    - Specify the time spent at each meal;
    - Provide the average cost of meals in euros (for one person) for budgeting;
    - Choose restaurants or cafes near the activities planned for that part of the day to minimize travel time.
    4. Cost Tracking:
    - Activity cost (entry fees);
    - Meal cost (per person);
    - Transport savings comparison.
    5. Local Intelligence:
    - Provide a short description of each activity to give users an idea of what to expect;
    - Pro tips for avoiding crowds/best experience;
    - Booking requirements.

    Transport Rules:
    1. Sync time windows with:
    - Opening hours/crowd patterns
    - Public transport frequency
    - Natural transitions (e.g., museum → lunch → park)
    - Announced transport strikes
    2. Always walk if:
    - Use A* star routing algorithm for activity sequence
    - Distance < 18-20min walking time
    - No dangerous intersections
    - Path has high walkability score (>4/5)
    - Route passes through interesting landmarks
    3. Consider public transport if:
    - Distance > 25m walking time
    - Requires crossing dangerous intersections
    - Extreme weather conditions expected
    Enhanced Requirements:
    - Calculate cumulative daily walking distance;
    - Show transport cost savings comparison;
    - Add "scenic walk" alternatives for pretty routes;
    - Include flexibility in the itinerary so users can skip activities if needed;
    - Suggest the best times to visit certain attractions to avoid crowds or take advantage of special events.

    The response should be structured as JSON to ensure clarity and compatibility. Use the following output schema:
    {{
    "trip_summary": {{
        "total_days": {days},
        "estimated_cost_per_person": {{
        "activities": "€X",
        "meals": "€Y",
        "transport": "€Z"
        }}
    }},
    "days": [
        {{
        "day_number": 1,
        "theme": "Historic Center & Modern Art",
        "activities": [
            {{
            "type": "landmark",
            "name": "Duomo Cathedral",
            "description": "Gothic masterpiece with rooftop terraces",
            "cost_€pp": 15.80,
            "time_window": {{
                "recommended_start": "09:00",
                "duration_min": 120,
                "crowd_forecast": "High"
            }},
            "coordinates": {{ "lat": 45.4642, "lng": 9.1900 }},
            "pro_tip": "Enter from north side for shorter queues",
            "need_booking": true,
            "next_transport": {{
                "recommended": {{
                "type": "walk",
                "details": {{
                    "distance": "750m",
                    "time": "9min",
                    "route": "Via Dante → Via Orefici",
                }},
                "cost": "€0"
                }},
                "alternative": {{
                "type": "metro",
                "details": {{
                    "line": "M1",
                    "stops": "2 stations",
                    "time": "6min",
                    "walk_to_station": "3min"
                }},
                "cost": "€2.10",
                "convenience_analysis": {{
                    "time_saved": "0min (including station access)",
                    "cost_vs_benefit": "Not recommended - same effective time",
                    "recommendation_score": "2/10"
                }}
                }}
            }}
            }},
            {{
            "type": "meal",
            "name": "Luini Panzerotti",
            "cuisine": "Fried dough pockets with various fillings",
            "cost_€pp": 5.00,
            "time_window": "12:30-13:30",
            "coordinates": {{ "lat": 45.4637, "lng": 9.1874 }},
            "dietary": [ "Vegetarian options" ],
            "pro_tip": "Order a mix of sweet and savory panzerotti",
            }}
        ],
        }},
        ]
    }}
    """
    #- Provide tips for optimizing the experience, such as purchasing skip-the-line tickets or using public transport passes.

    client = instructor.from_gemini(
        client=genai.GenerativeModel(
            model_name="models/gemini-1.5-flash",
        ),
        mode=instructor.Mode.GEMINI_JSON,
    )

    resp = client.messages.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_model=Trip,
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": resp.json()
    }