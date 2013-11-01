#!/usr/bin/env python
# coding=utf-8
#
## OxygenGuide - Offline travel guide
## http://code.google.com/p/oxygenguide
##
## Generate HTML files for articles from http://en.wikivoyage.org
## Input: Wikivoyage dump from http://dumps.wikimedia.org/enwikivoyage/
## Output: HTML for local browsing.
##
## Author: Nicolas Raoul http://nrw.free.fr

# Import useful libraries.
import os
import re
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from urllib import urlencode

## Settings
# Path to the input file:
databaseDump = sys.argv[1] #'enwikivoyage-20130101-pages-articles.xml'
print 'Using data from ' + databaseDump
outputDirectory = 'articles'
minimization = True

def urlencode_string(target):
    return urlencode({'':target})[1:]

re_redirect = re.compile('#REDIRECT', re.I) # Regular expression to detect REDIRECT
def is_redirect(wikicode):
    #print wikicode
    #print bool(re_redirect.match(wikicode))
    return re_redirect.match(wikicode)

# Some operating systems don't like 20000 files in the same directory, or filenames with exotic characters.
# This method builds a file path for this article that looks like '38/16720965.html'
# That means files will be distributed between 100 directories.
# Even though overall collision probability is 1/500k, a future enhancement could be to check for collisions.
def hashName(articleName):
    hashvalue = '%d' % abs(hash(articleName))
    directory = hashvalue[:2]
    file = hashvalue[2:]
    if not os.path.isdir('%s/%s' % (outputDirectory, directory)):
        os.mkdir('%s/%s' % (outputDirectory, directory))
    return directory + '/' + file + '.html'

