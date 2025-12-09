import hashlib
from pathlib import Path
import struct
from typing import List
from dataclasses import dataclass

from tig.core.repository import get_repo_root


@dataclass
class IndexEntry:
    # stat_data
    ## srtuct cache_time
    ### sd_ctime
    ctime_sec: int
    ctime_nano: int
    ### sd_mtime
    mtime_sec: int
    mtime_nano: int
    
    dev: int
    ino: int
    uid: int
    gid: int
    size: int

    ce_mode: int
    ce_flags: int

    sha1: bytes
    path: str

    def __post_init__(self):
        CE_STAGEMASK = 0x3000
        CE_STAGESHIFT = 12
        self.stage = ((CE_STAGEMASK & self.ce_flags) >> CE_STAGESHIFT) # ce_stage macro in read-cache-ll.h

    def __repr__(self) -> str:
        mode_str = oct(self.ce_mode)[2:].zfill(6)
        sha1_str = self.sha1.hex()
        return f"{mode_str} {sha1_str} {self.stage:<7d} {self.path}"


class GitIndex:
    CACHE_SIGNATURE = b'\x44\x49\x52\x43' # 'DIRC'

    def __init__(self, index_file: Path):
        self.index_file = index_file
        self.entries: List[IndexEntry] = []

    def parse(self):
        with open(self.index_file, 'rb') as fp:
            data = fp.read()

        # 1. 解析Header
        pos = 0
        signature = data[pos:pos+4]
        pos += 4
        assert signature == self.CACHE_SIGNATURE
        version = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        print(f"Version: {version}")
        n_entries = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4
        print(f"Total entries: {n_entries}")

        # 2. 解析Index Entries信息 (create_from_disk in read-cache.c)
        for _ in range(n_entries):
            # 60 Bytes 的元数据
            entry_fmt = '>IIIIIIIIII20s'
            entry_size = struct.calcsize(entry_fmt)
            info = struct.unpack(entry_fmt, data[pos:pos+entry_size])
            ctime_sec, ctime_nano, mtime_sec, mtime_nano, dev, ino, mode, uid, gid, size, sha1 = info
            pos += entry_size

            # 解析 2 Bytes on-disk flags
            flags = struct.unpack('>H', data[pos:pos+2])[0]
            pos += 2

            # 读取路径名 (以null字节结尾)
            path_end = pos
            while path_end < len(data) and data[path_end] != 0:
                path_end += 1
            
            path_bytes = data[pos:path_end]
            path = path_bytes.decode(errors='replace')
            pos = path_end + 1
            # 对齐到 8 Bytes
            entry_len_without_padding = 62 + len(path_bytes) + 1
            padding = (8 - (entry_len_without_padding % 8)) % 8
            if padding:
                pos += padding
            
            entry = IndexEntry(ctime_sec, ctime_nano, mtime_sec, mtime_nano, dev, ino, uid, gid, size, mode, flags, sha1, path)
            self.entries.append(entry)

        # TODO: 解析扩展
        remaining = len(data) - pos - 20 # 减去 20 Bytes 的checksum
        if remaining > 0:
            print('Parsing extension...')

        # 检验校验和
        expected_checksum = data[-20:]
        actual_checksum = hashlib.sha1(data[:-20]).digest()
        assert expected_checksum == actual_checksum

    def print(self):
        for entry in self.entries:
            print(entry)


def ls_files(repo_path: Path):
    dot_git_path = repo_path / '.git'
    assert dot_git_path.exists()
    index_file = dot_git_path / 'index'
    if not index_file.exists():
        return

    git_index = GitIndex(index_file)
    git_index.parse()
    git_index.print()


def main():
    repo_root = get_repo_root()
    ls_files(repo_root)
