from datetime import datetime, date, time
import json

# this is needed to serialize the data from the database
# alchemy has its own structure and if we just put the object into JSON it will not work


def to_dict(instance):
    if instance is None:
        return None
    result = {}
    for column in instance.__table__.columns:
        value = getattr(instance, column.name)
        if isinstance(value, (datetime, date, time)):
            value = value.isoformat()
        elif isinstance(value, dict):
            # Ensure nested dictionaries are serialized properly
            value = json.dumps(value)
        result[column.name] = value
    return result
