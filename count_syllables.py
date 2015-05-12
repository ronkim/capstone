# Portions of this code based on cmudict.py by Allison Parrish
import curses
from curses.ascii import isdigit
import nltk
from nltk.corpus import cmudict
import re
import string
import time
import datetime
import random
 
d = cmudict.dict() 

def parse_cmu(cmufh):
	"""Parses an incoming file handle as a CMU pronouncing dictionary file.
		Returns a list of 2-tuples pairing a word with its phones (as a string)"""
	pronunciations = list()
	for line in cmufh:
		line = line.strip()
		if line.startswith(';'): continue
		word, phones = line.split("  ")
		word = re.sub(r'\(\d\)$', '', word.lower())
		phones_list = phones.split(" ")
		pronunciations.append((word.lower(), phones))
	return pronunciations 

pronunciations = parse_cmu(open('cmudict-0.7b'))

def syllable_count(phones):
	return sum([phones.count(i) for i in '012'])

def phones_for_word(find):
	"""Searches a list of 2-tuples (as returned from parse_cmu) for the given
		word. Returns a list of phone strings that correspond to that word."""
	matches = list()
	for word, phones in pronunciations:
		if word == find:
			matches.append(phones)
	return matches

def approx_nsyl(word):
	digraphs = ["ai", "au", "ay", "ea", "ee", "ei", "ey", "oa", "oe", "oi", "oo", "ou", "oy", "ua", "ue", "ui"]
	# Ambiguous, currently split: ie, io
	# Ambiguous, currently kept together: ui
	digraphs = set(digraphs)
	count = 0
	array = re.split("[^aeiouy]+", word.lower())
	for i, v in enumerate(array):
		if len(v) > 1 and v not in digraphs:
			count += 1
		if v == '':
			del array[i]
			count += len(array)
		if re.search("(?&lang;=\w)(ion|ious|(?&lang;!t)ed|es|[^lr]e)(?![a-z']+)", word.lower()):
			count -= 1
		if re.search("'ve|n't", word.lower()):
			count += 1
	return count

def nsyl(word):
    # return max([len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]])
	lowercase = word.lower()
	if lowercase not in d:
		# approx_nsyl(word)
		print(lowercase, 'is not in the dictionary')
		return 0
 	else:
 		# return max([len([y for y in x if isdigit(y[-1])]) for x in d[lowercase]])
 		return min([len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]] )

panel_boundary = '************'

if __name__ == '__main__':
	import sys
	rhyming_panels_found= False

	transcripts = open('master_panel_transcripts.txt')
	
	for line in transcripts:
		panel_text = list()
		found_date = False
		line = line.rstrip()
		# print(line)
		found_stars = re.search('\*+',line)
		# found_date = re.findall('[\d+\-\d+\-\d+\.gif]',line)
		found_date = re.search(r'(\d+(?:-\d+)+\w\.gif)',line)
		if (found_date):
			date_looking_at = found_date.group(1)
		if (date_looking_at in line):
			print(line)
			date_of_strip = line
			cumulative_syllables = 0
			continue
		elif ((date_looking_at not in line) and (panel_boundary not in line)):
			panel_text.append(line)
			sentence  = line
			sentence = sentence.rstrip('?:!.,;')
			sentence = "".join(c for c in sentence if c not in ('!','.',':','"',',',';'))
			# print("The new sentence is", sentence)
			strip_line = sentence
			for word in sentence.split():
				matches = [x for x in pronunciations if x[0] == word.lower()]
				num_matches = len(matches)
				# print('The number of matches for ',word,' is',num_matches)
				if (num_matches > 0):
					for i in matches:
						# print("One pronunciation is", i)
						phones = phones_for_word(word.lower())
						syllables = syllable_count(phones[0])
				else:
					syllables = 0
				cumulative_syllables += syllables	
		elif (panel_boundary in line):
			continue
		else:
			continue

		if ((found_date) and (panel_boundary not in line)):
			
			date_line = False
			panel_boundary_line = False
			
		print("The total number of syllables for this line is",cumulative_syllables)
		if ((cumulative_syllables == 5) or (cumulative_syllables == 7)):
			print("The strip date is", date_of_strip)
			print("The strip line is", strip_line)
			print("The total number of syllables is",cumulative_syllables)