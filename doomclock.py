"""	
Copyright (C) 2011 by Mark Frimston

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.



TODO: unit markings
TODO: millisecond accuracy
TODO: detailed progress
TODO: chime
TODO: analog clockface
"""

import sys
import getopt
import curses
import time
import os.path

BIG_DIGITS = {
	' ':[
		"     ",
		"     ",
		"     ",
		"     "
	],
	'0':[
		"  _  ",
		" / \\ ",
		"|   |",
		" \\_/ "
	],
	'1':[
		"     ",
		" /|  ",
		"  |  ",
		" _|_ "
	],
	'2':[
		" ___ ",
		"'   |",
		"  /  ",
		"/____"	
	],
	'3':[
		" ____",
		"  __/",
		"    \\ ",
		" ___/",
	],
	'4':[
		"  _  ",
		" / | ",
		"/__|_",
		"   | "
	],
	'5':[
		"_____",
		"|___ ",
		"    \\",
		" ___/"
	],
	'6':[
		"  __ ",
		" /__ ",
		"|   \\",
		" \\__/"
	],
	'7':[
		"_____",
		"    |",
		"   / ",
		"  /  "
	],
	'8':[
		" ___ ",
		"/   \\",
		">---<",
		"\\___/"
	],
	'9':[
		" ___ ",
		"/   \\",
		"`-- /",
		"   / "
	],
	':':[
		"     ",
		"  O  ",
		"     ",
		"  O  "
	],
}

BAR_HEIGHT = 5
BIG_CHAR_HEIGHT = 4
BIG_CHAR_WIDTH = 5
CONFIG_FILEPATH = "~/.doomclock"

class Option(object):

	short = ""
	long = ""
	has_val = False
	value = False
	desc = ""
	
	def __init__(self, short, long, has_val=False, value=False, desc=""):
		self.short = short
		self.long = long
		self.has_val = has_val
		self.value = value
		self.desc = desc
		
def redraw_bar(scrn,frac):
	h,w = scrn.getmaxyx()
	total = w-2
	filled = int(round(total*frac))
	empty = total-filled
	barline = "#"*filled + ":"*empty
	barh = min(h-2,BAR_HEIGHT)
	for i in range(barh):
		scrn.addstr(1+i,1,barline)

def remainder(num,denom):
	return ( num//denom, num%denom )

def redraw_countdown(scrn,millisleft):
	h,w = scrn.getmaxyx()
	hour,rem = remainder(millisleft,1000*60*60)
	min,rem = remainder(rem, 1000*60)
	sec,mill = remainder(rem, 1000)
	timestr = str(hour).rjust(2,'0') + ":" + str(min).rjust(2,'0') + ":" + str(sec).rjust(2,'0')
	big_text(scrn,1+BAR_HEIGHT, w/2-len(timestr)*BIG_CHAR_WIDTH/2, timestr)

def redraw_all(scrn):
	redraw_bar(scrn,0)
	redraw_countdown(scrn,0)

def parse_time(strtime):
	t = time.strptime(strtime,"%H:%M")
	return t.tm_hour*60*60*1000 + t.tm_min*60*1000
	
def big_text(scrn,row,col,text):
	h,w = scrn.getmaxyx()
	for j in range(BIG_CHAR_HEIGHT):
		for i,c in enumerate(text):
			if c in BIG_DIGITS:
				charmap = BIG_DIGITS[c]
			else:
				charmap = BIG_DIGITS[' ']
			r,c = row+j, col+i*BIG_CHAR_WIDTH
			if r < h and c >= 0 and c+BIG_CHAR_WIDTH < w:
				scrn.addstr(r,c,charmap[j])
	
def current_mill():
	t = time.localtime(time.time())
	return t.tm_hour*60*60*1000 + t.tm_min*60*1000 + t.tm_sec*1000

def limit(val,minval,maxval):
	return min(maxval,max(minval,val))

def main(scrn,startmill,endmill):
	
	curses.curs_set(0)
	redraw_all(scrn)

	while True:
		currmill = current_mill()
		frac = limit(float(currmill-startmill)/(endmill-startmill), 0.0,1.0)
		redraw_bar(scrn,frac)
		leftmillis = limit(endmill-currmill, 0, endmill-startmill)
		redraw_countdown(scrn,leftmillis)
		scrn.refresh()
		time.sleep(1.0)

def print_usage():
	optdesc = "Options:\n"
	for k in options:
		optdesc += "-%s	--%s		%s\n" % (options[k].short,
			options[k].long, options[k].desc)
	print "Usage: python %s [options]\n\n%s" % (sys.argv[0],optdesc)		

def parse_arguments(optdata,arguments):
	
	opts,args = getopt.getopt( arguments,
		"".join([options[x].short+(":" if options[x].has_val else "") for x in optdata]),
		[optdata[x].long+("=" if optdata[x].has_val else "") for x in optdata] )
	
	for o,v in opts:
		for k in optdata:
			if o in ("-"+optdata[k].short,"--"+optdata[k].long):
				if optdata[k].has_val:
					optdata[k].value = v	
				else:
					optdata[k].value = True
				break					
	
def parse_config_file(optdata):
	
	path = os.path.expanduser(CONFIG_FILEPATH)
	if os.path.exists(path):
		with open(path,'r') as file:
			for line in file:
				if line.startswith("#"):
					continue
				parts = map(str.strip, line.split("=",1))
				name,val = parts if len(parts)>1 else (parts[0],None)
				print name,val
				for k in optdata:
					if name == optdata[k].long:
						if optdata[k].has_val:
							if not val is None:
								optdata[k].value = val
						else:
							optdata[k].value = True
						break

options = {
	"help" 	: Option("h","help",desc="Shows this help and exits"),
	"start" : Option("s","start",True,"9:00","The start of the working day, in 24hr hh:mm format"),
	"end"	: Option("e","end",True,"17:00","The end of the working day, in 24hr hh:mm format"),
}

parse_config_file(options)

try:
	parse_arguments(options,sys.argv[1:])
except getopt.GetoptError as e:
	print e
	print_usage()
	sys.exit(2)

if options["help"].value:
	print_usage()
	sys.exit(2)

start = parse_time(options["start"].value)
end = parse_time(options["end"].value)

curses.wrapper(lambda s: main(s,start,end))
