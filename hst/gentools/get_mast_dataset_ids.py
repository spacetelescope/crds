#! /usr/bin/env pysh
#-*-python-*-

"""This is a script to reduce the output of testall.err into a list
of datasets important enough to download.
"""
from crds.pysh import *

#wfc3 biasfile mismatched: w1k1448ri_bia.fits w1k1448si_bia.fits 75 IBLK05MNQ
# Mismatch Set: 11 wfc3 biasfile t6i1733ei_bia.fits v5j1716fi_bia.fits IBWH080K0 IBWH09040 IBWH09080 IBWH090C0 IBWH090G0 IBWH090K0 IBWH10040 IBWH10080 IBWH100C0 IBWH100G0 IBWH100K0

class Mismatched(object):
	def __init__(self, **keys):
		for key in keys:
			self.__dict__[key] = keys[key]

def get_mismatched(line):
	words = line.strip().split()
	return Mismatched(
		count = int(words[2]),
		instrument = words[3],
		filekind = words[4],
		old_file = words[5],
		new_file = words[6],		
		datasets = words[7:])
	
def get_mismatched_objects(filename="testall.err"):
	objects = []
	for line in lines("grep 'Mismatch Set:' ${filename}"):
		objects.append(get_mismatched(line))
	return objects

def main(filename, important):	
	for mismatched in get_mismatched_objects(filename):
		if mismatched.count > important:
			print mismatched.datasets[0]

if __name__ == "__main__":
	usage("<source_file> <test_count_importance_threshhold>", 2, 2);
	main(sys.argv[1], int(sys.argv[2]))
