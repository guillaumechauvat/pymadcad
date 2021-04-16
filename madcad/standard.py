'''
	Module exposing many functions to create/visualize standard parts.
	Those are following the ISO (metric) specifications as often as possible.
	
	Most parts are as easy to create as:
	
		>>> nut(8)    # nut with nominal diameter 8mm
		>>> screw(8, 16)   # screw with match diameter 8mm, and length 16mm
		
	The parts usually have many optional parameters that default to usual recommended values. You can override this by setting the keyword arguments:
	
		>>> screw(8, 16, head='button', drive='slot')
'''

from operator import itemgetter

from .mathutils import *
from .primitives import *
from .mesh import Mesh, Web, Wire, web, wire
from .generation import *
from .blending import *
from .boolean import *
from .cut import *
from .io import cachefunc

cachefunc = lambda x:x	# debug purpose


__all__ = [	'nut', 'screw', 'washer', 
			'coilspring_compression', 'coilspring_tension', 'coilspring_torsion',
			]


def ipn(h) -> Web:
	indev

def nut(d, b, h, type, detail=False) -> Mesh:
	indev
	
	
# --------- screw stuff -----------------------
	
	
@cachefunc
def screw(d, length, filet_length=None, head='SH', drive=None, detail=False):
	''' create a standard screw using the given drive and head shapes
	
	Parameters:
		:d:             nominal diameter of the screw
		:length:        length from the screw head to the tip of the screw
		:filet_length:  length of the filet on the screw (from the tip), defaults to `length`
		
		:head:          name of the screw head shape
		:drive:			name of the screw drive shape
		:detail:   if True, the thread surface will be generated, else it will only be a cylinder
		
	It's also possible to specify head and drive at once, using their codenames:
	
		>>> screw(5, 16, head='SHT')   # socket head and torx drive
		
	available screw heads:
		* socket (default)
		* button
		* flat (aka. cone)
		
	available screw drives:
		* hex
		* torx  *(not yet available)*
		* phillips (cross)  *(not yet available)*
		* slot
	
	All possible shapes:
		* see wikipedia for the [drive types](https://en.wikipedia.org/wiki/List_of_screw_drives)
		* see [here for a guide of what to use](https://www.homestratosphere.com/types-of-screws/)
		* see wikipedia for [standard screw thread](https://en.wikipedia.org/wiki/ISO_metric_screw_thread)
		
		
	'''
	if filet_length is None:	filet_length = length - 0.05*d
	elif length < filet_length:	raise ValueError('filet_length must be smaller than length')
	
	
	head, drive = screw_spec(head, drive)
	head = globals()['screwhead_'+head](d)
	if drive:
		drive = globals()['screwdrive_'+drive](d) .transform(boundingbox(head).max[2]*Z)
		head = intersection(head, drive)
		
	r = 0.5*d
	body = revolution(2*pi, (vec3(0),vec3(0,0,1)), wire([
					-vec3(r, 0, 0.05*d),
					-vec3(r, 0, length-filet_length),
					-vec3(r, 0, length-r*0.2),
					-vec3(r*0.8, 0, length),
					-vec3(0, 0, length),
					]) .segmented())
	screw = body + head
	screw.finish()
	return screw

def screwdrive_torx(d):
	indev
	
def screwdrive_hex(d):
	base = regon((-0.3*d*Z, -Z), 0.5*d, 6)
	socket = extrusion(d*Z, base) + blendloop(base, center=-0.6*d*Z, weight=-1)
	socket.mergeclose()
	return socket
	
def screwdrive_cross(d):
	indev
	
def screwdrive_slot(d):
	w = 0.15*d
	h = 0.3*d
	e = 2*d
	return extrusion(2*e*X, web([
				vec3(-e, w, h),
				vec3(-e, w, -h),
				vec3(-e, -w, -h),
				vec3(-e, -w, h),
				]) .segmented())

