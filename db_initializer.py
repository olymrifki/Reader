import sqlite3

conn = sqlite3.connect("reading_data.db")
print("Opened database successfully")

# conn.execute(
#     """CREATE TABLE reading_progress
#          (id INTEGER PRIMARY KEY AUTOINCREMENT,
#          bookmark       TEXT   NOT NULL,
#          pdf_path       TEXT    NOT NULL,
#          last_page_index      INTEGER,
#          audio_path       TEXT     NOT NULL,
#          last_time       TEXT);"""
# )


conn.execute(
    "INSERT INTO reading_progress (bookmark, pdf_path, last_page_index, audio_path, last_time) \
    VALUES (?,?,?,?, ?);",
    (
        "dwadwa",
        "asda",
        123,
        "2dasdwa",
        "dawidai d",
    ),
)


conn.commit()
print("Records created successfully")
conn.close()
