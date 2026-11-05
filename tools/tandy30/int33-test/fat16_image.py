"""Read and update existing FAT16 files on the Tandy 31,808-sector CF image."""
import struct

CARD_BYTES = 31808 * 512

class Fat16:
    def __init__(self, image):
        self.b = image
        if len(image) != CARD_BYTES or image[510:512] != b'\x55\xaa':
            raise ValueError('Wrong card image size or MBR')
        start, length = struct.unpack_from('<II', image, 454)
        if start != 63 or start + length != 31808:
            raise ValueError('Unexpected partition layout')
        self.part = start * 512
        sector = struct.unpack_from('<H', image, self.part + 11)[0]
        clustersz = image[self.part + 13]
        copies = image[self.part + 16]
        if sector != 512 or clustersz != 4 or copies != 2:
            raise ValueError('Unsupported FAT geometry')
        self.cs = sector * clustersz
        reserved = struct.unpack_from('<H', image, self.part + 14)[0]
        entries = struct.unpack_from('<H', image, self.part + 17)[0]
        fatlen = struct.unpack_from('<H', image, self.part + 22)[0]
        self.fat = self.part + reserved * sector
        self.root = self.fat + copies * fatlen * sector
        self.rootlen = entries * 32
        self.data = self.root + self.rootlen

    def chain(self, first):
        used = set()
        while 2 <= first < 0xfff8:
            if first in used or len(used) > 10000:
                raise ValueError('FAT loop')
            used.add(first)
            start = self.data + (first - 2) * self.cs
            if start + self.cs > len(self.b):
                raise ValueError('FAT cluster beyond disk')
            yield start
            first = struct.unpack_from('<H', self.b, self.fat + first * 2)[0]

    def entries(self, directory=None):
        if directory is None:
            positions = range(self.root, self.root+self.rootlen, 32)
        else:
            positions = (p for c in self.chain(directory) for p in range(c,c+self.cs,32))
        for p in positions:
            entry = self.b[p:p+32]
            if entry[0] == 0:
                break
            if entry[0] == 0xe5 or entry[11] == 0x0f or entry[11] & 8:
                continue
            base = entry[:8].decode('ascii').strip()
            ext = entry[8:11].decode('ascii').strip()
            yield p, (base + ('.'+ext if ext else '')).upper(), entry[11], struct.unpack_from('<H',entry,26)[0],struct.unpack_from('<I',entry,28)[0]

    def locate(self, path):
        directory = None
        names = path.upper().strip('/').split('/')
        for i,name in enumerate(names):
            result = next((v for v in self.entries(directory) if v[1] == name), None)
            if result is None:
                raise FileNotFoundError(path)
            if i < len(names) - 1:
                directory = result[3]
        return result

    def read(self, path):
        _, _, _, cluster, size = self.locate(path)
        return b''.join(self.b[p:p+self.cs] for p in self.chain(cluster))[:size]

    def write_existing(self, path, new):
        pos, _, _, cluster, old_size = self.locate(path)
        locations = list(self.chain(cluster))
        if len(new) > len(locations)*self.cs:
            raise ValueError(f'Existing FAT chain too short for {path}')
        for i,at in enumerate(locations):
            chunk = new[i*self.cs:(i+1)*self.cs]
            self.b[at:at+len(chunk)] = chunk
        struct.pack_into('<I',self.b,pos+28,len(new))
        if self.read(path) != new:
            raise ValueError(f'Unable to verify {path}')
        print(f'{path}: {old_size} -> {len(new)} bytes')
