import itertools
import math

from nhconstants_common import *
from nhconstants_flags import *
from nhconstants_flags_raw import *
from nhconstants_atk import *

wingy=False

def max_val_len(d:dict())->int:
    max=0
    for k in d.keys():
        l=len(d[k])
        if l>max:
            max=l
    return max

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

def split_line2(line:str,width:int)-> str:
    splitted=line.split(",")
    cur_line=""
    res_line=""
    for s in splitted:
        if len(cur_line)==0:
            cur_line=s
        else:
            if len(cur_line+","+s)>=width:
                res_line+=cur_line+",\n"
                if s[0]==' ':
                    cur_line=s[1:]
                else:
                    cur_line=s

            else:
                cur_line+=","+s
    res_line+=cur_line
    return res_line


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
        if "G_PLANES" in gen_flags and "G_HELL" not in gen_flags:
            freq_s+="Planes only, "
        if "G_DEPTHS" in gen_flags and "G_HELL" not in gen_flags:
            freq_s+="Depths only, "
        if "G_SHEOL" in gen_flags and "G_HELL" in gen_flags:
            freq_s+="Gehennom&Sheol only, "
        if "G_NOHELL" not in gen_flags and \
            "G_HELL" not in gen_flags and \
            "G_NOSHEOL" not in gen_flags and \
            "G_SHEOL" not in gen_flags and\
            "G_DEPTHS" not in gen_flags and\
            "G_PLANES" not in gen_flags:
            freq_s+="Everywhere, "
        if freq_s.endswith(", "):
            freq_s=freq_s[:-2]
        if format_length==2:
            freq_s="Generation:"+freq_s+"\n"
        else:
            freq_s="Generation:"+freq_s+"|"
        if "G_GENO" in gen_flags:
            freq_s+="Genocide:"
            found=False
            for k in genocide_f.keys():
                if k in gen_flags:
                    found=True
                    if format_length<2:
                        freq_s+=genocide_f[k]+"|"
                    else:
                        freq_s+=genocide_f_ext[k]+"|"
                    break
            if not found:
                freq_s+="Yes |"
        else:
            freq_s+=f"Genocide:No  |"
        if "M2_NOPOLY" in flags2:
            freq_s+=f"Poly to:No "
        else:
            freq_s+=f"Poly to:Yes"
        for form in flags_druid_forms.keys():#evil hack 0.9
            if form in flags2:
                freq_s=freq_s.strip()+", "+flags_druid_forms[form]
        if mon[rows['insight']]!="":#dNetHack
            ins=int(mon[rows['insight']])
            if ins>0:
                freq_s+=f"|Insight:>={mon[rows['insight']]}"
            else:
                freq_s+=f"|Insight:0"
        if format_length!=2:#in ext format we have two lines instead of one, so we don't have to split or condense
            if len(freq_s)>SCR_WIDTH:
                freq_s=" ".join(freq_s.split())
                freq_s=freq_s.replace(" |","|")
            if len(freq_s)>SCR_WIDTH:
                freq_s=freq_s.replace(", ",",")
            if len(freq_s)>SCR_WIDTH:
                freq_s=freq_s.replace("Generation:","Gen:")
            if len(freq_s)>SCR_WIDTH:
                freq_s=freq_s.replace(":Yes",":Y")
                freq_s=freq_s.replace(":No",":N")
        out_line.append(freq_s)
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
        for x in range(len(attack)):
            attack[x]=attack[x].strip()
        if format_length==-1:
            at_actual=at_short
            ad_actual=ad_short
        else:
            at_actual=at
            ad_actual=ad
        if(attack[2]=="0" and attack[3]=="0"):
            if attack[0]=="AT_NONE" and attack[1]=="AD_OONA":#passive oona
                attack_s+=at_actual[attack[0]]+ad_actual[attack[1]]+" Spawn v/e, "#Oona special
            else:
                attack_s+=at_actual[attack[0]]+ad_actual[attack[1]]+", "#0d0 is ignored
        else:
            attack_s+=at_actual[attack[0]]+" "+attack[2]+"d"+attack[3]+ad_actual[attack[1]]+", "

        if len(attack)>8:#dNetHack
            lev=0 if len(attack[4])==0 else int(attack[4])
            off=0 if len(attack[5])==0 else int(attack[5])
            poly=0 if len(attack[6])==0 else int(attack[6])
            ins=0 if len(attack[7])==0 else int(attack[7])
            san=0 if len(attack[8])==0 else int(attack[8])
            if format_length==2:#extended info
                ext=""
                if lev>0:
                    ext+=f"Lv{lev}+, "
                if off!=0:
                    ext+="Offhand, "
                if poly!=0:
                    ext+="Polyself weap, "
                if ins>0:
                    ext+=f"Insight>={ins}, "
                if san<0:
                    ext+=f"Sanity<{-san}, "
                if san>0:
                    ext+=f"Sanity>{san}, "
                if len(ext)>0:
                    ext=ext[:-2]
                    ext="["+ext+"]"
                    attack_s=attack_s[:-2]
                    attack_s+=ext+", "

        attacks+=attack_s
    
    if interrupted==0:#all six attacks present so we need to delete finilizing comma
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
                        if format_length!=-1:
                            attacks_list_condensed.append(attacks_list[x-1]+f" (x{cnt+1})")
                        else:
                            attacks_list_condensed.append(attacks_list[x-1]+f" x{cnt+1}")
                        cnt=0
        attacks_condensed=", ".join(attacks_list_condensed)
        attacks_list="Atk:"+attacks_condensed+"\n"
        if format_length==-1:#extra short
            if len(attacks_list)>SCR_WIDTH:
                attacks_list=attacks_list.replace(", ",",")
        if format_length==0:
            if len(attacks_list)>SCR_WIDTH:
                attacks_list=attacks_list.replace(", ",",")
            if len(attacks_list)>SCR_WIDTH:
                return card_atk(mon,-1)#swirth to extra short
        if format_length==1:
            sl2=split_line2(attacks_list,SCR_WIDTH)
        else:
            sl2=attacks_list
        out_line.append(sl2)
    else:
        attacks_list="Attacks:"+", ".join(attacks_list)+"\n"
        sl=split_line(attacks_list,SCR_WIDTH)
        sl2=split_line2(attacks_list,SCR_WIDTH)
        out_line.append(sl2)

    return out_line

