#!/usr/bin/env python

import argparse,srt,datetime
t = datetime.timedelta(microseconds=1000)

def hms2ms(string):
    parts = [x if x else 0 for x in string.replace(",",".").split(":")]
    parts = (3-len(parts))*[0]+parts
    assert(len(parts)==3)
    h,m,s = int(parts[0]),int(parts[1]),float(parts[2])
    return int((h*3600+m*60+s)*1000)

parser = argparse.ArgumentParser(description = 'subfix tool')

parser.add_argument('file')
parser.add_argument('-d', '--delay', type=int, default=0, help='apply delay in ms')
parser.add_argument('-l', '--linear', type=str, default=None, nargs=4, help='linear map: s1 to a1 and s2 to a2')
parser.add_argument('-D', '--delays', type=str, default=None, nargs=4, help='delays map: t1 delay1(ms) t2 delay2(ms)')

args = parser.parse_args()

with open(args.file,'r',encoding='utf-8') as f:
    lines = f.readlines()

file = list(srt.sort_and_reindex(srt.parse(''.join(lines))))
index,start,end,content = zip(*[[x.index,int(x.start/t),int(x.end/t),srt.make_legal_content(x.content)] for x in file])

if args.delay:
    start = [x + args.delay for x in start]
    end = [x + args.delay for x in end]
elif args.linear is not None:
    s1,a1,s2,a2 = [*map(hms2ms,args.linear)]
    fun = lambda x: int((x-s1)/(s2-s1)*(a2-a1)+a1)
    start = [fun(x) for x in start]
    end = [fun(x) for x in end]
elif args.delays is not None:
    a1,d1,a2,d2 = hms2ms(args.delays[0]),int(args.delays[1]),hms2ms(args.delays[2]),int(args.delays[3])
    s1 = a1-d1 ; s2 = a2-d2
    fun = lambda x: int((x-s1)/(s2-s1)*(a2-a1)+a1)
    start = [fun(x) for x in start]
    end = [fun(x) for x in end]

out = srt.compose([srt.Subtitle(index=i,start=datetime.timedelta(microseconds=s*1000),end=datetime.timedelta(microseconds=e*1000),content=c) for i,s,e,c in zip(index,start,end,content)])

with open(args.file.replace(".srt","_fixed.srt"),'w',encoding='utf-8') as f:
    f.writelines(out)