def screwhead_socket(d):
	''' screw head shape for socket head (SH) '''
	r = h = 0.7*d
	c = 0.05*d
	
	profile = wire([
			vec3(d/2,	0,	-c),
			vec3(d/2+c,	0,	0),
			vec3(r,     0,  0), 
			vec3(r,     0,  h-c),
			vec3(r-c,   0,  h),
			vec3(0,     0,  h),
			]) .segmented()
	head = revolution(-2*pi, (O,Z), profile)
	head.finish()
	return head
	
def screwhead_hex(d):
	''' screw head shape for hex head (HH) '''
	r = 0.9*d
	h = 0.6*d
	c = 0.05*d
	
	profile = extrusion(2*d*Z, regon((-d*Z,Z), r, 6))
	cone = revolution(2*pi, (O,Z), web([
		vec3(0,       0, h),
		vec3(0.8*r,   0, h),
		vec3(1.01*r,  0, h*0.8),
		vec3(1.01*r,  0, 0),
		vec3(0.5*d+c, 0, 0),
		vec3(0.5*d,   0, -c),
		]) .segmented())
	cone.mergeclose()
	head = intersection(cone, profile)
	head.finish()
	return head
	
def screwhead_button(d):
	r = 0.95*d
	h = 0.5*d
	c = 0.05*d
	
	profile = [
		wire([
			vec3(0, 0, h), 
			vec3(0, 0.5*d, h),
			]),
		TangentEllipsis(
			vec3(0, 0.5*d, h), 
			vec3(0, 0.9*r, h),
			vec3(0, r, 0.1*d)),
		wire([
			vec3(0, r, 0.1*d),
			vec3(0, r, 0),
			vec3(0, 0.5*d+c, 0),
			vec3(0, 0.5*d, -c),
			]) .segmented(),
		]
	head = revolution(2*pi, (O,Z), profile)
	head.mergeclose()
	return head
	
def screwhead_flat(d):
	r = d
	h = 0.5*d
	e = 0.1*d
	
	cone = revolution(2*pi, (O,Z), web([
		vec3(0, 0, h+e),
		vec3(0, r, h+e),
		vec3(0, r, h),
		vec3(0, 0.5*d, 0),
		]) .segmented() )
	cone.mergeclose()
	return cone
	
def screwhead_none(d):
	indev

	
'''
	head shapes:
	Abbreviation 	Expansion 	Comment
	BH 		button head 
	FH 		flat head 	
	OH 		oval head 	
	PH 		Phillips head 	
	RH 		round head 		
	FHP		flat head Phillips 	
	RHP 	round head Phillips 	
	SH 		socket head			Although "socket head" could logically refer to almost any female drive, it refers by convention to hex socket head unless further specified.
	SS 		set screw			The abbreviation "SS" more often means stainless steel. Therefore, "SS cap screw" means "stainless steel cap screw" but "SHSS" means "socket head set screw". As with many abbreviations, users rely on context to diminish the ambiguity, although this reliance does not eliminate it.
	VH		conic head
	
	CS 		cap screw 	
	MS 		machine screw 	
	
	BHCS 	button head cap screw 	
	BHMS 	button head machine screw 	
	FHCS 	flat head cap screw 
	FHSCS 	flat head socket cap screw 	
	FHPMS 	flat head Phillips machine screw 	
	FT 		full thread 	
	HHCS 	hex head cap screw 	
	HSHCS 	Hexalobular socket head cap screws 	
	RHMS 	round head machine screw 	
	RHPMS 	round head Phillips machine screw 	
	SBHCS 	socket button head cap screw 	
	SBHMS 	socket button head machine screw 	
	SHCS 	socket head cap screw 	
	SHSS 	socket head set screw 	Sometimes Socket Head Shoulder Screw.
	STS 	self-tapping screw
	
	[standard screw thread](https://en.wikipedia.org/wiki/ISO_metric_screw_thread)
'''

screwheads_codes = {
	'SH': 'socket',
	'HH': 'hex',
	'VH': 'flat',
	'cone': 'flat',
	'BH': 'button',
	'SBH': 'button',
	'SS': 'none',
	'FT': 'none',
	}
	
