import csv
import curses as c
import os
import itertools
import datetime

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
ver_idx=-1

MAX_SEARCH=50

def make_ver_list():
    global ver_list,ver_idx
    ver_list=os.listdir(data_folder)
    if len(ver_list)==0:
        print("No data files found. Exiting...")
        exit(1)
    ver_idx=0

def get_ver()->str:
    return ver_list[ver_idx].split(".")[0]




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
    attr=c.color_pair(BK)
    ch_prev=""
    idx=0
    for ch in out_str:
        if ch_prev=="|":
            attr=c.color_pair(BK)
        if ch=="*":
            attr=c.color_pair(INV)
        if ch=="|":
            attr=c.color_pair(BK)|c.A_BOLD
        ch_prev=ch
        if ch!="*" and idx<SCR_WIDTH-1:
            s.addstr(ch,attr)
            idx+=1
        
    s.chgat(c.color_pair(BK))
    s.refresh()
    return (cur-skip,selected_appeared)

def move_to_in(s,in_str):
    s.move(0,1+len(in_str))
    c.curs_set(1)


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
    cur_color1=c.COLOR_GREEN
    cur_color2=c.COLOR_CYAN
    cur_color_bk1=c.COLOR_BLACK
    cur_color_bk2=c.COLOR_BLACK
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
        if key=="9":
            cur_color1+=1
            if cur_color1>7:
                cur_color1=0
            c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
            c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
        if key=="0":
            cur_color2+=1
            if cur_color2>7:
                cur_color2=0
            c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
            c.init_pair(INV_CARD,cur_color2,cur_color_bk2)          
        if key=="]":
            cur_color_bk1+=1
            if cur_color_bk1>7:
                cur_color_bk1=0
            c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
            c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
            c.init_pair(SEPARATOR_BK,c.COLOR_WHITE,cur_color_bk1)
            c.init_pair(SEPARATOR_INV,c.COLOR_WHITE,cur_color_bk2)
        if key=="[":
            cur_color_bk2+=1
            if cur_color_bk2>7:
                cur_color_bk2=0
            c.init_pair(BK_CARD,cur_color1,cur_color_bk1)
            c.init_pair(INV_CARD,cur_color2,cur_color_bk2)
            c.init_pair(SEPARATOR_BK,c.COLOR_WHITE,cur_color_bk1)
            c.init_pair(SEPARATOR_INV,c.COLOR_WHITE,cur_color_bk2)  
        if key=="KEY_F(10)":
            last=open("default.txt","w",encoding="utf-8")
            last.write(ver_list[ver_idx])
            last.close()
            break
        if key=="KEY_F(1)":
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

        if len(key)==1 and key not in ["9","0","[","]"]:
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
    try:
        last=open("default.txt","r",encoding="utf-8")
        last_ver_file=last.read().strip()
        for x in range(len(ver_list)):
            if ver_list[x]==last_ver_file:
                ver_idx=x
                break
        last.close
    except:
        pass
    read_monsters(ver_list[ver_idx])
    c.wrapper(main)
