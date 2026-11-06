#!/usr/bin/env python3
"""Build exactly-pinned TR5 + RRECT + upstream compact320 OEM-resource variant.

This does not install anything on the user's disk. Compiles against a newly
materialized 16-bit DDK view and produces a separate, untested display driver.
The only bypassed *baseline identity* check is the intentionally different
resource SHA; the actual resource digest is recorded in RESULT.json.
All emitted 8086 instructions, linked objects, REP prefixes and ABI audits
from BUILD88.PY still run unchanged.
"""
import hashlib
import importlib.machinery
import json
import os
from pathlib import Path
import sys

def sha(data):
    return hashlib.sha256(data).hexdigest()

def build(repo, emulator, output):
    repo=Path(repo).resolve()
    output=Path(output).resolve()
    if output.exists():
        raise SystemExit('Refuse existing output')
    src=repo/'src'/'tandysw'
    sys.path.insert(0, str(src))
    b88=importlib.machinery.SourceFileLoader('b88_compact',str(src/'BUILD88.PY')).load_module()
    mod=importlib.machinery.SourceFileLoader('compact320',str(src/'COMPACT.PY')).load_module()
    rr=importlib.machinery.SourceFileLoader('rrect_compact',str(src/'RRPATCH.PY')).load_module()
    oldprep=b88.baseline.prepare
    oldrun=b88.bounded_run
    state={}
    def prepare(r,o):
        renderer,resources=oldprep(r,o)
        state['renderer']=renderer
        state['resources']=resources
        return renderer,resources
    def run(command,env,path,timeout=180):
        if not state.get('patched'):
            renderer=Path(state['renderer'])
            resources=Path(state['resources'])
            staged=mod.stage(renderer,resources,repo,'compact320','320x200x16')
            tsoft=renderer/'EGA'/'TSOFT.ASM'
            before=tsoft.read_bytes()
            content=rr.patch_candidate(before.decode('latin-1'))
            if '\n' in content.replace('\r\n',''):
                raise SystemExit('Unexpected bare LF in staged MASM')
            modified=content.encode('latin-1')
            tsoft.write_bytes(modified)
            state['patched']={'compact':staged,
                 'source_before':sha(before),
                 'source_after':sha(modified)}
        return oldrun(command,env,path,timeout)
    b88.baseline.prepare=prepare
    b88.bounded_run=run
    os.environ['TANDY_UI_PROFILE']='compact320'
    sys.argv=['BUILD88.PY','--repo',str(repo),'--dosbox',str(Path(emulator).resolve()),
              '--out',str(output),'--mode','320x200x16']
    b88.main()
    if 'patched' not in state:
        raise SystemExit('Hook was not invoked')
    r=json.loads((output/'RESULT.json').read_text())
    if r['build']!='PASS':
        raise SystemExit('Build audits did not pass')
    drv=output/'TANDY88.DRV'
    data=drv.read_bytes()
    if data[:2]!=b'MZ':
        raise SystemExit('Not an MZ/NE driver')
    ne=int.from_bytes(data[0x3c:0x40],'little')
    if data[ne:ne+2]!=b'NE':
        raise SystemExit('Not a NE driver')
    result={'profile':'compact320+rrect','bytes':len(data),'sha256':sha(data),
            'resources':r['resource_sha256'],'stage':state['patched'],
            'runtime':'NOT_TESTED_ON_PHYSICAL_HARDWARE'}
    (output/'COMPACT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    if len(sys.argv)!=4:
        raise SystemExit('Usage: COMPACTBUILD.PY <private source-view> <dosbox-x> <fresh output>')
    build(*sys.argv[1:])
