#! /usr/bin/env python2
# v0.11

#///////////////////////////////////////////////////////////////////////////////
#/ MIT License                                                                //
#/                                                                            //   
#/ Copyright (c) [2015] [Andreas Genewsky]                                    //  
#/                                                                            //
#/ Permission is hereby granted, free of charge, to any person obtaining a    //
#/ copy of this software and associated documentation files (the "Software"), //
#/ to deal in the Software without restriction, including without limitation  //
#/ the rights to use, copy, modify, merge, publish, distribute, sublicense,   //
#/ and/or sell copies of the Software, and to permit persons to whom the      //
#/ Software is furnished to do so, subject to the following conditions:       //
#/                                                                            //
#/ The above copyright notice and this permission notice shall be included    //
#/ in all copies or substantial portions of the Software.                     //
#/                                                                            //
#/ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR //
#/ IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   //
#/ FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    //
#/ THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER //
#/ LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    //
#/ FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        //   
#/ DEALINGS IN THE SOFTWARE.                                                  //
#///////////////////////////////////////////////////////////////////////////////

import serial
import time
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import ConfigParser
import tkMessageBox
import Tkinter as tk
from serial import SerialException
import sys
from time import sleep

global reset_var
reset_var = 0;
global running_var
running_var = 0
global curr_NoT
curr_NoT = 0
global lat_OFF_list 
lat_OFF_list = []
global lat_ON_list 
lat_ON_list = []
global trial_list 
trial_list = []
global sides_list 
sides_list = []
global dist_OFF_list 
dist_OFF_list = []
global dist_ON_list 
dist_ON_list = []
global tof_list
tof_list = []
global its_list
its_list = []
global start_t
start_t = 0.0
global stop_OFF_t
stop_OFF_t = 0.0
global stop_ON_t
stop_ON_t = 0.0
global last_t
last_t = 0.0
global lat_OFF
lat_OFF = 0.0
global lat_ON
lat_ON = 0.0
global we_are_moving
we_are_moving = 0
global we_are_flying
we_are_flying = 0
global we_are_balancing
we_are_balancing = 0
global curr_arm
curr_arm = None	
global opp_arm
opp_arm = None
global servo1_pos
servo1_pos = 0
global servo2_pos
servo2_pos = 0
global takeoff_t
takeoff_t = None
global landing_t
landing_t = None
global its
its = 0

global before 
before = None
global now
now = None


global ser

def portIsUsable(portName):
	global ser
	try:
		ser = serial.Serial(port=portName)
		return True
	except:
		tk.Tk().withdraw() #avoids the second window popping up!
		tkMessageBox.showerror("Open Port","Cannot open port\n\n(%s)" % portName)
		sys.exit(0)
		return False

if portIsUsable('/dev/ttyACM0'):
	ser = serial.Serial('/dev/ttyACM0', 115200,timeout=None)
	ser.flushInput()
	#print("Reset Arduino")
	time.sleep(2)


