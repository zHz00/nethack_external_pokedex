import curses as c
import json

colors_table={
    0:c.COLOR_BLACK,
    1:c.COLOR_RED,
    2:c.COLOR_GREEN,
    3:c.COLOR_YELLOW,
    4:c.COLOR_BLUE,
    5:c.COLOR_MAGENTA,
    6:c.COLOR_CYAN,
    7:c.COLOR_WHITE
}

colors_reverse_table={v:k for k,v in colors_table.items()}

cur_color1=c.COLOR_GREEN
cur_color2=c.COLOR_CYAN
cur_color_bk1=c.COLOR_BLACK
cur_color_bk2=c.COLOR_BLACK
cur_color_s=c.COLOR_WHITE
cur_color_s_bold=0
cur_color_bk_s=c.COLOR_BLUE

cur_theme_name="Default"
cur_theme_idx=0

fname="colors.json"
color_themes=dict()

def switch_theme(n:int):
    global cur_color1,cur_color2,cur_color_bk1,cur_color_bk2
    global cur_color_s,cur_color_s_bold,cur_color_bk_s
    global cur_theme_idx,cur_theme_name
    cur_color1=colors_table[int(color_themes[n]["colors_current"]["fg1"])]
    cur_color2=colors_table[int(color_themes[n]["colors_current"]["fg2"])]
    cur_color_bk1=colors_table[int(color_themes[n]["colors_current"]["bk1"])]
    cur_color_bk2=colors_table[int(color_themes[n]["colors_current"]["bk2"])]
    cur_color_s=colors_table[int(color_themes[n]["colors_current"]["fg_upper"])]
    cur_color_s_bold=int(color_themes[n]["colors_current"]["fg_upper_bold"])
    cur_color_bk_s=colors_table[int(color_themes[n]["colors_current"]["bk_upper"])]
    cur_theme_idx=n
    cur_theme_name=color_themes[n]["name"]

def restore_theme(n:int):
    global color_themes
    color_themes[n]["colors_current"]["fg1"]=color_themes[n]["colors_default"]["fg1"]
    color_themes[n]["colors_current"]["fg2"]=color_themes[n]["colors_default"]["fg2"]
    color_themes[n]["colors_current"]["bk1"]=color_themes[n]["colors_default"]["bk1"]
    color_themes[n]["colors_current"]["bk2"]=color_themes[n]["colors_default"]["bk2"]
    color_themes[n]["colors_current"]["fg_upper"]=color_themes[n]["colors_default"]["fg_upper"]
    color_themes[n]["colors_current"]["fg_upper_bold"]=color_themes[n]["colors_default"]["fg_upper_bold"]
    color_themes[n]["colors_current"]["bk_upper"]=color_themes[n]["colors_default"]["bk_upper"]
    switch_theme(n)

def new_defaults(n:int):
    global color_themes
    color_themes[n]["colors_default"]["fg1"]=color_themes[n]["colors_current"]["fg1"]
    color_themes[n]["colors_default"]["fg2"]=color_themes[n]["colors_current"]["fg2"]
    color_themes[n]["colors_default"]["bk1"]=color_themes[n]["colors_current"]["bk1"]
    color_themes[n]["colors_default"]["bk2"]=color_themes[n]["colors_current"]["bk2"]
    color_themes[n]["colors_default"]["fg_upper"]=color_themes[n]["colors_current"]["fg_upper"]
    color_themes[n]["colors_default"]["fg_upper_bold"]=color_themes[n]["colors_current"]["fg_upper_bold"]
    color_themes[n]["colors_default"]["bk_upper"]=color_themes[n]["colors_current"]["bk_upper"]
    switch_theme(n)    

def save_theme(n:int):
    global color_themes
    color_themes[n]["colors_current"]["fg1"]=str(colors_reverse_table[cur_color1])
    color_themes[n]["colors_current"]["fg2"]=str(colors_reverse_table[cur_color2])
    color_themes[n]["colors_current"]["bk1"]=str(colors_reverse_table[cur_color_bk1])
    color_themes[n]["colors_current"]["bk2"]=str(colors_reverse_table[cur_color_bk2])
    color_themes[n]["colors_current"]["fg_upper"]=str(colors_reverse_table[cur_color_s])
    color_themes[n]["colors_current"]["fg_upper_bold"]=str(cur_color_s_bold)
    color_themes[n]["colors_current"]["bk_upper"]=str(colors_reverse_table[cur_color_bk_s])

def load_colors():
    global color_themes
    color_themes=dict()
    f=open(fname,"r",encoding="utf-8")
    color_themes=json.load(f)
    switch_theme(cur_theme_idx)

def save_colors():
    f=open(fname,"w",encoding="utf-8")
    json.dump(color_themes,f,indent=1)