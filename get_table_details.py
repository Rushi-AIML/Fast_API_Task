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
        first_col_name = df.columns[0]
        row_names = df[first_col_name].dropna().astype(str).tolist()

        return {
            "table_name": table_name,
            "row_names": row_names
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
