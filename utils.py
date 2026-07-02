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

def show_message(s,noans=False,offset=0,minimal=False):
    W=60
    if c.COLS<W:
        W=c.COLS
    c.curs_set(0)
    max=0
    s=s.split("\n")
    for l in s:
        if len(l)>max:
            max=len(l)
    H=len(s)+5
    if c.LINES<H:
        H=c.LINES
    w=c.newwin(H,W,int((c.LINES-H)/2)+offset,int((c.COLS-W)/2))
    w.border()
    if minimal:
        s_out=s[0]
        if H>=3:
            y_pos=1
        else:
            y_pos=0
        if W>=3:
            x_pos=1
            s_out=s_out[:W-2]
        else:
            x_pos=0
            s_out=s_out[:W]
        w.addstr(y_pos,x_pos,s_out)
        if noans==False:
            w.getch()
        del w
        return
        
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

def multiline_textpad(s,y,x,width,height,attr):
    global user_cancel
    s.keypad(1)
    s.refresh()
    c.curs_set(1)
    win = s.derwin(height,width,y,x)
    win.bkgd(" ",attr)
    win.erase()
    win.refresh()
    #tb = c.textpad.Textbox(win)
    #tb.insert_mode=True
    #tb.stripspaces=False
    #text = tb.edit(edit_keys_multiline)
    lines=["test line 1 01234567890123456789","012345678qq90123456789 test line 2",
    "test line 3 01234567890123456789","01234567890123456789 test line 4",
    "test line 5 01234567890123456789","0123456789012qqqqqqq3456789 test line 6",
    "test line 7 01234567890123456789","01234567890123456789 test line 8",
    "test line 9 01234567890123456789","0123qqqq4567890123456789 test line 10"]
    xscroll=0
    yscroll=0
    xc=0
    yc=0
    win.move(xc,yc)
    while True:
        win.erase()
        c.curs_set(0)
        for i in range(len(lines)):
            if i<yscroll:
                continue
            if i-yscroll>height-1:
                break
            line=lines[i]
            line=line[xscroll:xscroll+width-1]
            #line+=" "*(width-len(line)-1)
            win.move(i-yscroll,0)
            win.addstr(line)
        win.refresh()
        c.curs_set(1)
        win.move(yc,xc)
        ch=win.getch()
        key=c.keyname(ch).decode("utf-8")
        if ch==27:
            break
        xpos=xc+xscroll
        ypos=yc+yscroll

        if key=="KEY_LEFT":
            if xc>0:
                xc-=1
            else:
                if xscroll>0:
                    xscroll-=1
        if key=="KEY_RIGHT":
            if xc<width-1:
                xc+=1
            else:
                xscroll+=1
        if key=="KEY_UP":
            if yc>0:
                yc-=1
            else:
                if yscroll>0:
                    yscroll-=1
        if key=="KEY_DOWN":
            if yc<height-1:
                yc+=1
            else:
                yscroll+=1
        if key=="KEY_HOME":
            xscroll=0
            xc=0
        if key=="KEY_END":
            if ypos>=len(lines):
                xc=0
                xscroll=0
            else:
                if len(lines[ypos])<width:
                    xscroll=0
                    xc=len(lines[ypos])
                else:
                    xc=width-1
                    xscroll=len(lines[ypos])-width+1
        if key=="^H":
            if xpos==0:
                continue
            if xc>0:
                xc-=1
            else:
                if xscroll>0:
                    xscroll-=1
            if ypos<len(lines) and xpos<len(lines[ypos])+1:
                lines[ypos]=lines[ypos][:xpos-1]+lines[ypos][xpos:]
        if key=="KEY_DC":
            if ypos<len(lines)-1 and xpos>=len(lines[ypos]):
                lines[ypos]=lines[ypos]+lines[ypos+1]
                lines.pop(ypos+1)
            else:
                if ypos<len(lines) and xpos<len(lines[ypos])+1:
                    lines[ypos]=lines[ypos][:xpos]+lines[ypos][xpos+1:]
        if key=="^J" or key=="^M":
            xc=0
            xscroll=0
            if yc<height-1:
                yc+=1
            else:
                yscroll+=1
            if ypos<len(lines):
                if xpos>=len(lines[ypos]):
                    lines.insert(ypos+1,"")
                else:
                    remainder=lines[ypos][xpos:]
                    lines.insert(ypos+1,remainder)
                    lines[ypos]=lines[ypos][:xpos]

        if len(key)==1:#ordinary character
            if ypos>len(lines)-1:
                lines.extend([""]*(ypos-len(lines)+1))
            if xpos>len(lines[ypos]):
                lines[ypos]=lines[ypos]+" "*(xpos-len(lines[ypos]))
            #insert mode
            lines[ypos]=lines[ypos][:xpos]+key+lines[ypos][xpos:]
            if xc<width-1:
                xc+=1
            else:
                xscroll+=1
        win.move(yc,xc)
    c.curs_set(0)
    del win
    if user_cancel:
        user_cancel=False
        return ""
    else:
        return "\n".join(lines)


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

def edit_keys_multiline(key):
    global user_cancel
    key_txt=c.keyname(key).decode("utf-8")
    #if key == 10 or key == 13 or key_txt=="PADENTER":
        #key = 7
    if key == 27:
        user_cancel=True
        key = 7
    return key


if __name__=="__main__":
    print("Not main module! ("+__file__+")")

