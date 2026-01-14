import itertools
import os
import datetime
import curses as c


from nhconstants_common import *
from nhconstants_flags_raw import *
from nhconstants_flags import *
from nhconstants_atk import *
from make_card import *


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

def check_monster(mon,ver_name):
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
        report_file.write("=== FILE: "+ver_name+"\n")
        report_file.writelines(report)
        report_file.close()
    return all_ok

def run_tests(s,table,ver_name):
    os.makedirs("reports",exist_ok=True)
    s.erase()
    file_suffixes=["short","long","ext"]
    name_longest=0
    name_longest_name=""
    for f_length in range(3):
        failed_lines=0
        failed_monsters=0
        error_cards=0
        total=0
        failed_current_monster=False
        report=open("reports/report-"+ver_name+"-"+file_suffixes[f_length]+".txt","w",encoding="utf-8")
        report_summary=open("report.log","a",encoding="utf-8")
        report_summary.write("==========\n")
        report_summary.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")+"\n")
        report_summary.write("File: "+ver_name+"\n")
        for mon in table.keys():
            total+=1
            if len(mon)>20:
                report_summary.write(f"long name({len(mon)}):{mon}\n")
            if len(mon)>name_longest:
                name_longest=len(mon)
                name_longest_name=mon
            if check_monster(table[mon],ver_name)==False:
                report.write("Error making card: "+mon+"\n")
                error_cards+=1
                continue
            test=make_card(table[mon],format_length=f_length)
            test=test.split("\n")
            if check_formatting(test)==False:
                report.write("Error formatting card: "+mon+"\n")
                error_cards+=1
            if len(test)>c.LINES-2:
                report.write(f"MANY LINES({len(test)}):{mon}\n")
                report.write(ln[:test_len]+"\n===\n")
            for i in range(len(test)):
                ln=test[i]
                if len(ln)>0 and (ln[0]=="#" or ln[0]=="$"):
                    ln=ln[1:]
                len_test=len(ln)
                if f_length!=2:
                    if i==0:
                        test_len=SCR_WIDTH-1
                    else:
                        test_len=SCR_WIDTH
                if f_length==2:
                    if i in [0,1,2]:
                        test_len=SCR_WIDTH-3
                    else:
                        test_len=SCR_WIDTH
                if len_test>test_len:
                    failed_lines+=1
                    failed_current_monster=True
                    report.write(f"LONG({len_test}):{mon}|[{ln[test_len:]}]\n")
                    report.write(ln[:test_len]+"\n===\n")

            if failed_current_monster==True:
                failed_monsters+=1
                failed_current_monster=False
        report.close()
        result_str="DONE-"+file_suffixes[f_length].upper()+f". Failed: {failed_monsters} of {total}, long lines: {failed_lines}, error:{error_cards}\n"
        report_summary.write(result_str)
        report_summary.write(f"longest name: {name_longest}, {name_longest_name}\n")
        report_summary.close()
        s.addstr(result_str)
    #explanation testing now is a separate process
    failed_lines=0
    failed_monsters=0
    error_cards=0
    total=0
    failed_current_monster=False
    report=open("reports/report-"+ver_name+"-"+"EXPL"+".txt","w",encoding="utf-8")
    report_summary=open("report.log","a",encoding="utf-8")
    report_summary.write("==========\n")
    report_summary.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")+"\n")
    report_summary.write("File: "+ver_name+"\n")
    for mon in table.keys():
        total+=1
        test_e="".join(card_explanation(table[mon]))
        if test_e.startswith("ERROR!"):
            failed_current_monster=True
            report.write(f"EXPLANATION DICT FAIL:{mon}: {test_e}\n")
            report.write(ln[:test_len]+"\n===\n")
        if test_e.find("DUMMY")!=-1:
            failed_current_monster=True
            report.write(f"EXPLANATION DUMMY:{mon}\n")
            report.write(ln[:test_len]+"\n===\n")
        test_e=test_e.split("\n")
        if len(test_e)>c.LINES-2:
            failed_current_monster=True
            report.write(f"MANY LINES EXPLANATION ({len(test_e)}):{mon}\n")
            report.write(ln[:test_len]+"\n===\n")
            
        if failed_current_monster==True:
            failed_monsters+=1
            failed_current_monster=False
    report.close()
    result_str="DONE-"+"EXPL"+f". Failed: {failed_monsters} of {total}, long lines: {failed_lines}, error:{error_cards}\n"
    report_summary.write(result_str)
    report_summary.write(f"longest name: {name_longest}, {name_longest_name}\n")
    report_summary.close()
    s.addstr(result_str)