class App (Tkinter.Frame):

	def __init__(self, master):
		
		Frame.__init__(self)
		global running_var
		global return_val
		global servoA_dir
		servoA_dir= 1

		global servoB_dir
		servoB_dir = 1
		return_val = None
		
		self._start = 0.0        
		self._elapsedtime = 0.0
		self._running = 0
		frame = Frame(master)
		frame.grid(row=0)
		
		global acclimation_period
		acclimation_period = StringVar(master)
		acclimation_period.set("2.0")
		
		global iti
		iti = StringVar(master)
		iti.set("1.0")
		
		global weight
		weight = StringVar(master)
		weight.set("15")
		
		global speed
		speed = StringVar(master)
		speed.set("2.3")
		
		global NoT
		NoT = StringVar(master)
		NoT.set("10")
		
		global acclimation_min
		acclimation_min = 0.1
		global acclimation_max
		acclimation_max = 10
		
		global iti_min
		iti_min = 0.1
		global iti_max
		iti_max = 10
		
		global weight_min
		weight_min = 1
		global weight_max
		weight_max = 50
		
		global speed_min
		speed_min = 0.1
		global speed_max
		speed_max = 5
		
		global NoT_min
		NoT_min = 1
		global NoT_max
		NoT_max = 50
		
		global weight_var_A
		weight_var_A=0
		
		global weight_var_B
		weight_var_B=0
		
		global vals_to_PC
		vals_to_PC = ['0', '0', '0', '0', '0']	
		
		global old_vals_to_PC
		old_vals_to_PC = ['0', '0', '0', '0', '0']	
		
		vcmd_acclimation = master.register(self._OnValidate_acclimation),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
		vcmd_iti = master.register(self._OnValidate_iti),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
		vcmd_weight = master.register(self._OnValidate_weight),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
		vcmd_speed = master.register(self._OnValidate_speed),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
		vcmd_NoT = master.register(self._OnValidate_NoT),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
		
		#ACCLIMATION		
		self.acclimation = Label(frame, text="Acclimation Period", justify=LEFT,height=2, width=20).grid(row=0,column=0,sticky=W,rowspan=2,padx=(2,0))
		self.acclimation_sb = Spinbox(frame, from_=acclimation_min, to=acclimation_max, increment=0.5, textvariable=acclimation_period,font="Verdana 11", validate="key", 
                              validatecommand=vcmd_acclimation, width = 10).grid(row=0,column=1,sticky=EW,rowspan=2, columnspan = 1)
		self.acc_ord = Label(frame, text="min", justify=RIGHT,height=2, font="fixedsys 10 bold").grid(row=0,column=2,sticky=W,rowspan=2,padx=(0,2))
		
		#ITI
		self.iti = Label(frame, text="Intertrial Interval", justify=LEFT,height=2, width=20).grid(row=2,column=0,sticky=W,rowspan=2,padx=(2,0))
		self.iti_sb = Spinbox(frame, from_=iti_min, to=iti_max, increment=0.5, textvariable=iti,font="Verdana 11", validate="key", 
                              validatecommand=vcmd_iti, width = 10).grid(row=2,column=1,sticky=EW,rowspan=2, columnspan = 1)
		self.iti_ord = Label(frame, text="min", justify=RIGHT,height=2, font="fixedsys 10 bold").grid(row=2,column=2,sticky=W,rowspan=2,padx=(0,2))
		
		#WEIGHT
		self.weight = Label(frame, text="Weight Threshold", justify=LEFT,height=2, width=20).grid(row=4,column=0,sticky=W,rowspan=2,padx=(2,0))
		self.weight_sb = Spinbox(frame, from_=weight_min, to=weight_max, increment=1, textvariable=weight,font="Verdana 11", validate="key", 
                              validatecommand=vcmd_weight, width = 10).grid(row=4,column=1,sticky=EW,rowspan=2, columnspan = 1)
		self.weight_ord = Label(frame, text="grams", justify=RIGHT,height=2, font="fixedsys 10 bold").grid(row=4,column=2,sticky=W,rowspan=2,padx=(0,2))
		
		#SPEED
		self.speed = Label(frame, text="Speed", justify=LEFT,height=2, width=20).grid(row=6,column=0,sticky=W,rowspan=2,padx=(2,0))
		self.speed_sb = Spinbox(frame, from_=speed_min, to=speed_max, increment=0.1, textvariable=speed,font="Verdana 11", validate="key", 
                              validatecommand=vcmd_speed, width = 10).grid(row=6,column=1,sticky=EW,rowspan=2, columnspan = 1)
		self.speed_ord = Label(frame, text="mm/s", justify=RIGHT,height=2, font="fixedsys 10 bold").grid(row=6,column=2,sticky=W,rowspan=2,padx=(0,2))
		
		#NoT
		self.NoT = Label(frame, text="Number of Trials", justify=LEFT,height=2, width=20).grid(row=8,column=0,sticky=W,rowspan=2,padx=(2,0))
		self.NoT_sb = Spinbox(frame, from_=NoT_min, to=NoT_max, increment=1, textvariable=NoT,font="Verdana 11", validate="key", 
                              validatecommand=vcmd_NoT, width = 10).grid(row=8,column=1,sticky=EW,rowspan=2, columnspan = 1)
		self.NoT_ord = Label(frame, text=" ", justify=RIGHT,height=2, font="fixedsys 10 bold").grid(row=8,column=2,sticky=W,rowspan=2,padx=(0,2))
		
		#TIME
		global timestr
		timestr = StringVar() 
		global time_label
		time_label = Label(frame, textvariable=timestr,relief=SUNKEN,borderwidth=3, font="device 10", bg="white", padx=8, pady=1)
		time_label.grid(row=10,column=0,rowspan=2)
		
		#CLOCK Control
		self.startbutton = Tkinter.Button(frame,text=u"Start", command=self.Start, font="fixedsys 10 bold",borderwidth=2, width = 2).grid(row=10,column=1,sticky=W,rowspan=2)
		self.stopbutton = Tkinter.Button(frame,text=u"Stop", command=self.Stop, font="fixedsys 10 bold",borderwidth=2, width = 2).grid(row=10,column=1,rowspan=2)
		self.resetbutton = Tkinter.Button(frame,text=u"Reset", command=self.Reset, font="fixedsys 10 bold",borderwidth=2, width = 2).grid(row=10,column=1,sticky=E,rowspan=2)
		#self.quitbutton = Tkinter.Button(frame,text=u"Quit", command=self.quit, font="fixedsys 10 bold",borderwidth=2).grid(row=10,column=2,sticky=E,rowspan=2)
		
		#SEPARATORS
		#those get poorly updated when the window is e.g. covered with the terminal .... maybe get removed in v0.2
		separator1=Frame(frame,height=10,bg="").grid(row=12, columnspan=4,sticky=NSEW,rowspan=1)
		separator2=Frame(frame,height=1,bg="").grid(row=14, columnspan=4,sticky=NSEW,rowspan=1)
		separator3=Frame(frame,height=10,bg="").grid(row=16, columnspan=4,sticky=NSEW,rowspan=1)
		separator4=Frame(frame,height=10,bg="").grid(row=21, columnspan=4,sticky=NSEW,rowspan=1)
		separator5=Frame(frame,height=10,bg="").grid(row=23, columnspan=4,sticky=NSEW,rowspan=1)
		
		#LED Control
		#No function till now!
		#led_a = Checkbutton(frame,text=" LED A",font="fixedsys 8")
		#led_a.grid(row=13,column=0,sticky=W,padx=5)
		#led_b = Checkbutton(frame,text=" LED B",font="fixedsys 8")
		#led_b.grid(row=15,column=0,sticky=W,padx=5)
		
		global weight_A
		weight_A_l = Label(frame,text="Weight A", height=1).grid(row=13,column=0,sticky=E)
		weight_A = Label(frame,text=weight_var_A, height=1, relief=SUNKEN, anchor=N)
		weight_A.grid(row=13,column=1,sticky=NSEW)
		weight_A_ord = Label(frame, text="grams", justify=RIGHT, font="fixedsys 10 bold").grid(row=13,column=2,sticky=W,padx=(0,2))
		
		global weight_B
		weight_A_l = Label(frame,text="Weight B", height=1).grid(row=15,column=0,sticky=E)
		weight_B = Label(frame,text=weight_var_B, height=1, relief=SUNKEN, anchor=N)
		weight_B.grid(row=15,column=1,sticky=NSEW)
		weight_B_ord = Label(frame, text="grams", justify=RIGHT, font="fixedsys 10 bold").grid(row=15,column=2,sticky=W,padx=(0,2))
		
		#SLIDERS
		global slide_A,slide_A_label2
		slide_A_label = Label(frame,text="Pos A").grid(row=18,column=0,sticky=E,rowspan=2,pady=(0,3))
		slide_A = Scale(frame, from_=140, to=0,orient=HORIZONTAL,showvalue=0,sliderlength=20,length=150,troughcolor="white")
		slide_A.grid(row=18,column=1,columnspan=1,sticky=W,rowspan=2)
		slide_A_label2 = Label(frame,text=servo1_pos, width=5)
		slide_A_label2.grid(row=18,column=2,sticky=W,rowspan=2,pady=(0,8),padx=(0,10))
		
		#RST A
		global slide_A_rst
		slide_A_rst = Button(frame,text="A Reset",font="fixedsys 10 bold",command=lambda: self.hard_reset("A"),bg="gray" )
		slide_A_rst.grid(row=18,column=0,sticky=W,ipadx=5,padx=5)
		
		global slide_B,slide_B_label2
		slide_B_label = Label(frame,text="Pos B").grid(row=20,column=0,sticky=E,rowspan=2,pady=(0,13))
		slide_B = Scale(frame, from_=140, to=0,orient=HORIZONTAL,showvalue=0,sliderlength=20,length=150,troughcolor="white")
		slide_B.grid(row=20,column=1,columnspan=1,sticky=W,rowspan=2)
		slide_B_label2 = Label(frame,text=servo2_pos, width=5)
		slide_B_label2.grid(row=20,column=2,sticky=W,rowspan=2,pady=(0,16),padx=(0,10))
		#RST B
		global slide_B_rst
		slide_B_rst = Button(frame,text="B Reset",font="fixedsys 10 bold", command=lambda: self.hard_reset("B"),bg="gray" )
		slide_B_rst.grid(row=20,column=0,sticky=W,ipadx=5,padx=5)
	
		#STATUS BAR
		global status_field
		status_field = Label(frame,text="... waiting ", fg="black",height=2, relief=SUNKEN, justify=LEFT)
		status_field.grid(row=22,column=0,columnspan=4,sticky=NSEW,padx=(2,2))
	
		#TEXT Fields
		global lines
		lines=NoT.get()
		global trial_window
		trial_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		trial_window.grid(row=24,column=0,sticky=W)
		global sides_window
		sides_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		sides_window.grid(row=24,column=0,sticky=E)		
		global lat_OFF_window
		lat_OFF_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		lat_OFF_window.grid(row=24,column=1,sticky=W)
		#global dist_OFF_window
		#dist_OFF_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		#dist_OFF_window.grid(row=24,column=1,sticky=W)
		#global dist_ON_window
		#dist_ON_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		#dist_ON_window.grid(row=24,column=1)
		#global tof_window
		#tof_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		#tof_window.grid(row=24,column=1,sticky=E)
		global lat_ON_window
		lat_ON_window=Text(frame,height=lines,width=12,font="fixedsys 8",spacing2=1,spacing3=2)
		lat_ON_window.grid(row=24,column=1,sticky=E)
		global its_window
		its_window=Text(frame,height=lines,width=8,font="fixedsys 8",spacing2=1,spacing3=2)
		its_window.grid(row=24,column=2,sticky=W)

		
		trial_window.insert(END,"TRIAL:"+"\n")
		sides_window.insert(END, "ARM:"+"\n")
		lat_OFF_window.insert(END,"LAT_OFF:"+"\n")
		#dist_OFF_window.insert(END,"DIST_OFF:"+"\n")
		lat_ON_window.insert(END,"LAT_ON:"+"\n")
		#dist_ON_window.insert(END,"DIST_ON:"+"\n")
		#tof_window.insert(END,"ToF:"+"\n")
		its_window.insert(END,"ITS:"+"\n")
		
		
		self.makeWidgets() 
		
	def hard_reset(self,arm): 
		""" Kinda the Emergency Reset, e.g. also stops the clock """
		global reset_var
		if (arm == "A"):
			reset_var=1
		if (arm == "B"):
			reset_var=2	
	
	def round_to(self,n, precision):
		correction = 0.5 if n >= 0 else -0.5
		return int( n/precision+correction ) * precision

	def round_to_5(self,n):
		return self.round_to(n, 0.5)
		
	def _update_values(self):
		""" This function updates and parses the values read from the arduino """
		global old_vals_to_PC
		global vals_to_PC
		global weight_var_A
		global weight_var_B
		global servo1_pos
		global servo2_pos
		global distanceA 
		global distanceB
		
		line = self._readline()
		vals_to_PC=line.split(',')
		
		if (self.validate_vals(4)==True):	
			old_vals_to_PC=vals_to_PC
		if (self.validate_vals(4)==False):
			print vals_to_PC
			vals_to_PC=old_vals_to_PC
		
		weight_var_A = int(round( (0.5*float(vals_to_PC[0])+0.5*float(old_vals_to_PC[0])),0))
		weight_var_B = int(round( (0.5*float(vals_to_PC[1])+0.5*float(old_vals_to_PC[1])),0))
		servo1_pos = float(round( (0.5*float(vals_to_PC[2])+0.5*float(old_vals_to_PC[2])),0))
		servo2_pos = float(round( (0.5*float(vals_to_PC[3])+0.5*float(old_vals_to_PC[3])),0))
		
		weight_var_A = self.round_to_5(round((0.0749129009*float(weight_var_A)-0.9088320258),2))
		weight_var_B = self.round_to_5(round((0.0763157054*float(weight_var_B)-0.9683740794),2))
				
		#update labels
		weight_A.configure(text=weight_var_A)
		weight_B.configure(text=weight_var_B)
		
		if weight_var_A>=float(weight.get()):
			weight_A.configure(bg='lawn green')
		else:
			weight_A.configure(bg=defaultbg)
		if weight_var_B>=float(weight.get()):
			weight_B.configure(bg='lawn green')	
		else:
			weight_B.configure(bg=defaultbg)
		
		distanceA = int( round(((-5.92613311630418E-8)*(servo1_pos*servo1_pos*servo1_pos)+0.0002948917*(servo1_pos*servo1_pos)-0.3487265211*servo1_pos+115.5057514142),0))
		distanceB = int( round(((7.19346722522172E-8)*(servo2_pos*servo2_pos*servo2_pos)-0.0003226514*(servo2_pos*servo2_pos)+0.3380168316*servo2_pos+49.1057851055),0))
		if (distanceA <= 1):
			distanceA = 0
		if (distanceB <= 1):
			distanceB = 0
		
		slide_A.set(distanceA)
		slide_A_label2.configure(text=distanceA)
		slide_B.set(distanceB)
		slide_B_label2.configure(text=distanceB)
		if (distanceA<140):
			slide_A_rst.config(bg="IndianRed1")
		else:
			slide_A_rst.config(bg="gray")
		if (distanceB<140):
			slide_B_rst.config(bg="IndianRed1")
		else:
			slide_B_rst.config(bg="gray")
				
	def validate_vals(self,length): 
		""" As not all values from the arduino are valid we need to make sense out of the gibberish """
		global vals_to_PC, old_vals_to_PC
		try:
			for x in range(0,length):
				vals_to_PC[x].isdigit()
				a=int(vals_to_PC[x])
			return True
				
		except (ValueError, IndexError) as e:
			print e
			print vals_to_PC
			vals_to_PC=old_vals_to_PC
			return False	
		except:
			print "Other Error!"
			print vals_to_PC
		
	def _OnValidate_acclimation(self, d, i, P, s, S, v, V, W):
		"""This function checks if the input values into the spinboxes are valid"""
		if S in '0123456789.':
			try:
				float(P)
				return (float(P)>=acclimation_min) and (float(P)<=acclimation_max)
			except ValueError:
				return False
		else:
			return False
			
	def _OnValidate_iti(self, d, i, P, s, S, v, V, W):
		"""This function checks if the input values into the spinboxes are valid"""		
		if S in '0123456789.':
			try:
				float(P)
				return (float(P)>=iti_min) and (float(P)<=iti_max)
			except ValueError:
				return False
		else:
			return False

	def _OnValidate_weight(self, d, i, P, s, S, v, V, W):
		"""This function checks if the input values into the spinboxes are valid"""		
		if S in '0123456789.':
			try:
				float(P)
				return (float(P)>=weight_min) and (float(P)<=weight_max)
			except ValueError:
				return False
		else:
			return False

	def _OnValidate_speed(self, d, i, P, s, S, v, V, W):
		"""This function checks if the input values into the spinboxes are valid"""		
		if S in '0123456789.':
			try:
				float(P)
				return (float(P)>=speed_min) and (float(P)<=speed_max)
			except ValueError:
				return False
		else:
			return False

	def _OnValidate_NoT(self, d, i, P, s, S, v, V, W):
		"""This function checks if the input values into the spinboxes are valid"""		
		if S in '0123456789.':
			try:
				float(P)
				return (float(P)>=NoT_min) and (float(P)<=NoT_max)
			except ValueError:
				return False
		else:
			return False

	def _readline(self):
		eol = b'\n'
		leneol = len(eol)
		line = bytearray()
		while True:
			c = ser.read(1)
			if c:
				line += c
				if line[-leneol:] == eol:
					break
			else:
				break
		return bytes(line)
	
	def makeWidgets(self):                         
		""" Make the time label. """
		self._setTime(self._elapsedtime)
		
	def _update(self): 
		""" Update the label with elapsed time. """
		self._elapsedtime = time.time() - self._start
		self._setTime(self._elapsedtime)
		self._timer = self.after(10, self._update)
		seconds=self._elapsedtime
		self.timed_control_new(seconds)
					   
	def _setTime(self, elap):
		global timestr
		timestr = StringVar() 
		global time_label
		""" Set the time string to Minutes:Seconds:Hundreths """
		minutes = int(elap/60)
		seconds = int(elap - minutes*60.0)
		hseconds = int((elap - minutes*60.0 - seconds)*100)                
		timestr.set('%02d:%02d:%02d' % (minutes, seconds, hseconds))
		time_label.configure(textvariable=timestr)
       
	def Start(self):   
		global running_var	 
		global servo1_dir                                                  
		""" Start the stopwatch, ignore if running. """
		if not self._running:            
			self._start = time.time() - self._elapsedtime
			self._update()
			self._running = 1    
			running_var = 1   
    
	def Stop(self):    
		global running_var	
		global servoA_dir 	
		global servoB_dir 
		global reset_var	
		
		reset_var = 0
		                                
		""" Stop the stopwatch, ignore if stopped. """
		if self._running:
			self.after_cancel(self._timer)            
			self._elapsedtime = time.time() - self._start    
			self._setTime(self._elapsedtime)
			self._running = 0
			servoA_dir = 1
			servoB_dir = 1
				   
	def Reset(self): 
		global running_var	 
		global status_field        
		global servoA_dir 	
		global servoB_dir                          
		""" Reset the stopwatch. """
		self._start = time.time()         
		self._elapsedtime = 0.0    
		self._setTime(self._elapsedtime)
		status_field.config(text="... waiting",fg="black")
		servoA_dir = 1
		servoB_dir = 1
		global curr_NoT
		curr_NoT = 0
		global lat_OFF_list 
		lat_OFF_list = []
		global lat_ON_list 
		lat_ON_list = []
		global trial_list 
		trial_list = []
		trial_window.delete(1.0, END)
		lat_OFF_window.delete(1.0, END)
		lat_ON_window.delete(1.0, END)
		global sides_list 
		sides_list = []
		sides_window.delete(1.0, END)
		global its_list
		its_list = []
		its_window.delete(1.0, END)
		global its
		its = 0
		global start_t
		start_t = 0.0
		global stop_OFF_t
		stop_OFF_t = 0.0
		global stop_ON_t
		stop_ON_t = 0.0
		global last_t
		last_t = 0.0
		global lat_OFF
		lat_OFF = 0.0
		global lat_ON
		lat_ON = 0.0
		global we_are_moving
		we_are_moving = 0
		global we_are_flying
		we_are_flying = 0
		global we_are_balancing
		we_are_balancing = 0

	def move_servo(self,arm):
		global servoA_dir
		global servoB_dir
		
		if(arm=="A"):
				servoA_dir = 2
				servoB_dir = 1
		if(arm=="B"):
				servoA_dir = 1
				servoB_dir = 2
		if(arm==None):
				servoA_dir = 1
				servoB_dir = 1
						
	def stop_servo(self):
		global servoA_dir
		global servoB_dir
		servoA_dir = 1
		servoB_dir = 1
			
	def which_arm(self, which):
		global weight_var_A
		global weight_var_B
		global weight
		val=(int(weight.get()))
		
		if(which=="current"):
			if (weight_var_A>val) and (weight_var_B<val): 	
				return "A"
			if (weight_var_A<val) and (weight_var_B>val):	
				return "B"
			if (weight_var_A>=val) and (weight_var_B>=val):	
				return None
			if (weight_var_A<=val) and (weight_var_B<=val):	
				return None
		if(which=="other"):
			if (weight_var_A>val) and (weight_var_B<val): 	
				return "B"
			if (weight_var_A<val) and (weight_var_B>val):	
				return "A"
			if (weight_var_A>=val) and (weight_var_B>=val):	
				return None
			if (weight_var_A<=val) and (weight_var_B<=val):	
				return None
	
	def distance_get(self,arm):
		global distanceA
		global distanceB
		if (arm == "A"):
			return distanceA
		if (arm == "B"):
			return distanceB
		else:
			return None
				
	def get_weight(self,arm):
		global weight_var_A
		global weight_var_B

		if(arm == "A"):
			return weight_var_A
		if(arm == "B"):
			return weight_var_B
			
	def show_data(self):
		global lat_OFF_list, lat_ON_list, lines, trial_list, sides_list, its_list
		top = Toplevel()
		top.title("Whole Data Set")
		all_data_window=Text(top,height=lines,width=50,font="fixedsys 8",spacing2=1,spacing3=2)
		all_data_window.grid(row=0,column=0,columnspan=1,sticky=NSEW)
		
		all_data_window.delete(1.0, END)
		lines=int(NoT.get())+2
		all_data_window.config(height=lines)
		
		header = "Trial"+"\t"+"ARM"+"\t"+"LAT_OFF"+"\t"+"LAT_ON"+"\t"+"ITS"+"\n"
		all_data_window.insert(END,header)
		for i in xrange(0,len(trial_list)):  
			all_data_window.insert(END,str(trial_list[i])+"\t"+str(sides_list[i])+"\t"+str(lat_OFF_list[i])+"\t"+str(lat_ON_list[i])+"\t"+str(its_list[i])+"\n")
		
		button = Button(top, text="Close", command=top.destroy)
		button.grid(row=1, column=0)
		
	def timed_control_new(self,seconds):
		global status_field
		global weight
		global NoT
		global curr_NoT
		global trials
		global start_t
		global stop_OFF_t
		global stop_ON_t
		global last_t
		global lat_OFF
		global lat_ON
		global distanceA, distanceB
		global curr_arm, opp_arm
		global we_are_moving
		global we_are_flying
		global we_are_balancing
		global weight_var_A
		global weight_var_B
		global reset_var
		global trial_window, lat_OFF_window, lat_ON_window, sides_window 
		global lat_OFF_list, lat_ON_list, lines, trial_list, sides_list 
		global servoA_dir, servoB_dir	
		global its
		global before, now
		
		w_threshold=(int(weight.get()))
		trials = int(NoT.get())
		iti_t = float(iti.get())*60.0
		acc_t = float(acclimation_period.get())*60.0
		
		# It is impossible to debug without a good EVENT pipe.
		# So we need a least a debug line
		
		
		if (curr_NoT<trials):
			
			if (seconds < acc_t):
				acc_var=StringVar()
				seconds_left= acc_t-seconds
				mins = int(seconds_left/60)
				secs = int(seconds_left-mins*60)
				acc_var = "Acclimation Period: "+ str('%02d:%02d' % (mins, secs))
				status_field.config(text=acc_var,fg="red2")
				
			if (seconds > acc_t): 
				if ((seconds < (last_t + iti_t)) and (curr_NoT > 0)):
					iti_var=StringVar()
					seconds_left= ( float(iti.get())*60.0 + last_t )-seconds
					mins = int(seconds_left/60.0)
					secs = int(seconds_left-mins*60.0)
					iti_var = "Time to next Trial: "+ str('%02d:%02d' % (mins, secs))
					status_field.config(text=iti_var,fg="black")	
					we_are_moving=0
					
					if (before == None):
						before = self.which_arm("current")
					if (before is not None):
						now = self.which_arm("current")
					if (before is not now) and (self.which_arm("current") is not None) :
						its += 1
						before = now
									
				if ((seconds > (last_t + iti_t)) or (curr_NoT==0)):
					
					if (we_are_moving==0):
						start_t = seconds
						we_are_moving = 1
										
					if (curr_arm == None):	
						curr_arm = self.which_arm("current")
						opp_arm = self.which_arm("other")
					if (curr_arm == None):	
						self.Stop()
						print "Where is the mouse?!"
						warn_var=StringVar()
						warn_var="#####     Empty Platforms ...  #####"
						status_field.config(text=warn_var,fg="red2")
					
					if (curr_arm is not None):
						
						curr_weight = self.get_weight(curr_arm)
						opp_weight = self.get_weight(opp_arm)
										
						if ((we_are_moving == 1) and (we_are_flying == 0) and (curr_weight <= w_threshold) and (opp_weight <= w_threshold)):
							stop_OFF_t = seconds 
							lat_OFF = round(stop_OFF_t - start_t,2)
							lat_OFF_list.append(lat_OFF)
							we_are_flying = 1
						
					
						if ((we_are_moving == 1) and (we_are_flying == 0) and (we_are_balancing == 0) and (curr_weight >= w_threshold) and (opp_weight >= w_threshold)):
							stop_OFF_t = seconds 
							lat_OFF = round(stop_OFF_t - start_t,2)
							lat_OFF_list.append(lat_OFF)
							we_are_balancing = 1
						
														
						if ((we_are_moving == 1) and (curr_weight < w_threshold) and (opp_weight > w_threshold)):
							we_are_moving = 0 
							we_are_flying = 0 
							we_are_balancing = 0 
							trial_list.append(curr_NoT+1)
							curr_NoT += 1 
							last_t = seconds 
							stop_ON_t = seconds
							lat_ON = round(stop_ON_t - start_t,2)
							lat_ON_list.append(lat_ON)
							
							if (len(lat_OFF_list) != len(lat_ON_list)): 
								# This means the animal jumped within less than 25 ms, and no takeoff event 
								# could be detected !!
								print "Superfast Jump!"
								stop_OFF_t = seconds 
								lat_OFF = round(stop_OFF_t - start_t,2)
								lat_OFF_list.append(lat_OFF)
																						
							if (curr_arm == "A"):
								reset_var=1
								sides_list.append("A")
							if (curr_arm == "B"):
								reset_var=2
								sides_list.append("B")
								
							lines=int(NoT.get())+2
							trial_window.config(height=lines)
							lat_OFF_window.config(height=lines)
							lat_ON_window.config(height=lines)
							sides_window.configure(height=lines)
							its_window.configure(height=lines)
							
							trial_window.delete(1.0, END)
							sides_window.delete(1.0, END)
							lat_OFF_window.delete(1.0, END)
							lat_ON_window.delete(1.0, END)
							its_window.delete(1.0, END)
											
							trial_window.insert(END,"Trial:"+"\n")
							sides_window.insert(END, "ARM:"+"\n")
							lat_OFF_window.insert(END,"LAT_OFF:"+"\n")
							lat_ON_window.insert(END,"LAT_ON:"+"\n")
							its_window.insert(END,"ITS:"+"\n")
							
							for z in trial_list:
								trial_window.insert(END, str(z)+"\n")
							for v in sides_list:
								sides_window.insert(END, str(v)+"\n")
							for y in lat_OFF_list:
								lat_OFF_window.insert(END, str(y)+"\n")
							for w in lat_ON_list:
								lat_ON_window.insert(END, str(w)+"\n")
							for q in its_list:
								its_window.insert(END, str(q)+"\n")
														
							self.stop_servo() #after landing
							curr_arm = None #after landing
							its = 0 #after landing
							now = None #after landing
							before = None #after landing
							sleep(0.05) #TEST to avoid Superfast Jumps with additional recordings seems to work for now
							
							
								
										
						if ((we_are_moving == 1) and (curr_weight > w_threshold)):
							
							if ((curr_NoT > 0) and its is not None):
								its_list.append(its)
								its_window.delete(1.0, END)
								its_window.insert(END,"ITS:"+"\n")
								for q in its_list:
									its_window.insert(END, str(q)+"\n")
								its=None
								
							elap_var=StringVar()
							seconds_elap = seconds-start_t
							mins = int(seconds_elap/60.0)
							secs = int(seconds_elap-mins*60.0)
							elap_var= "Trial: "+ str('%00d' % (curr_NoT+1))+"	elapsed Time: "+str('%02d:%02d' % (mins, secs))
							status_field.config(text=elap_var,fg="green4")
							self.move_servo(curr_arm)
						
						
		
		if ((curr_NoT>=trials) and (stop_ON_t > 0.0)):
			fin_var=StringVar()
			fin_var="FINISHED"
			status_field.config(text=fin_var,fg="green4")
			self.stop_servo()
			self.Stop()
				
			if ((curr_NoT > 0) and its is not None):
				its_list.append(its)
				its_window.delete(1.0, END)
				its_window.insert(END,"ITS:"+"\n")
				for q in its_list:
					its_window.insert(END, str(q)+"\n")
				its=None
			stop_OFF_t = 0.0 	#?
			stop_ON_t = 0.0		#?
			
