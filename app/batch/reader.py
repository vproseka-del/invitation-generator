import openpyxl


def read_xlsx(file_stream, field_map, optional_field_map=None):
    optional_field_map = optional_field_map or {}

    workbook = openpyxl.load_workbook(file_stream, read_only=True, data_only=True)
    worksheet = workbook.active

    rows = worksheet.iter_rows(values_only=True)
    try:
        header_row = next(rows)
    except StopIteration:
        workbook.close()
        return list(field_map.keys()), []

    known_headers = set(field_map) | set(optional_field_map)
    header_index = {}
    for index, cell in enumerate(header_row):
        if cell is None:
            continue
        header = str(cell).strip()
        if header in known_headers and header not in header_index:
            header_index[header] = index

    missing = [header for header in field_map if header not in header_index]
    if missing:
        workbook.close()
        return missing, []

    records = []
    for row_number, values in enumerate(rows, start=2):
        if all(value is None or str(value).strip() == "" for value in values):
            continue

        data = {}
        missing_cells = []
        for header, key in field_map.items():
            index = header_index[header]
            value = values[index] if index < len(values) else None
            value = "" if value is None else str(value).strip()
            data[key] = value
            if not value:
                missing_cells.append(header)

        for header, key in optional_field_map.items():
            index = header_index.get(header)
            value = values[index] if index is not None and index < len(values) else None
            data[key] = "" if value is None else str(value).strip()

        records.append({"row": row_number, "data": data, "missing": missing_cells})

    workbook.close()
    return [], records
