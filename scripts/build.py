"""Render editable worksheet content as vector A4 pages with tailored workspaces."""
from pathlib import Path
import json,re,math
from functools import lru_cache
from html import escape
import matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import MathTextParser
from matplotlib.font_manager import FontProperties,findfont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
ROWS=json.loads((ROOT/'content/worksheets.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('D',findfont(FontProperties(family='DejaVu Sans'))))
pdfmetrics.registerFont(TTFont('DB',findfont(FontProperties(family='DejaVu Sans',weight='bold'))))
STYLE=ParagraphStyle('body',fontName='D',fontSize=10.5,leading=15)
matplotlib.rcParams['mathtext.fontset']='dejavusans'
PARSER=MathTextParser('path');FONTS={};CHECKS=[];C=None;CURRENT=''
def plain(s,x,y,width=505,size=10.5,bold=False,min_y=0):
    st=ParagraphStyle('p',parent=STYLE,fontSize=size,leading=size+4,fontName='DB' if bold else 'D')
    p=Paragraph(escape(s).replace('\n','<br/>'),st);_,h=p.wrap(width,1000)
    assert y-h>=min_y,f'Text overflow {CURRENT}: {s[:45]} ends {y-h:.1f}, limit {min_y}'
    p.drawOn(C,x,y-h);CHECKS.append(dict(id=CURRENT,bottom=y-h,limit=min_y));return y-h
def heading(s,x,y,size=11):C.setFont('DB',size);C.drawString(x,y,s)
def note(s,x,y,size=9):C.setFont('D',size);C.drawString(x,y,s)
def line(x1,y1,x2,y2,width=.8):C.setLineWidth(width);C.line(x1,y1,x2,y2)
def arrow(x1,y1,x2,y2):
    line(x1,y1,x2,y2);a=math.atan2(y2-y1,x2-x1)
    for d in [-.5,.5]:line(x2,y2,x2-5*math.cos(a+d),y2-5*math.sin(a+d))
def dot(x,y,filled=True,r=4):C.circle(x,y,r,stroke=1,fill=int(filled))
@lru_cache(maxsize=512)
def parse_math(s,size):
    s=re.sub(r'\\sqrt(\d)',r'\\sqrt{\1}',s)
    s=re.sub(r'\\frac(\d)(\d)',r'\\frac{\1}{\2}',s.strip('$'))
    s=re.sub(r'\\frac(\d)\{',r'\\frac{\1}{',s)
    return PARSER.parse('$'+s+'$',dpi=72,prop=FontProperties(size=size))
def formula(s,x,top,maxwidth=240,size=12):
    p=parse_math(s,size)
    if p.width>maxwidth:
        size=size*maxwidth/p.width
        assert size>=9.2,f'Formula too wide {CURRENT}: {s}'
        p=parse_math(s,size)
    baseline=top-float(p.height)+float(p.depth)
    for font,fs,num,ox,oy in p.glyphs:
        if font.fname not in FONTS:
            name='M'+str(len(FONTS));pdfmetrics.registerFont(TTFont(name,font.fname));FONTS[font.fname]=name
        C.setFont(FONTS[font.fname],fs);C.drawString(x+float(ox),baseline+float(oy),chr(num))
    for rx,ry,rw,rh in p.rects:C.rect(x+float(rx),baseline+float(ry),float(rw),float(rh),fill=1,stroke=0)
    return top-float(p.height)
def lines(items,x,y,width=240,size=10.5,minimum=0):
    for s in items:
        y=(formula(s,x,y,width,size+1) if s.startswith('$') else plain(s,x,y,width,size,min_y=minimum))-4
    assert y>=minimum,f'Block overflow {CURRENT}: {y} < {minimum}'
    return y
def writing_grid(x,y,w,h,step=14.17):
    C.setStrokeColor(colors.HexColor('#d4d4d4'));C.setLineWidth(.35)
    for i in range(int(w/step)+1):xx=x+i*step;C.line(xx,y,xx,y-h)
    for i in range(int(h/step)+1):yy=y-i*step;C.line(x,yy,x+w,yy)
    C.rect(x,y-h,w,h,stroke=1,fill=0);C.setStrokeColor(colors.black)
def axes(x,y,w,h,xmax=5,ymax=60,xlabel='Tid (timmar)',ylabel='Pris (kr)',graph=None,read=None):
    def X(v):return x+w*v/xmax
    def Y(v):return y+h*v/ymax
    C.setStrokeColor(colors.HexColor('#d9d9d9'));C.setLineWidth(.35)
    for i in range(xmax*2+1):C.line(X(i/2),y,X(i/2),y+h)
    for i in range(0,ymax+1,5 if ymax==60 else 1):C.line(x,Y(i),x+w,Y(i))
    C.setStrokeColor(colors.black);arrow(x,y,x+w+7,y);arrow(x,y,x,y+h+6)
    for i in range(xmax+1):C.setFont('D',8);C.drawCentredString(X(i),y-13,str(i))
    for i in range(0,ymax+1,10 if ymax==60 else 1):C.setFont('D',8);C.drawRightString(x-6,Y(i)-3,str(i))
    heading(ylabel,x-14,y+h+16,9);C.setFont('DB',9);C.drawRightString(x+w,y-30,xlabel)
    if graph:
        k,m=graph;end=min(xmax,(ymax-m)/k);line(X(0),Y(m),X(end),Y(k*end+m),1.5)
    if read:
        a,b=read;C.setDash(3,3);line(X(a),y,X(a),Y(b));line(X(a),Y(b),x,Y(b));C.setDash()
        C.circle(X(a),Y(b),2.5,stroke=0,fill=1);heading(f'({a}, {b})',X(a)+5,Y(b)+5,9)
def table(x,y,width,rows,colwidths=None,rowh=26):
    cw=colwidths or [width/len(rows[0])]*len(rows[0]);C.setStrokeColor(colors.HexColor('#aaaaaa'));C.setLineWidth(.5)
    for k,row in enumerate(rows):
        xx=x;yy=y-k*rowh
        for j,v in enumerate(row):
            C.rect(xx,yy-rowh,cw[j],rowh,stroke=1,fill=0);plain(str(v),xx+6,yy-5,cw[j]-10,size=9);xx+=cw[j]
    C.setStrokeColor(colors.black)
def figure(id):
    x,y,w,h=322,553,218,138
    if id=='1.1':
        heading('−2 + 5 på tallinjen',x,y+135,10);yy=y+58;arrow(x,yy,x+w,yy)
        for n in range(-4,5):
            xx=x+12+(n+4)*23;line(xx,yy-4,xx,yy+4);note(str(n),xx-5,yy-20)
        a=x+58;b=x+173;dot(a,yy,True,2);dot(b,yy,True,2);arrow(a,yy+23,b,yy+23);note('+5',a+46,yy+33)
    elif id=='1.2':
        heading('Tecken i gånger och delat',x,y+135,10)
        table(x,y+112,w,[['Tecken','Svar'],['+ och +','+'],['− och −','+'],['+ och −','−'],['− och +','−']],rowh=22)
    elif id=='1.3':
        heading('Räkna i denna ordning',x,y+135,10)
        table(x,y+114,w,[['1','Parenteser'],['2','Potenser'],['3','Gånger och delat'],['4','Plus och minus']],colwidths=[28,190],rowh=26)
    elif id=='1.4':
        heading('Hur många fjärdedelar?',x,y+135,10);note('Hela remsan är 1 liter.',x,y+113)
        for j in range(4):
            C.setFillColor(colors.HexColor('#bbbbbb') if j<2 else colors.white);C.rect(x+j*52,y+58,52,28,stroke=1,fill=1)
        C.setFillColor(colors.black);note('1/4',x+17,y+40);note('1/4',x+69,y+40);note('Det grå är 1/2 liter: två fjärdedelar.',x,y+13,8.5)
    elif id=='1.5':
        heading('Samma faktor tre gånger',x,y+135,10);formula(r'2^3',x+72,y+102,size=22)
        formula(r'2\cdot2\cdot2=8',x+25,y+53,maxwidth=200,size=17);note('Bas: 2. Exponent: 3.',x+35,y+3)
    elif id=='1.6':
        heading('Tiopotenser',x,y+135,10);table(x,y+114,w,[['Potens','Värde'],['10³','1 000'],['10²','100'],['10⁻¹','0,1'],['10⁻²','0,01']],rowh=22)
    elif id=='2.1':
        heading('20 % rabatt på 100 kr',x,y+135,10)
        C.setFillColor(colors.HexColor('#bbbbbb'));C.rect(x,y+61,w*.8,30,fill=1,stroke=1)
        C.setFillColor(colors.white);C.rect(x+w*.8,y+61,w*.2,30,fill=1,stroke=1);C.setFillColor(colors.black)
        note('80 % kvar',x+37,y+72);note('20 %',x+w*.8+4,y+72,8);note('80 % = 0,80',x+57,y+30,11)
    elif id=='2.2':
        heading('Efter ett år',x,y+135,10);table(x,y+111,w,[['Sparat','1 000 kr'],['Ränta 3 %','30 kr'],['Totalt','1 030 kr']],rowh=30)
    elif id=='2.3':
        heading('Två olika jämförelser',x,y+135,10)
        for j,(v,lab) in enumerate([(20,'20 %'),(30,'30 %')]):
            yy=y+75-j*38;C.setFillColor(colors.HexColor('#bbbbbb'));C.rect(x+48,yy,w*v/100,22,fill=1,stroke=1);C.setFillColor(colors.black);note(lab,x,yy+7)
        note('Skillnad: 10 procentenheter.',x,y+9);note('Relativ ökning: 10/20 = 50 %.',x,y-9)
    elif id in ('2.4','2.6','2.7'):
        if id=='2.4':axes(x,y+3,w,h,graph=(10,0),read=(2,20))
        elif id=='2.6':axes(x,y+3,w,h,graph=(10,20))
        else:axes(x,y+3,w,h,xmax=5,ymax=6,xlabel='x',ylabel='y',graph=(1,1),read=(2,3))
    elif id=='2.5':
        heading('Samma styckpris: 5 kr',x,y+135,10);table(x,y+110,w,[['Antal x','Pris y (kr)'],['0','0'],['1','5'],['2','10'],['3','15']],rowh=22)
    elif id=='3.1':
        heading('Minus gäller hela parentesen',x,y+135,10);formula(r'5-(x+2)',x+30,y+99,maxwidth=200,size=19)
        arrow(x+84,y+68,x+84,y+47);formula(r'5-x-2',x+32,y+35,maxwidth=200,size=19)
    elif id=='3.2':
        heading('Tre lika delar',x,y+135,10)
        for j in range(3):
            yy=y+85-j*34;C.rect(x,yy,145,28);C.rect(x+145,yy,65,28);note('x',x+68,yy+9,11);note('2',x+173,yy+9,11)
        note('3x och 3 · 2 blir 3x + 6.',x,y-10)
    elif id=='3.3':
        heading('Samla lika termer',x,y+135,10);formula(r'2x+x+1',x+30,y+100,size=19)
        arrow(x+85,y+70,x+85,y+49);formula(r'3x+1',x+50,y+38,size=19);note('När x = 2 får vi 3 · 2 + 1 = 7.',x,y-8)
    elif id=='3.4':
        heading('Sträcka = hastighet × tid',x,y+135,10);arrow(x+8,y+65,x+w-8,y+65)
        for j,t in enumerate(['0 km','10 km','20 km']):
            xx=x+8+j*99;line(xx,y+60,xx,y+70);note(t,xx-8,y+41)
        note('0 h',x,y+85);note('1 h',x+99,y+85);note('2 h',x+198,y+85);note('10 km varje timme.',x+40,y+4)
    elif id=='3.5':
        heading('Platsnummer och tal',x,y+135,10);table(x,y+112,w,[['Plats n','1','2','3','4'],['Tal','3','5','7','9']],colwidths=[66,38,38,38,38],rowh=32);note('Ökning: +2 för varje ny plats.',x,y+22)
    elif id=='3.6':
        heading('Båda sidor är lika',x,y+135,10);line(x+10,y+87,x+w-10,y+87,1.3)
        p=C.beginPath();p.moveTo(x+109,y+87);p.lineTo(x+84,y+52);p.lineTo(x+134,y+52);p.close();C.drawPath(p)
        for j,txt in enumerate(['2(x + 3)','14']):
            xx=x+15+j*137;C.rect(xx,y+95,70,28);note(txt,xx+6,y+105,10)
        note('Dela båda sidor med 2.',x+22,y+18)
    elif id=='4.1':
        heading('Radie och diameter',x,y+135,10);cx,cy=x+108,y+57;r=49;C.circle(cx,cy,r)
        line(cx-r,cy,cx+r,cy);dot(cx,cy,True,2);line(cx,cy,cx,cy+r);note('r',cx+5,cy+25,11);note('d',cx-4,cy-16,11)
    elif id=='4.2':
        heading('90° är en fjärdedel',x,y+135,10);cx,cy=x+108,y+53;r=50
        C.setFillColor(colors.HexColor('#cccccc'));C.wedge(cx-r,cy-r,cx+r,cy+r,0,90,fill=1,stroke=1);C.setFillColor(colors.black)
        C.circle(cx,cy,r);line(cx,cy,cx+r,cy);line(cx,cy,cx,cy+r);note('90°',cx+6,cy+13);note('båge',cx+48,cy+45)
    elif id in ('4.3','4.4'):
        heading('1 dm³ = 1 liter' if id=='4.3' else 'Basyta gånger höjd',x,y+135,10)
        a,b,s=x+30,y+17,84;dx,dy=42,30;C.rect(a,b,s,s)
        for ax,ay in [(a,b+s),(a+s,b+s),(a+s,b)]:line(ax,ay,ax+dx,ay+dy)
        line(a+dx,b+s+dy,a+s+dx,b+s+dy);line(a+s+dx,b+dy,a+s+dx,b+s+dy)
        if id=='4.3':note('1 dm',a+22,b-15);note('1 dm',a+s+dx+5,b+50);note('1 dm',a+s+10,b-1)
        else:note('2 cm',a+23,b-15);note('4 cm',a+s+dx+5,b+50);note('3 cm',a+s+10,b-1)
    elif id=='4.5':
        heading('Pyramid: höjden går rakt ned',x,y+135,9.5)
        a=(x+25,y+15);b=(x+159,y+15);d=(x+62,y+52);e=(x+196,y+52);t=(x+110,y+116)
        for p,q in [(a,b),(b,e),(e,d),(d,a),(t,a),(t,b),(t,e),(t,d)]:line(*p,*q)
        C.setDash(3,3);line(t[0],t[1],t[0],y+34);C.setDash();note('h',t[0]+5,y+77,11);note('B = basytans area',x+18,y-7)
    elif id=='4.6':
        heading('Rätvinklig triangel',x,y+135,10);a=(x+35,y+15);b=(x+35,y+110);d=(x+180,y+15)
        for p,q in [(a,b),(b,d),(d,a)]:line(*p,*q,1.2)
        line(a[0]+11,a[1],a[0]+11,a[1]+11);line(a[0]+11,a[1]+11,a[0],a[1]+11)
        note('a',x+15,y+61,12);note('b',x+100,y-2,12);note('c',x+115,y+72,12);note('c = hypotenusan',x+69,y+104,8)
    elif id=='5.1':
        heading('4 röda och 6 blå kulor',x,y+135,10)
        for i in range(10):
            xx=x+23+(i%5)*42;yy=y+87-(i//5)*47
            C.setFillColor(colors.HexColor('#bbbbbb'))
            dot(xx,yy,i<4,12)
            C.setFillColor(colors.black);note('R' if i<4 else 'B',xx-3,yy-3,8)
        note('Bokstäver visar färg även i svartvitt.',x,y+2,8)
    elif id=='5.2':
        heading('Två myntkast',x,y+135,10);root=(x+5,y+63)
        for j,txt in enumerate(['K','L']):
            end=(x+95,y+103-j*80);line(*root,*end);note('1/2',x+37,y+91-j*51,8);note(txt,*end)
            for k,txt2 in enumerate(['K','L']):
                end2=(x+192,end[1]+18-k*36);line(end[0]+12,end[1],*end2);note(txt+txt2,end2[0]+2,end2[1]-3,8);note('1/2',x+142,end2[1]+2,7)
        note('K = krona. L = klave.',x,y-4)
    elif id=='5.3':
        heading('Två myntkast: fyra möjligheter',x,y+135,9);table(x,y+112,w,[['','K','L'],['K','KK','KL'],['L','LK','LL']],colwidths=[48,85,85],rowh=30);note('Minst en krona: KK, KL eller LK.',x,y+3,8.5)
    elif id=='5.4':
        heading('18 kronor på 40 kast',x,y+135,10)
        C.setFillColor(colors.HexColor('#bbbbbb'));C.rect(x,y+65,w*.45,28,fill=1,stroke=1);C.setFillColor(colors.white);C.rect(x+w*.45,y+65,w*.55,28,fill=1,stroke=1);C.setFillColor(colors.black)
        note('18 kronor',x+12,y+75);note('22 klavar',x+117,y+75);note('Andel kronor: 18/40 = 45 %.',x+9,y+31)
    elif id=='5.5':
        heading('2 tröjor och 3 byxor',x,y+135,10)
        for j,txt in enumerate(['T1','T2']):
            xx,yy=x+18,y+98-j*75;note(txt,xx,yy)
            for k in range(3):
                ey=yy+20-k*20;line(xx+20,yy+3,x+134,ey+3);note(f'B{k+1}',x+140,ey)
        note('Varje tröja har tre val av byxor.',x,y-7,8.5)
    elif id=='5.6':
        heading('Sortera talen först',x,y+135,10)
        for j,v in enumerate([2,3,3,8]):
            xx=x+25+j*49;C.rect(xx-5,y+66,31,30);note(str(v),xx+5,y+75,12)
        note('De två mittersta: 3 och 3.',x+11,y+35);note('Median: (3 + 3) ÷ 2 = 3.',x+11,y+12)
def workspace(row):
    layout=row['layout']
    if layout=='axes':axes(377,69,163,139,xmax=5,ymax=6,xlabel='x',ylabel='y')
    elif layout=='table':
        heading('Median',370,198,9)
        writing_grid(370,187,170,38)
        heading('Medelvärde',370,134,9)
        writing_grid(370,123,170,52)
        note('Passar bäst: ______________',370,48,9)
    elif layout=='tree':
        C.setFillColor(colors.HexColor('#cccccc'))
        for i in range(13):
            for j in range(13):C.circle(370+i*14.17,207-j*14.17,.5,stroke=0,fill=1)
        C.setFillColor(colors.black)
    elif layout=='tall':writing_grid(385,207,155,170)
    elif layout=='fraction':
        writing_grid(370,171,170,134)
        if row['id']=='1.4':
            note('En hel liter',370,211,8)
            for i in range(8):C.rect(370+i*21.25,185,21.25,17)
        else:note('Visa bråk och procent här.',370,196,8)
    else:writing_grid(370,207,170,170)
def worksheet(row,index):
    global CURRENT
    CURRENT=row['id'];note('MODUL 8  /  '+CURRENT,44,810)
    C.setFont('D',9);C.drawRightString(550,810,'Namn: ______________________')
    ts=18
    while pdfmetrics.stringWidth(row['title'],'DB',ts)>506:ts-=.5
    heading(row['title'],44,781,ts);plain(row['intro'],44,762,505,11,min_y=719)
    heading('Förstå och räkna',44,704)
    y=plain(row['idea'],44,689,248,10.5,min_y=615)-9
    y=formula(row['formula'],44,y,248,12)-10
    lines(row['example'],44,y,248,size=10,minimum=527)
    figure(CURRENT)
    C.setStrokeColor(colors.HexColor('#bbbbbb'));line(44,518,550,518,.5);C.setStrokeColor(colors.black)
    heading('Öva - börja med a)',44,501)
    for j,q in enumerate(row['practice']):
        x=44+(j%2)*262;top=486-(j//2)*85;heading(chr(97+j)+')',x,top-10,10)
        y=lines(q,x+21,top,219,size=10,minimum=top-49);available=max(21,y-(top-76))
        if any(s.startswith('$') for s in q) or row['layout'] in ('tall','fraction','geometry'):
            writing_grid(x+21,y-2,218,min(available,52))
        else:
            for yy in [y-13,y-28]:
                if yy>=top-77:
                    C.setStrokeColor(colors.HexColor('#c5c5c5'));line(x+21,yy,x+239,yy,.4);C.setStrokeColor(colors.black)
    heading('Textuppgift - så kan du tänka',44,306)
    y=plain(row['worked'][0],44,291,505,10.5,min_y=247)-7
    plain(row['worked'][1],44,y,505,10.5,min_y=215)
    heading('Prova själv',44,201);plain(row['own'],44,183,285,11,min_y=87);workspace(row)
    heading('Du har tränat på',44,76,10);plain('• '+row['skills'][0]+'\n• '+row['skills'][1],44,65,300,9,min_y=30)
    note(f'{index}  /  v2',510,18,8);C.showPage()
def answer_pages():
    global CURRENT
    for ch in range(1,6):
        CURRENT='facit-'+str(ch);heading('Facit - kapitel '+str(ch),44,791,20)
        plain('Till version 2. Svar a–d står i ordning. Därefter följer textövningen.',44,769,505,10);y=730
        for row in [r for r in ROWS if r['id'].startswith(str(ch)+'.')]:
            y=plain(row['id']+'  '+row['title'],44,y,505,10,bold=True,min_y=50)-4;a=row['answers']
            y=plain('a) '+a[0]+'   b) '+a[1]+'   c) '+a[2]+'   d) '+a[3],44,y,505,9.5,min_y=45)-4
            y=plain('Textövning: '+a[4],44,y,505,9.5,min_y=40)-18
        if ch==2:
            assert y>234, 'Answer graph would overlap answer text.'
            heading('Graf till textövning 2.7',337,225,10)
            axes(352,69,185,130,xmax=5,ymax=6,xlabel='x',ylabel='y',graph=(1,1))
            for a,b in [(0,1),(2,3),(4,5)]:
                dot(352+185*a/5,69+130*b/6,True,2.5)
        note('Cirklar och volymer: π ≈ 3,14. Likvärdiga svar går också bra.',44,26,8)
        C.setFont('D',8);C.drawRightString(550,26,str(31+ch)+'  /  v2');C.showPage()
if __name__=='__main__':
    C=canvas.Canvas(str(OUT/'Modul_8_studieblad.pdf'),pagesize=A4,pageCompression=1)
    C.setTitle('Modul 8 - korta studieblad och facit - version 2');C.setAuthor('Studiematerial matematik årskurs 8')
    assert len(ROWS)==31
    for i,row in enumerate(ROWS,1):worksheet(row,i)
    answer_pages();C.save()
    (OUT/'layout_checks.json').write_text(json.dumps(CHECKS,indent=2),encoding='utf-8')
    print(f'Built 31 worksheets and five answer pages; {len(CHECKS)} layout checks passed.')