def main(): 
	root = Tk()
	global defaultbg
	defaultbg = root.cget('bg')
	app = App(root)

	root.title("MWB Controller v0.11")
	global calibration_factor
	calibration_factor = 4.4
	global speed_time_iti
	speed_time_iti = int( round( (1000/(calibration_factor*float(speed.get()))),0) )
	
	def wait_for_mouse():
		global curr_arm
		global opp_arm
		global we_are_moving
		global start_t
		if((we_are_moving == 1) and (curr_arm == None)):
			curr_arm = app.which_arm("current")
			opp_arm = app.which_arm("other")
			if (curr_arm is not None):
				print "There it is!"
				we_are_moving = 0
				app.Start()
		root.after(1000,wait_for_mouse)
			
	def _send_data():
		global speed_time_iti
		global servo1_pos
		global servo2_pos
		global reset_var
		global servoA_dir, servoB_dir
		servo1_min = 2148
		servo2_min = 958
		
		global calibration_factor
		calibration_factor = 4.4
		global speed_time_iti
		speed_time_iti = int( round( (1000/(calibration_factor*float(speed.get()))),0) )
		global data
				
		reset_time_iti = 10
		
		#not elegant ... I know.
		data= str(servoA_dir)+"|"+str(servoB_dir)+":"
		if (reset_var==0):	
			ser.write(data)
			ser.flush()
			root.after(speed_time_iti,_send_data) 
		
		if (reset_var==1) and (servo1_pos<servo1_min):
			data= "0"+"|"+"1"+":"
			ser.write(data)
			ser.flushInput() 
			root.after(reset_time_iti,_send_data) 
		if (reset_var==1) and (servo1_pos==servo1_min):
			data= "1"+"|"+"1"+":"
			ser.write(data)
			ser.flushInput()
			reset_var=0
			root.after(reset_time_iti,_send_data) 
	
		if (reset_var==2) and (servo2_pos>servo2_min):
			data= "1"+"|"+"0"+":"
			ser.write(data)
			ser.flushInput()
			root.after(reset_time_iti,_send_data) 
		if (reset_var==2) and (servo2_pos==servo2_min):
			data= "1"+"|"+"1"+":"
			ser.write(data)
			ser.flushInput() 
			reset_var=0
			root.after(reset_time_iti,_send_data) 

	def _recieve_data():
		app._update_values()
		root.after(10,_recieve_data) #speed is the trick here!
		
	def show_about():
		top = Toplevel()
		top.title("About")
		about_message = "This app was created to control the Moving Wall Box. By Andreas Genewsky 2015. Enjoy ..."
		msg = Message(top, text=about_message)
		msg.pack()

		button = Button(top, text="Close", command=top.destroy)
		button.pack()
	
	menubar = Menu(root)
	# create a pulldown menu, and add it to the menu bar
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="Show Data", command=app.show_data)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=root.quit)
	menubar.add_cascade(label="File", menu=filemenu)
	helpmenu = Menu(menubar, tearoff=0)
	helpmenu.add_command(label="About", command=show_about)
	menubar.add_cascade(label="Help", menu=helpmenu)

	# display the menu
	root.config(menu=menubar)	
		

	
	root.after(500,wait_for_mouse)
	root.after( speed_time_iti,_send_data)
	#We always want to recieve data, with 15 Hz accuracy
	root.after( 67,_recieve_data)
	
	root.mainloop()
	ser.close()
		
if __name__ == '__main__':
	main()