# This class represents a Wikitravel article, parses it and processes its content.
class Article(object):
    def __init__ (self, wikicode, articleName):
        self.wikicode = wikicode
        self.articleName = articleName

    # Parse the wikicode and write this article as an HTML file.
    def saveHTML(self):
        print articleName
        outputFile = open('%s/%s' % (outputDirectory,hashName(self.articleName)), 'w')
        outputFile.write('<html><head><title>%s</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body>' % self.articleName)

        # Breadcrumb
        cursor = articleName
        breadcrumb = []
        while(cursor in isPartOfs):
            isPartOf = isPartOfs[cursor]
            breadcrumb.append(isPartOf)
            if len(breadcrumb) > 100:
                print "IsPartOf circular reference detected: " + '←'.join(breadcrumb)
                break
            cursor = isPartOf
        if len(breadcrumb) > 0:
            outputFile.write('<p><i>')
            buffer = ""
            for cursor in breadcrumb:
                buffer = ' → <a href="../' + hashName(cursor) + '"> ' + cursor + '</a>' + buffer
            outputFile.write(buffer)
            outputFile.write('</i></p>')

        lastLineWasBlank = True
        restOfWikicode = self.wikicode
        while 1:
            # Read one line from the article.
            if len(restOfWikicode)==0: break
            split = restOfWikicode.partition('\n')
            line = split[0]
            restOfWikicode = split[2]

            # Image and interwiki links (ignored).
            if re.compile('^\[\[[^\]]*:').match(line):
                continue

            # Region template (only display region wikilink and description).
            if re.compile('^\s*region[0-9]*color.*\|\s*$').match(line): #Ignore region color
                continue
            if re.compile('^\s*region[0-9]*items.*\|\s*$').match(line): #Ignore region items
                continue
            if re.compile('^\s*region[0-9]*name=\[\[[^\]]*\]\]\s*\|\s*$').match(line): # Leave only the wikilink, which will be processed afterwards.
                line = re.compile('^\s*region[0-9]*name=').sub('', line)
                line = re.compile('\s*\|\s*$').sub('', line)
            if re.compile('^\s*region[0-9]*description.*\|\s*$').match(line): # Leave only description.
                line = re.compile('^\s*region[0-9]*description=').sub(' ', line)
                line = re.compile(' \|').sub('', line)

            # Template (just print lines content).
            if re.compile('^\{\{').match(line):
                continue
            if re.compile('^\|').match(line):
                line=re.compile('^\|[^=]*=').sub('',line)
            if re.compile('^\}\}').match(line):
                continue

            # Comment (ignored)
            line = re.compile('<![^<>]*>').sub('', line) # does not seem to work
            if re.compile('^<!--').match(line): # does not seem to work
                continue

            # Blank line.
            if re.compile('^\s*$').match(line):
               if lastLineWasBlank:
                   continue
               else:
                   line = '<p>'
                   lastLineWasBlank = True
            else:
               lastLineWasBlank = False

            # Header.
            if re.compile('^\s*=====.*=====\s*$').match(line):
                line=re.compile('^(\s*=====\s*)').sub('<h5>',line)
                line=re.compile('(\s*=====\s*)$').sub('</h5>',line)
            if re.compile('^\s*====.*====\s*$').match(line):
                line=re.compile('^(\s*====\s*)').sub('<h4>',line)
                line=re.compile('(\s*====\s*)$').sub('</h4>',line)
            if re.compile('^\s*===.*===\s*$').match(line):
                line=re.compile('^(\s*===\s*)').sub('<h3>',line)
                line=re.compile('(\s*===\s*)$').sub('</h3>',line)
            if re.compile('^\s*==.*==\s*$').match(line):
                line=re.compile('^(\s*==\s*)').sub('<h2>',line)
                line=re.compile('(\s*==\s*)$').sub('</h2>',line)

            # List item.
            if re.compile('^\*').match(line):
                line = re.compile('^(\*)').sub('<li>',line)
                line = line+'</li>'

            # Wikilinks.
            if re.compile('.*\]\].*').match(line):
                # Contains at least one wikilink. Let's split the line and process one wikilink at a time.
                restOfLine = line
                line = ""
                while 1:
                    # Split one portion from the line.
                    if len(restOfLine)==0: break
                    split = restOfLine.partition(']]')
                    portion = split[0]
                    restOfLine = split[2]
                    # Process this portion
                    #print "parsing, portion:"+portion
                    split = portion.partition('[[')
                    text = split[0]
                    wikilink = split[2]
                    line = line+text
                    # Parse the inside of the wikilink
                    target = wikilink
                    label = wikilink
                    if '|' in wikilink:
                        split = wikilink.partition("|")
                        target = split[0].strip()
                        label = split[2].strip()
                    # Create link only if the article exists.
                    target = redirects.get(target, target) # Redirected target, or if inexistent the target itself
                    
                    if label: # Ignore if label is empty
                        if target in articleNames:
                            line += '<a href="../' + hashName(target) + '">' + label + '</a>'
                        else:
                            # Don't create a link, because it would be a broken link.
                            line += '<font color="red">' + label + '</font>'

            # External links.
            # TODO
            if re.compile('.*\].*').match(line):
                # Contains at least one wikilink. Let's split the line and process one wikilink at a time.
                restOfLine = line
                line = ""
                while 1:
                    # Split one portion from the line.
                    if len(restOfLine)==0: break
                    split = restOfLine.partition(']')
                    portion = split[0]
                    restOfLine = split[2]
                    # Process this portion
                    split = portion.partition('[')
                    text = split[0]
                    extlink = split[2]
                    line = line+text
                    # Parse the inside of the wikilink
                    target = extlink
                    label = ""
                    if " " in extlink:
                        split = extlink.partition(" ")
                        target = split[0].strip()
                        label = split[2].strip()
                    if extlink:
                        line += '<a href="' + target + '">[' + label + '↗]</a>'

            # Old-style listing.
            if re.compile('^<li>\s*(<|&lt;)(see|do|buy|eat|drink|sleep).*(<|&gt;)/.*').match(line):
                # Opening tag containing interesting attributes.
                line = re.compile('^<li>\s*(<|&lt;)(see|do|buy|eat|drink|sleep)[^\s]* [^\s]*="').sub('<li>',line)
                line = re.compile('" [^\s]*="[^"]').sub('. ', line)
                line = re.compile('" [^\s]*="').sub('', line)
                line = re.compile('"\s*(>|&gt;)').sub('. ', line)
                # Closing tag.
                line = re.compile('</.*>').sub('', line)
                line = re.compile('&lt;/.*&gt;').sub('', line)

            # New-style listing.
            # Coordinates
            if re.compile('.*lat=[-0-9][^ ]* \\| long=[-0-9].*').match(line):
                coords = re.search('.*lat=([^ ]*) \\| long=([^ ]*).*', line, re.I | re.U)
                lat = coords.group(1)
                lon = coords.group(2)
                line = line + ' <a href="geo:' + lat + ',' + lon + '">(map)</a>'
            # TODO: Rest of new listing. Difficult because multi-line

            # Bold: remove.
            line=re.compile("'''").sub("", line)

            # Italic: remove.
            line=re.compile("''").sub("", line)

            if minimization:
                line = re.compile('\s+').sub(' ', line)
            outputFile.write(line)
            if not minimization:
                outputFile.write('\n')
        outputFile.write('</body></html>')
