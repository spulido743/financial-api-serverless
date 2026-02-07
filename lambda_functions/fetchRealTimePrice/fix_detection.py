import sys
sys.path.insert(0, '.')
from lambda_function import lambda_handler

# Test con evento vacío
event_vacio = {}
result = lambda_handler(event_vacio, None)
print("Evento vacío:", result['statusCode'])

# Test con pathParameters vacío
event_path_vacio = {"pathParameters": {}}
result = lambda_handler(event_path_vacio, None)
print("PathParameters vacío:", result['statusCode'])

# Test EventBridge real
event_eventbridge = {"source": "aws.events", "detail-type": "Scheduled Event"}
result = lambda_handler(event_eventbridge, None)
print("EventBridge:", result['statusCode'])
