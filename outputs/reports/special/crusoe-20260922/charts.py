import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
plt.rcParams["text.parse_math"]=False
J=FontProperties(fname="fonts/Jost-Regular.ttf"); JB=FontProperties(fname="fonts/Jost-SemiBold.ttf")
NAVY="#1c2b3a"; GOLD="#b8860b"; GREY="#8a94a0"; RED="#b0322b"; GREEN="#1f7a3f"

# Chart 1: valuation ladder
fig,ax=plt.subplots(figsize=(7.2,3.4),dpi=200)
labels=["Series D\nDec 2024","Series E\nOct 2025","Series F\nSep 2026"]
vals=[2.8,10.0,30.9]; raised=[0.6,1.375,3.9]
bars=ax.bar(labels,vals,color=[GREY,NAVY,GOLD],width=0.55)
for b,v,r in zip(bars,vals,raised):
    ax.text(b.get_x()+b.get_width()/2,v+0.8,f"${v:.1f}B post\n(${r:.2f}B raised)".replace(".00B",".0B"),ha="center",va="bottom",fontproperties=JB,fontsize=9,color=NAVY)
ax.set_ylim(0,40); ax.set_ylabel("Post-money valuation, $B",fontproperties=J,fontsize=9,color=NAVY)
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.tick_params(colors=NAVY,labelsize=9)
for l in ax.get_xticklabels()+ax.get_yticklabels(): l.set_fontproperties(J)
ax.set_title("Exhibit 1. Crusoe valuation: 11x in 21 months, priced on contracts",fontproperties=JB,fontsize=10.5,color=NAVY,loc="left")
ax.text(0,-0.28,"Source: company releases (Series E, Series F); Bloomberg/TechCrunch for Series D. Round sizes as reported at initial close.",transform=ax.transAxes,fontproperties=J,fontsize=7,color=GREY)
plt.tight_layout(); plt.savefig("ex1_valuation.png",bbox_inches="tight"); plt.close()

# Chart 2: announced vs contracted vs operational
fig,ax=plt.subplots(figsize=(7.2,3.2),dpi=200)
cats=["Operational\n(delivered)","Gross contracted\n(data center + cloud)","Development pipeline\n(company-stated, US)"]
v=[1.0,6.0,45.0]; c=[GREEN,NAVY,GREY]
bars=ax.barh(cats,v,color=c,height=0.55)
for b,x in zip(bars,v):
    ax.text(x+0.6,b.get_y()+b.get_height()/2,f"{x:g} GW",va="center",fontproperties=JB,fontsize=10,color=NAVY)
ax.set_xlim(0,52); ax.invert_yaxis()
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.tick_params(colors=NAVY,labelsize=9)
for l in ax.get_xticklabels()+ax.get_yticklabels(): l.set_fontproperties(J)
ax.set_xlabel("GW",fontproperties=J,fontsize=9,color=NAVY)
ax.set_title("Exhibit 2. Announced is not contracted; contracted is not delivered",fontproperties=JB,fontsize=10.5,color=NAVY,loc="left")
ax.text(0,-0.34,"Source: Crusoe Series F release (Sep 17 2026) for 1 GW and 6 GW+; Crusoe Series E release / CERAWeek remarks (Mar 2026) for 45 GW pipeline.",transform=ax.transAxes,fontproperties=J,fontsize=7,color=GREY)
plt.tight_layout(); plt.savefig("ex2_capacity.png",bbox_inches="tight"); plt.close()
print("charts ok")

# Chart 3: capital by layer
fig,ax=plt.subplots(figsize=(7.2,3.0),dpi=200)
cats=["Corporate equity\n(Series D, E, F)","Corporate credit\n(Upper90, Brookfield, VPC)","Abilene project JV\n(Blue Owl, Primary Digital, JPM)"]
v=[5.875,1.15,15.0]; c=[GOLD,NAVY,GREY]
bars=ax.barh(cats,v,color=c,height=0.55)
for b,x in zip(bars,v):
    ax.text(x+0.25,b.get_y()+b.get_height()/2,f"${x:.2f}B".replace(".00B","B").replace(".15B",".15B"),va="center",fontproperties=JB,fontsize=10,color=NAVY)
ax.set_xlim(0,18); ax.invert_yaxis()
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.tick_params(colors=NAVY,labelsize=9)
for l in ax.get_xticklabels()+ax.get_yticklabels(): l.set_fontproperties(J)
ax.set_xlabel("$B committed, Dec 2024 to Sep 2026",fontproperties=J,fontsize=9,color=NAVY)
ax.set_title("Exhibit 3. Project-level capital is 2.5x corporate equity; the balance sheet is not the build",fontproperties=JB,fontsize=10.5,color=NAVY,loc="left")
ax.text(0,-0.36,"Source: company releases. Abilene JV total as announced May 2025; debt/equity split within JV per press (unverified). Microsoft Abilene, Goodnight, Childress financing n/d.",transform=ax.transAxes,fontproperties=J,fontsize=7,color=GREY)
plt.tight_layout(); plt.savefig("ex3_capital.png",bbox_inches="tight"); plt.close()
print("chart3 ok")
