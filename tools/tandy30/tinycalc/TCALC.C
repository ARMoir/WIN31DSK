/* Tandy TinyCalc: original fixed-point Win3.0 calculator for 320x200.
 * 8086-compatible, no FPU; decimal precision 0.001; maximum 99999.999.
 * Keeps the stock Microsoft Calculator unchanged.
 */
#define WINVER 0x0300
#include <windows.h>

#define MAXNUM 99999999L
#define DISP 200
#define FIRST 300
#define NBTN 20
static HINSTANCE instance;
static HWND display_hwnd,buttons[NBTN];
static char input[20]="0";
static long current=0,saved=0;
static char pending=0;
static int typing=0,failed=0;
static char *labels[NBTN]={
 "C","CE","Back","+/-",
 "7","8","9","/",
 "4","5","6","*",
 "1","2","3","-",
 "0",".","=","+"
};
static char symbols[NBTN]={
 'C','E','B','S',
 '7','8','9','/',
 '4','5','6','*',
 '1','2','3','-',
 '0','.','=','+'
};
static unsigned long mag(long x){return x<0?(unsigned long)(-x):(unsigned long)x;}
static void format(long val,char *dst){
 unsigned long v=mag(val),whole=v/1000L,frac=v%1000L;
 char base[20];int i=0,n;
 if(val<0)dst[i++]='-';
 wsprintf(base,"%lu",whole);
 lstrcpy(dst+i,base);i=lstrlen(dst);
 if(frac){
  dst[i++]='.';
  dst[i++]=(char)('0'+frac/100L);
  dst[i++]=(char)('0'+(frac/10L)%10L);
  dst[i++]=(char)('0'+frac%10L);
  while(i>0&&dst[i-1]=='0')i--;
 }
 dst[i]=0;
}
static int parse(const char *s,long *out){
 int neg=0,seen=0,scale=0;
 long whole=0,part=0,total;
 if(*s=='-'){neg=1;s++;}
 while(*s && *s!='.'){
  if(*s<'0'||*s>'9')return 0;
  whole=whole*10+(*s++-'0');
  if(whole>99999L)return 0;
  seen=1;
 }
 if(*s=='.'){
  s++;
  while(*s){
   if(*s<'0'||*s>'9'||scale>=3)return 0;
   part=part*10+(*s++-'0');scale++;
  }
 }
 if(!seen && !scale)return 0;
 while(scale<3){part*=10;scale++;}
 total=whole*1000L+part;
 if(total>MAXNUM)return 0;
 *out=neg?-total:total;return 1;
}
static void refresh(void){
 char buf[24];
 if(failed)lstrcpy(buf,"Overflow / divide 0");
 else if(typing)lstrcpy(buf,input);
 else format(current,buf);
 SetWindowText(display_hwnd,buf);
}
static void begin_entry(void){
 if(!typing){lstrcpy(input,"0");current=0;typing=1;failed=0;}
}
static void digit(char ch){
 int len;
 if(failed)return;
 begin_entry();
 len=lstrlen(input);
 if(ch=='.'){
  if(lstrchr(input,'.')==NULL && len<15){input[len]='.';input[len+1]=0;}
 }else{
  if(lstrchr(input,'.')!=NULL){
   char *p=lstrchr(input,'.');if(lstrlen(p)>=4)return;
  }
  if((input[0]=='0'&&input[1]==0) || (input[0]=='-'&&input[1]=='0'&&input[2]==0)){
   len=(input[0]=='-')?1:0;input[len]=ch;input[len+1]=0;
  }else if(len<15){input[len]=ch;input[len+1]=0;}
 }
 if(!parse(input,&current))failed=1;
 refresh();
}
static int checked_add(unsigned long a,unsigned long b,unsigned long *r){
 if(a>MAXNUM||b>MAXNUM-a)return 0;
 *r=a+b;return 1;
}
static int operate(char oper,long a,long b,long *result){
 int sign=((a<0) != (b<0));
 unsigned long x=mag(a),y=mag(b),z=0,t,aw,af,bw,bf,q,rem,frac;
 int i;
 if(oper=='+'){long v=a+b;if(v>MAXNUM||v< -MAXNUM)return 0;*result=v;return 1;}
 if(oper=='-'){long v=a-b;if(v>MAXNUM||v< -MAXNUM)return 0;*result=v;return 1;}
 if(oper=='*'){
  aw=x/1000L;af=x%1000L;bw=y/1000L;bf=y%1000L;
  if(bw && aw>(MAXNUM/1000L)/bw)return 0;
  z=aw*bw*1000L;
  if(!checked_add(z,aw*bf,&t))return 0;z=t;
  if(!checked_add(z,af*bw,&t))return 0;z=t;
  if(!checked_add(z,af*bf/1000L,&t))return 0;z=t;
 }else if(oper=='/'){
  if(!y)return 0;
  q=x/y;if(q>MAXNUM/1000L)return 0;
  z=q*1000L;rem=x%y;frac=0;
  for(i=0;i<3;i++){rem*=10L;frac=frac*10L+(rem/y);rem%=y;}
  if(!checked_add(z,frac,&t))return 0;z=t;
 }else return 0;
 *result=sign?-(long)z:(long)z;
 return 1;
}
static void press(HWND wnd,char key){
 long result;int n;
 if(key=='C'){typing=0;failed=0;pending=0;current=saved=0;}
 else if(key=='E'){typing=0;failed=0;current=0;}
 else if(key=='B'){
  if(!failed){if(!typing){format(current,input);typing=1;}
   n=lstrlen(input);
   if(n>1){input[n-1]=0;if(input[n-2]=='-'&&input[n-1]==0)lstrcpy(input,"0");}
   else lstrcpy(input,"0");
   if(!parse(input,&current)){current=0;lstrcpy(input,"0");}
  }
 }else if(key=='S'){
  if(!failed){current=-current;if(typing)format(current,input);}
 }else if((key>='0'&&key<='9') || key=='.'){digit(key);return;}
 else if(key=='+'||key=='-'||key=='*'||key=='/'){
  if(!failed){
   if(pending && typing){
    if(!operate(pending,saved,current,&result)){failed=1;pending=0;}
    else {current=result;saved=current;}
   }else saved=current;
   if(!failed)pending=key;typing=0;
  }
 }else if(key=='='){
  if(!failed && pending){
   if(!operate(pending,saved,current,&result))failed=1;
   else current=result;
   pending=0;typing=0;
  }
 }
 refresh();SetFocus(wnd);
}
LONG FAR PASCAL TinyProc(HWND wnd,UINT msg,WPARAM wp,LPARAM lp){
 int i;
 switch(msg){
 case WM_CREATE:
  display_hwnd=CreateWindow("STATIC","0",WS_CHILD|WS_VISIBLE|WS_BORDER|SS_RIGHT,
   4,3,181,22,wnd,(HMENU)DISP,instance,NULL);
  if(!display_hwnd)return -1L;
  SendMessage(display_hwnd,WM_SETFONT,(WPARAM)GetStockObject(SYSTEM_FIXED_FONT),0L);
  for(i=0;i<NBTN;i++){
   buttons[i]=CreateWindow("BUTTON",labels[i],WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON,
    4+(i%4)*46,28+(i/4)*22,43,20,wnd,(HMENU)(FIRST+i),instance,NULL);
   if(!buttons[i])return -1L;
   SendMessage(buttons[i],WM_SETFONT,(WPARAM)GetStockObject(SYSTEM_FIXED_FONT),0L);
  }
  return 0;
 case WM_COMMAND:
  if(wp>=FIRST && wp<FIRST+NBTN){press(wnd,symbols[wp-FIRST]);return 0;}
  break;
 case WM_CHAR:
  if((wp>='0'&&wp<='9')||wp=='.'||wp=='+'||wp=='-'||wp=='*'||wp=='/'||wp=='='){
   press(wnd,(char)wp);return 0;
  }
  if(wp==8){press(wnd,'B');return 0;}
  break;
 case WM_KEYDOWN:
  if(wp==VK_RETURN){press(wnd,'=');return 0;}
  if(wp==VK_ESCAPE){press(wnd,'C');return 0;}
  break;
 case WM_DESTROY:PostQuitMessage(0);return 0;
 }
 return DefWindowProc(wnd,msg,wp,lp);
}
int PASCAL WinMain(HINSTANCE inst,HINSTANCE prev,LPSTR cmd,int show){
 WNDCLASS wc;HWND wnd;MSG msg;int x,y;
 instance=inst;
 if(!prev){
  wc.style=CS_HREDRAW|CS_VREDRAW;wc.lpfnWndProc=TinyProc;
  wc.cbClsExtra=0;wc.cbWndExtra=0;wc.hInstance=inst;
  wc.hIcon=NULL;wc.hCursor=LoadCursor(NULL,IDC_ARROW);
  wc.hbrBackground=GetStockObject(WHITE_BRUSH);wc.lpszMenuName=NULL;
  wc.lpszClassName="TandyTinyCalc";
  if(!RegisterClass(&wc))return 1;
 }
 x=(GetSystemMetrics(SM_CXSCREEN)-194)/2;if(x<0)x=0;
 y=(GetSystemMetrics(SM_CYSCREEN)-166)/2;if(y<0)y=0;
 wnd=CreateWindow("TandyTinyCalc","TinyCalc 16",WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX|WS_CLIPCHILDREN,
  x,y,194,166,NULL,NULL,inst,NULL);
 if(!wnd)return 2;
 ShowWindow(wnd,show);UpdateWindow(wnd);SetFocus(wnd);
 while(GetMessage(&msg,NULL,0,0)){TranslateMessage(&msg);DispatchMessage(&msg);}
 return msg.wParam;
}