# End of Article class

# Main
print "### Generate index"
articles = ["Africa", "Antarctica", "Asia", "South Asia", "Southeast Asia", "Caribbean", "Central America", "Europe", "Middle East", "North America", "South America", "Other destinations", "Travel topics"]
index = open("index.html", "w")
index.write("<html> <head><title>OxygenGuide</title></head> <body> <ul>")
for article in articles:
    index.write('<li><a href="articles/')
    index.write(hashName(article))
    index.write('">')
    index.write(article)
    index.write('</a></li>')
index.write('</ul>')
index.write('<p>This content is based on work by all volunteers of <a href="http://wikivoyage.org">Wikivoyage</a> and <a href="http://wikitravel.org">Wikitravel</a>.')
index.write('Text is available under <a href="http://creativecommons.org/licenses/by-sa/1.0/">Creative Commons Attribution-ShareAlike 1.0</a>.')
index.write('Comments welcome on <a href="https://en.wikivoyage.org/w/index.php?title=User_talk:Nicolas1981&action=edit&section=new">my user page</a>.</p>')
index.write('</body> </html>')

# Create the directory where HTML files will be written.
if not os.path.isdir(outputDirectory):
    os.mkdir(outputDirectory)

print "### Build list of articles and map of redirects"
redirects = {}
articleNames = []
isPartOfs = {}
redirect = 0
isPartOf = 0
for line in open(databaseDump):
    if line.startswith("    <title>"):
        articleName = line.partition('>')[2].partition('<')[0]
    if line.startswith("    <redirect"):
        redirect = 1
        target = line.partition('"')[2].partition('"')[0].partition('#')[0]
    if line.startswith("{{IsPartOf|") or line.startswith("{{isPartOf|"):
        isPartOf = line[11:].partition('}')[0]
        isPartOf = isPartOf.replace("_", " ")
    if line.startswith("{{IsIn|") or line.startswith("{{isIn|"):
        isPartOf = line[7:].partition('}')[0]
        isPartOf = isPartOf.replace("_", " ")
    if line.startswith("  </page>"):
        if(redirect):
            #print "New redirect: " + articleName + " to " + target
            redirects[articleName] = target
        else:
            #print "New article: " + articleName
            articleNames.append(articleName)
        if(isPartOf != 0):
            isPartOfs[articleName] = isPartOf
        redirect = 0
        isPartOf = 0

print str(len(redirects)) + " redirects"
print str(len(articleNames)) + " articles"
print str(len(isPartOfs)) + " articles with breadcrumb"

#    if is_redirect_line(line):
#        # Get the wikilink of the REDIRECT
#        target = line.partition('[[')[2].partition(']]')[0].partition('#')[0]
#        # Substitute underscores with spaces
#        target = re.compile('_').sub(' ', target)
#        #print "Redirect from " + articleName + " to " + target
#        # Add to dictionary
#        redirects[articleName] = target
#    else:
#        articleNames.append(articleName)
#    if line.startswith("    <title>"):
#        articleName = line.partition('>')[2].partition('<')[0]

print "### Check for double-redirects"
for (name,target) in redirects.items():
    if target in redirects:
        print "Double redirect detected, please fix: " + name + " > " + target + " > " + redirects[target]

print "### Generate articles"
flag=0;skip=0
for line in open(databaseDump):
    if line.startswith("    <title>"):
        if "/Gpx" in line or ":" in line: # Skip GPS traces and articles such as Template: Title: Wikivoyage:
            skip=1
        else:
            articleName = re.compile('    <title>').sub('', line)
            articleName = re.compile('</title>.*', re.DOTALL).sub('', articleName)
    if line.startswith("  </page>"):
        flag=0
        if skip:
            skip=0
        else:
            wikicode = re.compile('.*preserve">', re.DOTALL).sub('', page)
            if not is_redirect(wikicode):
                wikicode = re.compile('      <sha1>.*', re.DOTALL).sub('', wikicode)
                article = Article(wikicode, articleName);
                article.saveHTML();
    if line.startswith("  <page>"):
        flag=1
        page=""
    if flag and not line.startswith("  <page>"):
        page += line

