import itertools

from nhconstants_common import *
from nhconstants_flags_raw import *
from nhconstants_flags import *
from nhconstants_atk import *

def check_formatting(card):
    for line in card:
        if len(line)==0:
            continue
        if line.find(",,")!=-1:
            return False
        if line.find(",|")!=-1:
            return False
        if line.find(", |")!=-1:
            return False
        if line.find(", ,")!=-1:
            return False
        if line.find("||")!=-1:
            return False
        if line.find("| ")!=-1:
            return False
        if line.find(":|")!=-1:
            return False        
        if line[-1]=="|":
            if line.find("Damage reduction")==0 or\
            line.find("Base")==0 or\
            line.find("Special")==0:
                continue#okay, this is normal finalizing |
            return False
    return True

def check_monster(mon):
    flags1=mon[rows["flags1"]].split("|")
    flags2=mon[rows["flags2"]].split("|")
    flags3=mon[rows["flags3"]].split("|")
    flags4=mon[rows["flags4"]].split("|")
    gen_flags=mon[rows["geno"]].split("|")
    if gen_flags[-1].isnumeric():
        gen_flags=gen_flags[:-1]#remove frequency
    mres=mon[rows["res"]].split("|")
    mh_flags=mon[rows["race"]].split("|")
    report=[]
    all_ok=True

    if mon[rows["symbol"]] not in monsym:
        report.append("Symbol absent:"+mon[rows["symbol"]])
        all_ok=False

    for f in flags1:
        if f not in flags1_str:
            report.append("Not found flag 1. Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False
    for f in flags2:
        if f not in flags2_str:
            report.append("Not found flag 2: Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False
    for f in flags3:
        if f not in flags3_str:
            report.append("Not found flag 3. Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False
    for f in flags4:
        if f not in flags4_str:
            report.append("Not found flag 4. Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False
    for f in gen_flags:
        if f not in geno_str:
            report.append("Not found gen flags. Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False
    for f in mh_flags:
        if f not in flags_cat_str:
            report.append("Not found MH flags. Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False
    for f in mres:
        if f not in resists_mon_str:
            report.append("Not found resists flags. Monster: "+mon[rows["name"]]+"; flag: "+f+"\n")
            all_ok=False

    for attack_n in itertools.chain(range(rows["attack1"],rows["attack6"]+1),range(rows["attack7"],rows["attack10"])):
        attack=mon[attack_n]
        attack=attack[5:]
        attack=attack[:-1]
        attack=attack.split(",")

        if mon[attack_n]==NO_ATTK or len(mon[attack_n])==0:
            break
        if attack[0].strip() not in at:
            all_ok=False
            report.append("Not found at. Monster: "+mon[rows["name"]]+"; at: "+attack[0].strip()+"\n")
        if attack[1].strip() not in ad:
            all_ok=False
            report.append("Not found ad. Monster: "+mon[rows["name"]]+"; ad: "+attack[1].strip()+"\n")

    if len(report)>0:
        report_file=open("errors.log","a",encoding="utf-8")
        report_file.write("=== FILE: "+ver_list[ver_idx]+"\n")
        report_file.writelines(report)
        report_file.close()
    return all_ok