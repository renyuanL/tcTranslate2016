#!/usr/bin/env python3
'''
ryViewer2.py

__main__viewer.py

中文龜程式 翻譯瀏覽器。

呂仁園 中文翻譯 修改。

2014/12/24, 2015/01/18, 01/23


'''
"""
  ----------------------------------------------
      turtleDemo - Help
  ----------------------------------------------

  This document has two sections:

  (1) How to use the demo viewer
  (2) How to add your own demos to the demo repository


  (1) How to use the demo viewer.

  Select a demoscript from the example menu.
  The (syntax coloured) source code appears in the left
  source code window. IT CANNOT BE EDITED, but ONLY VIEWED!

  The demo viewer windows can be resized. The divider between text
  and canvas can be moved by grabbing it with the mouse. The text font
  size can be changed from the menu and with Control/Command '-'/'+'.
  It can also be changed on most systems with Control-mousewheel
  when the mouse is over the text.

  Press START button to start the demo.
  Stop execution by pressing the STOP button.
  Clear screen by pressing the CLEAR button.
  Restart by pressing the START button again.

  SPECIAL demos, such as clock.py are those which run EVENTDRIVEN.

      Press START button to start the demo.

      - Until the EVENTLOOP is entered everything works
      as in an ordinary demo script.

      - When the EVENTLOOP is entered, you control the
      application by using the mouse and/or keys (or it's
      controlled by some timer events)
      To stop it you can and must press the STOP button.

      While the EVENTLOOP is running, the examples menu is disabled.

      - Only after having pressed the STOP button, you may
      restart it or choose another example script.

   * * * * * * * *
   In some rare situations there may occur interferences/conflicts
   between events concerning the demo script and those concerning the
   demo-viewer. (They run in the same process.) Strange behaviour may be
   the consequence and in the worst case you must close and restart the
   viewer.
   * * * * * * * *


   (2) How to add your own demos to the demo repository

   - Place the file in the same directory as turtledemo/__main__.py
     IMPORTANT! When imported, the demo should not modify the system
     by calling functions in other modules, such as sys, tkinter, or
     turtle. Global variables should be initialized in main().

   - The code must contain a main() function which will
     be executed by the viewer (see provided example scripts).
     It may return a string which will be displayed in the Label below
     the source code window (when execution has finished.)

   - In order to run mydemo.py by itself, such as during development,
     add the following at the end of the file:

    if __name__ == '__main__':
        main()
        mainloop()  # keep window open

    python -m turtledemo.mydemo  # will then run it

   - If the demo is EVENT DRIVEN, main must return the string
     "EVENTLOOP". This informs the demo viewer that the script is
     still running and must be stopped by the user!

     If an "EVENTLOOP" demo runs by itself, as with clock, which uses
     ontimer, or minimal_hanoi, which loops by recursion, then the
     code should catch the turtle.Terminator exception that will be
     raised when the user presses the STOP button.  (Paint is not such
     a demo; it only acts in response to mouse clicks and movements.)
"""
import sys
import os
import random

from tkinter import *
from idlelib.Percolator import Percolator
from idlelib.ColorDelegator import ColorDelegator
from idlelib.textView import view_text
from turtledemo import __doc__ as about_turtledemo

#import turtle as turtleOld

import turtle_tc as turtle
#import turtle_jp as turtle # 勿貪心，淺嘗即可。免得失去焦點。

import time
import inspect

from ryTranslate import 翻譯一個檔案

try:
    import ryGoogleTTS
except:
    print('import ryGoogleTTS: fail, No TTS functions ')
    pass

import io
import tokenize as tn

import importlib


def main():
    demo= DemoWindow()    
    demo.root.mainloop()



#------------------------------------------------------

darwin= sys.platform == 'darwin' # 測試 是否在 macOS 上，有些特殊問題要解決（似乎比較麻煩）

STARTUP= 1
READY= 2
RUNNING= 3
DONE= 4
EVENTDRIVEN= 5

menufont= ("Arial", 12, NORMAL)
btnfont=  ("Arial", 12, 'bold')
txtfont=  ['Lucida Console', 12, 'normal']

MINIMUM_FONT_SIZE= 6
MAXIMUM_FONT_SIZE= 100
font_sizes= [8, 9, 10, 11, 12, 14, 18, 20, 22, 24, 30]

