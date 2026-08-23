import sqlite3, csv, pathlib
DB = pathlib.Path("/home/claude/repo/outputs/reports/special/stranded-iron-20260727/global_rig_registry.db")
db = sqlite3.connect(DB); c = db.cursor()

c.executescript("""
DROP TABLE IF EXISTS segment_totals;
CREATE TABLE segment_totals (
  as_of TEXT, segment TEXT, metric TEXT, value INTEGER, source TEXT
);
""")

# Universe framing -- the distressed population, so the db states scale even where units are unnamed
ST = [
("2026-01","all","idle units tracked (RigLogix)",172,"Westwood RigLogix via Marine Link"),
("2026-01","all","idle units WITH future commitments",28,"Westwood RigLogix"),
("2026-01","jackup","stacked 5+ years",50,"Westwood RigLogix"),
("2026-01","semisub","stacked 5+ years",8,"Westwood RigLogix"),
("2026-01","drillship","stacked 5+ years",6,"Westwood RigLogix"),
("2026-01","jackup","idle 1+ year",74,"Westwood RigLogix"),
("2026-05","jackup","cold-stacked",54,"Westwood Offshore Energy Data Dashboard"),
("2026-05","jackup","marketed available",60,"Westwood dashboard"),
("2026-05","semisub","cold-stacked",7,"Westwood dashboard"),
("2026-05","semisub","marketed available",13,"Westwood dashboard"),
("2025-05","drillship","cold-stacked",5,"Westwood (retirement-candidate screen, stricter than Esgian count)"),
("2026-01","all","units retired during 2025",22,"Westwood RigLogix"),
("2026-01","all","2025 retirements: drillships",8,"Westwood RigLogix"),
("2026-01","all","2025 retirements: jackups",8,"Westwood RigLogix"),
("2026-01","all","2025 retirements: semisubs",6,"Westwood RigLogix"),
]
c.executemany("INSERT INTO segment_totals VALUES (?,?,?,?,?)", ST)

# Named units added: non-US-listed owners + segments previously excluded
R2 = [
("west_aquarius","West Aquarius","Seadrill","semisub","harsh-env semisub","n/d","n/d",2008,"cold_stacked","Norway","n/d",0,"Seadrill FSR May 2026: stacked"),
("west_phoenix","West Phoenix","Seadrill","semisub","harsh-env semisub","n/d","n/d",2008,"cold_stacked","Norway","n/d",0,"Seadrill FSR May 2026: stacked"),
("west_eclipse","West Eclipse","Seadrill","semisub","semisub","n/d","n/d",2011,"cold_stacked","Namibia","n/d",0,"Seadrill FSR May 2026: stacked"),
("platinum_explorer","Platinum Explorer","Eldorado (ex-Vantage)","drillship","DSME 12000","6th","DSME",2010,"idle_contract_lost","n/d","2026",0,"Lukoil Black Sea charter cancelled on sanctions; 3Q26 India start indicated"),
("dps1","Valaris DPS-1","Valaris","semisub","Samsung A1E","n/d","Samsung HI",2011,"retired","n/d","n/d",0,"retired from available fleet May 2026 per Westwood"),
("noble_resolve","Noble Resolve","Noble","semisub","n/d","n/d","n/d",2000,"sold","n/d","n/d",0,"sold to Ocean Oilfield Drilling for $64M cash, close 2Q26"),
("dvd","Deep Value Driller","Deep Value Driller AS","drillship","n/d","7th","n/d",2014,"idle","n/d","n/d",0,"Eldorado acquisition closing 3Q26; long-idle 7th gen"),
]
for r in R2:
    c.execute("INSERT OR REPLACE INTO rigs (rig_id,name,owner,rig_type,design,generation,shipyard,delivery_year,status,stack_location,stacked_since,never_worked,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", r)

# Material market correction: floater distress is CLOSING, jackup distress is not
c.execute("""INSERT INTO status_history VALUES
 ('gt2','2026-01','Noble redeployed 4 idle deepwater rigs; 92% of 24 marketed floaters contracted vs 75% prior FSR','Noble PR 2026-01-26')""")
c.execute("""INSERT INTO status_history VALUES
 ('ds11','2026-02','Transocean-Valaris all-stock merger announced ($5.8B); DOJ Second Request May 2026; close targeted 2H26','Westwood / Offshore Mag')""")

db.commit()
OUT = pathlib.Path("/mnt/user-data/outputs")
for t in ["rigs","power_plants","valuations","sources","segment_totals","status_history"]:
    cur = db.execute(f"SELECT * FROM {t}"); cols=[d[0] for d in cur.description]
    for dest in (OUT, DB.parent):
        with open(dest/f"{t}.csv","w",newline="") as f:
            w=csv.writer(f); w.writerow(cols); w.writerows(cur.fetchall())
    db.execute(f"SELECT * FROM {t}")

import shutil; shutil.copy(DB, OUT/"global_rig_registry.db")
print("rigs:", db.execute("select count(*) from rigs").fetchone()[0])
for row in db.execute("select rig_type, status, count(*) from rigs group by 1,2 order by 1,2"): print(row)