screwdrives_codes = {
	'TX': 'torx',
	'T': 'torx',
	'TR': 'torx',
	'CS': 'cap',
	'phillips': 'cross',
	'P': 'cross',
	'PH': 'cross',
	'PH': 'cross',
	}

def screw_spec(head, drive=None):
	if not drive:
		if head.isupper():
			for code in screwdrives_codes:
				if head.endswith(code):
					head, drive = head[:-len(code)], code
					break
	
	head = screwheads_codes.get(head, head)
	drive = screwdrives_codes.get(drive, drive)
	# special cases
	if head != 'hex' and not drive:
		drive = 'hex'
		
	return head, drive


# ------------------- nut stuff ----------------------

@cachefunc
def nut(d, type='hex', detail=False) -> Mesh:
	''' create a standard nut model using the given shape type 
	
		Parameters
			:d:        nominal diameter of the matching screw
			:type:     the nut shape
			:detail:   if True, the thread surface will be generated, else it will only be a cylinder
	
		If `d` alone is given, the other parameters default to the ISO specs: https://www.engineersedge.com/iso_flat_washer.htm
		
		Currently only shape 'hex' is available.
	'''
	args = standard_hexnuts[bisect(standard_hexnuts, d, key=itemgetter(0))]
	if args[0] != d:
		raise ValueError('no standard nut for the given diameter')
	return hexnut(*args)

	
def hexnut(d, w, h):
	''' create an hexagon nut with custom dimensions '''
	# revolution profile
	w *= 0.5
	r = 1.01 * w/cos(radians(30))
	profile = wire([
		vec3(0.5*d,	0,	0.5*h),
		vec3(0.95*w,	0,	0.5*h),
		vec3(r,	0,	0.5*h - (r-w)),
		vec3(r,	0,	-0.5*h + (r-w)),
		vec3(0.95*w,	0,	-0.5*h),
		vec3(0.5*d,	0,	-0.5*h),
		]) .close() .segmented()
	base = revolution(2*pi, (O,Z), web(profile))
	base.mergeclose()
	
	# exterior hexagon shape
	hexagon = regon((-h*Z,Z),  w/cos(radians(30)), 6)
	ext = extrusion(2*h*Z, hexagon)
	
	# intersect everything
	nut = intersection(base, ext)
	chamfer(nut, nut.frontiers(4,5) + nut.frontiers(0,5), ('width', d*0.1))

	nut.finish()
	return nut

''' iso hexagon nuts according to [EN ISO 4032](https://www.fasteners.eu/standards/ISO/4032/)
	columns:
	* thread
	* w
	* h
'''
standard_hexnuts = [
	(1.6,  3.2, 1.3),
	(2,    4,   1.6),
	(2.5,  5,   2),
	(3,    5.5, 2.4),
	(3.5,  6,   2.8), # non-prefered
	(4,    7,   3.2),
	(5,    8,   4.7),
	(6,    10,  5.2),
	(8,    13,  6.8),
	(10,   16,  8.4),
	(12,   18,  10.8),
	(14,   21,  12.8), # non-prefered
	(16,   24,  14.8),
	(18,   27,  15.8), # non-prefered
	(20,   30,  18),
	(22,   34,  19.4), # non-prefered
	(24,   36,  21.5),
	(27,   41,  23.8), # non-prefered
	(30,   46,  25.6),
	(33,   50,  38.7), # non-prefered
	(36,   55,  31),
	(39,   60,  33.4), # non-prefered
	(42,   65,  34),
	(45,   70,  36), # non-prefered
	(48,   75,  38),
	(52,   80,  42), # non-prefered
	(56,   85,  45),
	(60,   90,  48), # non-prefered
	(64,   95,  51),
	]
	
	
# -------------- washer stuff ----------------------
	
