import csv
from math import floor
from operator import itemgetter
import curses as c
import os
import itertools

from nhconstants import *

colors_table={
    0:c.COLOR_WHITE,#it must be COLOR_BLACK, but certain monsters are marked as black, but they are actually white (gray)
    1:c.COLOR_RED,
    2:c.COLOR_GREEN,
    3:c.COLOR_YELLOW,
    4:c.COLOR_BLUE,
    5:c.COLOR_MAGENTA,
    6:c.COLOR_CYAN,
    7:c.COLOR_WHITE
}

bold=0




cur_len_res=66
cur_len_con=44
cur_len_atk=94

max_len_res=0
max_len_con=0
max_len_atk=0

table=dict()
table_temp=[]
disable_sorting=False
data_folder="data/"
ver_list=[]
ver_idx=-1

MAX_SEARCH=50

def max_val_len(d:dict())->int:
    max=0
    for k in d.keys():
        l=len(d[k])
        if l>max:
            max=l
    return max

def make_ver_list():
    global ver_list,ver_idx
    ver_list=os.listdir(data_folder)
    if len(ver_list)==0:
        print("No data files found. Exiting...")
        exit(1)
    ver_idx=0

def get_ver()->str:
    return ver_list[ver_idx].split(".")[0]

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
            report.append("Not found ad. Monster: "+mon[rows["name"]]+"; at: "+attack[1].strip()+"\n")

    if len(report)>0:
        report_file=open("errors.log","a",encoding="utf-8")
        report_file.write("=== FILE: "+ver_list[ver_idx]+"\n")
        report_file.writelines(report)
        report_file.close()
    return all_ok





def read_monsters(file):
    global table,table_temp
    global disable_sorting
    table=dict()
    table_temp=[]
    monfile=open(data_folder+file,"r")
    reader=csv.reader(monfile)
    for x, mon in enumerate(reader):
        if x==0:#skip header
            continue
        mon_copy=None
        if len(mon)<len(rows):
            mon.extend([""]*(len(rows)-len(mon)))
        if len(mon[rows["namef"]])>0 and len(mon[rows["namef"]])>0:#two-gender monster
            mon_copy=mon.copy()
            mon_copy[rows["flags2"]]+="|M2_NEUTER"
            table[mon[rows["name"]]]=mon_copy
        else:
            table[mon[rows["name"]]]=mon
        if len(mon[rows["namef"]])>0:
            mon_copy=mon.copy()
            mon_copy[rows["flags2"]]+="|M2_FEMALE"
            table[mon[rows["namef"]]]=mon_copy
        if len(mon[rows["namem"]])>0:
            mon_copy=mon.copy()
            mon_copy[rows["flags2"]]+="|M2_MALE"
            table[mon[rows["namem"]]]=mon_copy

BK=20
INV=21
BK_CARD=22
INV_CARD=23
SEPARATOR=24
SCR_WIDTH=80
LIST_WIDTH=SCR_WIDTH-7

def out_input(s,in_str):

    s.clear()
    s.addstr(0,0,">"+in_str,c.color_pair(BK))
    s.chgat(-1,c.color_pair(BK))
    s.clrtoeol()
    s.refresh()

def out_results(s,results,sel,skip):
    selected_appeared=False
    s.move(1,0)
    if len(results)==0:
        s.addstr("(none)")
        selected_appeared=True#actually false, but we don't want to check selection in empty results
    start_ch=0
    cur=0
    for mon in results:
        if cur<skip:
            cur+=1
            continue
        if(start_ch+len(mon)>LIST_WIDTH):
            s.addstr(f"(+{len(results)-cur})")
            break
        start_ch+=len(mon)+1#for "|"
        if cur-skip==sel:
            s.addstr(mon,c.color_pair(INV))
            selected_appeared=True
        else:
            s.addstr(mon,c.color_pair(BK))
        s.addstr("|")
        cur+=1
    s.chgat(c.color_pair(BK))
    s.refresh()
    return (cur-skip,selected_appeared)

def move_to_in(s,in_str):
    s.move(0,1+len(in_str))
    c.curs_set(1)

def insert (source_str, insert_str, pos):
    return source_str[:pos]+insert_str+source_str[pos:]

def split_line(line:str,mid:int)->str:
    if len(line)<mid:
        return line
    mid=int(len(line)/2+.5)
    pos2=line.find(",",mid)
    pos1=line.rfind(",",0,mid)
    if(pos1==-1 and pos2 ==-1):
        return line
    insert_before=insert(line,"\n",pos1+2)
    insert_after=insert(line,"\n",pos2+2)
    if(pos1==-1):
        return insert_after
    if(pos2==-1):
        return insert_before
    if(pos2-mid<mid-pos1):
        return insert_after
    return insert_before

