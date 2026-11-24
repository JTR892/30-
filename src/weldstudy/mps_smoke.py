"""Synthetic MPS forward/backward smoke test; not the project training benchmark."""
import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

def run(batch_size=4,image_size=128,steps=10,warmup=3,seed=17):
    import torch
    import torchvision
    if not torch.backends.mps.is_built():
        raise RuntimeError("This PyTorch build does not include MPS support")
    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS is not available on this machine/runtime")
    fallback=os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK","0").lower()
    if fallback not in ("","0","false","no"):
        raise RuntimeError("PYTORCH_ENABLE_MPS_FALLBACK is enabled; unset it to avoid silent CPU fallback")
    torch.manual_seed(seed)
    device=torch.device("mps")
    model=torchvision.models.resnet18(weights=None,num_classes=2).to(device)
    model.train()
    optimizer=torch.optim.SGD(model.parameters(),lr=1e-3,momentum=0.9)
    loss_fn=torch.nn.CrossEntropyLoss()
    x=torch.randn(batch_size,3,image_size,image_size,device=device)
    y=torch.randint(0,2,(batch_size,),device=device)
    for _ in range(warmup):
        optimizer.zero_grad(set_to_none=True)
        loss_fn(model(x),y).backward()
        optimizer.step()
    torch.mps.synchronize()
    start=time.perf_counter()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss=loss_fn(model(x),y)
        loss.backward()
        optimizer.step()
    torch.mps.synchronize()
    elapsed=time.perf_counter()-start
    memory={}
    for name,fn in (("current_allocated_bytes",getattr(torch.mps,"current_allocated_memory",None)),
                    ("driver_allocated_bytes",getattr(torch.mps,"driver_allocated_memory",None))):
        if fn is not None:
            try: memory[name]=int(fn())
            except Exception: memory[name]=None
    return {
        "status":"OK",
        "synthetic_only":True,
        "purpose":"Verify basic MPS forward/backward/optimizer execution; not SimCLR or attention throughput",
        "python":platform.python_version(),
        "platform":platform.platform(),
        "torch":torch.__version__,
        "torchvision":torchvision.__version__,
        "device":str(device),
        "mps_built":bool(torch.backends.mps.is_built()),
        "mps_available":bool(torch.backends.mps.is_available()),
        "model":"torchvision ResNet18, random initialization, 2 synthetic classes",
        "batch_size":batch_size,
        "image_size":image_size,
        "warmup_steps":warmup,
        "measured_steps":steps,
        "elapsed_seconds":round(elapsed,4),
        "seconds_per_step":round(elapsed/steps,4),
        "samples_per_second":round(batch_size*steps/elapsed,2),
        "mps_memory":memory,
        "seed":seed,
        "real_dataset_used":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--batch-size",type=int,default=4)
    p.add_argument("--image-size",type=int,default=128)
    p.add_argument("--steps",type=int,default=10)
    p.add_argument("--warmup",type=int,default=3)
    p.add_argument("--seed",type=int,default=17)
    p.add_argument("--out",default="reports/local/mps_smoke.json")
    a=p.parse_args()
    if min(a.batch_size,a.image_size,a.steps)<1 or a.warmup<0:
        p.error("batch-size, image-size and steps must be positive; warmup must be nonnegative")
    out=Path(a.out)
    try:
        result=run(a.batch_size,a.image_size,a.steps,a.warmup,a.seed)
    except Exception as e:
        result={"status":"FAILED","synthetic_only":True,"error_type":type(e).__name__,"error":str(e),
                "python":platform.python_version(),"platform":platform.platform(),"real_dataset_used":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["status"]=="OK" else 2)

if __name__=="__main__":
    main()
