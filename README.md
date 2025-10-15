# srtfix

small &amp; simple script to fix srt subtitle timings

## motivation

i watch a lot of movies and needed a short and simple script to fix misaligned or stretched srt files

## usage

3 main features:

1. `-d` delay: delay subs by x ms,    
   example:

   ```
   # delay subs.srt by 1500ms (make them appear 1.5s later)
   ./srtfix.py -d 1500 subs.srt
   
   # to make subs appear 1500ms earlier instead, use negative delay
   ./srtfix.py -d -1500 subs.srt
   ```

2. `-l` linear map: stretch & shift subs by linearly mapping 2 timestamps in subs.srt to 2 timestamps in the video, useful if video and subtitles use different frame rates, such as if you have NTSC video but PAL subs (for best results, pick 2 timestamps far apart in the file)    
   example:

   ```
   # map 00:00:52.500 in subs.srt to 00:01:15.200 in video, and
   # map 01:25:52.000 in subs.srt to 01:27:00.000 in video
   ./srtfix.py -l 52.5 1:15.2 1:25:52 1:27:0 subs.srt
   
   # note leading components that are 0 can be omitted, and milliseconds become fractional seconds
   ```

3. `-D` delay map: stretch & shift subs by specifying at 2 timestamps in the video what delay in ms is necessary to fix alignment, this is personally my favorite way to stretch & shift, since it's easier to use and can achieve very precise alignment (again, for best results, pick 2 timestamps far apart in the file)
   example:

   ```
   # suppose at 00:01:30 in the video, the subs need to be delayed by -1500ms to be aligned,
   # but around 01:25:40 in the video, the subs need to be delayed by 3600ms to be aligned
   ./srtfix.py -D 1:30 -1500 1:25:40 3600 subs.srt
   ```

## output

output file is always the input srt with "_fixed" appended at the end of the filename (if this name already exists, it will be overwritten without warning)

## future todo

this file is currently a very simplistic mvp, future ideas of things to do:

- auto detect encoding of input
- add support for .ass subtitle files
- other?
