from madcad import *
from madcad.standard import *

d = 3
show([
	screw(d,12,10, head='BH'),
	nut(d) .transform(vec3(0,0,-7)),
	washer(d) .transform(vec3(0,0,-5)),
	
	screw(5,12, head='SH') .transform(vec3(10,0,0)),
	nut(5) .transform(vec3(10,0,-5)),
	
	screw(4,12, head='VH', drive='slot') .transform(vec3(-10,0,0)),
	nut(4) .transform(vec3(-10,0,-5)),
	
	coilspring_compression(20) .transform(vec3(0,10,0)),
	coilspring_tension(20) .transform(vec3(10,10,0)),
	coilspring_torsion(5) .transform(vec3(-10,10,0)),
	
	bearing(12, circulating='roller', contact=radians(20)) .transform(vec3(0,-30,0)),
	bearing(12, circulating='roller', contact=radians(20), detail=True) .transform(vec3(0,-30,20)),
	bearing(10, circulating='roller', contact=0, detail=True) .transform(vec3(0,-30,-20)),
	bearing(12, circulating='ball') .transform(vec3(30,-30,0)),
	bearing(12, circulating='ball', detail=True) .transform(vec3(30,-30,20)),
	bearing(12, contact=radians(90)) .transform(vec3(-30,-30,0)),
	bearing(12, contact=radians(90), detail=True) .transform(vec3(-30,-30,20)),
	
	slidebearing(10, shoulder=3) .transform(vec3(0, -60, 0)),
	slidebearing(10, openning=True) .transform(vec3(-20, -60, 0)),
	])
