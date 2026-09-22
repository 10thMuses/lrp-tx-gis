import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
plt.rcParams["text.parse_math"]=False
J=FontProperties(fname="fonts/Jost-Regular.ttf"); JB=FontProperties(fname="fonts/Jost-SemiBold.ttf")
NAVY="#1c2b3a"; GOLD="#b8860b"; GREY="#8a94a0"; GREEN="#1f7a3f"

fig,ax=plt.subplots(figsize=(7.2,3.3),dpi=200)
cats=["DFM fleet sold to NYDIG\n(Mar 2025)","Spark live\n(Sparks NV, Jun 2025)","Spark committed\n(Sparks 24 + Snyder 10)","Spark Factory\nstated capacity, per year"]
units=[425,4,34,100]; c=[GREY,GREEN,NAVY,GOLD]
bars=ax.barh(cats,units,color=c,height=0.55)
notes=["~270 MW, ~0.6 MW/unit avg","~4 MW, 2,000 GPUs","~34 MW","~100 MW/yr"]
for b,x,n in zip(bars,units,notes):
    ax.text(x+6,b.get_y()+b.get_height()/2,f"{x} units  ({n})",va="center",fontproperties=JB,fontsize=9,color=NAVY)
ax.set_xlim(0,600); ax.invert_yaxis()
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.tick_params(colors=NAVY,labelsize=9)
for l in ax.get_xticklabels()+ax.get_yticklabels(): l.set_fontproperties(J)
ax.set_xlabel("Modular units",fontproperties=J,fontsize=9,color=NAVY)
ax.set_title("Exhibit 1. Crusoe has already operated 425 modular units. Spark restarts the fleet with a new payload",fontproperties=JB,fontsize=10,color=NAVY,loc="left")
ax.text(0,-0.32,"Source: Crusoe/NYDIG releases (Mar 2025); Redwood and Crusoe releases (Jun 2025, Mar 2026); Energy Vault release (Jul 2026); Forbes (Mar 2026) for 100/yr and ~1 MW/unit.",transform=ax.transAxes,fontproperties=J,fontsize=7,color=GREY)
plt.tight_layout(); plt.savefig("ex1_modular.png",bbox_inches="tight"); plt.close()

fig,ax=plt.subplots(figsize=(7.2,3.0),dpi=200)
cats=["Spark output at stated\nfactory capacity (per year)","Gross contracted capacity\n(Sep 2026)","Development pipeline\n(company-stated, US)"]
v=[0.1,6.0,45.0]; c=[GOLD,NAVY,GREY]
bars=ax.barh(cats,v,color=c,height=0.55)
for b,x in zip(bars,v):
    ax.text(x+0.6,b.get_y()+b.get_height()/2,f"{x:g} GW",va="center",fontproperties=JB,fontsize=10,color=NAVY)
ax.set_xlim(0,52); ax.invert_yaxis()
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.tick_params(colors=NAVY,labelsize=9)
for l in ax.get_xticklabels()+ax.get_yticklabels(): l.set_fontproperties(J)
ax.set_xlabel("GW",fontproperties=J,fontsize=9,color=NAVY)
ax.set_title("Exhibit 2. Spark is under 2% of the contracted book. It is not the volume engine",fontproperties=JB,fontsize=10.5,color=NAVY,loc="left")
ax.text(0,-0.36,"Source: Crusoe Series F release (Sep 17 2026); Forbes (Mar 2026); Crusoe Series E release / CERAWeek remarks (Mar 2026).",transform=ax.transAxes,fontproperties=J,fontsize=7,color=GREY)
plt.tight_layout(); plt.savefig("ex2_share.png",bbox_inches="tight"); plt.close()
print("ok")