def out_symbol(s,mon):
    color=colors_table[int(mon[rows["color"]])&0x7]
    if bold==1:
        if int(mon[rows["color"]])>8:
            s.addstr(monsym[mon[rows["symbol"]]],c.color_pair(color+1)|c.A_BOLD)
        else:
            s.addstr(monsym[mon[rows["symbol"]]],c.color_pair(color+1))
    if bold==0:
        if int(mon[rows["color"]])==0:
            s.addstr(monsym[mon[rows["symbol"]]],c.color_pair(9))
        if int(mon[rows["color"]])>8:
            s.addstr(monsym[mon[rows["symbol"]]],c.color_pair(color+9))
        if int(mon[rows["color"]])<=8 and int(mon[rows["color"]])>0:
            s.addstr(monsym[mon[rows["symbol"]]],c.color_pair(color+1))


NO_ATTK="NO_ATTK"

def card_basic_info(mon,format_length):
    #Difficulty
    out_line=["#"]
    if format_length!=2:
        out_line.append("|")
    out_line.append(f"Dif:{mon[rows['difficulty']]:2}")
    out_line.append(f"|Lv:{mon[rows['level']]:2}")
    out_line.append(f"|Exp:{mon[rows['exp']]:4}")

    #Speed
    out_line.append(f"|Spd:{mon[rows['speed']]:2}")
    #AC
    out_line.append(f"|AC:{mon[rows['ac']]:3}")
    #MR
    out_line.append(f"|MR:{mon[rows['mr']]:3}")
    #Size
    out_line.append(f"|Sz:{szs[mon[rows['size']]]:8}")
    #Align
    al=int(mon[rows['alignment']])
    out_line.append(f"|Alignment:{al}")
    if 0:
        out_line.append("\n")
    else:
        if al==0:
            out_line.append(" (Neu)\n")
        if al>0:
            out_line.append(" (Law)\n")
        if al<0 and al!=-128:
            out_line.append(" (Cha)\n")
        if al==-128:
            out_line.append(" (Una)\n")
    
    return out_line

def card_gen(mon,format_length):
    flags1=mon[rows["flags1"]].split("|")
    flags2=mon[rows["flags2"]].split("|")
    flags3=mon[rows["flags3"]].split("|")
    gen_flags=mon[rows["geno"]].split("|")
    out_line=["#"]

    if format_length>0:
        for x in range(len(gen_flags)):
            gen_flags[x]=gen_flags[x].strip()
        freq_s=""
        freq=gen_flags[-1]
        freq_s+=freq+"["
        freq_s+=freq_str[freq]+"], "
        if "G_UNIQ" in gen_flags:
            freq_s+="Unique, "
        if "G_SGROUP" in gen_flags:
            freq_s+="Small Groups, "
        if "G_LGROUP" in gen_flags:
            freq_s+="Large Groups, "
        if "G_NOHELL" in gen_flags:
            freq_s+="No Gehennom, "
        if "G_HELL" in gen_flags and "G_SHEOL" not in gen_flags:
            freq_s+="Gehennom only, "
        if "G_NOSHEOL" in gen_flags:
            freq_s+="No Sheol, "
        if "G_SHEOL" in gen_flags and "G_HELL" not in gen_flags:
            freq_s+="Sheol only, "
        if "G_SHEOL" in gen_flags and "G_HELL" in gen_flags:
            freq_s+="Gehennom and Sheol only, "
        if "G_NOHELL" not in gen_flags and "G_HELL" not in gen_flags and "G_NOSHEOL" not in gen_flags and "G_SHEOL" not in gen_flags:
            freq_s+="Everywhere, "
        if freq_s.endswith(", "):
            freq_s=freq_s[:-2]
        if format_length==2:
            freq_s="Generation:"+freq_s+"\n"
        else:
            freq_s="Generation:"+freq_s+"|"
        out_line.append(freq_s)
        if "G_GENO" in gen_flags:
            g="Genocide: "
            found=False
            for k in genocide_f.keys():
                if k in gen_flags:
                    found=True
                    if format_length<2:
                        g+=genocide_f[k]+"|"
                    else:
                        g+=genocide_f_ext[k]+"|"
                    break
            if not found:
                g+="Yes |"
            out_line.append(g)
        else:
            out_line.append(f"Genocide: No  |")
        if "M2_NOPOLY" in flags2:
            out_line.append(f"Poly to: No ")
        else:
            out_line.append(f"Poly to: Yes")
    out_line.append("\n")

    return out_line

