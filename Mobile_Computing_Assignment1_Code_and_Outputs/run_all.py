
from pathlib import Path
import math,time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent; DATA=ROOT/"data"; OUT=ROOT/"outputs"
DATA.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
SEED=20261102; rng=np.random.default_rng(SEED)
AREA=12.; S=336; R=.5; TARGET=.02; SIR_TARGET=12.; USERS=[1000,10000,20000,100000]
CLUSTERS=[3,4,7,12,13]; EXPS=[2.5,3.5,4.]; NSAMP=10000
def hex_area(r): return 2.598076211*r*r
def cells(r=R): return math.ceil(AREA/hex_area(r))
def reuse(r,n): return r*math.sqrt(3*n)
def erlang_b(c,a):
 b=1.
 for k in range(1,int(c)+1): b=a*b/(k+a*b)
 return b
def gos_capacity(c):
 lo,hi=0.,c*4.
 for _ in range(90):
  m=(lo+hi)/2
  if erlang_b(c,m)>TARGET: hi=m
  else: lo=m
 return (lo+hi)/2
def sir(n,p): return 10*np.log10((3*n)**(p/2)/6)
def sector_sir(n,p): return 10*np.log10((3*n)**(p/2)/(2*.5))
def mc(n,p,sector=False):
 D=reuse(R,n); ang=np.arange(6)*np.pi/3
 bs=np.c_[D*np.cos(ang),D*np.sin(ang)]
 th=rng.uniform(0,2*np.pi,NSAMP); rad=R*np.sqrt(rng.random(NSAMP))
 xy=np.c_[rad*np.cos(th),rad*np.sin(th)]
 ds=np.maximum(np.linalg.norm(xy,axis=1),.03)
 sig=ds**(-p)*10**(rng.normal(0,6,NSAMP)/10)
 interf=np.zeros(NSAMP)
 for b in bs:
  d=np.maximum(np.linalg.norm(xy-b,axis=1),.03)
  gain=np.ones(NSAMP)
  if sector:
   bearing=np.arctan2(xy[:,1]-b[1],xy[:,0]-b[0])
   gain=np.where(np.abs(bearing)<np.pi/3,1.,.25)
  interf+=gain*d**(-p)*10**(rng.normal(0,6,NSAMP)/10)
 return 10*np.log10(sig/interf)
