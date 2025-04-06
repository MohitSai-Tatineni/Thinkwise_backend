from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Literal
import pandas as pd
import json
from src.database import db
from src.agents.agent import process_data

app = FastAPI()

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    file_type: Literal["csv", "json"] = "csv"
):
    try:
        content = await file.read()
        
        if file_type == "csv":
            df = pd.read_csv(pd.io.common.BytesIO(content))
            data = df.to_dict(orient="records")
        elif file_type == "json":
            data = json.loads(content.decode("utf-8"))

        result = process_data(data)  
        
        insert_result = await db["results"].insert_one({"input": data, "output": result})

        return {
            "message": "File processed and stored",
            "id": str(insert_result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