def card_resistances(mon,format_length):
    #Resistances
    out_line=["#"]
    ress=""
    ress_list=mon[rows["res"]].split("|")
    flags4=mon[rows["flags4"]].split("|")
    for res in resists_mon.keys():
        if res in ress_list:
            ress+=resists_mon[res]+", "
    for res in flags4:
        res=res.strip()
        if len(res)==0:
            break
        res=res.strip()
        if res in resists_mon:
            ress+=resists_mon[res.strip()]+", "


    for flag in mon[rows["flags1"]].split("|"):
        flag=flag.strip()
        if(flag=="M1_SEE_INVIS") and format_length==0:#in mini format we add see invisible to resistances bc it is important
            ress+="SeeInvis, "

    found=False
    hates=""
    for hate in resistes_mon_hates.keys():
        if hate in flags4:
            hates+=resistes_mon_hates[hate]+", "
    if len(hates)>0:
        if ress.endswith(", "):
            ress=ress[:-2]
        hates="|Hate:"+hates
        ress+=hates

    if ress.endswith(", "):
        ress=ress[:-2]
    if len(ress)==0:
        ress="Resistances:None\n"
    else:
        ress="Resistances:"+ress+"\n"
    if len(ress)>SCR_WIDTH:
        ress=ress.replace("Resistances:","Res:")
    if len(ress)>SCR_WIDTH:
        ress=ress.replace(", ",",")
    if len(ress)>SCR_WIDTH:
        ress=ress\
            .replace("Stoning","Stone")\
            .replace("Sickness","Sick")\
            .replace("Poison","Pois")\
            .replace("Disint.","Disit")
    if format_length>0:
        ress=split_line2(ress,SCR_WIDTH)
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
    scorpse=False
    for geno in mon[rows["geno"]].split("|"):
        geno=geno.strip()
        if(len(geno)==0):
            break
        if geno=="G_NOCORPSE":
            nocorpse=True
        if geno=="G_SCORPSE":
            scorpse=True

    prefix="Conveyed:"
    if mon[rows["name"]]=="Chromatic Dragon":
        prefix=prefix#debug; Chromatic Dragon is most difficult monster in terms of formatting
    gain_st_ordinary=True
    conv_special=mon[rows["conv_special"]]
    if conv_special.find("GAIN_ST")!=-1:
        gain_st_ordinary=False
    conv_special=conv_special.split("|")

    ress_final_line=""
    if nocorpse:
        ress_final_line+="("
    ress=mon[rows['prob']].split('|')
    ress_n=len(ress)
    if "M2_GIANT" in flags2 and gain_st_ordinary:
        ress_n+=1
    if len(ress[0])>0:
        for r in ress:
            r_name,r_prob=r.split("=")
            prob_parts=r_prob.split(";")
            r_prob=prob_parts[0]
            if len(prob_parts)>1:
                r_t=prob_parts[1]
            else:
                r_t=""
            #displacement in dnethack have both probabity and duration
            if r_name in resists_conv.keys():
                ress_final_line+=resists_conv[r_name]
            else:
                ress_final_line+=r_name
            if format_length!=2:
                ress_final_line+=", "
            else:#show probabilities
                prob_str=""
                if r_prob[0]=="+":#partial resistances from EvilHack
                    prob_str=f"({r_prob}%), "
                if r_prob[0]=="!":#special case for EvilHack, we don't need to normalize teleport, t. control and telepathy
                    prob_str=f"({r_prob[1:]}%), "
                if r_prob[0]=="T":#timeouts for dNetHack
                    prob_str=f"(+{r_prob[1:]}T), "
                    ress_n-=1#don't count these resistances for normalization
                if r_prob[0]=="#":#special case for permanent resist for dNetHack
                    prob_str=f"(permanent), "
                    ress_n-=1#don't count these resistances for normalization
                if len(r_t)>0:#special case for displacement for dnethack
                    prob_str=f"({r_prob}%,{r_t[1:]}T), "

                if len(prob_str)==0:#not special case
                    prob_normalized=int(int(r_prob)/ress_n)
                    prob_str="("+str(prob_normalized)+"%), "
                ress_final_line+=prob_str
    if "M2_GIANT" in flags2 and gain_st_ordinary:
        if ress_n==1:
            prob=int(50)
        else:
            prob=int(100/ress_n)
        ress_final_line+="Gain St"+(f"({prob}%), " if format_length==2 else ", ")

    #special conveys
    for conv in conv_special:
        if conv.find("=")==-1:
            continue
        name,prob=conv.split("=")
        ress_final_line+=conv_special_str[name]
        if format_length==2:
            if name!="PW": 
                ress_final_line+="("+prob+"%)"
            else:
                prob1,prob2,n=prob.split(";")
                ress_final_line+=f"({prob1}% restore, {prob2}% +{n} MAX)"
        ress_final_line+=", "
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
        ress_final_line=split_line2(ress_final_line,SCR_WIDTH)
    
    if len(ress_final_line)>SCR_WIDTH and format_length!=2:
        ress_final_line=ress_final_line.replace(", ",",")#remove spaces for shorter line
    out_line.append(ress_final_line+"\n")

    food_line=""
    #Wt
    food_line+=f"Weight:{mon[rows['weight']]:4}"
    #Nutrition
    food_line+=f"|Nutrition:{mon[rows['nutrition']]:4}"

    #Eat Danger
    bad=""
    eat_danger=mon[rows["eat_danger"]].split("|")
    for danger in eat_danger:
        if danger.find("=")==-1:
            continue
        name,prob=danger.split("=")
        bad+=conv_special_str[name]+", "

    bad=bad[:-2]
    if len(bad)==0:
        food_line+="|Eat danger: Safe\n"
    else:
        food_line+="|Eat danger: "+bad+"\n"

    if len(food_line)>SCR_WIDTH:
        food_line=food_line.replace(" (","(").replace(", ",",").replace("  "," ").replace(": ",":").replace(" |","|")
    out_line.append(food_line)
    return out_line

