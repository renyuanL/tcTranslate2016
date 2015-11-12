'''
ryTranslate.py

找到了 tokenize.py 這個強大的解析工具，
可以把 .py 解析成 各種類別的 token (塊狀物)。
我們的 python 程式 英翻中，就有譜了。

renyuan, 2015/01/11

又經過一天的奮鬥，

找到了  tn.untokenize(tokenL) 

哈哈哈，就這樣一行搞定！！！

於是，Python 英翻中，就做出來了！！

renyuan, 2015/01/12

藉機 把 turtle_tc 也更新一下 ==> turtle_tc_2015 ==> turtle_tc

也可以做些統計，觀賞一下 頻率分布。

進一步，把那些 普通名稱 (非內定) 也翻譯一下。
更進一步，連 comment, doc_string 也 透過 Google 翻譯一下。
這裡要研究對 Google Translate 下 查詢指令，並撈回答案的技術。

renyuan, 2015/01/13, 

加入更多中英對照表，
但要注意命名空間的衝突。

renyuan, 2015/01/14 

Google Translate 技術成功了！！！
檔頭的說明文件已經可以翻譯。

renyuan, 2015/01/15

把 額外的 80 幾支 程式 都拿來跑跑看，
居然大部分都能跑！

超酷的！
renyuan, 2015/01/15

''' 

from ryDic import getDic
import ryGoogleTranslate
import tokenize as tn
import keyword  as kw
import glob
import os
import sys
import datetime


def main():
    global tcDir, turtledemoDir

    # 在 桌面上 建一個 tcDir 來存放翻譯的檔案。
    # 暫時不要，因為還有很多 Debug 要做，(過早的優化是災難的開始。)
    '''
    desktopDir= os.path.join(os.path.expanduser('~'), 'Desktop')
    tcDir=  os.path.join(dektopDir, 'tcDir')
    '''
    tcDir= 'tcDir'
    # 創個 ./tcDir 來存放 翻譯結果
    if not os.path.exists(tcDir):
        os.mkdir(tcDir)

    # 直接拿官方的 turtledemo 來展示。
    import turtledemo
    turtledemoDir= os.path.dirname(os.path.abspath(turtledemo.__file__))

    main00()


def main00():
    global tcDir, turtledemoDir

    '''
    分塊、翻譯、分析、離線加詞。
    '''

    fL  = [f for f in glob.glob(turtledemoDir+os.path.sep+'*.py') if os.path.basename(f)[0]!='_']

    t1= 翻譯任務(fL, tcDir)

    fL= glob.glob(tcDir+os.path.sep+'*.py')
    t2= 分塊任務(fL)
    
    統計任務(t1,1)
    統計任務(t2,2)

def main01():
    global tcDir, turtledemoDir
    '''
    翻譯 1 個檔案、翻譯多個 檔案。
    '''
    
    '''
    fnIn=  turtledemoDir+os.path.sep+'fractalcurves.py' 
    fnOut= 'tcDir/tc_fractalcurves.py' 
    src= 翻譯一個檔案(fnIn, fnOut)
    '''
    
    #'''
    fL  = [f for f in glob.glob(turtledemoDir+os.path.sep+'*.py') if os.path.basename(f)[0]!='_']
    for f in fL:
        f2= tcDir + os.path.sep + 'tc_' + os.path.basename(f)
        src= 翻譯一個檔案(f, f2)
    #'''
    
    fL  = glob.glob(tcDir+os.path.sep+'*.py')
    fw= open('_all.py','w',encoding='utf-8')
    for f in fL:
        with open(f,'r',encoding='utf-8') as fp:
            s= fp.read()
            fw.write('\n\n# '+os.path.basename(f)+'-'*10+'\n\n')
            fw.write(s)
            
    fw.close()
    
def main02():
    '''
    有問題的程式，目前主要是函數內 帶名引數  (named argument) 會出包。
    '''
    hardDir= 'hardDir'
    if not os.path.exists(hardDir):
        os.mkdir(hardDir)
    
    for f in  ['trigeo.py', 'tdemo_twoPlants.py','penrose.py']:   
        fnIn=  hardDir+ os.path.sep+ f
        fnOut= hardDir+ os.path.sep+'tc_' + f

        src= 翻譯一個檔案(fnIn, fnOut)
    

