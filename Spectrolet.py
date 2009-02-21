#!/usr/bin/env python
#
#+   Copyright (c) 2009 Ian Halpern
#@   http://Spectrolet.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys, gtk, cairo, time, random, struct, signal
from gtk import gdk
from threading import Thread

from numpy import *

if gtk.pygtk_version < ( 2, 9, 0 ):
	print "PyGtk 2.9.0 or later required"
	raise SystemExit

CHUNK = 1024    # audio stream buffer size

keep_processing = True

audio_sample = ""
pixmap = None

# This is called when we need to draw the windows contents
def expose ( widget, event=None ):
	global pixmap

	widget.window.draw_drawable( widget.window.new_gc( ), pixmap,
        # Only copy the area that was exposed.
        event.area.x, event.area.y,
        event.area.x, event.area.y,
        event.area.width, event.area.height )
	return True


def draw ( ):
	global audio_sample, pixmap

	#audio_sample = ""

	if not audio_sample:
		audio_sample = ""

		#for x in range( CHUNK ):
		#	audio_sample += chr( int( random.random( ) * 256 ) )

	audio_sample_str = audio_sample.ljust( CHUNK, chr( 0x00 ) )

	audio_sample_array = array( map( ord, struct.unpack( 'c' * CHUNK, audio_sample_str ) ) )

	# audio_sample_array = fft.fft( audio_sample_array )

	l = len( audio_sample_array )

	gdk.threads_enter( )
	width, height = pixmap.get_size( )
	gdk.threads_leave( )

	cst = cairo.ImageSurface( cairo.FORMAT_ARGB32, width, height )

	cr = cairo.Context( cst )

	# start drawing spectrum

	cr.set_source_rgba( 0.0, 0.6, 1.0, 0.8 )

	for i in range( 0, l, l / 32 ):
		bar_freq = struct.unpack( 'i', ''.join( map( chr, audio_sample_array[ i : i + 4 ] ) ) )[ 0 ]

		#bar_freq = struct.unpack( 'i', audio_sample_str[ i : i + 4 ] )[ 0 ]

		#normalize
		bar_freq_norm = bar_freq / float( 0x7fffffff )

		bar_heigth = bar_freq_norm * height + 2

		bar_width = 16
		bar_spacing = 1

		cr.rectangle(
			( bar_width + bar_spacing ) * ( i / ( l / 32 ) ),
			height / 2 - bar_heigth / 2,
			bar_width,
			bar_heigth
		)

	cr.fill( )
	cr.stroke( )

	# end drawing

	gdk.threads_enter( )

	cr_pixmap = pixmap.cairo_create( )

	cr_pixmap.set_source_rgba( 1.0, 1.0, 1.0, 0.0 ) # Transparent
	# Draw the background
	cr_pixmap.set_operator( cairo.OPERATOR_SOURCE )
	cr_pixmap.paint( )

	cr_pixmap.set_source_surface( cst, 0, 0 )
	cr_pixmap.paint( )

	gdk.threads_leave( )

	return False

def screenChanged ( widget, old_screen=None ):

	# To check if the display supports alpha channels, get the colormap
	screen = widget.get_screen( )
	colormap = screen.get_rgba_colormap( )
	# Now we have a colormap appropriate for the screen, use it
	widget.set_colormap( colormap )

	return False

def timerExecFrame ( win ):
	global pixmap
	draw( )

	gdk.threads_enter( )
	width, height = pixmap.get_size( )
	win.queue_draw_area( 0, 0, width, height )
	win.window.process_updates( True )
	gdk.threads_leave( )

def discontinueProcessing ( ):
	global keep_processing
	keep_processing = False
	return 0

def captureAudio ( ):
	global keep_processing, audio_sample

	audio_stream = os.popen3( "esdmon" )

	while keep_processing:
		audio_sample = audio_stream[ 1 ].read( CHUNK )

	for stream in audio_stream:
		stream.close( )

	print "\ncaptureAudio Thread Die..."

def animationLoop ( win ):
	global keep_processing

	while keep_processing:
		timerExecFrame( win )
		time.sleep( 1.0 / 30 )

	print "\nanimationLoop Thread Die..."
#def triggerRedraw ( win ):
#	width, height = win.get_size( )
#	win.queue_draw_area(0, 0, width, height)
#	win.window.process_updates( True )


def main(args):
	global keep_processing, pixmap

	gdk.threads_init( )
	gdk.threads_enter( )


	width = 544
	height = 300

	screen = gdk.screen_get_default( )

	win = gtk.Window( )

	win.set_title( 'Spectrumize' )
	win.set_default_size( width, height )

	win.stick( )
	win.set_keep_below( True )
	win.set_decorated( False )
	win.set_skip_taskbar_hint( True )
	#win.set_gravity( gdk.GRAVITY_CENTER )

	win.connect( 'delete-event', gtk.main_quit )
	win.connect( 'expose-event', expose )
	win.connect( 'screen-changed', screenChanged )

	# initialize for the current display
	screenChanged( win )
	# Run the program
	win.show_all( )

	pixmap = gdk.Pixmap( win.window, width, height, -1 )

	# Tell GTK+ that we want to draw the windows background ourself.
	win.set_app_paintable(  True )
	win.set_double_buffered( False )

	screen_rect = screen.get_monitor_geometry( 0 )

	win.move( screen_rect.width / 2 - width / 2 + screen_rect.x, screen_rect.height / 2 - height / 2 + screen_rect.y )


	ca_thread = Thread( target=captureAudio )
	ca_thread.start( )

	al_thread = Thread( target=animationLoop, args=(win,) )
	al_thread.start( )

	#try:
	#	while keep_processing:
	#		timerExecFrame( win )
	#		time.sleep( 1.0 / 30 )
	#except KeyboardInterrupt:
	#	print "Error: KeyboardInterrupt Caught..."

	try:
		gtk.main( )
	except KeyboardInterrupt:
		pass

	gdk.threads_leave( )

	discontinueProcessing( )

	ca_thread.join( )
	#al_thread.join( )


	print "Main Thead Die..."
	return True

if __name__ == '__main__':

	try:
		import ctypes
		libc = ctypes.CDLL('libc.so.6')
		libc.prctl(15, sys.argv[ 0 ], 0, 0, 0)
	except:
		pass

	#signal.signal( signal.SIGINT, discontinueProcessing )
	sys.exit( main( sys.argv ) )

