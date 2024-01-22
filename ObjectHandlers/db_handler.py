import sqlite3
from collections import namedtuple

ReadingDataRow = namedtuple(
    "ReadingDataRow",
    ["bookmark", "pdf_path", "last_page_index", "audio_path", "last_time"],
)


class DBHandler:
    def __init__(self) -> None:
        self.db = sqlite3.connect("reading_data.db")
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()

    def create_data(self, data: ReadingDataRow):
        self.cursor.execute(
            f"INSERT INTO reading_progress (bookmark, pdf_path,last_page_index,audio_path,last_time) \
            VALUES (?,?,?,?,?);",
            data,
        )
        self.db.commit()

    def read_data(self, data: ReadingDataRow):
        filter_conditions = {
            key: value for key, value in data._asdict().items() if value is not None
        }
        query = "SELECT * FROM reading_progress WHERE "
        conditions = []
        values = []
        for key, value in filter_conditions.items():
            conditions.append(f"{key} = ?")
            values.append(value)
        query += " AND ".join(conditions)
        # # print(f"\n\n{query}\n{values}\n\n")
        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def update_data(self, data: ReadingDataRow):
        self.cursor.execute(
            "UPDATE reading_progress SET bookmark = ?, last_page_index = ?, last_time=? WHERE audio_path = ? AND pdf_path = ?",
            (
                data.bookmark,
                data.last_page_index,
                data.last_time,
                data.audio_path,
                data.pdf_path,
            ),
        )
        self.db.commit()

    def delete_data(self, data: ReadingDataRow):
        filter_conditions = {
            key: value for key, value in data._asdict().items() if value is not None
        }

        query = "DELETE FROM reading_progress WHERE "
        conditions = []
        values = []
        for key, value in filter_conditions.items():
            conditions.append(f"{key} = ?")
            values.append(value)
        query += " AND ".join(conditions)

        self.cursor.execute(query, values)
        self.db.commit()

    def filter_condition(
        self,
        bookmark=None,
        pdf_path=None,
        last_page_index=None,
        audio_path=None,
        last_time=None,
    ) -> ReadingDataRow:
        return ReadingDataRow(
            bookmark, pdf_path, last_page_index, audio_path, last_time
        )
