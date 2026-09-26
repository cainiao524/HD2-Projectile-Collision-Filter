"""Compare logical reads using synthetic memory, never native game execution."""
import argparse
import json
from pathlib import Path
from lupa.luajit21 import LuaRuntime

HERE=Path(__file__).resolve().parent

def measure(core):
    runtime=LuaRuntime(encoding=None,unpack_returned_tuples=True)
    runtime.globals()[b'Core']=runtime.execute(core)
    runtime.globals()[b'Fixture']=runtime.execute((HERE/'test_fixture.lua').read_bytes())
    run=runtime.eval(b'''function(n,scope,pistol,owner)
      local f=Fixture()
      f.zero(f.system+0xe5040,8192);f.zero(f.system+0x203c,4096)
      f.put(f.weapon,f.raw(pistol and '05e4e5c2db6e44a2' or '4a00000000000001'))
      f.put(f.base+0x37c7670+22*8,f.p(f.definition));f.put(f.definition,f.u(22))
      for slot=0,n-1 do f.slot(slot,owner,22) end
      local ok,count=pcall(Core.tick,f.api,{scope=scope,pistol_unit_hashes={'05e4e5c2db6e44a2'}})
      assert(ok,tostring(count))
      local reads=0;for _,v in pairs(f.hits) do reads=reads+v end
      return reads,#f.writes
    end''')
    rows=[]
    for case,scope,pistol,owner in (
        ('pistol_mode_rejects_own_primary','pistols',False,1001),
        ('pistol_mode_accepts_allowed_pellets','pistols',True,1001),
        ('broad_mode_accepts_own_primary','native_weapons',False,1001),
        ('broad_mode_rejects_foreign_owner','native_weapons',False,9999)):
        for pellets in (0,1,12,32,64):
            reads,writes=run(pellets,scope.encode(),pistol,owner)
            rows.append({'case':case,'pellets':pellets,'reads':reads,'writes':writes})
    return rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-core',type=Path,help='Optional previous core.lua, read only')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    rows=measure((HERE/'core.lua').read_bytes())
    if args.baseline_core:
        previous=measure(args.baseline_core.read_bytes())
        for row,old in zip(rows,previous):
            assert (row['case'],row['pellets'],row['writes'])==(old['case'],old['pellets'],old['writes'])
            row['previous_reads']=old['reads']
            row['read_reduction_percent']=round((old['reads']-row['reads'])*100/old['reads'],2)
    result={'scope':'Synthetic logical read counts including mock guard rechecks; not native API timings or game FPS.',
            'native_execution':False,'gameplay_verified':False,'results':rows}
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    print(text)

if __name__=='__main__':main()