def card_atk(mon,format_length):
    global max_len_atk,max_len_res,max_len_con
    out_line=["$"]
    #Attacks
    attacks=""
    interrupted=0
    for attack_n in itertools.chain(range(rows["attack1"],rows["attack6"]+1),range(rows["attack7"],rows["attack10"])):
        attack=mon[attack_n]
        attack_s=""

        if mon[attack_n]==NO_ATTK or len(mon[attack_n])==0:
            attacks=attacks[:-2]
            interrupted=1
            break

        attack=attack[5:]
        attack=attack[:-1]
        attack=attack.split(",")
        if(attack[2].strip()=="0" and attack[3].strip()=="0"):
            attack_s+=at[attack[0].strip()]+ad[attack[1].strip()]+", "#0d0 смотреть бесполезно
        else:
            attack_s+=at[attack[0].strip()]+" "+attack[2].strip()+"d"+attack[3].strip()+ad[attack[1].strip()]+", "
        attacks+=attack_s
    
    if interrupted==0:#используются все шесть атак, значит надо убрать последнюю запятую
        attacks=attacks[:-2]
    if len(attacks)>max_len_atk:
        max_len_atk=len(attacks)
    
    attacks_list=attacks.split(",")
    for x in range(len(attacks_list)):
        attacks_list[x]=attacks_list[x].strip()
    attacks_list_condensed=[]
    cnt=0
    if format_length!=2:
        attacks_list.append(NO_ATTK)
        for x in range(len(attacks_list)):

            if x>0:
                if attacks_list[x]==attacks_list[x-1]:
                    cnt+=1
                else:
                    if cnt==0:
                        attacks_list_condensed.append(attacks_list[x-1])
                    else:
                        attacks_list_condensed.append(attacks_list[x-1]+f" (x{cnt+1})")
                        cnt=0
        attacks_condensed=", ".join(attacks_list_condensed)
        out_line.append("Atk:"+attacks_condensed+"\n")
    else:
        attacks_list="Attacks:"+", ".join(attacks_list)+"\n"
        out_line.append(split_line(attacks_list,SCR_WIDTH-3))

    return out_line

def card_resistances(mon,format_length):
    #Resistances
    out_line=["#"]
    ress=""
    ress_list=mon[rows["res"]].split("|")
    for res in resists_mon.keys():
        if res in ress_list:
            ress+=resists_mon[res]+", "
    for res in mon[rows["flags4"]].split("|"):
        res=res.strip()
        if len(res)==0:
            break
        ress+=resists_mon[res.strip()]+", "


    for flag in mon[rows["flags1"]].split("|"):
        flag=flag.strip()
        if(flag=="M1_SEE_INVIS"):
            ress+="SeeInvis, "
    if ress.endswith(", "):
        ress=ress[:-2]
    if len(ress)==0:
        ress="Resistances:None\n"
    else:
        ress="Resistances:"+ress+"\n"
    out_line.append(ress)

    return out_line