# 原本是拿 本程式所在地的 英文程式
demo_dir= os.path.dirname(os.path.abspath(__file__))
def getExampleEntries000():
    return [entry[:-3] for entry in os.listdir(demo_dir) if
            entry.endswith(".py") and entry[0] != '_']

# 我把它換成 直接拿官方的 turtledemo 來展示。
import turtledemo
turtledemoDir= os.path.dirname(os.path.abspath(turtledemo.__file__))
def getExampleEntries():

    rootDir= turtledemoDir #demo_dir

    for r, dL, fL in os.walk(rootDir):
      if r not in sys.path:
        sys.path += [r]

    pyFiles = [f[:-3]
          for r, dL, fL in os.walk(rootDir)
          for f in fL if (     f.endswith('.py') 
                          and (f[0]!='_')
                          )]

    return pyFiles

help_entries = (  # (help_label,  help_doc)
    ('Turtledemo help', __doc__),
    ('About turtledemo', about_turtledemo),
    ('About turtle module', turtle.__doc__),
    ('龜作圖 網上資源','https://docs.python.org/3.4/library/turtle.html')
    )

class DemoWindow(object):

    def __init__(我, filename=None):
        
        #turtleOld._root=
        我.root= root= turtle._root=  Tk() #Toplevel() #Tk()
        # 我的「根」視窗，是一種 Tk() 窗。

        root.title('傳統漢字 (Traditional Chinese, tc) 龜作圖 範例集。')

        root.wm_protocol("WM_DELETE_WINDOW", 我._destroy)

        # 若本程式要在 mac 上執行，須加上以下數行，尚不求甚解。
        if darwin:
            import subprocess
            # Make sure we are the currently activated OS X application
            # so that our menu bar appears.
            p = subprocess.Popen(
                    [
                        'osascript',
                        '-e', 'tell application "System Events"',
                        '-e', 'set frontmost of the first process whose '
                              'unix id is {} to true'.format(os.getpid()),
                        '-e', 'end tell',
                    ],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,)

        root.grid_rowconfigure(0,    weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)#, minsize=90)
        root.grid_columnconfigure(2, weight=1)#, minsize=90)
        #root.grid_columnconfigure(3)#, weight=1, minsize=90)

        我.mBar= Menu(root)#, relief= RAISED, borderwidth=2)
        我.mBar.add_cascade(label= '範例',   menu= 我.makeLoadDemoMenu(我.mBar))#, underline=0)
        我.mBar.add_cascade(label= '字體',   menu= 我.makeFontMenu(我.mBar))#, underline=0)
        我.mBar.add_cascade(label= '求助',   menu= 我.makeHelpMenu(我.mBar))#, underline=0)
        我.mBar.add_cascade(label= '新功能', menu= 我.新功能選單(我.mBar))#, underline=0) # (1)
        root['menu']= 我.mBar

        pane= PanedWindow(orient=HORIZONTAL, bg='black')#'#ddd') #sashwidth=6, #sashrelief=SOLID,        
        pane.add(我.makeTextFrame(pane))  # for English program display
        pane.add(我.makeTextFrame2(pane)) # for 漢字程式 展示 及修改
        pane.add(我.makeGraphFrame(pane)) # for 畫圖
    
        pane.grid(row=0, columnspan= 4, sticky='news')

        我.output_lbl= Label(root,  text="---", font=btnfont, bg="#ddf", borderwidth=2, relief=RIDGE)
        我.start_btn=  Button(root, text="開始", command= 我.startDemo,   font=btnfont, fg="white", disabledforeground= "#fed")
        我.stop_btn=   Button(root, text="停止", command= 我.stopIt,      font=btnfont, fg="white", disabledforeground= "#fed")
        我.clear_btn=  Button(root, text="清除", command= 我.clearCanvas, font=btnfont, fg="white", disabledforeground= "#fed")
        
        我.output_lbl.grid(row=1, column=0, sticky='news', padx=(0,3))
        我.start_btn.grid( row=1, column=1, sticky='ew')
        我.stop_btn.grid(  row=1, column=2, sticky='ew')
        我.clear_btn.grid( row=1, column=3, sticky='ew')
        
  
        # 讓 程式內文 有 語法 顏色，超酷的！
        Percolator(我.text).insertfilter(ColorDelegator())
        Percolator(我.text2).insertfilter(ColorDelegator())

        我.dirty = False
        我.exitflag = False
        
        if filename:
            我.loadfile(filename)
        
        我.configGUI(DISABLED, DISABLED, DISABLED, "由選單 選範例", "black")
        我.state = STARTUP
        
        # 在 桌面上 建一個 _tcDir 來存放翻譯的檔案。
        dektopDir= os.path.join(os.path.expanduser('~'), 'Desktop')
        我.tcDir= tcDir=  os.path.join(dektopDir, '_tcDir') ## 用底線代表用過可丟。
        if not os.path.exists(tcDir):
          os.mkdir(tcDir)
        if tcDir not in sys.path: sys.path += [tcDir]

        # 順便 把 turtle_tc.py 們 copy 過去，方便在裡面 修改 學習。
        import shutil
        for f in ['turtle_tc.py', 'turtle_tc_alias.py', 'turtle_docstringdict_tc.py']:
          srcfile= os.path.join(os.path.dirname(__file__), f)
          tgtfile= os.path.join(tcDir, f)
          if not os.path.exists(tgtfile): shutil.copy(srcfile, tcDir)


    def onResize(我, event):
        cwidth = 我._canvas.winfo_width()
        cheight = 我._canvas.winfo_height()
        我._canvas.xview_moveto(0.5*(我.canvwidth-cwidth)/我.canvwidth)
        我._canvas.yview_moveto(0.5*(我.canvheight-cheight)/我.canvheight)

    def makeTextFrame(我, root):
        
        我.text_frame= text_frame= Frame(root)
        我.text= text= Text(text_frame, name='text', padx=5,
                                wrap='none', width=45, bg='#fafafa')

        我.vbar= vbar= Scrollbar(text_frame, name='vbar')
        vbar['command'] = text.yview
        vbar.pack(side=LEFT, fill=Y)
        
        我.hbar= hbar = Scrollbar(text_frame, name='hbar', orient=HORIZONTAL)
        hbar['command'] = text.xview
        hbar.pack(side=BOTTOM, fill=X)
        text['yscrollcommand'] = vbar.set
        text['xscrollcommand'] = hbar.set

        text['font'] = tuple(txtfont)
        shortcut = 'Command' if darwin else 'Control'
        text.bind_all('<%s-minus>' % shortcut, 我.decrease_size)
        text.bind_all('<%s-underscore>' % shortcut, 我.decrease_size)
        text.bind_all('<%s-equal>' % shortcut, 我.increase_size)
        text.bind_all('<%s-plus>' % shortcut, 我.increase_size)
        text.bind('<Control-MouseWheel>', 我.update_mousewheel)
        text.bind('<Control-Button-4>', 我.increase_size)
        text.bind('<Control-Button-5>', 我.decrease_size)

        text.pack(side=LEFT, fill=BOTH, expand=1)
        return text_frame

    def makeTextFrame2(我, root):
        
        我.text_frame2= text_frame= Frame(root)
        我.text2= text= Text(text_frame, name='text', padx=5,
                                wrap='none', width=45)

        我.vbar2= vbar= Scrollbar(text_frame, name='vbar')
        vbar['command'] = text.yview
        vbar.pack(side=LEFT, fill=Y)
        
        我.hbar2= hbar = Scrollbar(text_frame, name='hbar', orient=HORIZONTAL)
        hbar['command'] = text.xview
        hbar.pack(side=BOTTOM, fill=X)
        text['yscrollcommand'] = vbar.set
        text['xscrollcommand'] = hbar.set

        text['font'] = tuple(txtfont)
        shortcut = 'Command' if darwin else 'Control'
        text.bind_all('<%s-minus>' % shortcut, 我.decrease_size)
        text.bind_all('<%s-underscore>' % shortcut, 我.decrease_size)
        text.bind_all('<%s-equal>' % shortcut, 我.increase_size)
        text.bind_all('<%s-plus>' % shortcut, 我.increase_size)
        text.bind('<Control-MouseWheel>', 我.update_mousewheel)
        text.bind('<Control-Button-4>', 我.increase_size)
        text.bind('<Control-Button-5>', 我.decrease_size)

        text.pack(side=LEFT, fill=BOTH, expand=1)
        return text_frame

    def makeGraphFrame(我, root):
        
        #turtleOld._Screen._root=

        turtle._Screen._root= root

        我.canvwidth= 800  #1000
        我.canvheight= 600 #800
        
        #turtleOld._Screen._canvas= 
        turtle._Screen._canvas= 我._canvas= canvas= turtle.ScrolledCanvas(
                root, 800, 600, 我.canvwidth, 我.canvheight)
        
        canvas.adjustScrolls()
        canvas._rootwindow.bind('<Configure>', 我.onResize)
        canvas._canvas['borderwidth'] = 0

        我.screen = _s_ = turtle.Screen()

        turtle.TurtleScreen.__init__(_s_, _s_._canvas)
        我.scanvas = _s_._canvas
        turtle.RawTurtle.screens = [_s_]
        return canvas

    def set_txtsize(我, size):
        txtfont[1] = size
        我.text['font'] = tuple(txtfont)
        我.text2['font'] = tuple(txtfont)
        我.output_lbl['text'] = '字體大小 %d' % size

    def decrease_size(我, dummy=None):
        我.set_txtsize(max(txtfont[1] - 1, MINIMUM_FONT_SIZE))
        return 'break'

    def increase_size(我, dummy=None):
        我.set_txtsize(min(txtfont[1] + 1, MAXIMUM_FONT_SIZE))
        return 'break'

    def update_mousewheel(我, event):
        # For wheel up, event.delte = 120 on Windows, -1 on darwin.
        # X-11 sends Control-Button-4 event instead.
        if (event.delta < 0) == (not darwin):
            return 我.decrease_size()
        else:
            return 我.increase_size()

    def configGUI(我, start, stop, clear, txt="", color="blue"):
        我.start_btn.config(state=start,
                              bg="#d00" if start == NORMAL else "#fca")
        我.stop_btn.config(state=stop,
                             bg="#d00" if stop == NORMAL else "#fca")
        我.clear_btn.config(state=clear,
                              bg="#d00" if clear == NORMAL else"#fca")
        我.output_lbl.config(text=txt, fg=color)

    def makeLoadDemoMenu(我, master):
        menu = Menu(master)

        for 序號, entry in enumerate(getExampleEntries()):
            
            #print('entry= ',entry) # 沒有 path 了

            def load(entry=entry):
                我.loadfile(entry)

            menu.add_command(label='%02d. %s'%(序號, entry), underline=0,
                             font=menufont, command=load)
        return menu

    def 複製檔案(我):

        enSrc= 我.text.get("1.0", "end")       
        
        我.clearCanvas()
        turtle.TurtleScreen._RUNNING= False
                
        我.text2.delete("1.0", "end")        
        我.text2.insert("1.0", enSrc) #enSrc) #chars) 
        
        #我.root.title(fn + " --> [複製] --> " + )
        我.configGUI(NORMAL, DISABLED, DISABLED,
                       "按 開始", "red")
        我.state = READY

        #return tcSrc

        pass

    def 翻譯檔案(我):

        fn= 我.module.__file__
        #print('fn= ', fn)

        fnBase= os.path.basename(fn)
        if ('tc_' in fnBase) or ('td_' in fnBase):
          fn= 我.module0.__file__ 

        tcBase = 'tc_'+os.path.basename(fn) 
        
        # 在 桌面上 建一個 tcDir 來存放翻譯的檔案。
        #dektopDir= os.path.join(os.path.expanduser('~'), 'Desktop')
        #我.tcDir= tcDir=  os.path.join(dektopDir, 'tcDir')
        
        tcDir= 我.tcDir
                
        tcPath= os.path.join(tcDir, tcBase)

        tcSrc, enSrc= 翻譯一個檔案(fn, tcPath)

        我.clearCanvas()
        turtle.TurtleScreen._RUNNING = False

        modname= tcBase.replace('.py','')
 
        __import__(modname)
        我.module = sys.modules[modname]

        '''
        with open(tcPath, 'r', encoding='utf8') as f:
            chars = f.read()
        '''
        我.text2.delete("1.0", "end")
        
        # -------------------------------------------
        
        我.text2.insert("1.0", tcSrc) #enSrc) #chars) 
        
        我.root.title(fn + " --> [翻譯] --> " + tcPath )
        我.configGUI(NORMAL, DISABLED, DISABLED,
                       "按 開始", "red")
        我.state = READY

        #return tcSrc

    def 更新檔案(我):

        fn= 我.module.__file__
        #print('fn= ', fn)

        tcBase= os.path.basename(fn) 
        tcBase= tcBase.replace('tc_','td_') 
        
        tcDir= 我.tcDir #='tcDir'
        if not os.path.exists(tcDir):
          os.mkdir(tcDir)
        if tcDir not in sys.path: sys.path += [tcDir]
        tcPath= os.path.join(tcDir, tcBase)

        tcSrc= 我.text2.get('1.0', 'end')
        with open(tcPath, 'w', encoding='utf-8') as fpnew:
          fpnew.write(tcSrc)

        我.clearCanvas()
        turtle.TurtleScreen._RUNNING = False

        modname= tcBase.replace('.py','')
        
        __import__(modname)
 
        我.module= sys.modules[modname]
        
        我.module= importlib.reload(我.module)

        我.root.title(fn + " 更新成 " + tcPath )
        我.configGUI(NORMAL, DISABLED, DISABLED,
                       "按 開始", "red")
        我.state = READY

 
    def 開窗來跑(我):
        '''
        目前只准跑 翻譯後的 中文程式，
        並讓人隨意修改之，
        
        原版英文程式不准改，
        因為那是系統的一部份。
        
        本功能基本上可跑，
        但在「關」窗時，
        會出現一些 「髒」，
        仍待改。
        '''
      
        import sys

        '''
        import idlelib
        from idlelib import PyShell       
        PyShell= importlib.reload(idlelib.PyShell)
        '''
        #import idlelib.ryPyShell as PyShell
        import idlelib.PyShell as PyShell

        fn= 我.module.__file__
        
        #print('fn= ', fn)
        tcDir= 我.tcDir #= 'tcDir'
        if os.path.abspath(os.path.dirname(fn)) != os.path.abspath(tcDir):
            msg=  '%s not in %s\n'%(fn, os.path.abspath(tcDir))
            msg+= '目前只准跑 翻譯後的 中文程式，並隨意修改之。\n'
            print(msg)
            return
            
        sys.argv= ['', '-r', fn]

        #我.root.wm_protocol("WM_DELETE_WINDOW", 我._destroy)

 
        PyShell.main() #### 這行 在 windows 上 OK; 但 mac 不 OK !!!!
        # 因此 本功能 在 mac 上 仍有 bug

    def 語音合成(我):

        text= 我.text2.get('1.0', 'end')
        fp= io.StringIO(text)
        
        tokenL= [ x for x in tn.generate_tokens(fp.readline) ]

        fn= 我.module.__file__
        fn= fn.replace('.py','.mp3')

        #
        # 預設語音合成是台灣華語 (zh-tw)
        #
        ryGoogleTTS.ttsIt(tokenL, savefile= fn) #, langAnother= 'ja')
        
        #
        # 特別針對日語 (ja)
        #
        #ryGoogleTTS.ttsIt(tokenL, savefile= fn, langAnother= 'ja')
        
        ryGoogleTTS.playIt(audio_file= fn) # 純TTS playIt 較無趣，在此先 mark 掉
    
    def 語音合成之停止(我):
        ryGoogleTTS.quitIt()

    def 打亂程式(我):
    
        tcSrc= 我.text2.get('sel.first', 'sel.last')
        
        sL= tcSrc.split('\n')
        random.shuffle(sL)
        
        sT=''
        for x in sL:
            sT=sT+x+'\n'
                
        我.text2.insert('sel.last',sT)
        我.text2.delete('sel.first', 'sel.last')
        
        我.text2.update()
        
    def 音文同步(我):
    
        '''
        if 'yinyang.py' not in 我.module.__file__:
            msg= '非 yinyang.py, 暫無 音文同步！'
            print(msg)
            return msg
        '''
        
        from rySyncTTS import RySyncTTS
        
        fn= 我.module.__file__
        fn_mp3= fn.replace('.py','.mp3')
        fn_timeText= fn.replace('.py','_timeText')

        x= RySyncTTS(tx= 我.text2, file_mp3= fn_mp3, timeTextMod= fn_timeText)
        x.rySync()
        x.ryQuit()

        #print('not implemented !!')
        return
    
    def 新功能選單(我, master):
        
        menu= Menu(master)
        
        
        menu.add_command(label= '複製(英->英)', command= 我.複製檔案)
        menu.add_command(label= '翻譯(英->漢)', command= 我.翻譯檔案)
        
        menu.add_separator()
        menu.add_command(label= '更新檔案', command= 我.更新檔案)
        
        menu.add_separator()
        menu.add_command(label= '開窗來跑 !mac', command= 我.開窗來跑)
        
        menu.add_separator()
        menu.add_command(label= '語音合成', command= 我.語音合成)
        menu.add_command(label= '語音合成之停止', command= 我.語音合成之停止)
        
        menu.add_separator()
        menu.add_command(label= '打亂程式(選到的部分)', command= 我.打亂程式)

        menu.add_separator()
        menu.add_command(label= '音文同步', command= 我.音文同步)
        
        return menu

    def makeFontMenu(我, master):
        menu = Menu(master)
        menu.add_command(label="減 (C-'-')", command=我.decrease_size,
                         font=menufont)
        menu.add_command(label="增 (C-'+')", command=我.increase_size,
                         font=menufont)
        menu.add_separator()

        for size in font_sizes:
            def resize(size=size):
                我.set_txtsize(size)
            menu.add_command(label=str(size), underline=0,
                             font=menufont, command=resize)
        return menu

    def makeHelpMenu(我, master):
        menu = Menu(master)

        for help_label, help_file in help_entries:
            def show(help_label=help_label, help_file=help_file):

                if 'https:' in help_file:
                    try:
                        import webbrowser
                        webbrowser.open_new(help_file) #'https://docs.python.org/3.4/library/turtle.html'
                    except:
                        help_file += ' .. 但網路可能不通。'
                view_text(我.root, help_label, help_file)
                
            menu.add_command(label=help_label, font=menufont, command=show)
        return menu

    def refreshCanvas(我):
        if 我.dirty:
            我.screen.clear()
            我.dirty= False

    def loadfile(我, filename):
        我.clearCanvas()
        turtle.TurtleScreen._RUNNING = False

        modname= filename #'turtledemo.' + filename
        __import__(modname)
        我.module = sys.modules[modname]

        我.module0= 我.module  # 保存起來，以備回復。 
        
        #
        # 加入 encoding='utf8' 讓它可以讀中文程式
        #
        with open(我.module.__file__, 'r', encoding='utf8') as f:
            chars = f.read()

        我.text.configure(state='normal')
        我.text.delete("1.0", "end")
        
        #
        # 以下加入行號，我假設程式在 9999 行以內。
        #
        # 將會影響 copy-paste 程式的便利性，
        # 所以不必然好！可能先 mark 掉，
        # 等能放在GUI中自由調控再說。
        #
        '''
        aL= chars.split('\n')
        X=''
        for i,a in enumerate(aL):
            x= '%04d%s%s\n'%(i,' '*4, a)
            X += x
        chars= X
        '''
        # -------------------------------------------
        
        我.text.insert("1.0", chars)
        #我.text.configure(state='disabled') # 這行會讓它「不能改，也不能copy-paste」 
        
        我.root.title(" Python 龜作圖 之 傳統漢字(Traditional Chinese, tc) 範例。" + filename )
        我.configGUI(NORMAL, DISABLED, DISABLED,
                       "按 開始", "red")
        我.state = READY
        
        #我.翻譯檔案()  # 一輸入完畢 loadfile() 就直接翻譯了。
        我.複製檔案()

    def startDemo(我):
    
        我.更新檔案()  # 一按「開始」就先更新了。
        
        我.refreshCanvas()
        我.dirty = True
        turtle.TurtleScreen._RUNNING = True
        我.configGUI(DISABLED, NORMAL, DISABLED,
                       "執行中...", "black")
        我.screen.clear()
        我.screen.mode("standard")
        我.state = RUNNING

        try:
            if 'main' in vars(我.module):
              result = 我.module.main()
            elif '主函數' in vars(我.module):
              result = 我.module.主函數()
            else:
              result = ''

            if result == "EVENTLOOP":
                我.state = EVENTDRIVEN
            else:
                我.state = DONE
        except turtle.Terminator:
            我.state = DONE
            result = "已停止！"
        if 我.state == DONE:
            我.configGUI(NORMAL, DISABLED, NORMAL,
                           result)
        elif 我.state == EVENTDRIVEN:
            我.exitflag = True
            我.configGUI(DISABLED, NORMAL, DISABLED,
                           "用滑鼠、鍵盤 控制螢幕 或 按 停止", "red")

    def clearCanvas(我):
        我.refreshCanvas()
        我.screen._delete("all")
        我.scanvas.config(cursor="")
        我.configGUI(NORMAL, DISABLED, DISABLED)

    def stopIt(我):
        if 我.exitflag:
            我.clearCanvas() 
            我.exitflag = False
            我.configGUI(NORMAL, DISABLED, DISABLED,
                           "已停止！", "red")
        turtle.TurtleScreen._RUNNING = False

    def _destroy(我):
        我.root.destroy()




if __name__ == '__main__':
    main()
