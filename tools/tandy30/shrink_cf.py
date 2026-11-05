#!/usr/bin/env python3
"""Safely shrink the TANDY30 raw MBR/FAT16 image to a 31,808-sector CF card.

Do not simply truncate FAT partitions: update the MBR and FAT BPB and
ensure no allocated clusters are outside the smaller filesystem.
"""
import argparse
import hashlib
from pathlib import Path
import struct

SECTOR_SIZE = 512
TARGET_SECTORS = 31808

def chs(lba, heads, sectors_per_track):
    cylinder, remainder = divmod(lba, heads * sectors_per_track)
    head, sector0 = divmod(remainder, sectors_per_track)
    if cylinder > 1023:
        return b"\xfe\xff\xff"
    sector = sector0 + 1
    return bytes((head, (sector & 63) | ((cylinder >> 2) & 0xc0), cylinder & 0xff))

def shrink(source, target):
    data = bytearray(source.read_bytes())
    if len(data) != 32768 * SECTOR_SIZE:
        raise ValueError("Expected unchanged 16 MiB baseline (32768 sectors)")
    if data[510:512] != b"\x55\xaa":
        raise ValueError("Invalid MBR signature")
    entry = 446
    if data[entry + 4] not in (4, 6):
        raise ValueError("Unexpected partition type")
    start, old_length = struct.unpack_from("<II", data, entry + 8)
    if start != 63 or old_length != 32705:
        raise ValueError(f"Unexpected partition layout: {start=}, {old_length=}")
    new_length = TARGET_SECTORS - start
    boot = start * SECTOR_SIZE
    bpb = data[boot:boot + SECTOR_SIZE]
    if bpb[510:512] != b"\x55\xaa":
        raise ValueError("Bad filesystem boot sector")
    bps, = struct.unpack_from("<H", bpb, 11)
    spc = bpb[13]
    reserved, = struct.unpack_from("<H", bpb, 14)
    fats = bpb[16]
    roots, total16 = struct.unpack_from("<HH", bpb, 17)
    spf, spt, heads = struct.unpack_from("<HHH", bpb, 22)
    hidden, = struct.unpack_from("<I", bpb, 28)
    if (bps, spc, reserved, fats, roots, total16, spf, hidden) != (
        512, 4, 1, 2, 512, old_length, 32, start
    ):
        raise ValueError("FAT geometry changed, refusing to shrink")
    root_sectors = (roots * 32 + bps - 1) // bps
    first_data_sector = reserved + fats * spf + root_sectors
    old_clusters = (old_length - first_data_sector) // spc
    new_clusters = (new_length - first_data_sector) // spc
    if not (4085 <= new_clusters < 65525):
        raise ValueError("Target geometry is not FAT16")
    fat_start = boot + reserved * SECTOR_SIZE
    fat_size = spf * SECTOR_SIZE
    fat = data[fat_start:fat_start + fat_size]
    for copy in range(1, fats):
        pos = fat_start + copy * fat_size
        if fat != data[pos:pos + fat_size]:
            raise ValueError("FAT copies differ, refusing to shrink")
    for cluster in range(new_clusters + 2, old_clusters + 2):
        value, = struct.unpack_from("<H", fat, cluster * 2)
        if value != 0:
            raise ValueError(f"Cluster {cluster} is allocated in discarded region")
    # Confirm no retained cluster points to a discarded cluster.
    for cluster in range(2, new_clusters + 2):
        value, = struct.unpack_from("<H", fat, cluster * 2)
        if new_clusters + 2 <= value < 0xfff0:
            raise ValueError(f"Cluster {cluster} references discarded cluster {value}")
    struct.pack_into("<I", data, entry + 12, new_length)
    data[entry + 5:entry + 8] = chs(TARGET_SECTORS - 1, heads, spt)
    struct.pack_into("<H", data, boot + 19, new_length)
    data = data[:TARGET_SECTORS * SECTOR_SIZE]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    if len(data) != TARGET_SECTORS * SECTOR_SIZE:
        raise AssertionError("Unexpected output size")
    assert struct.unpack_from("<I", data, entry + 12)[0] == new_length
    assert struct.unpack_from("<H", data, boot + 19)[0] == new_length
    print(f"Shrunk to {len(data)} bytes ({TARGET_SECTORS} sectors), "
          f"FAT16 clusters {old_clusters} -> {new_clusters}; "
          f"SHA256 {hashlib.sha256(data).hexdigest()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    shrink(args.source, args.target)
