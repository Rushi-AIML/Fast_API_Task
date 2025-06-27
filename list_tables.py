@app.get("/list_tables")
async def list_tables(file_id: str = None):
    try:
        if not uploaded_files:
            raise HTTPException(status_code=404, detail="No files uploaded")

        if not file_id:
            file_id = str(len(uploaded_files))

        file_data = uploaded_files.get(file_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found")

        return {"tables": file_data["sheet_names"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
