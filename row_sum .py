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
        first_col = df.columns[0]

        # Find row by first column value
        target_row = df[df[first_col].astype(str) == row_name]
        if target_row.empty:
            raise HTTPException(status_code=404, detail="Row not found")

        # Sum all numeric columns excluding the first column (row label)
        row_values = target_row.iloc[0, 1:]
        numeric_values = [float(x) for x in row_values if pd.notnull(x) and isinstance(x, (int, float))]

        return {
            "table_name": table_name,
            "row_name": row_name,
            "sum": sum(numeric_values)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