def save(name,rows): pd.DataFrame(rows).to_csv(DATA/name,index=False)
t=time.perf_counter()
# Tasks 1-3: cluster/reuse/capacity and analytical sensitivity
rows=[]
for i in range(8):
 for j in range(8):
  n=i*i+i*j+j*j
  if n in CLUSTERS and not any(x["N"]==n for x in rows):
   rows.append(dict(i=i,j=j,N=n,channels_ideal=S/n,channels_integer=S//n,reuse_distance_km=reuse(R,n)))
save("q1_cluster_reuse_planning.csv",rows)
sr=[]; cr=[]
for n in CLUSTERS:
 c=S//n
 cr.append(dict(N=n,channels_per_cell=c,traffic_per_cell_at_2pct_erlangs=gos_capacity(c),reference_cells=cells(),system_capacity_erlangs=cells()*gos_capacity(c)))
 for p in EXPS: sr.append(dict(N=n,path_loss_exponent=p,analytical_SIR_dB=sir(n,p),illustrative_sector_SIR_dB=sector_sir(n,p)))
save("q3_analytical_sir_sensitivity.csv",sr); save("q3_channel_capacity.csv",cr)
# Tasks 4,8-10: Monte Carlo SIR and CDF
summ=[]; cdfs=[]
for name,n,sec in [("FCA_N7",7,False),("FCA_N13",13,False),("Sectorised_N7",7,True),("Hierarchical_sectorised_N7",7,True)]:
 v=mc(n,3.5,sec)
 summ.append(dict(strategy=name,N=n,n=3.5,samples=NSAMP,mean_SIR_dB=v.mean(),p5_SIR_dB=np.percentile(v,5),outage_below_12dB=np.mean(v<12)))
 order=np.sort(v)
 for ix in np.linspace(0,len(order)-1,200,dtype=int):
  cdfs.append(dict(strategy=name,SIR_dB=order[ix],CDF=(ix+1)/len(order)))
save("q4_monte_carlo_sir_summary.csv",summ); save("q4_sir_cdf.csv",cdfs)
# Task 8 Erlang-B
br=[]
for c in [25,26,28,48,84,112]:
 for a in np.linspace(.1,c*1.5,120): br.append(dict(channels=c,offered_erlangs=a,blocking_probability=erlang_b(c,a)))
save("q8_erlang_b_blocking.csv",br)
# Task 5 subscriber scaling
gr=[]
for u in USERS:
 for n in [7,13]:
  c=S//n; cap=gos_capacity(c); demand=u*.025
  gr.append(dict(subscribers=u,offered_erlangs=demand,N=n,channels_per_cell=c,capacity_per_cell_erlangs=cap,required_cell_equivalents=math.ceil(demand/cap)))
save("q5_subscriber_scaling.csv",gr)
# Tasks 6-7 cell splitting recurrence
spl=[]
for k in range(5):
 spl.append(dict(round=k,cells=cells()*4**k,radius_km=R/2**k,ideal_capacity_erlangs=342*4**k,handoff_relative=2**k,tx_power_relative_n4=1/2**(4*k)))
for f in [.1,.25,.5,1.]:
 for k in range(8): spl.append(dict(split_fraction=f,round=k,selective_cell_multiplier=(1+3*f)**k,selective_capacity_erlangs=342*(1+3*f)**k))
save("q6_q7_cell_splitting.csv",spl)
# Task 12 stadium event
event=25000*.05; normal=100000*.025/12
save("q12_stadium_event.csv",[
 dict(design="Original_two_macrocell_equivalents",event_erlangs=event,sites=2,estimated_capacity_erlangs=2*gos_capacity(26),density_erlangs_km2=event,normal_100k_density=normal),
 dict(design="Temporary_21_three_sector_equivalents",event_erlangs=event,sites=21,estimated_capacity_erlangs=21*3*gos_capacity(28),density_erlangs_km2=event,normal_100k_density=normal)])
save("q9_q10_strategy_comparison.csv",summ)
# Charts
plt.figure(figsize=(8,5))
for p in EXPS: plt.plot(CLUSTERS,[sir(n,p) for n in CLUSTERS],marker="o",label=f"n={p}")
plt.axhline(12,ls="--",label="12 dB target"); plt.xlabel("Cluster size N"); plt.ylabel("SIR (dB)"); plt.title("Analytical SIR vs Cluster Size"); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(OUT/"Q3_SIR_sensitivity.png",dpi=160); plt.close()
plt.figure(figsize=(8,5))
for name in sorted(set(x["strategy"] for x in cdfs)):
 q=[x for x in cdfs if x["strategy"]==name]; plt.plot([x["SIR_dB"] for x in q],[x["CDF"] for x in q],label=name)
plt.axvline(12,ls="--",label="12 dB target"); plt.xlabel("SIR (dB)"); plt.ylabel("Empirical CDF"); plt.title("Monte Carlo SIR CDF (n=3.5)"); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(OUT/"Q4_Monte_Carlo_SIR_CDF.png",dpi=160); plt.close()
df=pd.DataFrame(br); plt.figure(figsize=(8,5))
for c,g in df.groupby("channels"): plt.plot(g.offered_erlangs,g.blocking_probability,label=f"{c} channels")
plt.axhline(.02,ls="--",label="2% target"); plt.xlabel("Offered traffic (Erlangs)"); plt.ylabel("Blocking probability"); plt.title("Erlang-B Blocking Curves"); plt.ylim(0,1); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(OUT/"Q8_Erlang_B_blocking.png",dpi=160); plt.close()
df=pd.DataFrame(gr); plt.figure(figsize=(8,5))
for n,g in df.groupby("N"): plt.plot(g.subscribers,g.required_cell_equivalents,marker="o",label=f"N={n}")
plt.xlabel("Subscribers"); plt.ylabel("Required cell-equivalents"); plt.title("Cell Requirement vs Subscriber Growth"); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(OUT/"Q5_Subscriber_scaling.png",dpi=160); plt.close()
df=pd.DataFrame([x for x in spl if "cells" in x]); plt.figure(figsize=(8,5))
plt.plot(df["round"],df.cells,marker="o",label="Number of cells"); plt.plot(df["round"],df.ideal_capacity_erlangs,marker="s",label="Ideal capacity (Erlangs)")
plt.xlabel("Splitting round"); plt.ylabel("Relative quantity"); plt.title("Uniform Cell-Splitting Recurrence"); plt.grid(alpha=.3); plt.legend(); plt.tight_layout(); plt.savefig(OUT/"Q6_Q7_Cell_splitting.png",dpi=160); plt.close()
plt.figure(figsize=(8,5)); plt.bar(["100k township\naverage","Stadium event"],[normal,event]); plt.ylabel("Erlangs/km²"); plt.title("Stadium Event Traffic Density"); plt.tight_layout(); plt.savefig(OUT/"Q12_Stadium_event_density.png",dpi=160); plt.close()
plt.figure(figsize=(8,5)); plt.bar([str(x["N"]) for x in cr],[x["channels_per_cell"] for x in cr]); plt.xlabel("Cluster size N"); plt.ylabel("Channels per cell"); plt.title("Channels per Cell vs Cluster Size"); plt.tight_layout(); plt.savefig(OUT/"Q3_Channels_per_cell.png",dpi=160); plt.close()
summary=[f"Seed: {SEED}",f"Monte Carlo samples per strategy: {NSAMP}",f"Hexagonal cell area at R=0.5 km: {2.598076211*R*R:.4f} km^2",f"Approximate reference cell count: {cells()}",f"Stadium offered traffic: {event:.1f} Erlangs",f"Execution time: {time.perf_counter()-t:.2f} seconds","Monte Carlo SIR, analytical SIR and Erlang-B blocking are distinct measures."]
(ROOT/"run_summary.txt").write_text("\\n".join(summary),encoding="utf-8")
print("\\n".join(summary)); print("CSV files:",len(list(DATA.glob("*.csv"))),"PNG files:",len(list(OUT.glob("*.png"))))
