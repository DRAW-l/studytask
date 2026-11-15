import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """默认配置；测试可通过 create_app({...}) 覆盖。"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "studytask-local-dev-key")
    DATABASE = os.environ.get("STUDYTASK_DATABASE", str(BASE_DIR / "instance" / "studytask.db"))
    DEBUG = False