def main03():
    '''
    翻譯 1 個檔案，需要一些外部聲音及影像檔。先放在根目錄。
    '''
    
    fnIn=  'py_moorhuhn.py' 
    
    fnOut= 'tc_py_moorhuhn.py'
       
    src= 翻譯一個檔案(fnIn, fnOut) 
    

#---------------------------------------------------------------

def tokenizeAFile(fn):

    # 讀程式檔並把程式印出。
    f= open(fn, 'r', encoding='utf-8')
    src= f.read()
    f.close()
    
    # 重新讀程式檔，並把程式分塊，成為 tokenL。
    f= open(fn, 'r', encoding='utf-8')
    
    #
    # 這一行最了不起！！！ 這一波程式急行軍，這一行貢獻最大。
    #
    tokenL= [ x for x in tn.generate_tokens(f.readline) ] 

    f.close()
 
    return src, tokenL


def translate(tokenL, D= None):

    if D==None: D= getDic()

    insideParen= False
    本程式內定函數們= []

    for n,t in enumerate(tokenL):

        #
        # 檢查 於 函數 括弧內 的 name= ...
        # e.g. def f( name= 0)
        # 函數內引數名稱，暫不動它。
        # 但 def 內 的 函數引數，仍然要翻譯。
        #
        if t.string == '(':
            
            insideParen= True

            這個函數呼叫= None
            這行有def嗎= ('def ' in t.line) 
            if 這行有def嗎==True:
                本程式內定函數們 += [tokenL[n-1].string]
            else:
                這個函數呼叫= tokenL[n-1].string

        if insideParen == True:
            if t.string==')':
                insideParen = False

            這是函數內引數名稱嗎= all([ insideParen, 
                                  (t.type==tn.NAME), 
                                  (tokenL[n+1].string=='=')]) 
            
            #這行有def= ('def ' in t.line) 
            
            if 這是函數內引數名稱嗎==True:  
                if 這行有def嗎==False:
                    if((這個函數呼叫 not in  本程式內定函數們) 
                        or (這個函數呼叫=='__init__')):
                        continue     ##(1)
            
            #if 這是函數內引數名稱: continue # 這樣比較保守。 ##(2)
            
            #
            # 但 這保守型也會出錯！在同樣函數中！
            # def 測試(l=200, n=4, fun=日, startpos=(0,0), th=2):
            #     函數(l, n)
            #
            # 這個真是兩難！
            #
            # 所以這裡要再細想！！！
            #
            # 先再調回 ##(1)
            #
            
        #
        # 以上仍然碰到難題： 2015/01/19
        #
        # in penrose.py ...
        #
        # def 測試(l=200, n=4, 函數=日, 開始位置=(0,0), th=2):
        #
        # 測試(600, 8, startpos=(70, 117))
        #
        # 這裡要處理的是：
        # 1. 函數內的「帶名字的引數」名稱 (named argument)
        #
        #    若本函數 定義與於本程式內部，
        #    則「定義」與「呼叫」一律照正常情形翻譯
        #
        #    但若函數沒有定義在此，則其「呼叫」之 「帶名字的引數」名稱
        #    應該跳過，不翻譯，保持英文名。
        #
        #  以上描述似乎需要用更進一步的程式邏輯解決，
        #  上面幾行程式碼尚不足以支持這樣的邏輯。
        #   
        #  依上例，如何得知 測試() 這個函數，是在本程式中定義的呢？ 
        #  亦即 def 測試(): 也在本程式 中  
        #
        #   renyuan, 2015/01/19
        #
        #   penrose.py 解決，2015/01/20
        #
        #   這一塊 仍有改善空間。
        #
        #   果然， trigeo.py 又來亂！ 
        #   def __init__() vs 龜類.__init__()
        #
        #   它是 18 支以外，先放著咯！
        #
        
        #
        # 正常的 查字典，
        #
        # 這是最普遍的情形，
        # 但仍需面對 名稱衝突的問題。
        #
        if t.string in D:
            #tokenL[n][1]= D[t.string] ##### need to test
            t0= t.type
            
            t1= D[t.string]
            t2= t.start # 可能也要改
            t3= t.end   # 可能也要改
            t4= t.line  # 可能也要改

            tokenL[n]= tn.TokenInfo(t0,t1,t2,t3,t4)

    #print('本程式內定函數們= ', 本程式內定函數們)

    return tokenL



