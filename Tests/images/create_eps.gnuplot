#!/usr/bin/gnuplot

#This is the script that was used to create our sample EPS files
#We used the following version of the gnuplot program
#G N U P L O T
#Version 4.6 patchlevel 3    last modified 2013-04-12
#Build System: Darwin x86_64

#This file will generate the non_zero_bb.eps variant, in order to get the
#zero_bb.eps variant you will need to edit line6 in the result file to
#be "%%BoundingBox: 0 0 460 352" instead of "%%BoundingBox: 50 50 410 302"

set t postscript eps color
set o "sample.eps"
set dummy u,v
set key bmargin center horizontal Right noreverse enhanced autotitles nobox
set parametric
set view 50, 30, 1, 1
set isosamples 10, 10
set hidden3d back offset 1 trianglepattern 3 undefined 1 altdiagonal bentover
set ticslevel 0
set title "Interlocking Tori"

set style line 1 lt 1 lw 1 pt 3 lc rgb "red"
set style line 2 lt 1 lw 1 pt 3 lc rgb "blue"

set urange [ -3.14159 : 3.14159 ] noreverse nowriteback
set vrange [ -3.14159 : 3.14159 ] noreverse nowriteback
splot cos(u)+.5*cos(u)*cos(v),sin(u)+.5*sin(u)*cos(v),.5*sin(v) ls 1,\
      1+cos(u)+.5*cos(u)*cos(v),.5*sin(v),sin(u)+.5*sin(u)*cos(v) ls 2
