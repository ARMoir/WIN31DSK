"""Minimal read/write FAT12 floppy-image utility, no third-party dependencies."""
import struct

class FAT12:
    def __init__(self,b):
        self.b=bytearray(b)
        self.bps=struct.unpack_from('<H',self.b,11)[0]
        self.spc=self.b[13]
        self.rsv=struct.unpack_from('<H',self.b,14)[0]
        self.nfat=self.b[16]
        self.rootentries=struct.unpack_from('<H',self.b,17)[0]
        self.tot=struct.unpack_from('<H',self.b,19)[0]
        self.fatsz=struct.unpack_from('<H',self.b,22)[0]
        self.rootsecs=(self.rootentries*32+self.bps-1)//self.bps
        self.fatstart=self.rsv*self.bps
        self.rootstart=(self.rsv+self.nfat*self.fatsz)*self.bps
        self.datastart=self.rootstart+self.rootsecs*self.bps
        self.clusters=(self.tot-self.rsv-self.nfat*self.fatsz-self.rootsecs)//self.spc
        self.clsize=self.spc*self.bps
        assert self.tot==2880 and self.bps==512 and self.spc>=1 and self.fatsz>=1

    def clusterpos(self,c):
        return self.datastart+(c-2)*self.clsize

    def fatentry(self,i):
        addr=self.fatstart+(i*3)//2
        val=struct.unpack_from('<H',self.b,addr)[0]
        return (val>>4 if i&1 else val&0xfff)

    def setfat(self,i,val):
        for start in range(self.nfat):
            addr=self.fatstart+start*self.fatsz*self.bps+(i*3)//2
            word=struct.unpack_from('<H',self.b,addr)[0]
            word=((word&0x000f)|((val&0xfff)<<4)) if i&1 else ((word&0xf000)|(val&0xfff))
            struct.pack_into('<H',self.b,addr,word)

    def readchain(self,c):
        data=bytearray()
        seen=set()
        while c>=2 and c<0xff8:
            if c in seen:
                raise RuntimeError('FAT loop')
            seen.add(c)
            data.extend(self.b[self.clusterpos(c):self.clusterpos(c)+self.clsize])
            c=self.fatentry(c)
        return bytes(data)

    def rows(self,off=None,count=None):
        if off is None:
            off=self.rootstart
            count=self.rootentries
        result=[]
        for i in range(count):
            entry=self.b[off+i*32:off+i*32+32]
            if entry[0]==0: break
            if entry[0]==0xe5 or entry[11]==0xf or entry[11]&8: continue
            name=entry[:8].decode('cp437').strip()
            ext=entry[8:11].decode('cp437').strip()
            name=name + ('.'+ext if ext else '')
            clu=struct.unpack_from('<H',entry,26)[0]
            size=struct.unpack_from('<I',entry,28)[0]
            result.append((name,size,clu,entry[11],off+i*32))
        return result

    def walk(self):
        pending=[('',None,None)]
        while pending:
            pref,off,cnt=pending.pop(0)
            for name,size,clu,attr,ofs in self.rows(off,cnt):
                if name.startswith('.'): continue
                p=pref+name
                if attr&0x10:
                    cc=clu
                    while cc>=2 and cc<0xff8:
                        pending.append((p+'/',self.clusterpos(cc),self.clsize//32))
                        cc=self.fatentry(cc)
                else:
                    yield p,size,clu,attr,ofs

    def readfile(self,path):
        for p,size,clu,attr,ofs in self.walk():
            if p.upper()==path.upper():
                return self.readchain(clu)[:size]
        raise KeyError(path)

    def delete(self,path):
        for p,size,clu,attr,ofs in self.walk():
            if p.upper()==path.upper():
                self.b[ofs]=0xe5
                while clu>=2 and clu<0xff8:
                    nxt=self.fatentry(clu)
                    self.setfat(clu,0)
                    clu=nxt
                return
        raise KeyError(path)

    def writefile(self,path,data,attrs=0x20):
        if '/' in path or '\\' in path or len(path.split('.')[0])>8 or len(path.split('.')[-1])>3:
            raise ValueError('Root 8.3 only: '+path)
        try: self.delete(path)
        except KeyError: pass
        count=(len(data)+self.clsize-1)//self.clsize
        free=[i for i in range(2,self.clusters+2) if self.fatentry(i)==0]
        if len(free)<count: raise RuntimeError('No free space')
        slots=[self.rootstart+i*32 for i in range(self.rootentries)
               if self.b[self.rootstart+i*32] in (0,0xe5)]
        if not slots: raise RuntimeError('No root directory slots')
        chains=free[:count]
        for i,c in enumerate(chains):
            self.setfat(c,chains[i+1] if i+1<len(chains) else 0xfff)
            block=data[i*self.clsize:(i+1)*self.clsize]
            self.b[self.clusterpos(c):self.clusterpos(c)+self.clsize]=block.ljust(self.clsize,b'\0')
        parts=path.upper().split('.')
        name=parts[0].ljust(8)+(parts[1].ljust(3) if len(parts)>1 else '   ')
        o=slots[0]
        self.b[o:o+32]=b'\0'*32
        self.b[o:o+11]=name.encode('ascii')
        self.b[o+11]=attrs
        struct.pack_into('<H',self.b,o+26,chains[0] if chains else 0)
        struct.pack_into('<I',self.b,o+28,len(data))

    def freebytes(self):
        return sum(self.fatentry(i)==0 for i in range(2,self.clusters+2))*self.clsize
