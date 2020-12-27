import json

def open_query_plan_cache_file():
    with open('/tmp/mmo_temp_query.txt', 'r') as f:
        try:
            data = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            data = {}
    return data

def write_query_plan_file(data):
    with open('/tmp/mmo_temp_query.txt', 'w') as f:
        try:
            json.dump(data, f)
        except Exception as excep:
            raise excep