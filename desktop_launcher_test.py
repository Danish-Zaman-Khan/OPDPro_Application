import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from local_data import create_backup, restore_backup


class LocalDataBackupTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.database = self.root / "clinic.sqlite3"
        self.media = self.root / "media"
        self.media.mkdir()
        self._create_database(self.database, "before")
        (self.media / "reports").mkdir()
        (self.media / "reports" / "result.txt").write_text("original report", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def _create_database(path, clinic_name):
        with sqlite3.connect(path) as database:
            database.execute("CREATE TABLE django_migrations (id INTEGER)")
            database.execute("CREATE TABLE usermanagement_customuser (id INTEGER)")
            database.execute("CREATE TABLE clinic (name TEXT)")
            database.execute("INSERT INTO clinic VALUES (?)", [clinic_name])

    def test_backup_restores_database_and_uploaded_files(self):
        backup = self.root / "backup.zip"
        create_backup(self.database, self.media, backup)

        with sqlite3.connect(self.database) as database:
            database.execute("UPDATE clinic SET name = 'after'")
        (self.media / "reports" / "result.txt").write_text("changed report", encoding="utf-8")

        restore_backup(backup, self.database, self.media)

        with sqlite3.connect(self.database) as database:
            clinic_name = database.execute("SELECT name FROM clinic").fetchone()[0]
        self.assertEqual(clinic_name, "before")
        self.assertEqual(
            (self.media / "reports" / "result.txt").read_text(encoding="utf-8"),
            "original report",
        )

    def test_restore_rejects_unsafe_paths_without_changing_live_data(self):
        backup = self.root / "unsafe.zip"
        with zipfile.ZipFile(backup, "w") as archive:
            archive.writestr("db.sqlite3", b"not a database")
            archive.writestr("media/../../outside.txt", "unsafe")

        with self.assertRaises(ValueError):
            restore_backup(backup, self.database, self.media)

        with sqlite3.connect(self.database) as database:
            clinic_name = database.execute("SELECT name FROM clinic").fetchone()[0]
        self.assertEqual(clinic_name, "before")
        self.assertFalse((self.root / "outside.txt").exists())


if __name__ == "__main__":
    unittest.main()
