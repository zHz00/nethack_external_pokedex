import csv
import curses as c
import os
import datetime
import time
import json

from nhconstants_flags_raw import *
from nhconstants_flags import *
from nhconstants_atk import *
from nhconstants_common import *
from checker import *
from make_card import *
from filters import *
import utils

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

filter_list=[make_letter_filter("Letter",""),make_name_filter("Name",""),make_conveyed_filter("Conveyed",""),make_param_filter("Param","",0,0)]
filter_on=[False]*len(filter_list)

bold=0

SELECT_VER=1
SEARCH=2
CARD=3
LIST=4
SHOW_ALL=5
SELECT_SORT1=6
SELECT_SORT2=7
FILTERS=8
SELECT_RES=9
SELECT_PARAM=10
EXPLANATION_CARD=11
EXPLANATION_SEARCH=12

mode=SEARCH
mode_prev=SEARCH


cur_len_res=66
cur_len_con=44
cur_len_atk=94

max_len_res=0
max_len_con=0


table=dict()
table_temp=[]
e_at=dict()
e_ad=dict()
e_offset=0
disable_sorting=False
data_folder="data/"
ver_list=[]
ver_name=[]
ver_n=[]
ver_idx=-1
ver_idx_temp=-1
ver_selector_idx=0
format_length=0
list_mode_mons=[]
list_mode_sel=0
list_mode_skip=0
list_mode_max=0
sort_mode1=0
sort_mode2=0
sort_mode_sel=0
sort_dir1=0
sort_dir2=0

filter_mode_sel=0
filters_edits_offset_x=0
filters_edits_offset_y=0

res_mode_sel=0


param_mode_sel=0


sort_mode_lambdas=[
    lambda x:0,#"(none)",
    lambda x:monsym[table[x][rows["symbol"]]],#"Letter",
    lambda x:x.lower(),#"Name",
    lambda x:int(table[x][rows["difficulty"]]),#"Difficulty",
    lambda x:int(table[x][rows["level"]]),#"Level",
    lambda x:int(table[x][rows["exp"]]),#"Experience",
    lambda x:int(table[x][rows["speed"]]),#"Move speed",
    lambda x:int(table[x][rows["ac"]]),#"AC",
    lambda x:int(table[x][rows["mr"]]),#"MR",
    lambda x:int((table[x][rows["geno"]].split("|"))[-1]),#"Frequency",
    lambda x:int(table[x][rows["alignment"]]),#"Alignment",
    lambda x:int(table[x][rows["weight"]]),#"Weight",
    lambda x:int(table[x][rows["nutrition"]]),#"Nutrition",
    lambda x:szs_order[table[x][rows["size"]]],#"Size",
]

def active_filters(f_on,f_list):
    active=[]
    for x in range(len(f_list)):
        if f_on[x]:
            active.append(f_list[x])
    return active


def prepare_list(sort_field1,sort_field2,dir1,dir2,filters):
    global list_mode_mons
    global list_mode_max
    list_mode_mons=[]
    for mon in table.keys():
        if test_monster(table[mon],filters):
            list_mode_mons.append(mon)
    list_mode_max=len(list_mode_mons)

    list_mode_mons=\
        sorted(\
            sorted(\
                list_mode_mons,
                key=sort_mode_lambdas[sort_field2],
                reverse=bool(dir2)),
            key=sort_mode_lambdas[sort_field1],
            reverse=bool(dir1))

MAX_SEARCH=40

def show_ver_format(search_win):
    x1=50
    x2=60
    out_mode=""
    if mode==LIST or mode==FILTERS:
        out_mode="|Format:list"
    else:
        if format_length==0:
            out_mode="|Format:mini"
        if format_length==1:
            out_mode="|Format:full"
        if format_length==2:
            out_mode="|Format:ext"
    search_win.addstr(0,x2,out_mode,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    if ver_idx_temp!=-1:
        search_win.addstr(0,x1,"|Ver:"+get_ver_temp(),c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
        search_win.addstr(1,x1-5,"(List Ver:"+get_ver()+")",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    else:
        search_win.addstr(0,x1,"|Ver:"+get_ver(),c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
        if mode in [LIST,FILTERS,SELECT_RES,SELECT_PARAM]:
            search_win.addstr(1,x1,f"|{(list_mode_skip+list_mode_sel+1):4}/{list_mode_max:4}",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))

            num_filters=0
            last_filter=0
            for x in range(len(filter_on)):
                if filter_on[x] and filter_list[x]["short_name"]!="<any>":
                    last_filter=x
                    num_filters+=1
            if num_filters==0:
                search_win.addstr(1,x2,"|Filter:Ctrl+F",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
            if num_filters==1:
                search_win.addstr(1,x2,"|Filter:"+filter_list[last_filter]["short_name"],c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
            if num_filters>1:
                search_win.addstr(1,x2,f"|Filters:{num_filters}",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))


def show_select_ver(s,sel:int):
    w1=15
    w2=35
    w3=10
    cap1="Filename"
    cap2="Variant"
    cap3="Monsters"
    l=len(ver_list)
    h=c.LINES-2-1#one for header
    offset_y=0
    if l>=h:
        offset_y=0
    else:
        offset_y=int((h-l)/2)
    offset_x=int((c.COLS-w1-w2-w3-4)/2)#4 for |
    header=f"|{cap1:{w1}}|{cap2:{w2}}|{cap3:{w3}}|"
    s.addstr(offset_y,offset_x,header,c.color_pair(BK)|c.A_BOLD)
    for y in range(len(ver_list)):
        filename=ver_list[y][:w1]
        variant=ver_name[y][:w2]
        monsters=str(ver_n[y])
        info=f"|{filename:{w1}}|{variant:{w2}}|{monsters:{w3}}|"
        if y==sel:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(INV))
        else:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(BK))
    s.refresh()

def show_filters(s,sel:int):
    global filters_edits_offset_x,filters_edits_offset_y
    w1=2
    w2=15
    w3=40
    cap1="ON"
    cap2="Filter"
    cap3="Value"
    l=len(ver_list)
    h=c.LINES-2-1#one for header
    offset_y=0
    if l>=h:
        offset_y=0
    else:
        offset_y=int((h-l)/2)
    offset_x=int((c.COLS-w1-w2-w3-4)/2)#4 for |
    filters_edits_offset_x=offset_x+w1+w2+3
    filters_edits_offset_y=offset_y+1
    header=f"|{cap1:{w1}}|{cap2:{w2}}|{cap3:{w3}}|"
    s.addstr(offset_y,offset_x,header,c.color_pair(BK)|c.A_BOLD)
    for y in range(len(filter_list)):
        filter=filter_list[y]
        field=filter["fields"][0]
        on="+" if filter_on[y] else "-"
        name=filter["name"]
        value="<any>"
        if ("value" in field) and len(str(field["value"]))>0 and field["value"]!="*":
            if field["field"]=="prob":
                value=resists_conv[field["value"]]
            else:
                value=str(field["value"])
                if field["value"]==" ":
                    value="["+value+"]"
        if "min" in field:
            if field['field']=="":
                value="<any>"
            else:
                value=f"{param_mode_list[field['field']]}={field['min']}...{field['max']}"
        
        info=f"|{on:{w1}}|{name:{w2}}|{value:{w3}}|"
        if y==sel:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(INV))
        else:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(BK))
    s.addstr(offset_y+1+len(filter_list),offset_x,f"{'|Space:Toggle, Enter:Modify, Esc: Close':{w1+w2+w3+3}}|",c.color_pair(BK)|c.A_BOLD)
    s.refresh()


