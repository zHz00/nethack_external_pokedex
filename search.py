import csv
import curses as c
import os
import datetime
import time

from nhconstants_flags_raw import *
from nhconstants_flags import *
from nhconstants_atk import *
from nhconstants_common import *
from checker import *
from make_card import *

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

SELECT_VER=1
SEARCH=2
CARD=3
LIST=4
SHOW_ALL=5
SELECT_SORT1=6
SELECT_SORT2=7

mode=SEARCH
mode_prev=SEARCH


cur_len_res=66
cur_len_con=44
cur_len_atk=94

max_len_res=0
max_len_con=0


table=dict()
table_temp=[]
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


def prepare_list(sort_field1,sort_field2,dir1,dir2,filters):
    global list_mode_mons
    global list_mode_max
    if sort_field1==0:
        list_mode_mons=list(table.keys()).copy()
        list_mode_max=len(list_mode_mons)
    else:
        #list_mode_mons=sorted(list_mode_mons,key=double_sort(sort_field1,dir1,sort_field2,dir2))
        list_mode_mons=\
            sorted(\
                sorted(\
                    list_mode_mons,
                    key=sort_mode_lambdas[sort_field2],
                    reverse=bool(dir2)),
                key=sort_mode_lambdas[sort_field1],
                reverse=bool(dir1))

MAX_SEARCH=50

