from dynaconf import Dynaconf
from pathlib import Path

settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=[
        "../settings.toml",
    ],
    root_path=Path(__file__).parent,
    merge_enabled=True,
)
