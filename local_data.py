import os
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path, PurePosixPath


def create_backup(database_path, media_root, destination):
    database_path = Path(database_path)
    media_root = Path(media_root)
    destination = Path(destination)
    if not database_path.is_file():
        raise FileNotFoundError(f"Clinic database was not found: {database_path}")
    if destination.resolve() == database_path.resolve():
        raise ValueError("Choose a backup file location separate from the clinic database.")
    if destination.resolve().is_relative_to(media_root.resolve()):
        raise ValueError("Choose a backup location outside the uploaded reports folder.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opdpro-backup-", dir=destination.parent) as temp_dir:
        snapshot = Path(temp_dir) / "db.sqlite3"
        with closing(sqlite3.connect(database_path)) as source, closing(sqlite3.connect(snapshot)) as target:
            source.backup(target)

        archive_path = Path(temp_dir) / "backup.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(snapshot, "db.sqlite3")
            if media_root.is_dir():
                for root, directories, filenames in os.walk(media_root, followlinks=False):
                    directories[:] = sorted(
                        name for name in directories
                        if not (Path(root) / name).is_symlink()
                    )
                    for filename in sorted(filenames):
                        file_path = Path(root) / filename
                        if file_path.is_symlink():
                            raise ValueError(f"Cannot back up a symbolic link: {file_path}")
                        archive_name = PurePosixPath("media", *file_path.relative_to(media_root).parts)
                        archive.write(file_path, archive_name.as_posix())
        os.replace(archive_path, destination)
    return destination


def _validate_database(database_path):
    with closing(sqlite3.connect(database_path)) as database:
        result = database.execute("PRAGMA integrity_check").fetchone()
        tables = {
            row[0]
            for row in database.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    if result is None or result[0] != "ok":
        raise ValueError("The backup database failed SQLite's integrity check.")
    if "django_migrations" not in tables or "usermanagement_customuser" not in tables:
        raise ValueError("The selected file is not a valid OPDPro database backup.")


def restore_backup(archive_path, database_path, media_root):
    archive_path = Path(archive_path)
    database_path = Path(database_path)
    media_root = Path(media_root)
    if not archive_path.is_file():
        raise FileNotFoundError(f"Backup file was not found: {archive_path}")
    if archive_path.resolve().is_relative_to(media_root.resolve()):
        raise ValueError("Move the selected backup outside the uploaded reports folder before restoring it.")
    if not database_path.parent.is_dir() or not media_root.parent.is_dir():
        raise FileNotFoundError("The OPDPro data folders are not available.")

    with (
        tempfile.TemporaryDirectory(prefix="opdpro-restore-db-", dir=database_path.parent) as db_temp,
        tempfile.TemporaryDirectory(prefix="opdpro-restore-media-", dir=media_root.parent) as media_temp,
    ):
        extracted_database = Path(db_temp) / "db.sqlite3"
        extracted_media = Path(db_temp) / "media"
        extracted_media.mkdir()
        found_database = False

        with zipfile.ZipFile(archive_path, "r") as archive:
            for entry in archive.infolist():
                name = entry.filename
                member_path = PurePosixPath(name)
                if (
                    not name
                    or member_path.is_absolute()
                    or "\\" in name
                    or ":" in name
                    or ".." in member_path.parts
                    or stat.S_ISLNK(entry.external_attr >> 16)
                ):
                    raise ValueError("The backup contains an unsafe file path.")

                if name == "db.sqlite3":
                    if found_database or entry.is_dir():
                        raise ValueError("The backup has an invalid database entry.")
                    target_path = extracted_database
                    found_database = True
                elif member_path.parts and member_path.parts[0] == "media":
                    target_path = extracted_media.joinpath(*member_path.parts[1:])
                    if entry.is_dir():
                        target_path.mkdir(parents=True, exist_ok=True)
                        continue
                else:
                    raise ValueError("The selected file is not an OPDPro backup.")

                target_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, target_path.open("wb") as target:
                    shutil.copyfileobj(source, target)

        if not found_database:
            raise ValueError("The backup does not contain a clinic database.")
        _validate_database(extracted_database)

        staged_media = Path(media_temp) / "restored-media"
        shutil.copytree(extracted_media, staged_media)
        previous_database = Path(db_temp) / "previous.sqlite3"
        previous_media = Path(media_temp) / "previous-media"
        moved_database = False
        moved_media = False
        installed_database = False
        installed_media = False

        try:
            if database_path.exists():
                os.replace(database_path, previous_database)
                moved_database = True
            if media_root.exists():
                os.replace(media_root, previous_media)
                moved_media = True
            os.replace(extracted_database, database_path)
            installed_database = True
            os.replace(staged_media, media_root)
            installed_media = True
        except Exception:
            if installed_media and media_root.exists():
                shutil.rmtree(media_root)
            if installed_database and database_path.exists():
                database_path.unlink()
            if moved_database:
                os.replace(previous_database, database_path)
            if moved_media:
                os.replace(previous_media, media_root)
            raise

    return database_path
