import math

fft=True

def load_theme( screenlet ):
	screenlet.resize( 300, 300 )

def on_draw( audio_sample_array, cr ):

	l = len( audio_sample_array )

	width, height = ( 300, 300 )

	cr.set_source_rgba( 0.0, 0.6, 1.0, 0.8 )

	n_bars = 32

	cr.set_line_width( 4 )

	for i in range( 0, l, l / n_bars ):

		bar_amp_norm = audio_sample_array[ i ]

		bar_height = bar_amp_norm * 130 + 5

		for j in range( 0, int( bar_height / 5 ) ):
			cr.arc(
				width / 2,
				height / 2,
				20 + j * 5,
				( math.pi*2 / n_bars ) * ( i / ( l / n_bars ) ),
				( math.pi*2 / n_bars ) * ( i / ( l / n_bars ) + 1 ) - .05
			)

			cr.stroke( )
