from datetime import datetime
from pathlib import Path


# -----------------------------
# ファイルバックアップ
# -----------------------------
def backup_file(path: Path) -> Path | None:
    """
    指定ファイルが存在する場合、日付付きでバックアップを作成する。
    戻り値: バックアップファイルの Path（存在しない場合は None）
    """
    if not path.exists():
        return None

    backup_name = f"{path.stem}_{datetime.now():%Y%m%d}{path.suffix}"
    backup_path = path.parent / backup_name

    path.rename(backup_path)
    return backup_path
