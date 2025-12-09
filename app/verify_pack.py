import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import struct
from typing import List

@dataclass
class PackIndexEntry:
    sha1: bytes
    crc32: int
    offset: int

    def __repr__(self):
        return f"{self.sha1.hex()} {self.offset}"


class GitPackIndex:
    """Git version 2"""

    IDX_SIGNATURE = b'\xff\x74\x4f\x63' # b'\xfftOc'
    IDX_VERSION = 2

    def __init__(self, idx_file: Path):
        self.idx_file = idx_file
        self.entries: List[PackIndexEntry] = []
        self.fanout_table = []

    def parse(self):
        with open(self.idx_file, 'rb') as f:
            data = f.read()
        
        # 1. 解析头部 (8 Byets)
        pos = 0
        signature = data[pos:pos+4]
        pos += 4
        version = struct.unpack('>I', data[pos:pos+4])[0]
        pos += 4

        assert signature == self.IDX_SIGNATURE
        assert version == self.IDX_VERSION

        # 2. 解析 Fan-out 表 (256个uint32)
        self.fanout_table = []
        for i in range(256):
            count = struct.unpack('>I', data[pos:pos+4])[0]
            self.fanout_table.append(count)
            pos += 4
        
        # 对象总数 = fanout_table 的最后一项
        total_objects = self.fanout_table[-1]
        print(f"Object counts: {total_objects}")

        # 3. 解析SHA-1列表 (20 Bytes * total_objects)
        sha1_list = []
        for _ in range(total_objects):
            sha1 = data[pos:pos+20]
            sha1_list.append(sha1)
            pos += 20
        
        # 4. 解析CRC32列表(4 Bytes * total_objects)
        crc32_list = []
        for _ in range(total_objects):
            crc32 = struct.unpack('>I', data[pos:pos+4])[0]
            crc32_list.append(crc32)
            pos += 4

        # 5. 解析偏移量列表 (4 Bytes / 8 Bytes(large offset) * n)
        offsets = []
        for _ in range(total_objects):
            # 先读取4B的偏移
            offset = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4

            if offset & 0x80000000:
                # 清除高位标志, 读取后4B
                offset = offset & 0x7fffffff
                offset_high = struct.unpack('>I', data[pos:pos+4])[0]
                pos += 4
                offset = (offset << 32) | offset_high
            
            offsets.append(offset)

        # 6. TODO: 验证pack文件的SHA-1
        self.packfile_sha1 = data[pos:pos+20]
        pos += 20

        # 7. 验证idx文件的SHA-1
        expected_idx_sha1 = data[pos:pos+20]
        actual_idx_sha1 = hashlib.sha1(data[:-20]).digest()
        assert expected_idx_sha1 == actual_idx_sha1, f"idx file SHA-1 does not match, the file may be broken!"

        # 构建pack index entry列表
        self.entries = [
            PackIndexEntry(sha1, crc32, offset)
            for sha1, crc32, offset in zip(sha1_list, crc32_list, offsets)
        ]

    def print(self):
        for entry in sorted(self.entries, key=lambda e: e.offset):
            print(entry)        


def verfiy_pack(idx_file: Path):
    assert idx_file.exists()

    pack_index = GitPackIndex(idx_file)
    pack_index.parse()
    pack_index.print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('idx_file', type=Path)
    args = parser.parse_args()

    verfiy_pack(args.idx_file)

