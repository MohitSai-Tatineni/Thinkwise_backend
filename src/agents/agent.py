def process_data(data):
    # Example: return the number of rows or records
    if isinstance(data, list):
        return {"record_count": len(data)}
    elif isinstance(data, dict):
        return {"keys": list(data.keys())}
    else:
        return {"message": "Unsupported format"}
