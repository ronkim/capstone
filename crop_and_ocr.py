from __future__ import print_function
from wand.image import Image
from wand.color import Color
from nltk import tokenize
from PIL import Image
from time import mktime
from datetime import datetime
import pytesseract
import re
import Levenshtein
import nltk.data
import sys
import time
import datetime
import os.path
import re, math
from collections import Counter

# import elementtree.ElementTree as ET
from xml.etree import ElementTree as ET

WORD = re.compile(r'\w+')

def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)


xmlfilename = "cropped_dialogue_regions.xml"
croppedimagefilename = "temp.gif"

tree = ET.parse(xmlfilename)
doc = tree.getroot()
thingy = doc.find('STRIP')

f1 = open("log1.txt","a")
f1.truncate()

with open(xmlfilename, 'rt') as f:
    tree = ET.parse(f)


# print (tree)

for node in tree.iter("STRIP"):
	strip_attrib = str(node.attrib)
	imagefilename = strip_attrib[14:29]
	strip_date = strip_attrib[14:24]
	strip_date_format = time.strptime(strip_date, "%Y-%m-%d")
	dt = time.mktime(strip_date_format)
	dt = datetime.datetime.fromtimestamp(dt)
	date_minus_one = dt - datetime.timedelta(days=1)
	# newdate = time.mktime(date_minus_one)
	next_date = str(date_minus_one).split()
	next_strip_date = str(next_date[0])

	print ('The image file to load is:',imagefilename)
	print ('The strip date is is:',strip_date)
	print ('The next strip date is is:',next_strip_date)
	if (os.path.isfile(imagefilename)):
		im = Image.open(imagefilename) #Can be many different formats.
		print('\n==============================================\n')
		print("The file ", imagefilename, " has been opened.")
		text_in_panel = []
		rgb_im = im.convert('RGB')

		for child in node:
			print(child.tag)
			cropcoords = [];
			for subchild in child:
				# print('coord:',subchild.text)
				cropcoords.append(subchild.text)
			print (int(float(cropcoords[0])),int(float(cropcoords[1])),int(float(cropcoords[2])),int(float(cropcoords[3])))
			leftcoord  = int(float(cropcoords[0]))
			uppercoord = int(float(cropcoords[1]))
			rightcoord = int(float(cropcoords[2])) + int(float(cropcoords[0]))
			lowercoord = int(float(cropcoords[3])) + int(float(cropcoords[1]))

			croppedimage = im.crop((leftcoord,uppercoord,rightcoord,lowercoord))
			print("SAVING IMAGE")
			try:
				croppedimage.save(croppedimagefilename)
				# f.write(strip_date + 'a.gif\n')
			except SystemError:
				print('!!!Could not save ', croppedimagefilename)
				msg = '!!!Could not save', croppedimagefilename+'\n'
				# f1.write(msg)

			if (os.path.isfile(croppedimagefilename)):
				img = Image.open(croppedimagefilename)
				img.load()
				img.split()
				dialog = pytesseract.image_to_string(img)
				new_dialog = dialog.replace('\n', ' ').replace('\r', '')
				#print new_dialog.capitalize()
				ocrd_string = new_dialog.capitalize()
				print('OCR text from ', croppedimagefilename, 'is ',ocrd_string)
				ocrd_sentences = tokenize.sent_tokenize(ocrd_string.decode('utf-8'))
				for sentence in ocrd_sentences:
					print(sentence)

				transcripts = open('dilbertstripsall_formatted_transcript.txt')
				found_strip = False
				gt_sentence_array = []
				gt_sentences = []
				for line in transcripts:
					line = line.rstrip()
					if strip_date in line:
						print('Found Date:', line)
						found_strip = True
					if next_strip_date in line:
						print('End of text for strip of interest')
						found_strip = False
						break
					if (found_strip):
						found_star_or_brackets = re.search('[\>+\<+\*]',line)
						if (found_star_or_brackets):
				# print('+++++++++++++++++++++++++++Found line with star')
							dummy = True
						else:
							gt_sentences = tokenize.sent_tokenize(line)
							for gt_sentence in gt_sentences:
								gt_sentence_array.append(gt_sentence.encode('utf-8'))
				# Print out each sentence of text on separate line
				# for index, s in enumerate(gt_sentence_array):
				# 	print('Sentence[index]:' ,s,':',index)


				temp_panel_text = gt_sentence_array

				new_distance = 10000
				found_strip = False
				saved_line = ''

				for gt_sentence in gt_sentence_array:
					for ocrd_sentence in ocrd_sentences:
				# print(' ')
						print('******** GT Sentence:',gt_sentence)
						words = gt_sentence.split()
						num_words = len(words)
						print('******** OCR Sentence', ocrd_sentence)
						distance = Levenshtein.distance(str(ocrd_sentence.encode('utf-8')),str(gt_sentence.encode('utf-8')))
						print('******** Levenshtein distance:',distance)
						vector1 = text_to_vector(ocrd_sentence)
						vector2 = text_to_vector(gt_sentence)
						cosine = get_cosine(vector1, vector2)
						print ('Cosine:', cosine)
						# print ('Cosine:', cosine)
						# if (distance < new_distance) and (num_words > 2):
						# 	saved_line = gt_sentence
						# 	new_distance = distance
						if ((cosine > 0.6) or ((distance < 10) and (cosine >0.3))):
							saved_line = gt_sentence
							print('CONFIDENT MATCH:')
							print('******** GT Sentence:',gt_sentence)
							print('******** OCR Sentence', ocrd_sentence)
							print('******** Levenshtein distance:',distance)
							print ('Cosine:', cosine)
							text_in_panel.append(saved_line)
						else:
							ocrd_words = ocrd_sentence.split()
							# for word in ocrd_words:
							# 	print("the word is ",word)
							found_star_or_brackets = False

						# print ('Matching line for ', imagefilename, ' is ', saved_line, '(distance: ', new_distance)
				print("-----------------------------------------------------------------------\n")
	ftrans = open("panel_transcripts3.txt","a")
	try:
		ftrans.truncate()
		print('Panel in ',imagefilename,'contains:')
		string_to_write = imagefilename + '\n'
		ftrans.write(string_to_write)
		for sentence in text_in_panel:
			string_to_write = sentence + '\n'
			print (sentence)
			ftrans.write(string_to_write)
		string_to_write = '************\n'
		ftrans.write(string_to_write)
		print('=====================================================================================')
	finally:
		ftrans.close()
				


			# print('SUBCHILD:',subchild.text)
    # print ("NODE TAG:",node.tag)
    # print ("NODE TEXT:",node.text)
    # print ("NODE ATTRIB:",node.attrib)

now = datetime.datetime.now()