def card_flags(mon,format_length):
    infravisible_to_perks=False
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

        prefix="Category:"
        cat_len=max_val_len(flags_cat_str)
        cat_list=[]
        for flag in flags_cat_str.keys():
            if len(flag)==0:
                continue#don't check empty flags mh_flags can contain empty strings and this leads to empt entries in cat_list
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
            if "M1_METALLIVORE" in flags1:
                flag_str=f"{'Omni+metallivore':{cat_len}}|"
            else:
                flag_str=f"{'Omnivore':{cat_len}}|"
        else:
            for flag in flags_diet.keys():
                if flag in flags1:
                    found=True
                    flag_str=f"{flags_diet[flag]:{cat_len}}|"
        if found==False:
            flag_str=f"{'Inediate':{cat_len}}|"
        line+=prefix+flag_str
        prefix="Infravisible:"
        if "M3_INFRAVISIBLE" in flags3:
            flag_str="Yes"
        else:
            flag_str="No"
        line+=prefix+flag_str
        if len(line.strip())>SCR_WIDTH:
            line=" ".join(line.split())
            line=line.replace(" |","|")
        if len(line)>SCR_WIDTH:
            line=line.replace(", ",",")
        if len(line)>SCR_WIDTH:#still too long
            line=line.replace("Gender:Male","Sex:M")
            line=line.replace("Gender:Female","Sex:F")
            line=line.replace("Gender:None","Sex:-")
            line=line.replace("Gender:Neuter","Sex:N")
            line=line.replace("Category:","Cat:")
            line=line.replace("Infravisible:Yes","IR-vis:Y")
            line=line.replace("Infravisible:No","IR-vis:N")
        line+="\n"
        out_line.append(line)
        line=""
    #LINE 2. BODY PLAN
        flag_str=""
        prefix="Body:"
        cat_len=max_val_len(flags_body)
        found=False
        for d in flags_body.keys():
            if set(d).issubset(set(flags1).union(set(flags3))):
                found=True
                flag_str=f"{flags_body[d]:{cat_len}}|"
                break
        if found==False:
            flag_str=f"{'Unusual':{cat_len}}|"

        line+=prefix+flag_str

        tmpf=open("tmp.txt","a",encoding="utf-8")
        """if "M1_NOFEET" not in flags1 and "M1_HAS_FEET" not in flags1 and ("M1_NOLIMBS" in flags1 or "M1_SLITHY" in flags1):
            f1=str("M1_NOLIMBS" in flags1)
            f2=str("M1_NOFEET" in flags1)
            f3=str("M1_HAS_FEET" in flags1)
            f4=str("M1_SLITHY" in flags1)
            tmpf.write(mon[rows["name"]]+f":animal feet: {f1},{f2},{f3},{f4}\n")"""
        if "M1_NOFEET" in flags1 and "M1_NOLIMBS" in flags1:
            tmpf.write(mon[rows["name"]]+f":no limbs duplicated by no feet")
        if "M1_HAS_FEET" in flags1 and "M1_NOLIMBS" in flags1:
            tmpf.write(mon[rows["name"]]+f":no limbs, but has feet")
        tmpf.close()
        """
        if "M1_HUMANOID" in flags1 and "M1_NOFEET" in flags1:
            tmpf.write(mon[rows["name"]]+":Humanoid, but no feet\n")
        if "M1_HUMANOID" not in flags1 and "M1_HAS_FEET" in flags1:
            tmpf.write(mon[rows["name"]]+":Not Humanoid, but has feet\n")
        if "M1_HUMANOID" in flags1 and "M1_NOLIMBS" in flags1:
            tmpf.write(mon[rows["name"]]+":Humanoid, but no limbs\n")
        if "M1_HUMANOID" in flags1 and "M1_NOHANDS" in flags1:
            tmpf.write(mon[rows["name"]]+":Humanoid, but no hands\n")
#       if "M1_NOHANDS" not in flags1 and "M1_NOLIMBS" in flags1 and "M1_HUMANOID" not in flags1:
#            tmpf.write(mon[rows["name"]]+":Hands, but no limbs (not humanoid)\n")
        if "M1_NOHANDS" not in flags1 and "M1_NOLIMBS" in flags1 and "M1_HUMANOID" in flags1:
            tmpf.write(mon[rows["name"]]+":Hands, but no limbs (HUMANOID!)\n")
        if "M1_NOHANDS" in flags1 and "M1_NOLIMBS" in flags1:
            tmpf.write(mon[rows["name"]]+":No hands duplicated by no limbs\n")
        if "M1_NOFEET" in flags1 and "M1_NOLIMBS" in flags1:
            tmpf.write(mon[rows["name"]]+":Humanoid, but no feet\n")
        tmpf.close()"""

        prefix="Parts:"
        flag_str=""
        res=""
        for flags_test in body_plan:
            if flags_test==flags_wings and wingy==False:
                continue
            for t in flags_test.keys():
                if set(t).issubset(set(flags1)):
                    #if len(t)>1 and flags_test==flags_head:
                    #    print("!")
                    res=flags_test[t]
            flag_str+=res+", "
        flag_str=flag_str[:-2]
        line+=prefix+flag_str+"\n"
        if len(line)>SCR_WIDTH:
            line=line.replace("  "," ")
            line=line.replace(" |","|")
            line=line.replace(", ",",")
            line=line.replace("Y,no gloves","no gloves")
            line=line.replace("Y,long neck","long neck")
        if len(line)>SCR_WIDTH:
            line=line.replace("|Parts:",";")
        out_line.append(line)
        line=""

        #LINE 3. BEHAVIOR: DEMEANOR, MOVEMENT, WANTS, PICK

        prefix="Demeanor:"
        found=False
        flag_str=""
        flag_str_ext=""
        flag_str_short=""
        if mon[3]=="ball of light":
            found=found
        for flag in flags_demeanor.keys():
            if flag in flags2 or flag in flags3 or flag in flags1:
                found=True
                flag_str_ext+=flags_demeanor_ext[flag]+", "
                flag_str_short+=flags_demeanor[flag]+", "
        if format_length!=2:
            flag_str=flag_str_short
        else:
            if len(prefix+flag_str_ext)-2>SCR_WIDTH:#-2 is for finalizing ", "
                flag_str_ext=flag_str_ext.replace(", ",",")
                if len(prefix+flag_str_ext)-1>SCR_WIDTH:#still longer than we want
                    flag_str=flag_str_short
                else:
                    flag_str=flag_str_ext
            else:
                flag_str=flag_str_ext
        if len(flag_str)>SCR_WIDTH:
            flag_str=flag_str.replace(", ",",")
        if found==False:
            flag_str="None, "
        if flag_str.endswith(","):
            flag_str=flag_str[:-1]
        if flag_str.endswith(", "):
            flag_str=flag_str[:-2]
        if format_length==2:
            flag_str+="\n"
        else:
            flag_str+="|"
        line+=prefix+flag_str

        if mon[rows["name"]]=="Juiblex":
            flag_str=""

        prefix="Move:"
        flag_str=""
        found=False
        for flag in flags_move.keys():
            if flag in flags1 or flag in flags3:
                if flag=="M1_NEEDPICK":
                    flag_str=flag_str[:-2]+" "#remove "," from "Tunnel"
                if flag=="M1_FLY":
                    if "M1_FLOAT" in flags1:
                        continue#float always have fly flag, so it can be skipped, for string shortening
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

        if len(line)>SCR_WIDTH and format_length==1:#move goes to next line
            halves=line.split(prefix)
            line=halves[0][:-1]+"\n"
            remainder=prefix+halves[1].strip()
            if remainder[-1]!="|":
                remainder+= "|"#remove new line
            line=line+remainder

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
        remainder=""
        if len(line)>SCR_WIDTH and format_length!=2:
            line=line.replace(", ",",")#remove spaces for shorter line
            if len(line)>SCR_WIDTH:#picks goes to next line
                halves=line.split(prefix)
                line=halves[0][:-1]+"\n"
                remainder=prefix+halves[1].strip()+"|"#remove new line

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
        flags_move_picks=remainder+prefix+flag_str
        test_split=line.split("\n")
        if len(test_split)>1:
            l1=len(test_split[-1])
            l2=len(test_split[-2])
            if l1==0:
                l=l2
            else:
                l=l1
        if l+len(flags_move_picks)<SCR_WIDTH-2:
            line=line[:-1]+"|"#move "wants" to prev line
        line+=flags_move_picks+"\n"
        if len(line)>SCR_WIDTH:
            line=line.replace(", ",",")

        out_line.append(line)
        line=""

        #LINE 4. PERKS

        prefix="Perks:"
        flag_str=""
        found=False
        for flag in flags_perks.keys():
            if flag in flags1 or flag in flags2 or flag in flags3 or flag in mres or flag in gen_flags or flag in flags4:
                found=True
                flag_str+=flags_perks[flag]+", "
        if mon[rows['light_radius']]!="":#dNetHack
            r=int(mon[rows['light_radius']])
            if r>0:
                found=True
                flag_str+=f'Light radius:{r}, '
        if found==False:
            flag_str="None, "
        flag_str=flag_str[:-2]

        if mon[rows['light_radius']]!="":#dNetHack
            flag_str+="|Vision: "
            for flag in flags_vision_str.keys():
                if flag in flags3:
                    found=True
                    flag_str+=flags_vision_str[flag]+", "



        if flag_str.endswith(", "):
            flag_str=flag_str[:-2]
        line+=split_line2(prefix+flag_str,SCR_WIDTH)+"\n"

        out_line.append(line)
        line=""

    return out_line