def card_eat(mon,format_length):
    flags1=mon[rows["flags1"]].split("|")
    flags2=mon[rows["flags2"]].split("|")
    flags3=mon[rows["flags3"]].split("|")
    gen_flags=mon[rows["geno"]].split("|")
    out_line=["$"]
    #Conveyed
    ress_conv=""
    resn=0
    nocorpse=False
    for geno in mon[rows["geno"]].split("|"):
        geno=geno.strip()
        if(len(geno)==0):
            break
        if geno=="G_NOCORPSE":
            nocorpse=True

    prefix="Conveyed:"
    if mon[rows["name"]]=="Chromatic Dragon":
        prefix=prefix#degub; Chromatic Dragon is most difficult monster in terms of formatting
    ress_final_line=""
    if nocorpse:
        ress_final_line+="("
    ress=mon[rows['prob']].split('|')
    ress_n=len(ress)
    if "M2_GIANT" in flags2:
        ress_n+=1
    if len(ress[0])>0:
        for r in ress:
            r_name,r_prob=r.split("=")
            if r_name in resists_conv.keys():
                ress_final_line+=resists_conv[r_name]
            else:
                ress_final_line+=r_name
            prob_normalized=int(int(r_prob)/ress_n)
            if format_length==2:
                ress_final_line+="("+str(prob_normalized)+"%), "
            else:
                ress_final_line+=", "
    if "M2_GIANT" in flags2:
        if ress_n==1:
            prob=int(50)
        else:
            prob=int(100/ress_n)
        ress_final_line+="Gain St"+(f"({prob}%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["newt"]:
        ress_final_line+="Pw"+("(66% restore, 22% +1 MAX), " if format_length==2 else ", ")
    attacks=""
    for attack_n in range(rows["attack1"],rows["attack6"]+1):
        if mon[attack_n]=="NO_ATTK":
            attacks=attacks[:-2]
            interrupted=1
            break
        attack=mon[attack_n]
        attack=attack[5:]
        attack=attack[:-1]
        attack=attack.split(",")
        if attack[0]=="AT_MAGC":
            ress_final_line+="Pw"+("(66% restore, 22% +1), " if format_length==2 else ", ")
            break
    if mon[rows["name"]] in ["wraith"]:
        ress_final_line+="Gain level"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["nurse"]:
        ress_final_line+="Heal"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["stalker"]:
        ress_final_line+="Invisibility"+("(100%), " if format_length==2 else ", ")+"See invisible"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["quantum mechanic"]:
        ress_final_line+="Toggle speed"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["lizard"]:
        ress_final_line+="Reduce conf/stun"+("(100%), " if format_length==2 else ", ")+"Stop petrification"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["chameleon","doppelganger","sandestin","genetic engineer"]:
        ress_final_line+="Polymorph"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["disenchanter"]:
        ress_final_line+="Steal intrinsic"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["displacer beast"]:
        ress_final_line+="Displacement (temp)"+("(100%), " if format_length==2 else ", ")
    if mon[rows["name"]] in ["mind flayer","master mind flayer"]:
        ress_final_line+="Gain In"+("(50%), " if format_length==2 else ", ")
    ress_final_line=ress_final_line[:-2]
    if nocorpse:
        ress_final_line+=")"
    if len(ress_final_line)<=2:#"()" with no resistances and no corpse
        if nocorpse:
            ress_final_line=prefix+"No corpse"
        else:
            ress_final_line=prefix+"None"
    else:
        ress_final_line=prefix+ress_final_line

    if format_length==2:
        ress_final_line=split_line(ress_final_line,SCR_WIDTH)
    
    if len(ress_final_line)>SCR_WIDTH and format_length!=2:
        ress_final_line=ress_final_line.replace(", ",",")#remove spaces for shorter line
    out_line.append(ress_final_line+"\n")


    #Wt
    out_line.append(f"Weight:{mon[rows['weight']]:4}")
    #Nutrition
    out_line.append(f"|Nutrition:{mon[rows['nutrition']]:4}")

    #вредные эффекты при еде
    #Eat Danger
    bad=""
    badn=0
    for flag in mon[rows["flags1"]].split("|"):
        flag=flag.strip()
        if flag=="M1_POIS":
            bad+="POISON, "
        if flag=="M1_ACID":
            bad+="ACID, "

    for flag in mon[rows["flags2"]].split("|"):
        flag=flag.strip()
        if flag=="M2_HUMAN":
            bad+="human, "
        if flag=="M2_DWARF":
            bad+="dwarf, "
        #if flag=="M2_ORC":#орки едят орков -- им разрешён каннибализм
        #    bad+="orc\n"
        if flag=="M2_ELF":
            bad+="elf, "
        if flag=="M2_GNOME":
            bad+="gnome, "

    attacks=""
    for attack_n in range(rows["attack1"],rows["attack6"]+1):
        if mon[attack_n]=="NO_ATTK":
            attacks=attacks[:-2]
            interrupted=1
            break
        attack=mon[attack_n]
        attack=attack[5:]
        attack=attack[:-1]
        attack=attack.split(",")
        if attack[1]=="AD_STUN" or mon[rows["name"]]=="violet fungus":
            bad+="HALLU, "
            break


    if mon[rows["name"]] in ["kitten","housecat","large cat","little dog","dog","large dog"]:
        bad+="Aggravate, "
    if mon[rows["name"]] in ["cockatrice","chickatrice","Medusa"]:
        bad+="PETRIFY, "
    if mon[rows["name"]] in ["Death","Pestilence","Famine"]:
        bad+="FATAL, "
    if mon[rows["name"]] in ["green slime"]:
        bad+="SLIME, "
    if mon[rows["name"]] in ["stalker","yellow light","giant bat","bat"]:
        bad+="Stun, "
    if mon[rows["name"]] in ["small mimic","large mimic","giant mimic"]:
        bad+="Mimic, "
    if mon[rows["name"]] in ["wererat","werejackal","werewolf"]:
        bad+="Lycantropy, "

    bad=bad[:-2]
    if len(bad)==0:
        out_line.append("|Eat danger: Safe\n")
    else:
        out_line.append("|Eat danger: "+bad+"\n")

    return out_line

def card_flags(mon,format_length):
    out_line=["#"]
    flags1=mon[rows["flags1"]].split("|")
    flags2=mon[rows["flags2"]].split("|")
    flags3=mon[rows["flags3"]].split("|")
    flags4=mon[rows["flags4"]].split("|")
    mres=mon[rows["res"]].split("|")
    mh_flags=mon[rows["race"]].split("|")
    gen_flags=mon[rows["geno"]].split("|")
    if format_length>0:#flags
        flags_all=""
        for f in flags1_str.keys():
            if f in flags1:
                flags_all+=flags1_str[f]+", "
        for f in flags2_str.keys():
            if f in flags2:
                flags_all+=flags2_str[f]+", "
        for f in flags3_str.keys():
            if f in flags3:
                flags_all+=flags3_str[f]+", "
        flags_all=flags_all[:-2]+"\n"
        #out_line.append(flags_all)
        #for debug

    #FLAGS PARSING

    #LINE1. CATEGORY. GENDER. DIET
    if format_length>0:
        line=""
        flag_str=""
        cat_len=max_val_len(flags_cat_str)

        prefix="Catetory:"
        cat_len=max_val_len(flags_cat_str)
        cat_list=[]
        for flag in flags_cat_str.keys():
            if flag in flags2:
                cat_list.append(flags_cat_str[flag])
            if flag in mh_flags:
                cat_list.append(flags_cat_str[flag])
        if len(cat_list)==0:
            flag_str=f"{'Ordinary':{cat_len}}|"
        else:
            for c in cat_list:
                flag_str+=c+", "
            flag_str=flag_str[:-2]
            flag_str=f"{flag_str:{cat_len}}|"

        line+=prefix+flag_str

        prefix="Gender:"
        cat_len=max_val_len(flags_gender)
        found=False
        for flag in flags_gender.keys():
            if flag in flags2:
                found=True
                flag_str=f"{flags_gender[flag]:{cat_len}}|"
        if found==False:
            flag_str=f"{'None':{cat_len}}|"
        line+=prefix+flag_str

        prefix="Diet:"
        cat_len=max_val_len(flags_diet)
        found=False
        if "M1_CARNIVORE" in flags1 and "M1_HERBIVORE" in flags1:
            found=True
            flag_str=f"{'Omnivore':{cat_len}}|"
        else:
            for flag in flags_diet.keys():
                if flag in flags1:
                    found=True
                    flag_str=f"{flags_diet[flag]:{cat_len}}|"
        if found==False:
            flag_str=f"{'Inediate':{cat_len}}|"
        line+=prefix+flag_str
        prefix="Infravisible: "
        if "M3_INFRAVISIBLE" in flags3:
            flag_str="Yes"
        else:
            flag_str="No"
        line+=prefix+flag_str+"\n"

        out_line.append(line)
        line=""
    #LINE 2. BODY PLAN
        flag_str=""
        prefix="Body type:"
        cat_len=max_val_len(flags_body)
        found=False
        for flag in flags_body.keys():
            if flag in flags1 or flag in flags3:
                found=True
                flag_str=f"{flags_body[flag]:{cat_len}}|"
        if found==False:
            flag_str=f"{'Unusual':{cat_len}}|"

        line+=prefix+flag_str

        prefix="Body parts:"
        flag_str=""
        no_limbs=False
        if "M1_NOLIMBS" in flags_parts_no.keys() and "M1_NOHANDS" not in flags_parts_no.keys():
            no_limbs=no_limbs
        for flag in flags_parts_no.keys():
            if flag in flags1:
                if flag=="M1_NOLIMBS":
                    no_limbs=True
                if flag=="M1_NOHANDS" and no_limbs:
                    continue
                flag_str+=flags_parts_no[flag]+", "
            else:
                flag_str+=flags_parts_have[flag]+", "
        flag_str=flag_str[:-2]
        line+=prefix+flag_str+"\n"
        out_line.append(line)
        line=""

        #LINE 3. BEHAVIOR: DEMEANOR, MOVEMENT, WANTS, PICK
        prefix="Demeanor:"
        found=False
        flag_str=""
        for flag in flags_demeanor.keys():
            if flag in flags2 or flag in flags3:
                found=True
                if format_length==2:
                    flag_str+=flags_demeanor_ext[flag]+", "
                else:
                    flag_str+=flags_demeanor[flag]+", "
        if found==False:
            flag_str="None, "
        flag_str=flag_str[:-2]
        if format_length==2:
            flag_str+="\n"
        else:
            flag_str+="|"
        line+=prefix+flag_str

        prefix="Move:"
        flag_str=""
        found=False
        for flag in flags_move.keys():
            if flag in flags1 or flag in flags3:
                if flag=="M1_NEEDPICK":
                    flag_str=flag_str[:-2]+" "#remove "," from "Tunnel"
                flag_str+=flags_move[flag]+", "
        for flag in flags_move_type.keys():
            if flag in flags1:
                found=True
            if flag in flags3:
                found=True
        if found==False and int(mon[rows["speed"]])>0:
            flag_str="Walk, "+flag_str
        if found==False and int(mon[rows["speed"]])==0:
            flag_str="Sessile, "+flag_str
        flag_str=flag_str[:-2]+"|"
        line+=prefix+flag_str

        prefix="Picks:"
        flag_str=""
        found=False
        for flag in flags_pick.keys():
            if flag in flags1 or flag in flags2:
                found=True
                flag_str+=flags_pick[flag]+", "
        if found==False:
            if "M1_NOTAKE" in flags1:
                flag_str+="Can't, "
            else:
                flag_str+="None, "
        flag_str=flag_str[:-2]+"\n"
        line+=prefix+flag_str
        if len(line)>SCR_WIDTH and format_length!=2:
            line=line.replace(", ",",")#remove spaces for shorter line

        prefix="Wants:"
        flag_str=""
        found=False
        for flag in flags_covet.keys():
            if flag in flags3:
                found=True
                flag_str+=flags_covet[flag]+", "
        if found==False:
            flag_str="None, "
        flag_str=flag_str[:-2]
        line+=prefix+flag_str+"\n"

        out_line.append(line)
        line=""

        prefix="Perks:"
        flag_str=""
        found=False
        for flag in flags_perks.keys():
            if flag in flags1 or flag in flags2 or flag in flags3 or flag in mres:
                found=True
                flag_str+=flags_perks[flag]+", "
        if found==False:
            flag_str="None, "
        flag_str=flag_str[:-2]
        line+=prefix+flag_str+"\n"

        out_line.append(line)
        line=""

    return out_line


def make_card(mon,format_length=0):
    global max_len_atk,max_len_res,max_len_con
    out_line=[]
    out_line.extend(card_basic_info(mon,format_length))
    out_line.extend(card_gen(mon,format_length))
    out_line.extend(card_atk(mon,format_length))
    out_line.extend(card_resistances(mon,format_length))
    out_line.extend(card_eat(mon,format_length))
    out_line.extend(card_flags(mon,format_length))

   
    #Preparing string
    out_line_s="".join(out_line)
    return out_line_s

def show_hello_msg(card_win):
    hello_msg=["=== Nethack external Pokedex ===",
    "Enter monster name to see its properties. Keys:",
    "LEFT, RIGHT: Scroll search results",
    "UP, DOWN: Change output format",
    "ESC: Clear search; F10: Exit"]
    card_win.chgat(-1,c.color_pair(BK_CARD))
    card_win.addstr(0,int((SCR_WIDTH-len(hello_msg[0]))/2),hello_msg[0],c.color_pair(INV_CARD)|c.A_BOLD)
    for i in range(len(hello_msg)):
        if i==0:
            continue
        card_win.addstr(i,15,hello_msg[i])
    card_win.refresh()

def show_not_found_msg(card_win,mon_name):
    msg=[f"'{mon_name}' does not extist in current version.","Try another search or switch version."]
    card_win.chgat(-1,c.color_pair(BK_CARD))
    card_win.addstr(0,int((SCR_WIDTH-len(msg[0]))/2),msg[0],c.color_pair(INV_CARD)|c.A_BOLD)
    card_win.addstr(1,int((SCR_WIDTH-len(msg[1]))/2),msg[1],c.color_pair(BK_CARD)|c.A_BOLD)
    card_win.refresh()

def main(s):
    global bold
    global ver_idx
    if c.COLORS<16:
        bold=1
    else:
        bold=0
    c.raw()
    c.mousemask(-1)
    c.mouseinterval(0)
    c.curs_set(1)
    s.clear()
    c.init_pair(BK,c.COLOR_WHITE,c.COLOR_BLUE)
    c.init_pair(INV,c.COLOR_BLUE,c.COLOR_WHITE)
    c.init_pair(BK_CARD,c.COLOR_GREEN,c.COLOR_BLACK)
    c.init_pair(INV_CARD,c.COLOR_CYAN,c.COLOR_BLACK)
    if bold==1:
        for x in range(1,9):
            c.init_pair(x,x-1,c.COLOR_BLACK)
    else:
        for x in range(1,17):
            c.init_pair(x,x-1,c.COLOR_BLACK)
    c.update_lines_cols()
    lines=c.LINES
    cols=c.COLS
    s.bkgd(' ',c.color_pair(BK))
    s.clear()
    s.refresh()
    colors_n=c.COLORS
    for x in range(1,17):
        s.addstr(f"TEST:{x-1} ",c.color_pair(x))
    s.refresh()
    in_str=""
    sel=0
    skip=0
    max_sel=0
    tries=0
    format_length=0
    reloaded=False
    search_win=c.newwin(2,c.COLS,0,0)
    search_win.keypad(1)
    search_win.bkgd(' ',c.color_pair(BK))
    search_win.clear()
    search_win.refresh()  
    card_win=c.newwin(c.LINES-2,c.COLS,2,0)
    card_win.bkgd(' ',c.color_pair(BK_CARD))
    card_win.clear()
    card_win.refresh()
    not_found_after_reload=False
    while True:
        results=[]
        not_found_after_reload=False
        for mon in table.keys():
            if mon.lower().find(in_str.lower())!=-1:
                results.append(mon)
        if reloaded:
            if mon_name not in results:
                not_found_after_reload=True
            else:
                idx=results.index(mon_name)
                skip=idx
                sel=0
        else:
            if sel+skip<len(results):
                mon_name=results[sel+skip]
            else:
                mon_name=""

        card_win.clear()
        card_win.refresh()
        if len(results)>0 and len(in_str)>0 and not_found_after_reload==False:
            card_win.chgat(-1,c.color_pair(BK_CARD))
            if format_length!=2:
                card_win.move(0,0)
                out_symbol(card_win,table[results[sel+skip]])
            else:#extended
                card_win.move(0,0)
                card_win.addch(c.ACS_ULCORNER,c.color_pair(SEPARATOR))
                card_win.addch(c.ACS_HLINE,c.color_pair(SEPARATOR))
                card_win.addch(c.ACS_URCORNER,c.color_pair(SEPARATOR))
                card_win.move(1,0)
                card_win.addch(c.ACS_VLINE,c.color_pair(SEPARATOR))
                out_symbol(card_win,table[mon_name])
                card_win.addch(c.ACS_VLINE,c.color_pair(SEPARATOR))
                card_win.move(2,0)
                card_win.addch(c.ACS_LLCORNER,c.color_pair(SEPARATOR))
                card_win.addch(c.ACS_HLINE,c.color_pair(SEPARATOR))
                card_win.addch(c.ACS_LRCORNER,c.color_pair(SEPARATOR))
            if check_monster(table[mon_name])==True:
                card=make_card(table[mon_name],format_length)
            else:
                card="Eror making card: "+mon_name
            card=card.split("\n")
            cur_pair=BK_CARD
            line_n=0
            for i in range(len(card)):
                line=card[i]
                if len(line)==0:
                    continue
                color=line[0]
                remainder=False
                if i!=0 and (card[i-1].strip()[-1])==",":
                    remainder=True
                if color=="#" or color=="$":
                    line=line[1:]

                if color=="#":
                    cur_pair=BK_CARD
                if color=="$":
                    cur_pair=INV_CARD
                if len(line.strip())==0:#only special character
                    continue
                if remainder==False:
                    attrib=c.A_BOLD
                else:
                    attrib=0
                if len(line)>=SCR_WIDTH:
                    line=line[:SCR_WIDTH-1]+"!"
                for i in range(len(line)):
                    if format_length!=2:
                        if line_n==0:
                            pos=i+1
                        else:
                            pos=i
                    if format_length==2:
                        if line_n in [0,1,2]:
                            pos=i+3
                        else:
                            pos=i
                    if line[i]=="|":
                        card_win.addstr(line_n,pos,line[i],c.color_pair(SEPARATOR)|c.A_BOLD)
                    else:
                        card_win.addstr(line_n,pos,line[i],c.color_pair(cur_pair)|attrib)
                    if line[i]==":":
                        attrib=0
                    if line[i]=="|":
                        attrib=c.A_BOLD
                line_n+=1
                    
                #card_win.addstr(line_n,1 if line_n==0 else 0,line,c.color_pair(cur_pair))
                card_win.chgat(-1,c.color_pair(cur_pair))
            card_win.refresh()
        else:
            if not_found_after_reload:
                show_not_found_msg(card_win,mon_name)
            else:
                show_hello_msg(card_win)

        out_input(search_win,in_str)
        if len(in_str)>0:
            (max_sel,appeared)=out_results(search_win,results,sel,skip)
            if appeared==False:#next selected monster too long
                skip+=1
                sel-=1
                tries+=1
                if tries<5:
                    continue
                else:
                    tries=tries
        tries=0
        out_mode=""
        if format_length==0:
            out_mode="Format:mini"
        if format_length==1:
            out_mode="Format:full"
        if format_length==2:
            out_mode="Format:ext"
        search_win.addstr(0,65,out_mode)
        search_win.addstr(0,55,"Ver:"+get_ver())
        move_to_in(search_win,in_str)
        search_win.refresh()
        ch=search_win.getch()
        key=c.keyname(ch).decode("utf-8")
        if ch==27:#ESC
            search_win.nodelay(True)
            while search_win.getch()!=-1:
                pass
            search_win.nodelay(False)
            in_str=""
            reloaded=False
        if key=="KEY_F(10)":
            break
        if key=="KEY_F(1)":
            s.clear()
            file_suffixes=["short","long","ext"]
            for f_length in range(3):
                failed_lines=0
                failed_monsters=0
                total=0
                failed_current_monster=False
                report=open("report-"+file_suffixes[f_length]+".txt","w",encoding="utf-8")
                for mon in table.keys():
                    total+=1
                    if check_monster(table[mon])==False:
                        report.write("Error making card: "+mon)
                        continue
                    test=make_card(table[mon],format_length=f_length)
                    test=test.split("\n")
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
                s.addstr("DONE-"+file_suffixes[f_length].upper()+f". Failed: {failed_monsters} of {total}, long lines: {failed_lines}\n")
            for x in range(1,17):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x))
            s.addstr("\n")        
            for x in range(1,9):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x)|c.A_BOLD)
            s.addstr("\n")        
            for x in range(1,9):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x)|c.A_STANDOUT)
            s.addstr("\n")        
            for x in range(1,9):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x)|c.A_BLINK)
            s.addstr("\n")        
            for x in range(1,9):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x)|c.A_UNDERLINE)
            s.addstr("\n")        
            for x in range(1,9):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x)|c.A_ITALIC)
            s.addstr("\n")        
            for x in range(1,9):
                s.addstr(f"TEST:{x-1} ",c.color_pair(x)|c.A_DIM)
            s.refresh()
            for i in range(8):
                c.init_pair(i+30,c.COLOR_WHITE,i)
                c.init_pair(i+38,c.COLOR_BLACK,i)
            for i in range(8):
                s.addstr(" TEST ",c.color_pair(i+30))
                s.addstr(" TEST ",c.color_pair(i+38))
                s.addstr("\n")
            
            s.refresh()
            s.getch()

        if len(key)==1:
            if len(in_str)<MAX_SEARCH:
                in_str+=key
                sel=0
                skip=0
                reloaded=False
            else:
                s.addch(0x7)
        if key=="KEY_RIGHT":
            sel+=1
            if sel>max_sel-1:
                sel=max_sel-1
                if sel+skip<len(results)-1:
                    skip+=1
            reloaded=False
        if key=="KEY_LEFT":
            sel-=1
            if sel<0:
                if skip>0:
                    skip-=1
                sel=0
            reloaded=False
        if key=="KEY_UP" :
            format_length-=1
            if format_length<=0:
                format_length=0
        if key=="KEY_DOWN" :
            format_length+=1
            if format_length>2:
                format_length=2
        if key=="KEY_BACKSPACE" or key=="^H":
            in_str=in_str[:-1]
            sel=0
            skip=0
            reloaded=False
        if key=="KEY_NPAGE":
            ver_idx+=1
            if ver_idx>=len(ver_list):
                ver_idx=0
            read_monsters(ver_list[ver_idx])
            if mon_name!="":
                reloaded=True
        if key=="KEY_PPAGE":
            ver_idx-=1
            if ver_idx<0:
                ver_idx=len(ver_list)-1
            read_monsters(ver_list[ver_idx])
            if mon_name!="":
                reloaded=True








if __name__=="__main__":
    make_ver_list()
    read_monsters(ver_list[ver_idx])
    c.wrapper(main)