def show_ver_format(search_win):
    out_mode=""
    if mode==LIST:
        out_mode="Format:list"
    else:
        if format_length==0:
            out_mode="Format:mini"
        if format_length==1:
            out_mode="Format:full"
        if format_length==2:
            out_mode="Format:ext"
    search_win.addstr(0,65,out_mode,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    if ver_idx_temp!=-1:
        search_win.addstr(0,55,"Ver:"+get_ver_temp(),c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
        search_win.addstr(1,49,"(List Ver:"+get_ver()+")",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    else:
        search_win.addstr(0,55,"Ver:"+get_ver(),c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
        if mode==LIST:
            search_win.addstr(1,55,f"{list_mode_skip+list_mode_sel+1}/{list_mode_max}")


def show_ver_list(s,sel:int):
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

def show_sort_list(s,sel:int):
    w1=20
    w2=0
    w3=0
    cap1="Sort field"
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

def make_ver_list():
    global ver_list,ver_idx
    global ver_name,ver_n
    ver_list=os.listdir(data_folder)
    if len(ver_list)==0:
        print("No data files found. Exiting...")
        exit(1)
    ver_idx=0
    ver_name=[""]*len(ver_list)
    ver_n=[0]*len(ver_list)
    for x in range(len(ver_list)):
        monfile=open(data_folder+ver_list[x],"r")
        reader=csv.reader(monfile)
        for y,mon in enumerate(reader):
            if y==0:
                ver_name[x]=mon[0]
        ver_n[x]=y-1
        

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
    

def read_monsters(file):
    global table,table_temp
    global disable_sorting
    global wingy
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

BK=20
INV=21
BK_CARD=22
INV_CARD=23
SEPARATOR_BK=24
SEPARATOR_INV=25
SEPARATOR_BLACK=26

def out_input(s,in_str):

    s.clear()
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



def show_hello_msg(card_win):
    hello_msg=["=== Nethack external Pokedex ===",
    "Enter monster name to see its properties. Keys:"]
    #"Ctrl+O: Choose variant, or PgUp/PgDn to switch",
    #"LEFT, RIGHT: Scroll search results",
    #"UP, DOWN: Change output format",
    #"ESC: Clear search; F10: Exit"

    block1=["Ctrl+O, [, ]: Choose variant",
            "Tab: Switch to List mode",
            "F10, Ctrl+Q: Exit"]
    block2=["UP, DOWN: Change format",
            "LEFT, RIGHT: Scroll results",
            "ESC: Clear search"]
    col1=10
    col2=45
    card_win.chgat(-1,c.color_pair(BK_CARD))
    card_win.addstr(0,int((SCR_WIDTH-len(hello_msg[0]))/2),hello_msg[0],c.color_pair(INV_CARD)|c.A_BOLD)
    card_win.addstr(1,int((SCR_WIDTH-len(hello_msg[1]))/2),hello_msg[1],c.color_pair(INV_CARD))
    for i in range(len(block1)):
        card_win.addstr(i+2,col1,block1[i])
        card_win.addstr(i+2,col2,block2[i])
    card_win.refresh()

def show_not_found_msg(card_win,mon_name):
    msg=[f"'{mon_name}' does not extist in current version.","Try another search or switch version."]
    card_win.chgat(-1,c.color_pair(BK_CARD))
    card_win.addstr(0,int((SCR_WIDTH-len(msg[0]))/2),msg[0],c.color_pair(INV_CARD)|c.A_BOLD)
    card_win.addstr(1,int((SCR_WIDTH-len(msg[1]))/2),msg[1],c.color_pair(BK_CARD)|c.A_BOLD)
    card_win.refresh()

def show_search_wnd(search_win,results,mon_name):
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


def show_list_wnd(search_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global sort_mode1
    global sort_dir1

    sort_dir1_str="Ascending" if sort_dir1==0 else "Descending"
    sort_dir2_str="Ascending" if sort_dir2==0 else "Descending"

    search_win.clear()

    search_win.addstr(0,0,f"Sort1 (Ctrl+S) :{sort_mode_str[sort_mode1]:10}|Dir1 (Ctrl+D) :{sort_dir1_str}",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    if sort_mode1!=0:
        search_win.addstr(1,0,f"Sort2 (Shift+S):{sort_mode_str[sort_mode2]:10}|Dir2 (Shift+D):{sort_dir2_str}",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    else:
        search_win.addstr(1,0,f"Tab: Switch to search mode",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))

    show_ver_format(search_win)
    disable_cursor()
    search_win.refresh()

def show_card_header_wnd(search_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global sort_mode1
    global sort_dir1

    search_win.clear()

    search_win.addstr(0,0,"Monster:"+mon_name,c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))
    search_win.addstr(1,0,f"Esc: Back to list",c.color_pair(BK)|(c.A_BOLD if cur_color_s_bold else 0))

    show_ver_format(search_win)
    disable_cursor()
    search_win.refresh()



def show_card_wnd(card_win,results,mon_name):
    global format_length
    global in_str,not_found_after_reload
    global sel,skip
    global max_sel
    global ver_idx
    global tries
    card_win.clear()
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


def react_to_key_search(s,search_win,ch,key,results,mon_name):
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
        c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
        c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
    if key=="2":
        cur_color_bk1+=1
        if cur_color_bk1>7:
            cur_color_bk1=0
        c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
        c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
        c.init_pair(SEPARATOR_BK,c.COLOR_WHITE,cur_color_bk1)
        c.init_pair(SEPARATOR_INV,c.COLOR_WHITE,cur_color_bk2)
    if key=="3":
        cur_color2+=1
        if cur_color2>7:
            cur_color2=0
        c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
        c.init_pair(INV_CARD,cur_color2,cur_color_bk2)          
    if key=="4":
        cur_color_bk2+=1
        if cur_color_bk2>7:
            cur_color_bk2=0
        c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
        c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
        c.init_pair(SEPARATOR_BK,c.COLOR_WHITE,cur_color_bk1)
        c.init_pair(SEPARATOR_INV,c.COLOR_WHITE,cur_color_bk2)  
    if key=="5":
        cur_color_s+=1
        if cur_color_s>7:
            cur_color_s=0
            if cur_color_s_bold==0:
                cur_color_s_bold=1
            else:
                cur_color_s_bold=0
        c.init_pair(BK,cur_color_s,cur_color_bk_s)
        c.init_pair(INV,cur_color_bk_s,cur_color_s)
    if key=="6":
        cur_color_bk_s+=1
        if cur_color_bk_s>7:
            cur_color_bk_s=0
        c.init_pair(BK,cur_color_s,cur_color_bk_s)
        c.init_pair(INV,cur_color_bk_s,cur_color_s)

    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    if key=="KEY_F(14)":
        mode=SHOW_ALL
        current_mon=0
        return 0
    if key=="KEY_F(1)":
        os.makedirs("reports",exist_ok=True)
        s.clear()
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
        if mon_name!="":
            reloaded=True
    if key=="[":
        ver_idx-=1
        if ver_idx<0:
            ver_idx=len(ver_list)-1
        read_monsters(ver_list[ver_idx])
        reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="^O":
        mode_prev=SEARCH
        mode=SELECT_VER
        ver_selector_idx=ver_idx
    if key=="^I":
        mode=LIST
        format_length=2
        prepare_list(0,0,0,0,0)
        list_mode_sel=0
        list_mode_skip=0

    return 0

def react_to_key_select_ver(ch,key,mon_name):
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
        prepare_list(0,0,0,0,0)
        list_mode_sel=0
        list_mode_skip=0
        if mon_name!="":
            reloaded=True
        mode=mode_prev


def react_to_key_select_sort(ch,key,mon_name):
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
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,0)
        mode=LIST
    return 0

def react_to_key_list(ch,key,mon_name):
    global list_mode_sel
    global list_mode_skip
    global mode
    global sort_dir1,sort_dir2
    global ver_idx,ver_selector_idx
    global mode_prev
    global reloaded
    if key=="]":
        ver_idx+=1
        if ver_idx>=len(ver_list):
            ver_idx=0
        read_monsters(ver_list[ver_idx])
        reset_sort()
        prepare_list(0,0,0,0,0)
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
        prepare_list(0,0,0,0,0)
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
        if list_mode_sel<LIST_LINES-1:
            list_mode_sel+=1
        else:
            if list_mode_skip+list_mode_sel<list_mode_max-1:
                list_mode_skip+=1
    if key=="KEY_PPAGE" :
        list_mode_skip-=LIST_LINES
        if list_mode_skip<0:
            list_mode_skip=0
    if key=="KEY_NPAGE" :
        list_mode_skip+=LIST_LINES
        if list_mode_skip+LIST_LINES>list_mode_max-1:
            list_mode_skip=list_mode_max-LIST_LINES
    if key=="KEY_HOME":# or alt_ch=="[H" or alt_ch=="[1~":
        list_mode_skip=0
        list_mode_sel=0
    if key=="KEY_END":# or key=="KEY_A1" or alt_ch=="[4~":
        list_mode_skip=list_mode_max-LIST_LINES
        list_mode_sel=LIST_LINES-1
    if key=="^I":
        mode=SEARCH
    if key=="^J" or key=="^M":
        mode=CARD
    if key=="^S":
        mode=SELECT_SORT1
    if key=="S":
        if sort_mode1!=0:
            mode=SELECT_SORT2
    if key=="^D":
        if sort_dir1==0:
            sort_dir1=1
        else:
            sort_dir1=0
        prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,0)
    if key=="D":
        if sort_mode1!=0:
            if sort_dir2==0:
                sort_dir2=1
            else:
                sort_dir2=0
            prepare_list(sort_mode1,sort_mode2,sort_dir1,sort_dir2,0)
 
    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    return 0

def react_to_key_card(ch,key,mon_name):
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
        reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="[":
        if ver_idx_temp==-1:
            ver_idx_temp=ver_idx
        ver_idx_temp-=1
        if ver_idx_temp<0:
            ver_idx_temp=len(ver_list)-1
        read_monsters(ver_list[ver_idx_temp])
        reset_sort()
        if mon_name!="":
            reloaded=True
    if key=="KEY_F(10)" or key=="^Q":
        save_settings()
        return -1
    if ch==27 or key=="BACKSPACE" or key=="^H":
        ver_idx_temp=-1
        read_monsters(ver_list[ver_idx])
        mode=LIST

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
    if c.COLORS<16:
        bold=1
    else:
        bold=0
    c.raw()
    c.mousemask(-1)
    c.mouseinterval(0)
    c.curs_set(1)
    s.clear()
    c.init_pair(BK,cur_color_s,cur_color_bk_s)
    c.init_pair(INV,cur_color_bk_s,cur_color_s)

    c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
    c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
    c.init_pair(SEPARATOR_BK,c.COLOR_WHITE,cur_color_bk1)
    c.init_pair(SEPARATOR_INV,c.COLOR_WHITE,cur_color_bk2)
    c.init_pair(SEPARATOR_BLACK,c.COLOR_WHITE,c.COLOR_BLACK)
    #c.init_pair(BK_CARD,c.COLOR_GREEN,c.COLOR_BLACK)
    #c.init_pair(INV_CARD,c.COLOR_YELLOW,c.COLOR_BLACK)
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
    search_win=c.newwin(2,c.COLS,0,0)
    search_win.keypad(1)
    search_win.bkgd(' ',c.color_pair(BK))
    search_win.clear()
    search_win.refresh()  
    card_win=c.newwin(c.LINES-2,c.COLS,2,0)
    card_win.bkgd(' ',c.color_pair(BK_CARD))
    card_win.clear()
    card_win.refresh()
    while True:
        results=[]
        not_found_after_reload=False
        if mode==SELECT_SORT1 or mode==SELECT_SORT2:
            show_sort_list(card_win,sort_mode1)
        if mode==LIST:
            selected_mon_name=""
            card_win.clear()
            card_win.addstr(0,1,one_line_header_str(),c.color_pair(SEPARATOR_BK))
            for x in range(LIST_LINES):
                current_mon=table[list_mode_mons[x+list_mode_skip]]
                card_win.move(x+1,0)
                out_symbol(card_win,current_mon)
                line=make_card_one_line(current_mon,list_mode_mons[x+list_mode_skip])#key is monster name, it can be different from "name" column
                if x==list_mode_sel:
                    selected_mon_name=list_mode_mons[x+list_mode_skip]
                    card_win.addstr(x+1,1,line[:SCR_WIDTH-2],c.color_pair(BK_CARD))
                    if len(line)>=SCR_WIDTH-1:#-1 for monster character in first column
                        card_win.insch(x+1,SCR_WIDTH-1,line[SCR_WIDTH-2],c.color_pair(BK_CARD))
                else:
                    card_win.addstr(x+1,1,line[:SCR_WIDTH-2],c.color_pair(INV_CARD))
                    if len(line)>=SCR_WIDTH-1:#-1 for monster character in first column
                        card_win.insch(x+1,SCR_WIDTH-1,line[SCR_WIDTH-2],c.color_pair(INV_CARD))
            card_win.refresh()
            show_list_wnd(search_win,results,selected_mon_name)

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
            show_search_wnd(search_win,results,mon_name)
            show_card_wnd(card_win,results,mon_name)
        if mode==SHOW_ALL:
            show_card_wnd(search_win,card_win,table,mon_name)
            time.sleep(0.05)
            mon_name=list(table.keys())[current_mon]
            current_mon+=1
            if current_mon>=len(table)-1:
                mode=SEARCH
            continue
        if mode==CARD:
            mon_name=list_mode_mons[list_mode_sel+list_mode_skip]
            show_card_header_wnd(search_win,results,mon_name)
            show_card_wnd(card_win,table,mon_name)
        if mode==SELECT_VER:
            show_ver_list(card_win,ver_selector_idx)
            card_win.refresh()
        ch=search_win.getch()
        key=c.keyname(ch).decode("utf-8")
        if mode==SEARCH:
            res=react_to_key_search(s,search_win,ch,key,results,mon_name)
            if res!=0:
                break
            continue
        if mode==SELECT_VER:
            react_to_key_select_ver(ch,key,mon_name)
            continue
        if mode==LIST:
            res=react_to_key_list(ch,key,mon_name)
            if res!=0:
                break
        if mode==CARD:
            res=react_to_key_card(ch,key,mon_name)
            if res!=0:
                break
        if mode==SELECT_SORT1 or mode==SELECT_SORT2:
            res=react_to_key_select_sort(ch,key,mon_name)
            if res!=0:
                break            

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
    os.environ.setdefault('ESCDELAY', '25')
    c.wrapper(main)
