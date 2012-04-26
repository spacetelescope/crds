#! /usr/bin/env pysh
#-*-python-*-

"""This is a script to reduce the output of testall.err into a list
of datasets important enough to download.
"""
from crds.pysh import *

#wfc3 biasfile mismatched: w1k1448ri_bia.fits w1k1448si_bia.fits 75 IBLK05MNQ
class Mismatched(object):
	def __init__(self, **keys):
		for key in keys:
			self.__dict__[key] = keys[key]

def get_mismatched(line):
	words = line.strip().split()
	return Mismatched(
		instrument = words[0],
		filekind = words[1],
		old_file = words[3],
		new_file = words[4],
		count = int(words[5]),
		datasets = words[6:])
	
def get_mismatched_objects(filename="testall.err"):
	objects = []
	for line in lines("grep mismatched ${filename}"):
		objects.append(get_mismatched(line))
	return objects

def main(important):	
	for mismatched in get_mismatched_objects():
		if mismatched.count > important:
			print mismatched.datasets[0]

if __name__ == "__main__":
	usage("<test_count_importance_threshhold>", 1, 1);
	main(int(sys.argv[1]))
