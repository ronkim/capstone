# Portions of code to detect rhyming from cmudict.py credited to Allison Parrish
# 
import random
import string
from cherrypy.lib import file_generator
import StringIO
import cherrypy
import re
import string
import time
import datetime
import random


# array of panels to create haikus
# panels generated from find_count_syllables.py
five_syllable_panels = ['2015-02-11b.gif','2014-11-12b.gif','2014-08-07c.gif','2014-03-05c.gif','2014-01-18a.gif','2013-12-04a.gif','2013-11-11b.gif','2013-10-26b.gif','2013-07-11b.gif','2013-05-16c.gif','2013-05-13b.gif','2013-04-09b.gif','2012-12-15c.gif']
seven_syllable_panels = ['2015-01-26a.gif','2015-01-17b.gif','2015-01-16c.gif','2014-11-17a.gif','2014-09-17b.gif','2014-02-12a.gif','2014-02-05c.gif','2013-12-04c.gif','2013-10-21b.gif','2013-06-17c.gif','2013-06-10c.gif','2013-04-27c.gif','2013-04-11b.gif','2013-03-01b.gif','2013-02-14a.gif','2013-02-12b.gif','2013-01-11c.gif']

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

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

def rhyming_part(phones):
  """Returns the "rhyming part" of a string with phones. "Rhyming part" here
    means everything from the vowel in the stressed syllable nearest the end
    of the word up to the end of the word."""
  idx = 0
  phones_list = phones.split()
  for i in reversed(range(0, len(phones_list))):
    if phones_list[i][-1] in ('1', '2'):
      idx = i
      break
  return ' '.join(phones_list[idx:])

def search(pattern):
  """Searches a list of 2-tuples (as returned from parse_cmu) for
    pronunciations matching a given regular expression. (Word boundary anchors
    are automatically added before and after the pattern.) Returns a list of
    matching words."""
  matches = list()
  for word, phones in pronunciations:
    if re.search(r"\b" + pattern + r"\b", phones):
      matches.append(word)
  return matches

def rhymes(word):
  """Searches a list of 2-tuples (as returned from parse_cmu) for words that
    rhyme with the given word. Returns a list of such words."""
  all_rhymes = list()
  all_phones = phones_for_word(word)
  for phones_str in all_phones:
    part = rhyming_part(phones_str)
    rhymes = search(part + "$")
    all_rhymes.extend(rhymes)
  return [r for r in all_rhymes if r != word]