def show_select_sort(s):
    w1=20
    w2=0
    w3=0
    cap1=""
    if mode==SELECT_SORT1:
        cap1="Sort field (1)"
    if mode==SELECT_SORT2:
        cap1="Sort field (2)"
    cap2=""
    cap3=""
    l=len(sort_mode_str)
    h=c.LINES-2-1#one for header
    offset_y=0
    if l>=h:
        offset_y=0
    else:
        offset_y=int((h-l)/2)
    offset_x=int((c.COLS-w1-w2-w3-4)/2)#4 for |
    header=f"|{cap1:{w1}}|"
    s.addstr(offset_y,offset_x,header,c.color_pair(BK)|c.A_BOLD)
    for y in range(len(sort_mode_str)):
        sort_mode_line=sort_mode_str[y]
        info=f"|{sort_mode_line:{w1}}|"
        if y==sort_mode_sel:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(INV))
        else:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(BK))
    s.refresh()

def show_select_res(s):
    w1=20
    w2=0
    w3=0
    cap1="Conveyed"
    cap2=""
    cap3=""
    l=len(res_mode_list)
    h=c.LINES-2-1#one for header
    offset_y=0
    if l>=h:
        offset_y=0
    else:
        offset_y=int((h-l)/2)
    offset_x=int((c.COLS-w1-w2-w3-4)/2)#4 for |
    header=f"|{cap1:{w1}}|"
    s.addstr(offset_y,offset_x,header,c.color_pair(BK)|c.A_BOLD)
    for y,r in enumerate(res_mode_list.keys()):
        info=f"|{r:{w1}}|"
        if y==res_mode_sel:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(INV))
        else:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(BK))
    s.refresh()
def show_select_param(s):
    w1=30
    w2=0
    w3=0
    cap1="Numeric parameters"
    cap2=""
    cap3=""
    l=len(filters_mode_param_str)
    h=c.LINES-2-1#one for header
    offset_y=0
    if l>=h:
        offset_y=0
    else:
        offset_y=int((h-l)/2)
    offset_x=int((c.COLS-w1-w2-w3-4)/2)#4 for |
    header=f"|{cap1:{w1}}|"
    s.addstr(offset_y,offset_x,header,c.color_pair(BK)|c.A_BOLD)
    for y,r in enumerate(filters_mode_param_str.keys()):
        info=f"|{r:{w1}}|"
        if y==param_mode_sel:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(INV))
        else:
            s.addstr(y+offset_y+1,offset_x,info,c.color_pair(BK))
    s.refresh()


def make_ver_list():
    global ver_list,ver_idx
    global ver_name,ver_n
    file_list=os.listdir(data_folder)
    ver_list=[]
    for name in file_list:
        if name.endswith(".csv"):
            ver_list.append(name)
    if len(ver_list)==0:
        print("No data files found. Exiting...")
        exit(1)
    ver_list=sorted(ver_list)
    ver_idx=0
    ver_name=[""]*len(ver_list)
    ver_n=[0]*len(ver_list)
    for x in range(len(ver_list)):
        monfile=open(data_folder+ver_list[x],"r")
        reader=csv.reader(monfile)
        multigender=0
        for y,mon in enumerate(reader):
            if y==0:
                ver_name[x]=mon[0]
            else:
                if len(mon[rows["namef"]])>0:
                    #multigender monster, add 2
                    multigender+=2
        ver_n[x]=y+multigender
        

def get_ver()->str:
    return ver_list[ver_idx].split(".")[0]

def get_ver_temp()->str:
    return ver_list[ver_idx_temp].split(".")[0]

def save_settings():
    last=open("default.txt","w",encoding="utf-8")
    last.write(ver_list[ver_idx])
    last.write(f"\n{cur_color1}\n{cur_color_bk1}\n{cur_color2}\n{cur_color_bk2}\n{cur_color_s}\n{cur_color_bk_s}\n{cur_color_s_bold}\n")
    last.close()


def table_insert(table:dict(),mon):
    namef=mon[rows["namef"]]
    namem=mon[rows["namem"]]
    if mon[rows["flags2"]].find("M2_FEMALE")!=-1 and len(namef)>0:
        name=namef+"("+mon[rows["name"]]+")"
        if name in table:
            raise#why?
        table[name]=mon
        return
    if mon[rows["flags2"]].find("M2_MALE")!=-1 and len(namem)>0:
        name=namem+"("+mon[rows["name"]]+")"
        if name in table:
            raise#why?
        table[name]=mon
        return
    if mon[rows["name"]] not in table:
        table[mon[rows["name"]]]=mon
    else:
        temp_mon=table[mon[rows["name"]]]
        name1=temp_mon[rows["name"]]+" ("+monsym[temp_mon[rows["symbol"]]]+")"
        name2=mon[rows["name"]]+" ("+monsym[mon[rows["symbol"]]]+")"
        if name1 in table or name2 in table:
            raise#monsters with equal names and letters? nonsense!
        table[name1]=temp_mon
        table[name2]=mon
        table.pop(mon[rows["name"]])

def reset_sort():
    global sort_mode1,sort_mode2,sort_dir1,sort_dir2
    sort_mode1=0
    sort_mode2=0
    sort_dir1=0
    sort_dir2=0

def reset_filters():
    global filter_on
    filter_on=[False]*len(filter_on)
    

def read_monsters(file):
    global table,table_temp
    global disable_sorting
    global wingy
    global e_at,e_ad
    wingy=False
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
        if len(mon[rows["namef"]])>0 and len(mon[rows["namem"]])>0:#two-gender monster
            mon_copy=mon.copy()
            mon_copy[rows["flags2"]]+="|M2_NEUTER"
            table_insert(table,mon_copy)
        else:
            table_insert(table,mon)
        if len(mon[rows["namef"]])>0:
            mon_copy=mon.copy()
            mon_copy[rows["flags2"]]+="|M2_FEMALE"
            table_insert(table,mon_copy)
        if len(mon[rows["namem"]])>0:
            mon_copy=mon.copy()
            mon_copy[rows["flags2"]]+="|M2_MALE"
            table_insert(table,mon_copy)
        if "M1_WINGS" in mon[rows["flags1"]]:
            wingy=True
    base_name=file.replace(".csv","")
    try:
        attacks_file=open(data_folder+base_name+".attacks.json","r")
        explanation_attacks=json.load(attacks_file)
        attacks_file.close()
        e_at=explanation_attacks["at"]
        e_ad=explanation_attacks["ad"]
    except FileNotFoundError as e:
        e_at=dict()
        e_ad=dict()
        for mon_name in table.keys():
            mon=table[mon_name]
            for attack_n in itertools.chain(range(rows["attack1"],rows["attack6"]+1),range(rows["attack7"],rows["attack10"])):
                if mon[attack_n]==NO_ATTK or len(mon[attack_n])==0:
                    continue
                attack=mon[attack_n]
                attack=attack[5:]
                attack=attack[:-1]
                attack=attack.split(",")
                at_cur=attack[0].strip()
                ad_cur=attack[1].strip()
                if at_cur not in e_at:
                    at_item=dict()
                    at_item["type"]=at_cur
                    at_item["caption"]=at[at_cur].strip()
                    at_item["caption_short"]=at_short[at_cur].strip()
                    at_item["explanation"]="DUMMY"#at[at_cur].strip()
                    at_item["ad_list_name"]=at_cur
                    e_at[at_cur]=at_item
                if at_cur not in e_ad:
                    e_ad[at_cur]=dict()
                if ad_cur not in e_ad[at_cur]:
                    ad_item=dict()
                    ad_item["type"]=ad_cur
                    ad_item["caption"]=ad[ad_cur].strip()
                    ad_item["caption_short"]=ad_short[ad_cur].strip()
                    ad_item["explanation"]="DUMMY"#ad[ad_cur].strip()
                    ad_item["resisted"]=False
                    ad_item["can_be_cancelled"]=False
                    ad_item["mc"]=False
                    e_ad[at_cur][ad_cur]=ad_item
                #ad=mon[attack_n][1]
        explanation_attacks=dict()
        explanation_attacks["at"]=e_at
        explanation_attacks["ad"]=e_ad
        attacks_file=open(data_folder+base_name+".attacks.json","w",encoding="utf-8")
        json.dump(explanation_attacks,attacks_file,indent=1)
        attacks_file.close()
    set_at_ad(e_at,e_ad)

