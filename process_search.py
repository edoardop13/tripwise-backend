import instructor
import json
import boto3
import google.generativeai as genai
from shared.utils import Trip

sqs = boto3.client("sqs", region_name="eu-central-1")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("TripwiseResults")
try:
    response = sqs.get_queue_url(QueueName="TripwiseQueue")
    QUEUE_URL = response["QueueUrl"]
except sqs.exceptions.QueueDoesNotExist:
    print("Errore: La coda TripwiseQueue non esiste")
    QUEUE_URL = None

genai.configure(api_key= "AIzaSyD3x1WpBzgZMxbtPzLypVzyz04tBF5UVDs")  #os.environ["API_KEY"]) # right way to get the API key

def handler(event, context):
    for record in event["Records"]:
        message = json.loads(record["body"])
        request_id = message["request_id"]
        city = message["city"]
        days = message["days"]
        month = message["month"]
        number_of_people = message["number_of_people"]
        withKids = message["withKids"]

        prompt = f"""
            Create a comprehensive {days}-day itinerary for exploring {city} for {number_of_people} people in the month of {month}. 
            Each day should include a rich selection of activities, meals, and considerations to make the experience memorable and practical. 
            Ensure the itinerary balances iconic landmarks, cultural experiences, and hidden gems, with plenty of activities for each day.
            Focus on minimizing travel time within a single day by grouping attractions that are near each other in the same or adjacent neighborhoods. 
            If a key landmark is in a distant area, dedicate a separate day to exploring that region so that travelers don’t bounce across the city multiple times on the same day.
            {"This trip is for a family with children, so please include family-friendly activities and meals." if withKids else "This trip is for people without children."}
            Ensure each day includes a mix of experiences, such as: Historical landmarks, Art and culture, Nature and parks, Shopping and local life.
            Requirements:
            Activity Requirements:
            1. Time Management:
            - Time windows with queue buffer: "recommended_start" + "duration_min";
            - Include typical crowd levels (Low/Med/High) for each attraction;
            - Each activity and meal must be scheduled sequentially to prevent time conflicts;
            - Consider the duration of each activity, meal, and transport time before scheduling the next event;
            - If an activity is too long, ensure a meal break is inserted before or after based on logical meal times.
            3. Meals:
            - Include one lunch and one dinner location per day;
            - Specify the time spent at each meal;
            - Provide the average cost of meals in euros (for one person) for budgeting;
            - Choose restaurants or cafes with a distance < 18-20min of walking time from the activities planned for that part of the day to minimize travel time.
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
            - Opening hours/crowd patterns;
            - Public transport frequency;
            - Announced transport strikes.
            2. Always walk if:
            - Use A* star routing algorithm for activity sequence;
            - Distance < 18-20min walking time;
            - No dangerous intersections;
            - Path has high walkability score (>4/5);
            - Route passes through interesting landmarks.
            3. Consider public transport if:
            - Distance > 25m walking time;
            - Requires crossing dangerous intersections;
            - Extreme weather conditions expected.
            Enhanced Requirements:
            - Calculate cumulative daily walking distance;
            - Show transport cost savings comparison;
            - Add "scenic walk" alternatives for pretty routes;
            - Include flexibility in the itinerary so users can skip activities if needed;
            - Suggest the best times to visit certain attractions to avoid crowds or take advantage of special events.

            IMPORTANT:
            1. Only use the following JSON structure. No extra fields allowed.
            2. Any field that cannot be determined should be omitted (not null).
            3. All string fields must be valid, non-empty strings. No 'None' or 'null'.
            4. The day should be fully covered from morning (starting around 8:00–9:00) to evening (finishing around 19:00–20:00);
            5. Provide at least 6 total activities per day (including morning, afternoon, and late-afternoon segments).

            Return valid JSON only, matching this structure strictly:
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
                                            "line": "",
                                            "stops": "",
                                            "time": "6min"
                                        }},
                                        "cost": "€0"
                                    }},
                                    "alternative": {{
                                        "type": "metro",
                                        "details": {{
                                            "line": "M1",
                                            "stops": "2 stations",
                                            "time": "6min"
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
                        ],
                        "meals": [
                            {{
                                "type": "meal",
                                "name": "Luini Panzerotti",
                                "cuisine": "Fried dough pockets with various fillings",
                                "cost_€pp": 5.00,
                                "time_window": "time_window": {{
                                    "recommended_start": "12:30",
                                    "duration_min": 60,
                                    "crowd_forecast": "High"
                                }},
                                "address": "Via Santa Radegonda, 16, 20121 Milano MI",
                                "dietary": [ "Vegetarian options" ],
                                "pro_tip": "Order a mix of sweet and savory panzerotti",
                            }}
                        ]
                    }}
                ]
            }}
        """
        
        try:
            client = instructor.from_gemini(
                client=genai.GenerativeModel(
                    model_name="models/gemini-1.5-flash",
                ),
                mode=instructor.Mode.GEMINI_JSON,
            )

            response = client.messages.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_model=Trip,
            )

            result = response.json()
            print(f"Result for request {request_id}: {result}")
            table.put_item(Item={"request_id": request_id, "result": json.dumps(result)})

            # Rimuove il messaggio dalla coda dopo aver elaborato
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=record["receiptHandle"])

        except Exception as e:
            print(f"Error processing request {request_id}: {e}")