@cachefunc
def washer(d, e=None, h=None) -> Mesh:
	''' create a standard washer.
		Washers are useful to offset screws and avoid them to scratch the mount part
		
		Parameters
			:d:        the nominal interior diameter (screw or anything else),
			           the exact washer interior is slightly bigger
			:e:        exterior diameter
			:h:        height/thickness
			
		If `d` alone is given, the other parameters default to the ISO specs: https://www.engineersedge.com/iso_flat_washer.htm
	'''
	if e is None and h is None:
		args = standard_washers[bisect(standard_washers, d, key=itemgetter(0))]
		if abs(args[0] - d)/d < 0.2:
			_, d, e, h = args
		else:
			raise ValueError('no standard nut for the given diameter')
	else:
		d *= 1.1
		if e is None:	e = d*2
		if h is None:	h = d*0.1
	o = vec3(0)
	surf = blendpair(
			Circle((o,vec3(0,0,-1)), d/2), 
			Circle((o,vec3(0,0,1)), e/2),
			tangents='straight',
			)
	return extrusion(vec3(0,0,h), surf)


''' metric washers according to https://www.engineersedge.com/iso_flat_washer.htm
	columns;
	* nominal screw
	* interior size
	* exterior size
	* thickness
'''
standard_washers	= [
	(1.6, 1.7, 4,   0.3),
	(2,   2.2, 5,   0.3),
	(2.5, 2.7, 6,   0.5),
	(2.6, 2.8, 7,   0.5),
	(3,   3.2, 7,   0.5),
	(3.5, 3.7, 8,   0.5),
	(4,   4.3, 9,   0.8),
	(5,   5.3, 10,  1),
	(6,   6.4, 12,  1.6),
	(7,   7.4, 14,  1.6),
	(8,   8.4, 16,  1.6),
	(10,  10.5, 20, 2),
	(12,  13,  24,  2.5),
	(14,  15,  28,  2.5),
	(16,  17,  30,  3),
	(18,  19,  34,  3),
	(20,  21,  37,  3),
	(22,  23,  39,  3),
	(24,  25,  44,  4),
	(27,  28,  50,  4),
	(30,  31,  56,  4),
	(33,  34,  60,  5),
	(36,  37,  66,  5),
	(39,  40,  72,  6),
	(42,  43,  78,  7),
	(45,  46,  85,  7),
	(48,  50,  92,  8),
	(52,  54,  98,  8),
	(56,  58,  105, 9),
	]
	
	
	
# --------------------- coilspring stuff ------------------------

@cachefunc
def coilspring_compression(length, d=None, thickness=None, solid=True):
	''' return a Mesh model of a croilspring meant for use in compression
	
		Parameters
			:length:     the distance between its two ends
			:d:          the exterior diameter (the coilspring can fit in a cylinder of that diameter)
			:thickness:  the wire diameter of the spring (useless if solid is disabled)
			:solid:      disable it to get only the tube path of the coil, and have a `Wire` as return value
	'''
	if not d:			d = length*0.2
	if not thickness:	thickness = d*0.1
	r = d/2 - thickness		# coil radius
	e = r					# coil step
	div = settings.curve_resolution(d*pi, 2*pi)
	step = 2*pi/(div+1)
	
	t = 0
	
	t0, z0 = t, -0.5*length
	top = []
	for t in linrange(t0, t0 + 4*pi, step):
		top.append( vec3(r*cos(t), r*sin(t), z0 + (t-t0)/(2*pi) * thickness) )
	
	t0, z0 = t, -0.5*length + 2*thickness
	coil = []
	for t in linrange(t0, t0 + 2*pi * (length-4*thickness) / e, step):
		coil.append( vec3(r*cos(t), r*sin(t), z0 + (t-t0)/(2*pi) * e) )
	
	t0, z0 = t, 0.5*length - 2*thickness
	bot = []
	for t in linrange(t0, t0 + 4*pi, step):
		bot.append( vec3(r*cos(t), r*sin(t), z0 + (t-t0)/(2*pi) * thickness) )
		
	path = Wire(top, groups=['coil']) + Wire(coil, groups=['spring']) + Wire(bot, groups=['coil'])
	
	if not solid:
		return path
	
	return tube(
			flatsurface(Circle(
				(path[0],Y), 
				thickness/2, 
				resolution=('div',6)
				)) .flip(), 
			path,
			)
	
