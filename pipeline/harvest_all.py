#!/usr/bin/env python3
"""harvest_all.py — windowed resumable harvest driver.
Usage: harvest_all.py <wave-label> [budget_s]
Harvests all cached sources to clips/, skipping already-cut segments."""
import json, os, subprocess, sys, time

BASE="/home/z/my-project/engine/projects/blackpink"
CACHE=f"{BASE}/ytdl_cache"; CLIPS=f"{BASE}/clips"
SOURCES={s["video_id"]: s for s in json.load(open(f"{BASE}/subject_sources.json"))}

def main():
    wave=sys.argv[1]; budget=int(sys.argv[2]) if len(sys.argv)>2 else 480
    jobs=[]
    for vid,meta in SOURCES.items():
        if not os.path.exists(f"{CACHE}/{vid}.mp4"): continue
        n={"A":5,"B":4,"C":4,"D":2,"E":3}.get(meta["category"],4)
        seg_len={"A":10,"B":10,"C":9,"D":8,"E":9}.get(meta["category"],9)
        jobs.append({"src":f"{CACHE}/{vid}.mp4","label":vid,"tags":meta["subject_tags"],"n":n,"seg_len":seg_len})
    cfg={"out_dir":CLIPS,"jobs":jobs}
    json.dump(cfg,open(f"/tmp/harvest_{wave}.json","w"),indent=1)
    t0=time.time()
    for job in jobs:
        if time.time()-t0>budget: print("BUDGET_STOP",flush=True); break
        if not os.path.exists(job["src"]): continue
        one={"out_dir":CLIPS,"jobs":[job]}
        json.dump(one,open("/tmp/h_one.json","w"))
        print(f"== {job['label']} ({job['n']}x{job['seg_len']}s {job['tags']}) ==",flush=True)
        try:
            r=subprocess.run(["python3","/home/z/my-project/engine/pipeline/harvest.py","run","/tmp/h_one.json"],
                             capture_output=True,text=True,timeout=420)
            print(r.stdout.strip()[-400:],flush=True)
        except subprocess.TimeoutExpired:
            print("  TIMEOUT (partial segments kept)",flush=True)
    total=len([f for f in os.listdir(CLIPS) if f.endswith('.mp4')])
    print(f"CLIPS TOTAL: {total}",flush=True)

if __name__=="__main__":
    os.makedirs(CLIPS,exist_ok=True)
    main()
