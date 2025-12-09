from pathlib import Path

from tig.core.repository import get_repo_root


def collect_refs_info(dir: Path) -> list:
    if not dir.exists():
        return []
    
    refs = []
    for file in dir.glob('*'):
        if file.is_file():
            with open(file, 'r') as fp:
                data = fp.read().strip()
            refs.append((data, file))
    return refs


def show_ref(repo_path: Path):
    dot_git_path = repo_path / '.git'
    assert dot_git_path.exists()
    refs_dir = dot_git_path / 'refs'

    # 收集ref信息
    refs = []
    refs.extend(collect_refs_info(refs_dir / 'heads'))
    refs.extend(collect_refs_info(refs_dir / 'tags'))

    for sub_dir in (refs_dir / 'remotes').glob('*'):
        if sub_dir.is_dir():
            refs.extend(collect_refs_info(sub_dir))

    # 构建ref表，解决 'ref: xxx' 的情况
    ref_table: dict[str, str] = {} # rel_path_str, hash
    to_parse_ref: dict[str, str] = {} # ref: xxx, hash -> rel_path_str
    for item in refs:
        sha1: str = item[0]
        fpath: Path = item[1]
        if sha1.startswith('ref: '):
            to_parse_ref[sha1.removeprefix('ref: ')] = str(fpath.absolute().relative_to(dot_git_path))
        else:
            ref_table[str(fpath.absolute().relative_to(dot_git_path))] = sha1
    
    for sha1, rel_path_str in to_parse_ref.items():
        if sha1 in ref_table:
            ref_table[rel_path_str] = ref_table[sha1]
        else:
            ref_table[rel_path_str] = sha1

    for rel_path_str, sha1 in sorted(ref_table.items(), key=lambda x: x[0]):
        print(f"{sha1:40} {rel_path_str}")


def main():
    repo_root = get_repo_root()
    show_ref(repo_root)