def googleTranslate(tokenL):

    gTranslator= ryGoogleTranslate.Translator(from_lang='auto', to_lang='zh-tw')

    for n,t in enumerate(tokenL):
    
        if (    (t.type==tn.STRING) 
            and (  ('"""' in t.string) 
                or ("'''" in t.string) )):

            
            triQuot= '"""' if ('"""' in t.string) else "'''"

            text= t.string.strip(triQuot)
            #text= text.strip("'''")
            try:
                gTranslation= gTranslator.translate(text)
                gTranslation= google翻譯修正(gTranslation)
            except:
                gTranslation= 'Google翻譯失敗，網路可能有問題！保留原文 ... ' + text  

            newString = "'''" # 我愛用 三單引號 '''
            #newString += '== begin Google 翻譯 ==' 
            newString += gTranslation 
            newString += '=== 以上由 Google 翻譯，請協助改善 ===\n'
            #newString += text  # 必要時，印出原文。the original english comment 
            newString += "'''"

            t0= t.type

            t1= newString #D[t.string]
            t2= t.start # 可能也要改
            t3= t.end   # 可能也要改
            t4= t.line  # 可能也要改
            
            tokenL[n]= tn.TokenInfo(t0,t1,t2,t3,t4)

        if (    (t.type==tn.COMMENT) 
            and('#' in t.string)
            and('#!' not in t.string)
            ): 
 
            text= t.string.strip('#')

            gTranslation= gTranslator.translate(text)
            gTranslation= google翻譯修正(gTranslation)

            newString = "# " 

            newString += gTranslation 
            newString += '' #' ..by Google'

            t0= t.type

            t1= newString #D[t.string]
            t2= t.start # 可能也要改
            t3= t.end   # 可能也要改
            t4= t.line  # 可能也要改
            
            tokenL[n]= tn.TokenInfo(t0,t1,t2,t3,t4)
    
    return tokenL

def google翻譯修正(gTranslation):
    
    修正列表= [
        ('龜例如套房','龜作圖範例集'),
        ('例子套房',  '範例集'),
        ('例如套房',  '範例集'),
        ('編程',     '程式設計'),
        ('發電機',   '生成器'),
        ('海龜',     '龜'),
        ('克隆',     '複製'),
        ('播放器',   '玩家'),
        ('合肥鵬遠', 'Kolam'),
        ('用戶',    '使用者'),
        ('龜套房示例','龜作圖範例集')
        ]

    for x in 修正列表:
        gTranslation= gTranslation.replace(x[0], x[1])
    
    return gTranslation

def postProcess(src):
    
    L= [
        ('from turtle import *\n',
         'from turtle_tc import *\n'),

        ('import turtle\n',
         'import turtle_tc as turtle; from turtle_tc import *\n'),

        ('from turtle import',
         'from turtle_tc import *; from turtle_tc import'),

        ('# -*- coding: cp1252 -*-', '# 預設編碼為 utf-8'), # 這行當然是暴力，以後可能凡找到 coding: 就刪吧！
        ('TK.主迴圈()','TK.mainloop()')                     # two_canvases.py 中的特例

        ]
    
    for x in L:
        src= src.replace(x[0], x[1])

    #
    # 以下這行
    # 特別針對 日文
    #
    # _tc ---> _jp, 
    #
    # using this way is no good, 
    # just a test
    #
    #src= src.replace('_tc', '_jp')
    
    return src