def fill_attacks(file):
    global e_at,e_ad
    attacks_file=open(data_folder+file,"r")
    explanation_attacks=json.load(attacks_file)
    attacks_file.close()
    e_at=explanation_attacks["at"].copy()
    e_ad=explanation_attacks["ad"].copy()

    for mon_name in table.keys():
        mon=table[mon_name]
        for attack_n in itertools.chain(range(rows["attack1"],rows["attack6"]+1),range(rows["attack7"],rows["attack10"])):
            if mon[attack_n]==NO_ATTK or len(mon[attack_n])==0:
                continue
            attack=mon[attack_n]
            attack=attack[5:]
            attack=attack[:-1]
            attack=attack.split(",")
            at_cur=attack[0].strip()
            ad_cur=attack[1].strip()
            if at_cur not in e_at:
                at_item=dict()
                at_item["type"]=at_cur
                at_item["caption"]=at[at_cur].strip()
                at_item["caption_short"]=at_short[at_cur].strip()
                at_item["explanation"]="DUMMY"#at[at_cur].strip()
                at_item["ad_list_name"]=at_cur
                e_at[at_cur]=at_item
                e_ad[at_cur]=dict()
            at_cur=e_at[at_cur]["ad_list_name"]
            if ad_cur not in e_ad[at_cur]:
                ad_item=dict()
                ad_item["type"]=ad_cur
                ad_item["caption"]=ad[ad_cur].strip()
                ad_item["caption_short"]=ad_short[ad_cur].strip()
                ad_item["explanation"]="DUMMY"#ad[ad_cur].strip()
                ad_item["resisted"]=False
                ad_item["can_be_cancelled"]=False
                ad_item["mc"]=False
                e_ad[at_cur][ad_cur]=ad_item
    explanation_attacks=dict()
    explanation_attacks["at"]=e_at
    explanation_attacks["ad"]=e_ad
    base_name=ver_list[ver_idx].replace(".csv","")
    attacks_file=open(data_folder+base_name+".attacks.json","w",encoding="utf-8")
    json.dump(explanation_attacks,attacks_file,indent=1)
    attacks_file.close()
    utils.show_message("DONE")

BK=20
INV=21
BK_CARD=22
INV_CARD=23
SEPARATOR_BK=24
SEPARATOR_INV=25
SEPARATOR_BLACK=26

def reset_colors():
    c.init_pair(BK,cur_color_s,cur_color_bk_s)
    c.init_pair(INV,cur_color_bk_s,cur_color_s)

    c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
    c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
    c.init_pair(SEPARATOR_BK,c.COLOR_WHITE,cur_color_bk1)
    c.init_pair(SEPARATOR_INV,c.COLOR_WHITE,cur_color_bk2)
    c.init_pair(SEPARATOR_BLACK,c.COLOR_WHITE,c.COLOR_BLACK)


