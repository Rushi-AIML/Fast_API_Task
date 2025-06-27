from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded files
uploaded_files = {}

@app.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        excel_data = pd.ExcelFile(io.BytesIO(contents))
        
        file_id = str(len(uploaded_files) + 1)
        uploaded_files[file_id] = {
            "file_name": file.filename,
            "sheets": {},
            "sheet_names": excel_data.sheet_names
        }
        
        for sheet_name in excel_data.sheet_names:
            df = pd.read_excel(excel_data, sheet_name=sheet_name)
            uploaded_files[file_id]["sheets"][sheet_name] = {
                "data": df.where(pd.notnull(df), None).to_dict(orient="list"),
                "preview": df.head(10).where(pd.notnull(df), None).values.tolist()
            }
        
        return {
            "message": "File uploaded successfully",
            "file_id": file_id,
            "tables": excel_data.sheet_names
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_table_details")
async def get_table_details(table_name: str, file_id: str = None):
    try:
        if not uploaded_files:
            raise HTTPException(status_code=404, detail="No files uploaded")
        
        if not file_id:
            file_id = str(len(uploaded_files))
        
        file_data = uploaded_files.get(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        sheet_data = file_data["sheets"].get(table_name)
        if not sheet_data:
            raise HTTPException(status_code=404, detail="Sheet not found")
        
        df = pd.DataFrame.from_dict(sheet_data["data"])
        row_names = [str(i) for i in df.index]
        
        return {
            "preview": sheet_data["preview"],
            "row_names": row_names
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/row_sum")
async def calculate_row_sum(table_name: str, row_name: str, file_id: str = None):
    try:
        if not uploaded_files:
            raise HTTPException(status_code=404, detail="No files uploaded")
        
        if not file_id:
            file_id = str(len(uploaded_files))
        
        file_data = uploaded_files.get(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")
        
        sheet_data = file_data["sheets"].get(table_name)
        if not sheet_data:
            raise HTTPException(status_code=404, detail="Sheet not found")
        
        df = pd.DataFrame.from_dict(sheet_data["data"])
        
        try:
            row_index = int(row_name)
        except ValueError:
            row_index = row_name
        
        if row_index not in df.index:
            raise HTTPException(status_code=404, detail="Row not found")
        
        row_values = df.loc[row_index].values
        numeric_values = [float(x) for x in row_values if isinstance(x, (int, float)) and pd.notnull(x)]
        
        if not numeric_values:
            raise HTTPException(status_code=400, detail="No numeric values in row")
        
        return {
            "row_name": str(row_index),
            "values": numeric_values,
            "sum": sum(numeric_values)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")