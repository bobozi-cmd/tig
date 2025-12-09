
from pathlib import Path
from typing import Optional


def get_repo_root(path: Path = None) -> Optional[Path]:
    if path is None:
        path = Path.cwd()
    
    while path != path.parent:
        if (path / '.git').exists():
            return path
        path = path.parent
    
    return None