cherrypy.config.update({'server.socket_port': 3030,})

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
      logo_file = "images/dilbert_logo.jpg"
      logo2_file = "images/mashup.png"
      return """ <html>
          <head></head>
          <body>
          <DIV ALIGN=CENTER>
            <img src ="{0}" width="276" height="188">
            <br>
            <img src ="{1}">
            <form method="get" action="generate">
              <!--<input type="text" value="" name="length" />-->
              <button type="submit" style="font-family: sans-serif; font-size: 18px;">Generate Rhyming Mashup!</button>
            </form>
            <form method="get" action="haiku">
              <!--<input type="text" value="" name="length" />-->
              <button type="submit" style="font-family: sans-serif; font-size: 18px;">Generate Haiku Mashup!</button>
            </form>
          </DIV>
          </body>
        </html>""".format(logo_file,logo2_file)

    @cherrypy.expose
    def generate(self, length=8):
      import sys
      panel_boundary = '************'
      rhyming_panels_found= False
      logo_file = "images/dilbert_logo.jpg"
      logo2_file = "images/mashup.png"
      seed_panel = ""
      while(rhyming_panels_found==False):

        i = random.randint(61, 9600)
        suffix = random.randint(1,3)
        rhymes_list = list()
        rhyming_panels = list()

        if (suffix == 1):
          strip_letter = 'a'
        elif (suffix == 2):
          strip_letter = 'b'
        elif (suffix == 3):
          strip_letter = 'c'
        else:
          strip_letter = 'a'

        print(i)
        # for line in sys.stdin:
        now = datetime.datetime.now()

        datetime_to_read = now - datetime.timedelta(days=i)
        # print(datetime_to_read)
        #Split up the date/time components
        date = str(datetime_to_read).split()

        date_minus_one = datetime_to_read - datetime.timedelta(days=1)
        next_date = str(date_minus_one).split()

        # Just get the YYYY-MM-DD
        # print (date[0])
        strip_date = str(date[0]) + strip_letter
        print('The date is',strip_date)

        transcripts = open('master_panel_transcripts.txt')
        panel_text = list()
        found_date = False
        print("looking for ",strip_date)
        for line in transcripts:
          line = line.rstrip()
          # print(line)
          found_stars = re.search('\*+',line)
          # found_date = re.findall('[\d+\-\d+\-\d+\.gif]',line)
          # if (found_date):
          if strip_date in line:
            print('Found date: ',line)
            found_date = True
            seed_panel = line
          if (found_date):
            panel_text.append(line)
          if (found_date) and (panel_boundary in line):
            # print(line)
            break
        if (found_date):
          del panel_text[-1]
          words = panel_text[-1].split()
          word_to_rhyme = words[-1].rstrip('?:!.,;')
          print('The word to rhyme is',word_to_rhyme)
          rhymes_list = rhymes(word_to_rhyme)
          for rhyme in rhymes_list:
            print rhyme
        
        transcripts = open('master_panel_transcripts.txt')
        rhyming_panels = list()
        for line in transcripts:
          found_date = False
          found_stars = False
          found_date = re.search(r'(\d+(?:-\d+)+\w\.gif)',line)

          found_stars = re.search('\*+',line)
          if (found_date):
            panel_lines = list()
            # print ("Comic date is",found_date.group(1))
            saved_panel_date = found_date.group(1)
          else:
            panel_lines.append(line)
            panel_words = panel_lines[-1].split()
            if (panel_boundary in line):
              asterisk_line = True
            else:
              word_to_match = panel_words[-1].rstrip('?:!.,;')
              # print('The word to match is',word_to_match)
            matching = [s for s in panel_lines if panel_boundary in s]
            if (matching):
              for rhyme in rhymes_list:
                # print('Comparing ',rhyme,'with ',word_to_match.lower())
                if rhyme == word_to_match.lower():
                  print ('***************************************************************************')
                  print ('Found a match between', rhyme, 'and ', word_to_match, 'in comic panel', saved_panel_date)
                  rhyming_panels.append(saved_panel_date)
                  rhymes_list.remove(rhyme)

        for panel in rhyming_panels:
          print('Rhyming panels include:', panel)
          rhyming_panels_found = True
        if len(rhyming_panels) == 0:
          print('No rhyming panels found')

          # result = remove_duplicates(values)
        result = f7(rhyming_panels)
        rhyming_panels = result

        for panel in rhyming_panels:
          print('Updated rhyming panels include:', panel)
      panel_zero ="images/1x1.png"
      panel_one = "images/1x1.png"
      panel_two = "images/1x1.png"
      panel_three = "images/1x1.png"
      panel_four = "images/1x1.png"
      panel_five = "images/1x1.png"
      panel_six = "images/1x1.png"
      panel_seven = "images/1x1.png"
      panel_eight = "images/1x1.png"
      dimension11 = """ width="1" height="1" """
      dimension12 = """ width="1" height="1" """
      dimension13 = """ width="1" height="1" """
      dimension14 = """ width="1" height="1" """
      dimension15 = """ width="1" height="1" """
      dimension16 = """ width="1" height="1" """
      dimension17 = """ width="1" height="1" """
      dimension18 = """ width="1" height="1" """


      if 0 < len(rhyming_panels):
      	panel_zero = "images/" + seed_panel
        dimension11 = """ width="288" height="279" """
        print(panel_zero)

      if 1 <= len(rhyming_panels):
        panel_one = "images/" + rhyming_panels[0]
        dimension12 = """ width="288" height="279" """
        print(panel_one)

      if 2 <= len(rhyming_panels):
        panel_two = "images/" + rhyming_panels[1]
        dimension13 = """ width="288" height="279" """
        print(panel_two)

      if 3 <= len(rhyming_panels):
        panel_three = "images/" + rhyming_panels[2]
        dimension14 = """ width="288" height="279" """
        print(panel_three)

      if 4 <= len(rhyming_panels):
        panel_four = "images/" + rhyming_panels[3]
        dimension15 = """ width="288" height="279" """
        print(panel_four)

      if 5 <= len(rhyming_panels):
        panel_five = "images/"  + rhyming_panels[4]
        dimension16 = """ width="288" height="279" """
        print(panel_five)

      if 6 <= len(rhyming_panels):
        panel_six = "images/"  + rhyming_panels[5]
        dimension17 = """ width="288" height="279" """
        print(panel_six)

      if 7 <= len(rhyming_panels):
        panel_seven = "images/"  + rhyming_panels[6]
        dimension18 = """ width="288" height="279" """
        print(panel_seven)

        # return ''.join(random.sample(string.hexdigits, int(length)))
      # panel_one = "images/1989-04-24a.gif"
      # panel_two = "images/1989-04-24b.gif"
      # panel_three = "images/1989-04-24a.gif"
      # panel_one = "images/2013-09-05c.gif"
      # panel_two = "images/2012-11-23a.gif"
      # panel_three = "images/2008-01-12b.gif"
      # panel_four = "images/2002-06-10a.gif"
      # panel_five = "images/2000-08-30a.gif"
      # panel_six = "images/1992-03-14c.gif"
      return """ <html>
          <head>
          <title>Dilbert Mashup</title>
          </head>
          <html>
          <body>
          <DIV ALIGN=CENTER>
          <img src="{8}" width="276" height="188">
          <br>
          <img src="{9}">
          <br>
          </DIV>
          <DIV ALIGN=CENTER>
          <img src="{0}" "{10}">
          <img src="{1}" "{11}">
          <img src="{2}" "{12}">
          <img src="{3}" "{13}">
          <img src="{4}" "{14}">
          <img src="{5}" "{15}">
          <img src="{6}" "{16}">
          <img src="{7}" "{17}">
          <br>
          <FORM METHOD="LINK" ACTION="http://localhost:3030/?">
          <INPUT style="font-family: sans-serif; font-size: 18px;" TYPE="submit" VALUE="GO HOME">
          </FORM>
          </DIV>
          </body>
          </html>""".format(panel_zero,panel_one,panel_two,panel_three,panel_four,panel_five,panel_six,panel_seven,logo_file,logo2_file,dimension11,dimension12,dimension13,dimension14,dimension15,dimension16,dimension17,dimension18)
    
    @cherrypy.expose
    def haiku(self, length=8):
      import sys    
      logo_file = "images/dilbert_logo.jpg"
      logo2_file = "images/mashup.png"
      five_syllable_panel_count = len(five_syllable_panels) - 1
      seven_syllable_panel_count = len(seven_syllable_panels) - 1
      haiku_panel_one_index = random.randint(0, five_syllable_panel_count)
      haiku_panel_two_index = random.randint(0, seven_syllable_panel_count)
      haiku_panel_three_index = random.randint(0, five_syllable_panel_count)

      haiku_panel_one = "images/" + five_syllable_panels[haiku_panel_one_index]
      haiku_panel_two = "images/" + seven_syllable_panels[haiku_panel_two_index]
      haiku_panel_three = "images/" + five_syllable_panels[haiku_panel_three_index]

      return """ <html>
          <head>
          <title>Dilbert Mashup</title>
          </head>
          <html>
          <body>
          <DIV ALIGN=CENTER>
          <img src="{0}" width="276" height="188">
          <br>
          <img src="{1}">
          <br>
          </DIV>
          <DIV ALIGN=CENTER>
          <img src="{2}" width="288" height="279">
          <img src="{3}" width="288" height="279">
          <img src="{4}" width="288" height="279">
          <br>
          <FORM METHOD="LINK" ACTION="http://localhost:3030/?">
          <INPUT style="font-family: sans-serif; font-size: 18px;" TYPE="submit" VALUE="GO HOME">
          </FORM>
          </DIV>
          </body>
          </html>""".format(logo_file,logo2_file,haiku_panel_one,haiku_panel_two,haiku_panel_three)


if __name__ == '__main__':
    # cherrypy.quickstart(StringGenerator())
  conf = {'/images': {'tools.staticdir.on': True,
        'tools.staticdir.dir': '/Volumes/Mac HDD/IACD/test/images'}}
  print conf
  cherrypy.quickstart(StringGenerator(),'/',config=conf)
