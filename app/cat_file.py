import argparse
from pathlib import Path
import zlib

from tig.core.repository import get_repo_root


def parse_blob(content: bytes):
    print(content.decode(), end='') # 简化实现，假设文件内容是文本形式


def parse_tree(content: bytes):
    # tree entry format: mode name\0sha1
    i = 0
    while i < len(content):
        space_idx = content.find(b' ', i)
        null_idx = content.find(b'\x00', space_idx)

        mode = content[i:space_idx].decode()
        name = content[space_idx+1:null_idx].decode()
        sha1 = content[null_idx+1:null_idx+21].hex() # 40-bit

        print(f"{mode} {sha1} {name}")
        i = null_idx + 21


def parse_commit(content: bytes):
    print(content.decode(), end='')


def cat_file(repo_path: Path, file_hash: str):
    # 1. 根据sha1找到文件路径
    dot_git_path = repo_path / '.git'
    assert dot_git_path.exists()
    target_path = dot_git_path / 'objects' / file_hash[:2] / file_hash [2:]
    assert target_path.exists(), f"Cannot find object file: {target_path}, may be packed."

    # 2. 读取文件，zlib解压文件内容
    with open(target_path, 'rb') as fp:
        data = zlib.decompress(fp.read())
    
    # 3.1 解析头部信息，确认对象类型
    head = data.split(b'\0')[0].decode()
    content = b'\0'.join(data.split(b'\0')[1:])
    object_type = head.split(' ')[0]
    content_size = int(head.split(' ')[-1])
    
    # 3.2 根据不同对象类型解析文件的内容
    print(f"Type: {object_type}, Size: {content_size}")
    if object_type == 'blob':
        parse_blob(content)
    elif object_type == 'tree':
        parse_tree(content)
    elif object_type == 'commit':
        parse_commit(content)
    else:
        raise ValueError(f"Cannot recognize object type: {object_type}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("object", type=str)
    args = parser.parse_args()

    repo_root = get_repo_root()
    cat_file(repo_root, args.object)
