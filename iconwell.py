#!/usr/bin/env python

# Adapted from:
# a pygtk widget that implements a clock face
# porting of Davyd Madeley's 
# http://www.gnome.org/~davyd/gnome-journal-cairo-article/clock-ex3.c

# and adapted from Rounded rect example (cairo website)

# author: Lawrence Oluyede <l.oluyede@gmail.com>
# date: 03 December 2005

"""
(C) Ulrik Sverdrup 2007
My changes: GNU GPL v2 (or later)
"""

from __future__ import division
import gtk

class IconWell(gtk.DrawingArea):
	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.connect("expose_event", self.expose)
		self.icon = None
		self.size = None
		self.active = False
	
	def set_from_pixbuf(self, pbuf):
		"""
		Set the icon from a pixbuf
		"""
		self.icon = pbuf
		if not self.size and pbuf:
			self.size = 10 + max(pbuf.get_width(), pbuf.get_height())
			self.set_size_request(self.size, self.size)
		self.queue_draw()
	
	def clear(self):
		"""
		Clear cur icon
		"""
		self.icon = None
		self.queue_draw()
	
	def set_active(self, flag):
		self.active = flag
		self.queue_draw()
		
	def expose(self, widget, event):
		self.context = widget.window.cairo_create()
		
		# set a clip region for the expose event
		self.context.rectangle(event.area.x, event.area.y,
							   event.area.width, event.area.height)
		self.context.clip()
		
		self.draw(self.context)
		
		return False
	
	def draw(self, context):
		rect = self.get_allocation()
		if self.active:
			self.setup_rounded(context)
		if self.icon:
			ic_w, ic_h = self.icon.get_width(), self.icon.get_height()
			corner_x = (rect.width-ic_w)/2
			corner_y = (rect.height-ic_h)/2
			context.set_source_pixbuf(self.icon, corner_x, corner_y)
			context.paint()
	
	def setup_rounded(self, context):
		rect = self.get_allocation()
		offs = 30
		self.rounded_rect(context, -offs/2, -offs/2,rect.width +offs, rect.height + offs, radius=40)
		# Get the current selection color
		ent = gtk.Entry()
		newc = ent.style.bg[3]
		scale = 1/2**16
		context.set_source_rgb (newc.red*scale, newc.green*scale, newc.blue*scale) 
		context.fill_preserve ()
		
	def rounded_rect(self,cr,x,y,width,height,radius=5):
		"""
		From cairo examples. Draws a rounded rectangle
		"""
		x0	   = x+radius/2.0  
		y0	   = y+radius/2.0
		rect_width  = width - radius
		rect_height = height - radius

		cr.save()

		x1=x0+rect_width
		y1=y0+rect_height
		if rect_width/2<radius:
			if rect_height/2<radius:
				cr.move_to  (x0, (y0 + y1)/2)
				cr.curve_to (x0 ,y0, x0, y0, (x0 + x1)/2, y0)
				cr.curve_to (x1, y0, x1, y0, x1, (y0 + y1)/2)
				cr.curve_to (x1, y1, x1, y1, (x1 + x0)/2, y1)
				cr.curve_to (x0, y1, x0, y1, x0, (y0 + y1)/2)
			else:
				cr.move_to  (x0, y0 + radius)
				cr.curve_to (x0 ,y0, x0, y0, (x0 + x1)/2, y0)
				cr.curve_to (x1, y0, x1, y0, x1, y0 + radius)
				cr.line_to (x1 , y1 - radius)
				cr.curve_to (x1, y1, x1, y1, (x1 + x0)/2, y1)
				cr.curve_to (x0, y1, x0, y1, x0, y1- radius)

		else:
			if rect_height/2<radius:
				cr.move_to  (x0, (y0 + y1)/2)
				cr.curve_to (x0 , y0, x0 , y0, x0 + radius, y0)
				cr.line_to (x1 - radius, y0)
				cr.curve_to (x1, y0, x1, y0, x1, (y0 + y1)/2)
				cr.curve_to (x1, y1, x1, y1, x1 - radius, y1)
				cr.line_to (x0 + radius, y1)
				cr.curve_to (x0, y1, x0, y1, x0, (y0 + y1)/2)
			else:
				cr.move_to  (x0, y0 + radius)
				cr.curve_to (x0 , y0, x0 , y0, x0 + radius, y0)
				cr.line_to (x1 - radius, y0)
				cr.curve_to (x1, y0, x1, y0, x1, y0 + radius)
				cr.line_to (x1 , y1 - radius)
				cr.curve_to (x1, y1, x1, y1, x1 - radius, y1)
				cr.line_to (x0 + radius, y1)
				cr.curve_to (x0, y1, x0, y1, x0, y1- radius)

		cr.close_path ()

		cr.restore()

if __name__ == "__main__":
	import icons
	window = gtk.Window()
	clock = IconWell()
	clock.set_from_pixbuf(icons.get_icon_for_name("folder", 96))
	clock.set_active(True)
	
	window.add(clock)
	window.connect("destroy", gtk.main_quit)
	window.show_all()
	
	gtk.main()