@cachefunc
def coilspring_tension(length, d=None, thickness=None, solid=True):
	''' return a Mesh model of a croilspring meant for use in tension 
	
		Parameters
			:length:     the distance between its two hooks
			:d:          the exterior diameter (the coilspring can fit in a cylinder of that diameter)
			:thickness:  the wire diameter of the spring (useless if solid is disabled)
			:solid:      disable it to get only the tube path of the coil, and have a `Wire` as return value
	'''
	if not d:			d = length*0.2
	if not thickness:	thickness = d*0.1
	r = d/2 - thickness		# coil radius
	e = r					# coil step
	
	# separate the coilspring in 3 parts:  the coil and the 2 hooks at both ides
	spring_length = length - 2*r
	ncoil = floor(spring_length / thickness) - 0.5
	hold = 0.5*length - r
	
	# create coil
	div = settings.curve_resolution(d*pi, 2*pi)
	step = 2*pi/(div+1)
	z0 = -0.5 * ncoil * thickness
	coil = Wire([	vec3(r*cos(t), r*sin(t), z0 + t/(2*pi) * thickness)
					for t in linrange(0, 2*pi * ncoil, step) ], 
				groups=['spring'])
	# create path with hooks
	path = wire([
				ArcCentered((-0.5*length*Z, X), vec3(0, -r, -0.5*length), -hold*Z),
				ArcThrough(-hold*Z, (-hold*Z + coil[0])*0.5 - 0.5*r*Y, coil[0]),
				coil,
				ArcThrough(coil[-1], (hold*Z + coil[-1])*0.5 - 0.5*r*Y, hold*Z),
				ArcCentered((0.5*length*Z, X), hold*Z, vec3(0, -r, 0.5*length)),
				])
	if not solid:
		return path
	
	return tube(
			flatsurface(Circle(
				(path[0],Z), 
				thickness/2, 
				resolution=('div',6)
				)), 
			path,
			)
	
@cachefunc
def coilspring_torsion(arm, angle=radians(45), d=None, length=None, thickness=None, hook=None, solid=True):
	''' return a Mesh model of a croilspring meant for use in torsion
	
		Parameters
			:arm:        the arms length from the coil axis
			:length:     the coil length (and distance between its hooks)
			:d:          the exterior diameter (the coilspring can fit in a cylinder of that diameter)
			:thickness:  the wire diameter of the spring (useless if solid is disabled)
			:hook:       the length of arm hooks (negative for hooks toward the interior)
			:solid:      disable it to get only the tube path of the coil, and have a `Wire` as return value
	'''
	if not length:		length = arm*0.5
	if not d:			d = arm
	if not thickness:	thickness = d*0.1
	if not hook:		hook = -length
	r = d/2 - thickness		# coil radius
	e = r					# coil step
	angle = pi - angle
	
	# separate the coilspring in 3 parts:  the coil and the 2 hooks at both ides
	ncoil = ceil(length / thickness) + angle/(2*pi)
	
	# create coil
	div = settings.curve_resolution(d*pi, 2*pi)
	step = 2*pi/(div+1)
	z0 = -0.5 * ncoil * thickness
	coil = Wire([	vec3(-r*sin(t), r*cos(t), z0 + t/(2*pi) * thickness)
					for t in linrange(0, 2*pi * ncoil, step) ], 
				groups=['spring'])
				
	# create hooks
	c = thickness * sign(hook)
	if abs(c) > abs(hook):
		hook = c
	top = Wire([
			vec3(arm, 0, hook),
			vec3(arm, 0, c),
			vec3(arm-abs(c), 0, 0),
			vec3(0),
			]) .transform(coil[0])
	bot = (top 
			.flip() 
			.transform(scaledir(Z,-1)*scaledir(X,-1)) 
			.transform(angleAxis(angle, Z))
			)
	
	# create path
	path = top + coil + bot
	path.mergeclose()
	
	if not solid:
		return path
	
	return tube(
		flatsurface(Circle(
			(path[0], normalize(path[0]-path[1])),
			thickness/2,
			resolution=('div',6),
			)),
		path,
		)
		
		
		
