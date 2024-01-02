from django.shortcuts import render
import boto3

import datetime
from datetime import datetime


def refresh_dynamodb_client():
    return boto3.client("dynamodb", region_name="us-east-1")


dynamodb_client = refresh_dynamodb_client()


def result(request):
    # DynamoDB setup
    table_name = "newtest"
    # dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")
    # dynamodb_client = refresh_dynamodb_client()

    try:
        # Scan operation to get most recent data
        response = dynamodb_client.scan(
            TableName=table_name,
            Limit=1,  # Limit the result to 1 item
            ScanFilter={
                "datetime": {
                    "AttributeValueList": [{"S": "2023-01-01T00:00:00"}],
                    "ComparisonOperator": "GT",
                }
            },
            # ScanIndexForward=False,
        )

        # Check if there are items returned
        if "Items" in response:
            most_recent_item = response["Items"][0]
            item_date = most_recent_item["datetime"]["S"]
            date_strptime = datetime.strptime(item_date, "%Y-%m-%dT%H:%M:%S.%f")
            temperature = most_recent_item["temperature"]["N"]
            humidity = most_recent_item["humidity"]["N"]
            iaq = most_recent_item["iaq"]["N"]
        else:
            most_recent_item = None  # No items found
    except Exception as e:
        print(f"Error: {e}")
        most_recent_item = None  # Handle errors gracefully

    temp_reading = int(temperature)
    temp_response = None
    if temp_reading < 14:
        temp_interpretation = "Low / Poor IAQ"
        temp_badge = "warning"
        temp_response = "Adjust HVAC Heating"
    elif temp_reading >= 15 or temp_reading <= 25:
        temp_interpretation = "OK"
        temp_badge = "success"
    elif temp_reading >= 26 or temp_reading <= 100:
        temp_interpretation = "High / V-Poor IAQ"
        temp_badge = "danger"
        temp_response = "Adjust HVAC Heating"
    else:
        temp_interpretation = None

    humidity_reading = int(humidity)
    humidity_response = None
    if humidity_reading < 29:
        humidity_interpretation = "Low / Poor IAQ"
        humidity_badge = "warning"
        humidity_response = "Adjust HVAC Ventilation"
    elif humidity_reading >= 30 or humidity_reading <= 59:
        humidity_interpretation = "OK"
        humidity_badge = "success"
    elif humidity_reading >= 60 or humidity_reading <= 100:
        humidity_interpretation = "High / V-Poor IAQ"
        humidity_badge = "danger"
        humidity_response = "Adjust HVAC Ventilation"
    else:
        humidity_interpretation = None

    iaq_reading = int(iaq)
    iaq_response = None
    if iaq_reading >= 51 or iaq_reading <= 74:
        iaq_interpretation = "Low / Poor IAQ"
        iaq_badge = "danger"
        iaq_response = "Activate HVAC AQC"
    elif iaq_reading >= 0 or iaq_reading <= 50:
        iaq_interpretation = "OK"
        iaq_badge = "success"
    elif iaq_reading >= 75 or iaq_reading <= 100:
        iaq_interpretation = "High / V-Poor IAQ"
        iaq_badge = "danger"
        iaq_response = "Activate HVAC AQC"
    else:
        iaq_interpretation = None

    context = {
        "most_recent_item": most_recent_item,
        "date_strptime": date_strptime,
        "temperature": temperature,
        "temp_interpretation": temp_interpretation,
        "temp_badge": temp_badge,
        "temp_response": temp_response,
        "humidity": humidity,
        "humidity_interpretation": humidity_interpretation,
        "humidity_badge": humidity_badge,
        "humidity_response": humidity_response,
        "iaq": iaq,
        "iaq_interpretation": iaq_interpretation,
        "iaq_badge": iaq_badge,
        "iaq_response": iaq_response,
    }
    return render(request, "index.html", context)


def historical_readings(request):
    # DynamoDB setup
    table_name = "newtest"
    dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")

    try:
        # Scan operation to get historical readings
        response = dynamodb_client.scan(
            TableName=table_name,
            Limit=30,  # Limit the result to the most recent 30 items
            ScanFilter={
                "datetime": {
                    "AttributeValueList": [{"S": "2023-01-01T00:00:00"}],
                    "ComparisonOperator": "GT",
                }
            },
        )

        # Check if there are items returned
        if "Items" in response:
            historical_readings = response["Items"]
        else:
            historical_readings = []  # No items found
    except Exception as e:
        print(f"Error: {e}")
        historical_readings = []  # Handle errors gracefully

    # Pass data to template
    context = {"historical_readings": historical_readings}
    return render(request, "historical_readings.html", context)
