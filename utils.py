import curses as c
import curses.textpad

user_cancel=False

HELP_NORMAL = 30
HELP_HEADER = 31
HELP_BOLD = 32
HELP_ITALIC = 33
HELP_NAME = 34

def init_pairs():
    c.init_pair(HELP_NORMAL,c.COLOR_WHITE,c.COLOR_BLACK)#black on black: not visible
    c.init_pair(HELP_HEADER,c.COLOR_WHITE,c.COLOR_BLACK)
    c.init_pair(HELP_BOLD,c.COLOR_MAGENTA,c.COLOR_BLACK)
    c.init_pair(HELP_ITALIC,c.COLOR_CYAN,c.COLOR_BLACK)
    c.init_pair(HELP_NAME,c.COLOR_YELLOW,c.COLOR_BLACK)

def show_message(s,noans=False,offset=0):
    W=60
    c.curs_set(0)
    max=0
    s=s.split("\n")
    for l in s:
        if len(l)>max:
            max=len(l)
    H=len(s)+5
    w=c.newwin(H,W,int((c.LINES-H)/2)+offset,int((c.COLS-W)/2))
    w.border()
    begin=int((W-max)/2)
    if begin<0:
        begin=0
    for i in range(len(s)):
        if i<len(s):
            w.move(i-0,0)
            prev_ch=''
            ln=s[i]
            mode=HELP_NORMAL
            ch_counter=0
            for ch in range(len(s[i])):
                if ln[ch]=='\\' and prev_ch!='\\':
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch!='\\' and mode==HELP_NORMAL:
                    mode=HELP_BOLD
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch!='\\' and prev_ch!='*' and mode==HELP_BOLD:
                    mode=HELP_NORMAL
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='_' and prev_ch!='\\' and mode==HELP_NORMAL:
                    mode=HELP_NAME
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='_' and prev_ch!='\\' and prev_ch!='_' and mode==HELP_NAME:
                    mode=HELP_NORMAL
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch=='*' and mode in [HELP_NORMAL,HELP_BOLD]:
                    mode=HELP_ITALIC
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch=='*' and mode==HELP_ITALIC:
                    mode=HELP_NORMAL
                    prev_ch=ln[ch]
                    continue
                if ln[ch]=='*' and prev_ch!='\\':#we have asterisk that was not caught before. probably this is **. Skipping
                    prev_ch=ln[ch]
                    continue


                if ln[ch]=='#' and ch==0:
                    mode=HELP_HEADER
                    prev_ch=ln[ch]
                    continue
                w.addstr(1+i,begin+ch_counter,ln[ch],c.color_pair(mode))
                ch_counter+=1
                prev_ch=ln[ch]
    hint="<Hit any key to close>"
    w.addstr(H-3,int((W-len(hint))/2),hint)
    if noans==False:
        w.getch()
    del w

def textpad(s,y,x,width):
    global user_cancel
    s.keypad(1)
    s.refresh()
    c.curs_set(1)
    win = s.derwin(1,width,y,x)
    win.erase()
    win.refresh()
    tb = c.textpad.Textbox(win)
    tb.stripspaces=False
    text = tb.edit(edit_keys)
    c.curs_set(0)
    del win
    if user_cancel:
        user_cancel=False
        return ""
    else:
        return text

user_cancel=False#there is no way to distinguish Esc from Enter after curses.TextBox.edit(), so i use global variable
def edit_keys(key):
    global user_cancel
    key_txt=c.keyname(key).decode("utf-8")
    if key == 10 or key == 13 or key_txt=="PADENTER":
        key = 7
    if key == 27:
        user_cancel=True
        key = 7
    return key

if __name__=="__main__":
    print("Not main module! ("+__file__+")")