# ----------------------- bearing stuff --------------------------

@cachefunc
def bearing(dint, dext=None, h=None, circulating='ball', contact='radial', sealing=False, detail=False):
	''' 
		see bearing specs at https://koyo.jtekt.co.jp/en/support/bearing-knowledge/
		
		circulating
		
			- ball
			- roller
			
		orient
		
			- straight
			- inclined
			- radial
	'''
	if isinstance(dint, str):
		dint, dext, h = bearing_spec(dint)
	else:
		if not dext:	dext = 2*dint
		if not h:		h = 0.5*dint
	
	rint = dint/2
	rext = dext/2
	c = 0.05*h
	w = 0.5*h
	e = (dext-dint)/8

	axis = Axis(O,Z)
	interior = Wire([
		vec3(rint+c, 0, w), vec3(rint, 0, w-c),
		vec3(rint,	0,	-w+c), vec3(rint+c, 0,	-w),
		vec3(rint+e, 0,	-w), vec3(rint+e, 0, -w+c),
		]) .close() .segmented() .flip()
	exterior = Wire([
		vec3(rext-e, 0,	-w+c), vec3(rext-e,	0, -w),
		vec3(rext-c, 0, -w), vec3(rext, 0, -w+c),
		vec3(rext, 0, w-c), vec3(rext-c, 0, w),
		]) .close() .segmented() .flip()
	rlt = revolution(pi, axis, web([exterior, interior]))
	indev
	
	
def bearing_spec(code):
	# iso code
	if ' ' in code:
		indev
	# simple code
	elif re.match(r'[\d\.]+x[\d\.]+x[\d\.]+', code):
		return tuple(float(d) for d in re.split('x'))
	
'''
	all existing bearing dimensions according to https://koyo.jtekt.co.jp/en/support/bearing-knowledge/6-3000.html
'''
standard_bearing_ball_straight = [
	(16, 35, 11),
	]

'''
* profilés
	+ ipn
	+ (carrés a rails)
	+ U
	+ L
* nut
	+ carrés
	+ hex
	+ auto-stopable
	+ fermés au bout
	+ support
* screw
	+ forme tete (UH, BH, VH, ...)
	+ forme empreinte (torx, hex, crux, line, ...)
* rondelle
	+ simple
	+ stobable
	+ ressort
	+ entretoise
* roulement
	+ bille, rouleau
	+ droit, oblique, radial
	+ etancheité
* coussinet
	+ droit
	+ a epaule
	+ fendu
* anneaux elastiques
	+ circlip interieur/exterieur
	+ ressort
	
* helice
	+ rotor de ventilateur ...
	
* vis/ecrou
	+ a billes
	+ a profil trapezoidal
* accouplements
	+ ressort
	+ encastrement: prisme, cannelures, clavete, meplat
* ressorts
	+ lineaire
	+ extension
	+ conique
	+ pli
	+ spiral
	+ concentrique
	+ lame
	
* tuyau
	+ embouchure
	+ droit/coude
	+ le long d'un chemin ?
	
pour tout:
	- liste des tailles standard
'''

def linrange(start, stop=None, step=None, div=0, end=True):
	''' yield successive intermediate values between start and stop 
		
		stepping:
		* if `step` is given, it will be the amount between raised value until it gets over `stop`
		* if `div` is given, it will be the number of intermediate steps between `start` and `stop` (with linear spacing)
		
		ending:
		* if `end` is True, it will stop iterate with value `stop` (or just before)
		* if `end` is False, it will stop iterating just before `stop` and never with `stop`
		
		NOTE:  
			If step is given and is not a multiple of `stop-start` then `end` has not influence
	'''
	if stop is None:	start, stop = 0, start
	if step is None:	step = (stop-start)/(div+1)
	elif step * (stop-start) < 0:	step = -step
	if not end:			stop -= step
	stop += NUMPREC
	
	t = start
	while t <= stop:
		yield t
		t += step
