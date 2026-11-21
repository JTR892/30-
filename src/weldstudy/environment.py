import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def command(args):
    try: return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception: return None

def probe():
    r={"python_executable":sys.executable,"python":platform.python_version(),"platform":platform.platform(),
       "machine":platform.machine(),"chip":command(["sysctl","-n","machdep.cpu.brand_string"]),
       "memory_bytes":command(["sysctl","-n","hw.memsize"]),"macos":command(["sw_vers"]),
       "free_bytes_workspace_volume":shutil.disk_usage(Path.cwd()).free,
       "modules":{m:bool(importlib.util.find_spec(m)) for m in ["torch","torchvision","sklearn","PIL"]}}
    if r["modules"]["torch"]:
        import torch
        r.update(torch_version=torch.__version__,mps_built=torch.backends.mps.is_built(),mps_available=torch.backends.mps.is_available())
    else: r["mps_status"]="NOT_TESTED: torch absent in this interpreter"
    r["training_throughput"]="NOT_MEASURED"
    return r

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args();out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    result=probe();out.write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))