def card_dnethack(mon,format_length):
    if format_length!=2:
        return ""
    if len(mon[rows["insight"]])==0:#empty field, exteded while reading. so, this is not dnethack file
        return ""
    out_line=["$"]
    out_line.append(f'Natural AC:{mon[rows["nac"]]:4}|Dodge AC:{mon[rows["dac"]]:4}|Protection AC:{mon[rows["pac"]]:4}|Total AC:10-{mon[rows["nac"]]}-{mon[rows["dac"]]}-{mon[rows["pac"]]}={mon[rows["ac"]]:4}\n')
    out_line.append(f"Damage reduction|Head|Body|Arms|Legs|Feet|\n")
    out_line.append(f'Base            |{mon[rows["hdr"]]:4}|{mon[rows["bdr"]]:4}|{mon[rows["gdr"]]:4}|{mon[rows["ldr"]]:4}|{mon[rows["fdr"]]:4}|\n')
    out_line.append(f'Special         |{mon[rows["spe_hdr"]]:4}|{mon[rows["spe_bdr"]]:4}|{mon[rows["spe_gdr"]]:4}|{mon[rows["spe_ldr"]]:4}|{mon[rows["spe_fdr"]]:4}|\n')
    
    wards_list_str=""
    wards=mon[rows["wards"]]
    wards=wards.split("|")
    wards_amount_int=0
    wards_amount_int_prev=0
    for w in wards:
        if len(w)==0:
            break
        name,prob=w.split("=")
        if name[-2]=="_":#we hame number of wards
            name_splitted=name.split("_")
            wards_amount_int=int(name_splitted[-1])
        else:
            wards_amount_int=0
        if wards_amount_int_prev!=0 and wards_amount_int>wards_amount_int_prev:
            wards_amount_int_prev=wards_amount_int
            continue
        prob=int(prob)
        if prob==100:
            ward=wards_str[name]+", "
        else:
            if prob>0:
                if prob==255:#pacify
                    ward=wards_str[name]+f"(pacify), "
                else:
                    ward=wards_str[name]+f"({prob}%), "
            else:
                prob_normalized=math.floor(math.fabs(prob)/10)
                n=prob+prob_normalized*10
                ward=wards_str[name]+f"({prob_normalized}*N%, min {int(math.fabs(n))}), "
        wards_list_str+=ward
        wards_amount_int_prev=wards_amount_int
    if len(wards_list_str)==0:
        wards_list_str="Wards:None"
    else:
        wards_list_str="Wards:"+wards_list_str
        wards_list_str=wards_list_str[:-2]
    if len(wards_list_str)>SCR_WIDTH:
        wards_list_str=wards_list_str.replace(", ",",")
    if len(wards_list_str)>SCR_WIDTH:
        wards_list_str=split_line2(wards_list_str,SCR_WIDTH)
    out_line+=wards_list_str
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
    out_line.extend(card_dnethack(mon,format_length))

   
    #Preparing string
    out_line_s="".join(out_line)
    return out_line_s