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
# # conn.execute(
#     "INSERT INTO reading_progress (id,pdf_path,last_page,audio_path,last_time) \
#       VALUES (1, 'Paul', 32, 'California', 20000.00 )"
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

# conn.execute(
#     "INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (2, 'Allen', 25, 'Texas', 15000.00 )"
# )

# conn.execute(
#     "INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )"
# )

# conn.execute(
#     "INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#       VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )"
# )

conn.commit()
print("Records created successfully")
conn.close()
