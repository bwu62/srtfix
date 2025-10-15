#!/usr/bin/env python

import argparse,srt,datetime

# define t=1000microseconds, used later to convert srt package's output from microseconds to milliseconds (ms)
t = datetime.timedelta(microseconds=1000)

# define custom function to convert hms timestamp to ms, while respecting omitted leading components
def hms2ms(string):
    # fix comma-decimals then hms timestamp into components
    parts = [x if x else 0 for x in string.replace(",",".").split(":")]
    # if any leading components missing, add them back in as 0s
    parts = (3-len(parts))*[0]+parts
    # assert we have exactly 3 components for h,m,s, then save
    assert(len(parts)==3)
    h,m,s = int(parts[0]),int(parts[1]),float(parts[2])
    # compute and return ms
    return int((h*3600+m*60+s)*1000)

# parse arguments
parser = argparse.ArgumentParser(description = 'srtfix tool')
parser.add_argument('file')
parser.add_argument('-d', '--delay', type=int, default=0, help='apply delay in ms')
parser.add_argument('-l', '--linear', type=str, default=None, nargs=4, help='linear map: s1 to v1 and s2 to v2')
parser.add_argument('-D', '--delays', type=str, default=None, nargs=4, help='delays map: t1 delay1(ms) t2 delay2(ms)')
args = parser.parse_args()

# read in subtitle file assuming utf-8 encoding
with open(args.file,'r',encoding='utf-8') as f:
    lines = f.readlines()

# use srt package to parse and check sort/index of each subtitle entry
file = list(srt.sort_and_reindex(srt.parse(''.join(lines))))
# also check each entry for "legality", then separately store indices, start/end times, and text
# note srt package gives start/end times in microseconds, so divide by t and round to nearest ms
index,start,end,content = zip(*[[x.index,int(x.start/t),int(x.end/t),srt.make_legal_content(x.content)] for x in file])

# switch for what operation is requested
if args.delay:
    # for simple delay, just add delay in ms to each start/end time
    start = [x + args.delay for x in start]
    end = [x + args.delay for x in end]
elif args.linear is not None:
    # for linear map, first parse each timestamp to ms
    # s1,s2 are 2 points in subtitle file, v1,v2 are two points in video
    s1,v1,s2,v2 = [*map(hms2ms,args.linear)]
    # define the linear map function, can check this is correct by plugging in s1,s2 and noting it's indeed linear
    fun = lambda x: int((x-s1)/(s2-s1)*(v2-v1)+v1)
    # apply map to each start/end time
    start = [fun(x) for x in start]
    end = [fun(x) for x in end]
elif args.delays is not None:
    # for delay map, again parse timestamps & delay amounts to ms
    # at points v1,v2 in video, delay values of d1,d2 are respectively necessary to align subs
    v1,d1,v2,d2 = hms2ms(args.delays[0]),int(args.delays[1]),hms2ms(args.delays[2]),int(args.delays[3])
    # compute corresponding s1,s2 which are timestamps in subtitle file that should be linearly mapped to v1,v2
    # note if d1 > 0 then s1 < v1 by amount of d1, thus s1 = v1-d1, and same goes for d2,s2,v2
    s1 = v1-d1 ; s2 = v2-d2
    # apply same map function to start/end times
    fun = lambda x: int((x-s1)/(s2-s1)*(v2-v1)+v1)
    start = [fun(x) for x in start]
    end = [fun(x) for x in end]

# convert times back to microseconds, zip everything, then "compose" into a subtitle file
out = srt.compose([srt.Subtitle(index=i,start=datetime.timedelta(microseconds=s*1000),end=datetime.timedelta(microseconds=e*1000),content=c) for i,s,e,c in zip(index,start,end,content)])

# write file back out with filename suffix
with open(args.file.replace(".srt","_fixed.srt"),'w',encoding='utf-8') as f:
    f.writelines(out)