def 翻譯任務(fnL, tcDir= 'tcDir'):

    fnin= '_'+os.path.basename(__file__)+'_in.py'
    fpin= open(fnin,'w', encoding= 'utf-8')
   
    fnout= '_'+os.path.basename(__file__)+'_out.py'
    fpout= open(fnout,'w', encoding= 'utf-8')

    print('# ', len(fnL), ' fnL= ',fnL, file= fpin)
    print('#','-'*50, file= fpin) #----------------------

    print('# ', len(fnL), ' fnL= ',fnL, file= fpout)
    print('#','-'*50, file= fpout) #----------------------

    tokenLL= []

    #fn2Dir= 'fn2Dir'
    if not os.path.exists(tcDir):
        os.mkdir(tcDir)
    
    for fn in fnL:

        ## 關鍵處理，把程式分塊，(tokenize)，
        
        # 切出所有 變數，函數，物類，方法 及它們的形態(type)。
        #
        src, tokenL= tokenizeAFile(fn)

        print('# fn= ',fn, file= fpin)
        print('#','-'*50, file= fpin) #----------------------

        print(src, file= fpin) # 原始 英文程式 印出
        #exec( src)  # 原始 英文程式 要能跑
        print('#','='*50, file= fpin) #========================


        tokenLL += tokenL
  


        ## 第一級翻譯， 變數，函數，物類，方法。
        tokenL= translate(tokenL)

        ## 第二級翻譯，google Translation of doc string
        tokenL= googleTranslate(tokenL)

        # 由 tokenL 把 src 接回來，文法無誤仍可跑。

        src2= tn.untokenize(tokenL) # 就這樣一行搞定！！！這也是關鍵。

        src2= postProcess(src2)  # 後處理，大多是暴力法 字串取代。

        print('# fn= ',fn, file= fpout)
        print('#','-'*50, file= fpout) #----------------------

        print(src2, file= fpout)

        try:
            #exec(src2) # 初步 翻譯過的 中文程式 也要能跑。
            pass
        except:
            print('# %s .... bugs!'%fn, file= fpout)
            pass

        print('#','='*50, file= fpout) #========================

        #
        # 把翻譯過的程式 個別 存起來，檔名前加上 tc_
        #
        # dir2= fn[0:fn.rfind('\\')+1]
        # fn2= 'tc_'+ fn[fn.rfind('/')+1:]
        fn2= tcDir + os.path.sep + 'tc_'+ fn[fn.rfind(os.path.sep)+1:]

        fp= open(fn2,'w', encoding= 'utf-8')
        print(src2, file= fp)
        fp.close()

    fpin.close()
    fpout.close()
    return tokenLL


def 分塊任務(fnL):

    tokenLL= []

    for fn in fnL:
        src, tokenL= tokenizeAFile(fn)
        tokenLL += tokenL
  
    return tokenLL

def 統計任務(tokenLL, outFileId= 1):

    fnout= '_%s_out%d.py'%(os.path.basename(__file__), outFileId)
    fpout= open(fnout,'w', encoding= 'utf-8')
        
    L0= [x.type   for x in tokenLL]
    L1= [x.string for x in tokenLL]

    sL0= sorted(list(set(L0)))
    sL1= sorted(list(set(L1)))

    D0= [(L0.count(x), x) for x in sL0]
    D1= [(L1.count(x), x) for x in sL1]

    print('len(tokenLL)= ', len(tokenLL), file= fpout)

    print('\nDistribution of token type: ....', file= fpout)
    #print(sorted(D0))
    for x in sorted(D0, reverse= True):
        print(x[0], tn.tok_name[x[1]], file= fpout)

    print('\nDistribution of token string: ....', file= fpout)
    #print(sorted(D1))
    for x in sorted(D1, reverse= True):
        print(x[0], x[1], file= fpout)

    print('\nDistribution of token string: ....', file= fpout)
    #print(sorted(D1))
    for x in sorted(D1, key= lambda D1: D1[1], reverse= True):
        print(x[0], x[1], file= fpout)

    fpout.close()


def 翻譯一個檔案(fnIn, fnOut= 'tcTempOut.py', fnInIncluded= False):

    ## 關鍵處理，把程式分塊，(tokenize)，
    #    
    # 切出所有 變數，函數，物類，方法 及它們的形態(type)。
    #
    src1, tokenL= tokenizeAFile(fnIn)

    ## 第一級翻譯， 變數，函數，物類，方法。
    tokenL= translate(tokenL)

    #
    # 由於 google 翻譯不再免費，因此我們暫時關掉這部分功能。
    #
    ## 第二級翻譯，google Translation of doc string
    #tokenL= googleTranslate(tokenL)

    # 由 tokenL 把 src 接回來，文法無誤仍可跑。

    src2= tn.untokenize(tokenL) # 就這樣一行搞定！！！這也是關鍵。

    src2= postProcess(src2)  # 後處理，大多是暴力法 字串取代。

    #
    # 把翻譯過的程式 個別 存起來，
    #

    fp= open(fnOut,'w', encoding= 'utf-8')

    print(src2, file= fp)
    
    now = datetime.datetime.now()
    print('# Above: "%s", by Renyuan Lyu (呂仁園), %s'%(os.path.basename(fnOut), now.date()), file=fp)
    print('# Original: "%s", by Gregor Lingl. '%os.path.basename(fnIn), file=fp)

    if fnInIncluded:
        triQuot= "'''" if not "'''" in src1 else '"""'
        print(triQuot, file= fp)
        print(src1, file= fp)
        print(triQuot, file= fp)

    fp.close()

    return src2, src1

#-----------------------------------------------------------------

if __name__=='__main__':
    main()