def out_input(s,in_str):

    s.erase()
    s.addstr(0,0,">"+in_str,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    s.chgat(-1,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
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
    out_str=""
    for mon in results:
        if cur<skip:
            cur+=1
            continue
        if(start_ch+len(mon)>LIST_WIDTH):
            out_str+=f"(+{len(results)-cur})"
            break
        start_ch+=len(mon)+1#for "|"
        if cur-skip==sel:
            out_str+="*"+mon
            selected_appeared=True
        else:
            out_str+=mon
        out_str+="|"
        cur+=1
    attr=c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0)
    ch_prev=""
    idx=0
    for ch in out_str:
        if ch_prev=="|":
            attr=c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0)
        if ch=="*":
            attr=c.color_pair(INV)|(c.A_BOLD if cur_color_s_bold else 0)
        if ch=="|":
            attr=c.color_pair(BK)|c.A_BOLD
        ch_prev=ch
        if ch!="*" and idx<SCR_WIDTH-1:
            s.addstr(ch,attr)
            idx+=1
        
    s.chgat(c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    s.refresh()
    return (cur-skip,selected_appeared)

def move_to_in(s,in_str):
    s.move(0,1+len(in_str))
    c.curs_set(1)

def disable_cursor():
    c.curs_set(0)


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

def show_hint(search_win):
    search_win.addstr(0,3,"<- Type here",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    search_win.addstr(1,0,"In this line you'll see search results",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    search_win.addstr(0,SCR_WIDTH-4,"<-+",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    search_win.addstr(1,SCR_WIDTH-25,"^--------------------+ |",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))

def show_hello_msg(card_win):
    hello_msg=["=== Nethack external Pokedex ===",
    "Enter monster name to see its properties. Keys:"]
    #"Ctrl+O: Choose variant, or PgUp/PgDn to switch",
    #"LEFT, RIGHT: Scroll search results",
    #"UP, DOWN: Change output format",
    #"ESC: Clear search; F10: Exit"

    block1=["LEFT, RIGHT: Scroll results",
            "ESC: Clear search",
            "Tab: Switch to List mode"]
    block2=["[, ], Ctrl+O: Choose variant",
            "UP, DOWN: Change format",
            "F10, Ctrl+Q: Exit"]
    col1=10
    col2=45
    card_win.chgat(-1,c.color_pair(BK_CARD))
    card_win.addstr(0,int((SCR_WIDTH-len(hello_msg[0]))/2),hello_msg[0],c.color_pair(INV_CARD)|c.A_BOLD)
    card_win.addstr(1,int((SCR_WIDTH-len(hello_msg[1]))/2),hello_msg[1],c.color_pair(INV_CARD))
    for i in range(len(block1)):
        card_win.addstr(i+2,col1,block1[i])
        card_win.addstr(i+2,col2,block2[i])

    if len(in_str)==0:

        card_win.addstr(0,0,"^",c.color_pair(SEPARATOR_BK)|c.A_BOLD)
        card_win.addstr(1,0,"|",c.color_pair(SEPARATOR_BK)|c.A_BOLD)
        card_win.addstr(2,0,"+---------",c.color_pair(SEPARATOR_BK)|c.A_BOLD)

        card_win.addstr(0,SCR_WIDTH-4,"| |",c.color_pair(SEPARATOR_BK)|c.A_BOLD)
        card_win.addstr(1,SCR_WIDTH-4,"| |",c.color_pair(SEPARATOR_BK)|c.A_BOLD)
        card_win.addstr(2,SCR_WIDTH-7,"---+ |",c.color_pair(SEPARATOR_BK)|c.A_BOLD)
        card_win.addstr(3,SCR_WIDTH-12,"----------+",c.color_pair(SEPARATOR_BK)|c.A_BOLD)
    card_win.refresh()

def show_not_found_msg(card_win,mon_name):
    msg=[f"'{mon_name}' does not extist in current version.","Try another search or switch version."]
    card_win.chgat(-1,c.color_pair(BK_CARD))
    card_win.addstr(0,int((SCR_WIDTH-len(msg[0]))/2),msg[0],c.color_pair(INV_CARD)|c.A_BOLD)
    card_win.addstr(1,int((SCR_WIDTH-len(msg[1]))/2),msg[1],c.color_pair(BK_CARD)|c.A_BOLD)
    card_win.refresh()

def show_search_upper(search_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global tries
    out_input(search_win,in_str)
    if len(in_str)>0:
        appeared=False
        tries=0
        while(appeared==False and tries<5):
            (max_sel,appeared)=out_results(search_win,results,sel,skip)
            if appeared==False:#next selected monster too long
                skip+=1
                sel-=1
                tries+=1
    show_ver_format(search_win)
    move_to_in(search_win,in_str)
    search_win.refresh()


def show_list_upper(search_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global sort_mode1
    global sort_dir1

    sort_dir1_str="Ascending" if sort_dir1==0 else "Descending"
    sort_dir2_str="Ascending" if sort_dir2==0 else "Descending"

    search_win.erase()

    search_win.addstr(0,0,f"Sort1(Ctrl+S) :{sort_mode_str[sort_mode1]:10}|Dir1(Ctrl+D) :{sort_dir1_str}",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    if sort_mode1!=0:
        search_win.addstr(1,0,f"Sort2(Shift+S):{sort_mode_str[sort_mode2]:10}|Dir2(Shift+D):{sort_dir2_str}",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    else:
        search_win.addstr(1,0,f"Tab: Switch to search mode",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))

    show_ver_format(search_win)
    disable_cursor()
    search_win.refresh()

def show_card_upper(search_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global sort_mode1
    global sort_dir1

    search_win.erase()

    if mode in [EXPLANATION_CARD,EXPLANATION_SEARCH]:
        addition=f"[Lv:{table[mon_name][rows['level']]}]"
    else:
        addition=""

    search_win.addstr(0,0,"Monster:"+mon_name+addition,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    if mode in [EXPLANATION_SEARCH,EXPLANATION_CARD]:
        hint="Esc:Back to card"
    else:
        hint="Esc:Back to list"
    search_win.addstr(1,0,hint,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))

    show_ver_format(search_win)
    disable_cursor()
    search_win.refresh()

def show_list(card_win,search_win,results):
    global selected_mon_name
    selected_mon_name=""
    card_win.bkgd(' ',c.color_pair(BK_CARD))
    card_win.erase()
    card_win.addstr(0,1,one_line_header_str(),c.color_pair(SEPARATOR_BK))
    for x in range(LIST_LINES):
        if x+list_mode_skip>=len(list_mode_mons):
            break
        current_mon=table[list_mode_mons[x+list_mode_skip]]
        card_win.move(x+1,0)
        out_symbol(card_win,current_mon)
        line=make_card_one_line(current_mon,list_mode_mons[x+list_mode_skip])#key is monster name, it can be different from "name" column
        if x==list_mode_sel:
            selected_mon_name=list_mode_mons[x+list_mode_skip]
            card_win.addstr(x+1,1,line[:SCR_WIDTH-2],c.color_pair(BK_CARD)|c.A_BOLD)
            if len(line)>=SCR_WIDTH-1:#-1 for monster character in first column
                card_win.insch(x+1,SCR_WIDTH-1,line[SCR_WIDTH-2],c.color_pair(BK_CARD)|c.A_BOLD)
        else:
            card_win.addstr(x+1,1,line[:SCR_WIDTH-2],c.color_pair(INV_CARD))
            if len(line)>=SCR_WIDTH-1:#-1 for monster character in first column
                card_win.insch(x+1,SCR_WIDTH-1,line[SCR_WIDTH-2],c.color_pair(INV_CARD))
    card_win.refresh()
    show_list_upper(search_win,results,selected_mon_name)

EX_NORMAL = 30
EX_HEADER = 31
EX_BOLD = 32
EX_ITALIC = 33
EX_NAME = 34

modes_bk={
    EX_NORMAL:BK_CARD,
    EX_HEADER:INV_CARD,
    EX_BOLD:INV_CARD,
    EX_ITALIC:SEPARATOR_BK,
    EX_NAME:INV_CARD}
modes_inv={
    EX_NORMAL:INV_CARD,
    EX_HEADER:BK_CARD,
    EX_BOLD:BK_CARD,
    EX_ITALIC:SEPARATOR_INV,
    EX_NAME:BK_CARD}
modes_attr={
    EX_NORMAL:0,
    EX_HEADER:c.A_BOLD,
    EX_BOLD:c.A_BOLD,
    EX_ITALIC:0,
    EX_NAME:0
}


def show_explanation(card_win,results,mon_name):
    global e_offset
    card_win.erase()
    attacks=card_explanation(table[mon_name])
    card="".join(attacks).split("\n")
    cur_pair=BK_CARD
    line_n=0
    if e_offset>len(card):
        e_offset=0#cycle scroll
    mode=EX_NORMAL
    for i in range(e_offset,len(card)):
        line=card[i]
        if len(line)==0:
            continue
        color=line[0]
        remainder=False
        if i!=0 and (card[i-1].strip()[-1])==",":
            remainder=True
        if color in ["#","$","^"]:
            line=line[1:]

        if color in ["#","^"]:
            cur_pair=BK_CARD
        if color=="$":
            cur_pair=INV_CARD
        if len(line.strip())==0:#only special character
            continue
        if color=="^":
            remainder=True
        if remainder==False:
            attrib=c.A_BOLD
        else:
            attrib=0
        line=line.rstrip()
        if len(line)>SCR_WIDTH:
            line=line[:SCR_WIDTH-1]+"!"
        prev_ch=''
        pos=0
        for i in range(len(line)):
            if line[i]=='\\' and prev_ch!='\\':
                prev_ch=line[i]
                continue
            if line[i]=='*' and prev_ch!='\\' and mode==EX_NORMAL:
                mode=EX_BOLD
                prev_ch=line[i]
                continue
            if line[i]=='*' and prev_ch!='\\' and prev_ch!='*' and mode==EX_BOLD:
                mode=EX_NORMAL
                prev_ch=line[i]
                continue
            if line[i]=='_' and prev_ch!='\\' and mode==EX_NORMAL:
                mode=EX_NAME
                prev_ch=line[i]
                continue
            if line[i]=='_' and prev_ch!='\\' and prev_ch!='_' and mode==EX_NAME:
                mode=EX_NORMAL
                prev_ch=line[i]
                continue
            if line[i]=='*' and prev_ch=='*' and mode in [EX_NORMAL,EX_BOLD]:
                mode=EX_ITALIC
                prev_ch=line[i]
                continue
            if line[i]=='*' and prev_ch=='*' and mode==EX_ITALIC:
                mode=EX_NORMAL
                prev_ch=line[i]
                continue
            if line[i]=='*' and prev_ch!='\\':#we have asterisk that was not caught before. probably this is **. Skipping
                prev_ch=line[i]
                continue
            if line_n<c.LINES-2:
                if line_n==c.LINES-3 and i>=c.COLS-1:
                    break
                if line[i]=="|":
                    if cur_pair==BK_CARD:
                        card_win.addstr(line_n,pos,line[i],c.color_pair(SEPARATOR_BK)|c.A_BOLD)
                    else:
                        card_win.addstr(line_n,pos,line[i],c.color_pair(SEPARATOR_INV)|c.A_BOLD)
                else:
                    if cur_pair==BK_CARD:
                        card_win.addstr(line_n,pos,line[i],c.color_pair(modes_bk[mode])|(modes_attr[mode] if mode!=EX_NORMAL else attrib))
                    else:
                        card_win.addstr(line_n,pos,line[i],c.color_pair(modes_inv[mode])|(modes_attr[mode] if mode!=EX_NORMAL else attrib))
            if line[i]==":":
                attrib=0
            if line[i]=="|":
                attrib=c.A_BOLD
            prev_ch=line[i]
            pos+=1
        line_n+=1
            
        #card_win.addstr(line_n,1 if line_n==0 else 0,line,c.color_pair(cur_pair))
        card_win.chgat(-1,c.color_pair(cur_pair))
        if line_n>c.LINES-2 or e_offset>0:#two or more screens
            p=1+e_offset//(c.LINES-3)
            p_max=1+len(card)//(c.LINES-3)
            page_n=f"[Page {p} of {p_max}. SPACE: Scroll]"
            spaces=(c.COLS-len(page_n))//2-1
            page_n=" "*spaces+page_n+" "*spaces
            card_win.addstr(c.LINES-3,0,page_n,c.color_pair(SEPARATOR_BK))
    card_win.refresh()
    

def show_card(card_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global tries
    card_win.erase()
    #card_win.refresh()
    if (len(results)>0 and len(in_str)>0 and not_found_after_reload==False) or mode in [SHOW_ALL,CARD]:
        if mon_name not in table:
            show_not_found_msg(card_win,mon_name)
        else:
            card_win.chgat(-1,c.color_pair(BK_CARD))
            if format_length!=2:
                card_win.move(0,0)
                out_symbol(card_win,table[mon_name])
            else:#extended
                card_win.move(0,0)
                card_win.addch(c.ACS_ULCORNER,c.color_pair(SEPARATOR_BLACK))
                card_win.addch(c.ACS_HLINE,c.color_pair(SEPARATOR_BLACK))
                card_win.addch(c.ACS_URCORNER,c.color_pair(SEPARATOR_BLACK))
                card_win.move(1,0)
                card_win.addch(c.ACS_VLINE,c.color_pair(SEPARATOR_BLACK))
                out_symbol(card_win,table[mon_name])
                card_win.addch(c.ACS_VLINE,c.color_pair(SEPARATOR_BLACK))
                card_win.move(2,0)
                card_win.addch(c.ACS_LLCORNER,c.color_pair(SEPARATOR_BLACK))
                card_win.addch(c.ACS_HLINE,c.color_pair(SEPARATOR_BLACK))
                card_win.addch(c.ACS_LRCORNER,c.color_pair(SEPARATOR_BLACK))
            if check_monster(table[mon_name])==True:
                card=make_card(table[mon_name],format_length)
            else:
                card="Error making card: "+mon_name
            card=card.split("\n")
            #if check_formatting(card)==False:
            #    card="Error formatting card:"+mon_name
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
                if len(line.strip())>SCR_WIDTH:
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
                    if line_n<c.LINES-2:
                        if line_n==c.LINES-3 and i>=c.COLS-1:
                            break
                        if line[i]=="|":
                            if cur_pair==BK_CARD:
                                card_win.addstr(line_n,pos,line[i],c.color_pair(SEPARATOR_BK)|c.A_BOLD)
                            else:
                                card_win.addstr(line_n,pos,line[i],c.color_pair(SEPARATOR_INV)|c.A_BOLD)
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
def run_tests(s):
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
        report=open("reports/report-"+ver_list[ver_idx]+"-"+file_suffixes[f_length]+".txt","w",encoding="utf-8")
        report_summary=open("report.log","a",encoding="utf-8")
        report_summary.write("==========\n")
        report_summary.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")+"\n")
        report_summary.write("File: "+ver_list[ver_idx]+"\n")
        for mon in table.keys():
            total+=1
            if len(mon)>20:
                report_summary.write(f"long name({len(mon)}):{mon}\n")
            if len(mon)>name_longest:
                name_longest=len(mon)
                name_longest_name=mon
            if check_monster(table[mon])==False:
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
    report=open("reports/report-"+ver_list[ver_idx]+"-"+"EXPL"+".txt","w",encoding="utf-8")
    report_summary=open("report.log","a",encoding="utf-8")
    report_summary.write("==========\n")
    report_summary.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")+"\n")
    report_summary.write("File: "+ver_list[ver_idx]+"\n")
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

def react_to_key_search(s,search_win,ch,key,alt_ch,results,mon_name):
    global reloaded
    global cur_color1,cur_color2,cur_color_bk1,cur_color_bk2
    global cur_color_s,cur_color_bk_s,cur_color_s_bold
    global in_str
    global sel,skip
    global format_length
    global max_sel
    global ver_idx
    global mode
    global ver_selector_idx
    global current_mon
    global list_mode_sel, list_mode_skip
    global mode_prev
    if ch==27:#ESC
        search_win.nodelay(True)
        while search_win.getch()!=-1:
            pass
        search_win.nodelay(False)
        in_str=""
        reloaded=False
    if key=="1":
        cur_color1+=1
        if cur_color1>7:
            cur_color1=0
        reset_colors()
    if key=="2":
        cur_color_bk1+=1
        if cur_color_bk1>7:
            cur_color_bk1=0
        reset_colors()
    if key=="3":
        cur_color2+=1
        if cur_color2>7:
            cur_color2=0
        reset_colors()
    if key=="4":
        cur_color_bk2+=1
        if cur_color_bk2>7:
            cur_color_bk2=0
        reset_colors()
    if key=="5":
        cur_color_s+=1
        if cur_color_s>7:
            cur_color_s=0
            if cur_color_s_bold==0:
                cur_color_s_bold=1
            else:
                cur_color_s_bold=0
        reset_colors()
    if key=="6":
        cur_color_bk_s+=1
        if cur_color_bk_s>7:
            cur_color_bk_s=0
        reset_colors()

    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    if key=="KEY_F(14)":
        mode=SHOW_ALL
        current_mon=0
        return 0
    if key=="KEY_F(3)":
        run_tests(s)
        for x in range(1,17):
            s.addstr(f"TEST:{(x-1):2} ",c.color_pair(x))
            if x==8:
                s.addstr("\n")
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
        ch=s.getch()
        if ch==ord("f"):
            s.addstr(15,15,"Enter file name to fill attacks:")
            file=utils.textpad(s,16,15,20).strip()
            if len(file)>0:
                if file.endswith(".json")==False:
                    file+=".json"
                fill_attacks(file)
                set_at_ad(e_at,e_ad)
        
        reset_colors()
        utils.init_pairs()

    if len(key)==1 and key not in ["1","2","3","4","5","6","[","]"]:
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
    if key=="]":
        ver_idx+=1
        if ver_idx>=len(ver_list):
            ver_idx=0
        read_monsters(ver_list[ver_idx])
        reset_sort()
        reset_filters()
        if mon_name!="":
            reloaded=True
    if key=="[":
        ver_idx-=1
        if ver_idx<0:
            ver_idx=len(ver_list)-1
        read_monsters(ver_list[ver_idx])
        reset_sort()
        reset_filters()
        if mon_name!="":
            reloaded=True
    if key=="^O":
        mode_prev=SEARCH
        mode=SELECT_VER
        ver_selector_idx=ver_idx
    if key=="^I":
        mode=LIST
        format_length=2
        prepare_list(0,0,0,0,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
    if key=="^A":
        if len(in_str)>0 and len(mon_name)>0:
            mode=EXPLANATION_SEARCH
    if key=="KEY_F(1)":
        utils.show_message("Quick help:\n\
\n\
_Ctrl+O:_        Select NetHack variant to search\n\
_[, ]:_          Switch to next NetHack variant\n\
_Left, Right:_   Scroll through search results\n\
_Esc:_           Clear search line\n\
_Up:_            Show less information\n\
_Down:_          Show more information\n\
_Ctrl+A:_        Show attacks analysis windows\n\
_Tab:_           Switch to **List** mode\n\
_Ctrl+Q or F10:_ Exit\n\
_1...6:_         Change colors\n")

    return 0

def react_to_key_select_ver(ch,key,alt_ch,mon_name):
    global ver_selector_idx
    global ver_idx
    global mode
    global reloaded
    global list_mode_sel,list_mode_skip
    if ch==27:
        mode=mode_prev
    if key=="KEY_UP" :
        if ver_selector_idx>0:
            ver_selector_idx-=1
    if key=="KEY_DOWN" :
        if ver_selector_idx+1<len(ver_list):
            ver_selector_idx+=1
    if key=="^M" or key=="^J":
        ver_idx=ver_selector_idx
        read_monsters(ver_list[ver_idx])
        reset_sort()
        reset_filters()
        prepare_list(0,0,0,0,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
        if mon_name!="":
            reloaded=True
        mode=mode_prev


def react_to_key_select_sort(ch,key,alt_ch,mon_name):
    global sort_mode_sel
    global sort_mode1,sort_mode2
    global mode
    global reloaded
    if ch==27:
        mode=LIST
    if key=="KEY_UP" :
        if sort_mode_sel>0:
            sort_mode_sel-=1
    if key=="KEY_DOWN" :
        if sort_mode_sel+1<len(sort_mode_str):
            sort_mode_sel+=1
    if key=="^M" or key=="^J":
        if mode==SELECT_SORT1:
            reset_sort()
            sort_mode1=sort_mode_sel
        if mode==SELECT_SORT2:
            sort_mode2=sort_mode_sel
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
        mode=LIST
    return 0

def react_to_key_select_res(card_win,search_win,ch,key,alt_ch,mon_name):
    global res_mode_sel
    global sort_mode1,sort_mode2
    global mode
    global reloaded
    global list_mode_sel,list_mode_skip
    if ch==27:
        mode=FILTERS
        show_list(card_win,search_win,[])
    if key=="KEY_UP" :
        if res_mode_sel>0:
            res_mode_sel-=1
    if key=="KEY_DOWN" :
        if res_mode_sel+1<len(res_mode_list):
            res_mode_sel+=1
    if key=="^M" or key=="^J":
        filter_list[filter_mode_sel]=make_conveyed_filter("Conveyed",list(resists_conv.keys())[res_mode_sel])
        filter_on[filter_mode_sel]=True
        mode=FILTERS
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
        show_list(card_win,search_win,[])
    return 0
def react_to_key_select_param(card_win,search_win,ch,key,alt_ch,mon_name):
    global param_mode_sel
    global sort_mode1,sort_mode2
    global mode
    global reloaded
    global list_mode_sel,list_mode_skip
    if ch==27:
        mode=FILTERS
        show_list(card_win,search_win,[])
    if key=="KEY_UP" :
        if param_mode_sel>0:
            param_mode_sel-=1
    if key=="KEY_DOWN" :
        if param_mode_sel+1<len(filters_mode_param_str):
            param_mode_sel+=1
    if key=="^M" or key=="^J":
        param_caption=list(filters_mode_param_str.keys())[param_mode_sel]
        filter_list[filter_mode_sel]=make_param_filter("Param",filters_mode_param_str[param_caption],0,0)
        filter_on[filter_mode_sel]=True
        show_list(card_win,search_win,[])
        show_filters(card_win,filter_mode_sel)
        if param_mode_sel==0:#(none), we don't have to enter min and max
            prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
            list_mode_sel=0
            list_mode_skip=0
            show_list(card_win,search_win,[])
            mode=FILTERS
            return 0
        min=utils.textpad(card_win,filters_edits_offset_y+filter_mode_sel,filters_edits_offset_x+len(param_caption)+1,6).strip()
        if min=="":
            mode=FILTERS
            return 0
        try:
            int(min)
        except:
            utils.show_message("Only integers allowed!")
            show_list(card_win,search_win,[])
            show_filters(card_win,filter_mode_sel)
            mode=FILTERS
            return 0
        filter_list[filter_mode_sel]=make_param_filter("Param",filters_mode_param_str[param_caption],int(min),0)
        show_filters(card_win,filter_mode_sel)
        max=utils.textpad(card_win,filters_edits_offset_y+filter_mode_sel,filters_edits_offset_x+len(param_caption)+1+3+len(min),6).strip()
        if max=="":
            mode=FILTERS
            return 0
        try:
            int(max)
        except:
            utils.show_message("Only integers allowed!")
            show_list(card_win,search_win,[])
            show_filters(card_win,filter_mode_sel)
            mode=FILTERS
            return 0
        filter_list[filter_mode_sel]=make_param_filter("Param",filters_mode_param_str[param_caption],int(min),int(max))
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
        show_list(card_win,search_win,[])
        show_filters(card_win,filter_mode_sel)

        mode=FILTERS
    return 0


def react_to_key_filters(card_win,search_win,ch,key,alt_ch,mon_name):
    global filter_mode_sel
    global filter_on
    global mode
    global reloaded
    global filter_list
    global list_mode_sel,list_mode_skip
    f=filter_list[filter_mode_sel]["fields"][0]
    if ch==27:
        mode=LIST
    if key=="KEY_UP" :
        if filter_mode_sel>0:
            filter_mode_sel-=1
    if key=="KEY_DOWN" :
        if filter_mode_sel+1<len(filter_list):
            filter_mode_sel+=1
    if key==" ":
        filter_on[filter_mode_sel]=not filter_on[filter_mode_sel]
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
        show_list(card_win,search_win,[])
    if key=="^M" or key=="^J":
        #f=make_name_filter("test","z")
        #prepare_list(0,0,0,0,[f])
        #reset_sort()
        #prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,[])
        if f["field"]=="symbol":
            new=utils.textpad(card_win,filters_edits_offset_y+filter_mode_sel,filters_edits_offset_x,2)
            if len(new)>0:
                filter_list[filter_mode_sel]=make_letter_filter("Letter",new[0])
                filter_on[filter_mode_sel]=True
                prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
                list_mode_sel=0
                list_mode_skip=0
                show_list(card_win,search_win,[])
            show_filters(card_win,filter_mode_sel)
        if f["field"]=="name":
            new=utils.textpad(card_win,filters_edits_offset_y+filter_mode_sel,filters_edits_offset_x,20)
            if len(new)>0:
                filter_list[filter_mode_sel]=make_name_filter("Name",new.strip())
                filter_on[filter_mode_sel]=True
                prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
                list_mode_sel=0
                list_mode_skip=0
                show_list(card_win,search_win,[])
            show_filters(card_win,filter_mode_sel)
        if f["field"]=="prob":
            mode=SELECT_RES
        if "min" in f:#param filter
            mode=SELECT_PARAM
    return 0


def react_to_key_list(ch,key,alt_ch,mon_name):
    global list_mode_sel
    global list_mode_skip
    global mode
    global sort_dir1,sort_dir2
    global ver_idx,ver_selector_idx
    global mode_prev
    global reloaded
    global sort_mode_sel
    if key=="]":
        ver_idx+=1
        if ver_idx>=len(ver_list):
            ver_idx=0
        read_monsters(ver_list[ver_idx])
        reset_sort()
        reset_filters()
        prepare_list(0,0,0,0,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
        if mon_name!="":
            reloaded=True
    if key=="[":
        ver_idx-=1
        if ver_idx<0:
            ver_idx=len(ver_list)-1
        read_monsters(ver_list[ver_idx])
        reset_sort()
        reset_filters()
        prepare_list(0,0,0,0,active_filters(filter_on,filter_list))
        list_mode_sel=0
        list_mode_skip=0
        if mon_name!="":
            reloaded=True
    if key=="^O":
        mode_prev=LIST
        mode=SELECT_VER
        ver_selector_idx=ver_idx
    if key=="KEY_UP" :
        if list_mode_sel>0:
            list_mode_sel-=1
        else:
            if list_mode_skip>0:
                list_mode_skip-=1            
    if key=="KEY_DOWN" :
        if list_mode_sel<LIST_LINES-1 and list_mode_sel+list_mode_skip+1<list_mode_max:
            list_mode_sel+=1
        else:
            if list_mode_skip+list_mode_sel<list_mode_max-1:
                list_mode_skip+=1
    if key=="KEY_PPAGE" :
        list_mode_skip-=LIST_LINES
        if list_mode_skip<0:
            list_mode_skip=0
    if key=="KEY_NPAGE":
        if list_mode_max<LIST_LINES:
            list_mode_skip=0
            list_mode_sel=list_mode_max-1
        else:
            list_mode_skip+=LIST_LINES
            if list_mode_skip+LIST_LINES>list_mode_max-1:
                list_mode_skip=list_mode_max-LIST_LINES
    if key=="KEY_HOME" or alt_ch=="[H" or alt_ch=="[1~":
        list_mode_skip=0
        list_mode_sel=0
    if key=="KEY_END" or key=="KEY_A1" or alt_ch=="[4~":
        if list_mode_max>LIST_LINES:
            list_mode_skip=list_mode_max-LIST_LINES
            list_mode_sel=LIST_LINES-1
        else:
            list_mode_skip=0
            list_mode_sel=list_mode_max-1
    if key=="^I":
        mode=SEARCH
    if key=="^J" or key=="^M":
        mode=CARD
    if key=="^S":
        sort_mode_sel=sort_mode1
        mode=SELECT_SORT1
    if key=="^F":
        mode=FILTERS
        #f=make_letter_filter("test","b")
    if key=="S":
        if sort_mode1!=0:
            sort_mode_sel=sort_mode2
            mode=SELECT_SORT2
    if key=="^D":
        if sort_dir1==0:
            sort_dir1=1
        else:
            sort_dir1=0
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
    if key=="D":
        if sort_mode1!=0:
            if sort_dir2==0:
                sort_dir2=1
            else:
                sort_dir2=0
            prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,active_filters(filter_on,filter_list))
 
    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    if key=="KEY_F(1)":
        utils.show_message("Quick help:\n\
\n\
_Tab:_           Switch to **Search** mode\n\
_Ctrl+O:_        Select NetHack variant to view\n\
_[, ]:_          Switch to next NetHack variant\n\
_Up, Down:_      Scroll through list\n\
_PgUp, PgDn:_    Scorll, but faster\n\
_Home, End:_     Scroll with speed of light\n\
_Enter:_         View selected monster's card\n\
_Ctrl+S:_        Select primary sorting field\n\
_Ctrl+D:_        Change primary sorting direction\n\
_Shift+S:_       Select secondary sorting field\n\
_Shift+D:_       Change secondary sorting direction\n\
(You must use primary field first)\n\
\n\
_Ctrl+F:_        Show filters window\n\
_Ctrl+Q or F10:_ Exit\n")
    return 0

def react_to_key_explanation(card_win,ch,key,alt_ch,mon_name):
    global format_length
    global mode
    global ver_idx
    global ver_idx_temp
    global e_offset
    if key=="KEY_UP" :
        format_length-=1
        if format_length<=0:
            format_length=0
    if key=="KEY_DOWN" :
        format_length+=1
        if format_length>2:
            format_length=2
    if key=="]":
        if ver_idx_temp==-1:
            ver_idx_temp=ver_idx
        ver_idx_temp+=1
        if ver_idx_temp>=len(ver_list):
            ver_idx_temp=0
        read_monsters(ver_list[ver_idx_temp])
        #reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="[":
        if ver_idx_temp==-1:
            ver_idx_temp=ver_idx
        ver_idx_temp-=1
        if ver_idx_temp<0:
            ver_idx_temp=len(ver_list)-1
        read_monsters(ver_list[ver_idx_temp])
        #reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    if key==" ":
        e_offset+=(c.LINES-3)
    if ch==27 or key=="BACKSPACE" or key=="^H":
        ver_idx_temp=-1
        read_monsters(ver_list[ver_idx])
        if mode==EXPLANATION_CARD:
            mode=CARD
        if mode==EXPLANATION_SEARCH:
            mode=SEARCH
    if key=="KEY_F(1)":
        card_win.addstr(0,25,"|Attack can be resisted ------------->",c.color_pair(SEPARATOR_INV)|c.A_BOLD)
        card_win.addstr(1,25,"|Monster can be cancelled --------------------^    ^",c.color_pair(SEPARATOR_INV)|c.A_BOLD)
        card_win.addstr(2,25,"|Attack can be prevented by magic cancellation ----+",c.color_pair(SEPARATOR_INV)|c.A_BOLD)
        card_win.refresh()
        utils.show_message("Quick help:\n\
\n\
_Esc:_           Return to lilst\n\
_[, ]:_          Switch variant\n\
(Variant will be reverted when you press Esc)\n\
\n\
_Ctrl+O:_        Nothing. Use square brackets!\n\
_Up:_            Show less information (main screen)\n\
_Down:_          Show more information (main screen)\n\
_Space:_         Scroll screens if more than one available\n\
_F10 or Ctrl+Q:_ Exit",offset=1)

    return 0

def react_to_key_card(ch,key,alt_ch,mon_name):
    global format_length
    global mode
    global ver_idx
    global ver_idx_temp
    if key=="KEY_UP" :
        format_length-=1
        if format_length<=0:
            format_length=0
    if key=="KEY_DOWN" :
        format_length+=1
        if format_length>2:
            format_length=2
    if key=="]":
        if ver_idx_temp==-1:
            ver_idx_temp=ver_idx
        ver_idx_temp+=1
        if ver_idx_temp>=len(ver_list):
            ver_idx_temp=0
        read_monsters(ver_list[ver_idx_temp])
        #reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="[":
        if ver_idx_temp==-1:
            ver_idx_temp=ver_idx
        ver_idx_temp-=1
        if ver_idx_temp<0:
            ver_idx_temp=len(ver_list)-1
        read_monsters(ver_list[ver_idx_temp])
        #reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="^A":
        mode=EXPLANATION_CARD
    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    if ch==27 or key=="BACKSPACE" or key=="^H":
        ver_idx_temp=-1
        read_monsters(ver_list[ver_idx])
        mode=LIST
    if key=="KEY_F(1)":
        utils.show_message("Quick help:\n\
\n\
_Esc:_           Return to list\n\
_[, ]:_          Switch variant\n\
(Variant will be reverted when you press Esc)\n\
\n\
_Ctrl+O:_        Nothing. Use square brackets!\n\
_Up:_            Show less information\n\
_Down:_          Show more information\n\
_F10 or Ctrl+Q:_ Exit")

    return 0

in_str=""
not_found_after_reload=False
cur_color1=c.COLOR_GREEN
cur_color2=c.COLOR_CYAN
cur_color_bk1=c.COLOR_BLACK
cur_color_bk2=c.COLOR_BLACK
cur_color_s=c.COLOR_WHITE
cur_color_s_bold=0
cur_color_bk_s=c.COLOR_BLUE
reloaded=False
sel=0
skip=0
max_sel=0
tries=0
current_mon=0

def main(s):
    global current_mon
    global bold
    global ver_idx
    global mode
    global ver_selector_idx
    global format_length
    global in_str
    global not_found_after_reload
    global reloaded
    global cur_color1,cur_color2,cur_color_bk1,cur_color_bk2
    global sel,skip
    global sort_mode_sel
    if c.COLORS<16:
        bold=1
    else:
        bold=0
    c.raw()
    c.mousemask(-1)
    c.mouseinterval(0)
    c.curs_set(1)
    s.erase()
    reset_colors()
    #c.init_pair(BK_CARD,c.COLOR_GREEN,c.COLOR_BLACK)
    #c.init_pair(INV_CARD,c.COLOR_YELLOW,c.COLOR_BLACK)
    utils.init_pairs()
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
    s.erase()
    s.refresh()
    colors_n=c.COLORS
    #for x in range(1,17):
    #    s.addstr(f"TEST:{x-1} ",c.color_pair(x))
    #    if x==8:
    #        s.addstr("\n")
    s.refresh()
    search_win=c.newwin(2,c.COLS,0,0)
    search_win.keypad(1)
    search_win.bkgd(' ',c.color_pair(BK))
    search_win.erase()
    search_win.refresh()  
    card_win=c.newwin(c.LINES-2,c.COLS,2,0)
    card_win.bkgd(' ',c.color_pair(BK_CARD))
    card_win.erase()
    card_win.refresh()
    while True:
        results=[]
        not_found_after_reload=False
        if mode in [EXPLANATION_CARD,EXPLANATION_SEARCH]:
            show_card_upper(search_win,results,mon_name)
            show_explanation(card_win,results,mon_name)
        if mode==SELECT_RES:
            show_select_res(card_win)
        if mode==SELECT_PARAM:
            show_select_param(card_win)
        if mode==FILTERS:
            show_filters(card_win,filter_mode_sel)
        if mode==SELECT_SORT1 or mode==SELECT_SORT2:
            show_select_sort(card_win)
        if mode==LIST:
            show_list(card_win,search_win,results)

        if mode==SEARCH:
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
            show_search_upper(search_win,results,mon_name)
            if in_str=="":
                show_hint(search_win)
                move_to_in(search_win,in_str)
            show_card(card_win,results,mon_name)
        if mode==SHOW_ALL:
            show_card(card_win,table,mon_name)
            time.sleep(0.05)
            mon_name=list(table.keys())[current_mon]
            current_mon+=1
            if current_mon>=len(table)-1:
                mode=SEARCH
            continue
        if mode==CARD:
            mon_name=list_mode_mons[list_mode_sel+list_mode_skip]
            show_card_upper(search_win,results,mon_name)
            show_card(card_win,table,mon_name)
        if mode==SELECT_VER:
            show_select_ver(card_win,ver_selector_idx)
            card_win.refresh()
        ch=search_win.getch()
        key=c.keyname(ch).decode("utf-8")        
        alt_ch=""
        if ch==27:
            s.nodelay(True)
            next_key=s.getch()
            if next_key!=-1:
                alt_ch=c.keyname(next_key).decode("utf8")
            else:
                alt_ch=""
            if alt_ch=="[":#home and end keys
                for i in range(2):
                    next_key=s.getch()
                    if next_key!=-1:
                        alt_ch+=c.keyname(next_key).decode("utf8")
            s.nodelay(False)
        if mode==SEARCH:
            res=react_to_key_search(s,search_win,ch,key,alt_ch,results,mon_name)
            if res!=0:
                break
            continue
        if mode==SELECT_VER:
            react_to_key_select_ver(ch,key,alt_ch,mon_name)
            continue
        if mode==LIST:
            res=react_to_key_list(ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue
        if mode==FILTERS:
            res=react_to_key_filters(card_win,search_win,ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue
        if mode==SELECT_RES:
            res=react_to_key_select_res(card_win,search_win,ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue
        if mode==SELECT_PARAM:
            res=react_to_key_select_param(card_win,search_win,ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue
        if mode==CARD:
            res=react_to_key_card(ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue
        if mode==SELECT_SORT1 or mode==SELECT_SORT2:
            res=react_to_key_select_sort(ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue
        if mode in [EXPLANATION_CARD,EXPLANATION_SEARCH]:
            res=react_to_key_explanation(card_win,ch,key,alt_ch,mon_name)
            if res!=0:
                break
            continue

if __name__=="__main__":
    make_ver_list()
    try:
        last=open("default.txt","r",encoding="utf-8")
        last_ver_file=last.readline().strip()
        cur_color1=int(last.readline().strip())
        cur_color_bk1=int(last.readline().strip())
        cur_color2=int(last.readline().strip())
        cur_color_bk2=int(last.readline().strip())
        cur_color_s=int(last.readline().strip())
        cur_color_bk_s=int(last.readline().strip())
        cur_color_s_bold=int(last.readline().strip())
        for x in range(len(ver_list)):
            if ver_list[x]==last_ver_file:
                ver_idx=x
                break
        last.close
    except:
        pass
    read_monsters(ver_list[ver_idx])
    reset_sort()
    reset_filters()
    os.environ.setdefault('ESCDELAY', '25')
    c.wrapper(main)
