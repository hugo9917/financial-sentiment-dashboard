import json
import base64
from textblob import TextBlob

def lambda_handler(event, context):
    results = []
    for record in event.get("Records", []):
        # Kinesis data is base64 encoded, decode here
        payload = record["kinesis"]["data"]
        data = json.loads(base64.b64decode(payload).decode("utf-8"))
        if data.get("type") == "news":
            text = data.get("title", "") + " " + (data.get("description", "") or "")
            sentiment = TextBlob(text).sentiment.polarity if text else 0.0
            data["sentiment"] = sentiment
        results.append(data)
    # Aquí podrías guardar en S3, Redshift, etc.
    print("Processed records:", results)
    return {"statusCode": 200, "body": json.dumps("Processed")} 