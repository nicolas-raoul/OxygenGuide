#!/usr/bin/env python
## OxygenGuide - Offline travel guide
##
## Generate HTML files for articles from http://wikitravel.org
## Input: Wikicode files generated with OxygenPump
## Output: HTML for local browsing.
##
## Author: Nicolas Raoul http://nrw.free.fr
##
## TODO
## Remove directory articles beforehand
## Build page of all articles, preferably regions-structured.

# Import useful libraries.
import os
import re
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from urllib import urlencode

## Settings
# Path to the input file:
#databaseDump = '/home/nico/Downloads/enwikivoyage-20121118-pages-articles/head1000.xml'
databaseDump = '/home/nico/Downloads/enwikivoyage-20121118-pages-articles/enwikivoyage-20121118-pages-articles.xml'
outputDirectory = 'articles'
minimization = False
hashnames = True

# Create the directory where HTML files will be written.
if not os.path.isdir(outputDirectory):
    os.mkdir(outputDirectory)

def urlencode_string(target):
    return urlencode({'':target})[1:]

def traverse_redirects(target):
    # Value in the dictionary if there is one, otherwise the target itself
    return redirects.get(target, target)
    #print 'traverse_redirects ' + target
#    path = wikicodeDirectory + "/" + target + ".wikicode"
#    if not os.path.isfile(path):
#        return target
#    line = open(path).read()
#    if "#REDIRECT" in line:
#        target = line.partition('[[')[2].partition(']]')[0]
#        #print "is a redirect to " + target
#        return traverse_redirects(target)
#    else:
#        return target
#        #print "is not a redirect"

# This class represents a Wikitravel article, parses it and processes its content.
class Article(object):
    def __init__ (self, wikicode, articleName):
        self.wikicode = wikicode
        self.articleName = articleName

    # Some operating systems don't like 20000 files in the same directory, or filenames with exotic characters.
    # This method builds a file path for this article that looks like '38/16720965.html'
    # That means files will be distributed between 100 directories.
    # Even though overall collision probability is 1/500k, a future enhancement could be to check for collisions.
    def hashName(self, articleName):
        if hashnames:
            hashvalue = '%d' % abs(hash(articleName))
            directory = hashvalue[:2]
            file = hashvalue[2:]
            if not os.path.isdir('%s/%s' % (outputDirectory, directory)):
                os.mkdir('%s/%s' % (outputDirectory, directory))
            return directory + '/' + file + '.html'
        else:
            return articleName + '.html'

    # Parse the wikicode and write this article as an HTML file.
    def saveHTML(self):
        print articleName
        outputFile = open('%s/%s' % (outputDirectory,self.hashName(self.articleName)), 'w')
        outputFile.write('<html><head><title>%s</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body>' % self.articleName)
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

            # Region template (only display region wikilink).
            if re.compile('^\s*region.?name=\[\[[^\]]*\]\]\s*\|\s*$').match(line):
                line = re.compile('^\s*region.?name=\[\[').sub('', line)
                line = re.compile('\]\]\s*\|\s*$').sub('', line)
                line = '<li><a href="../%s">%s</a></li>' % (self.hashName(line), line)
            if re.compile('^\s*region.*\|\s*$').match(line):
                continue

            # Template (just print lines content).
            if re.compile('^\{\{').match(line):
                continue
            if re.compile('^\|').match(line):
                line=re.compile('^\|[^=]*=').sub('',line)
            if re.compile('^\}\}').match(line):
                continue

            # Comment (ignored)
            line = re.compile('<![^<>]*>').sub('', line)

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
                        target = split[0]
                        label = split[2]
                    # Create link only if the article exists.
                    target = target.replace(" ", "_")
                    target = urlencode_string(target)
                    #print "parsing, target:"+target
                    target = traverse_redirects(target)
#                    path = wikicodeDirectory + "/" + target + ".wikicode"
#                    
#                    if os.path.isfile(path):
                        #if "#REDIRECT" in os.path.isfile(path).read:
                        #while():
                        
                    level = '../' if hashnames else ''
                    line += '<a href="' + level + '%s">%s</a>' % (self.hashName(target), label)
#                    else:
#                        # Don't create a link, because it would be a broken link.
#                        line += '<font color="red">' + label + '</font>'

            # External links.
            # TODO

            # Listing.
            if re.compile('^<li>\s*(<|&lt;)(see|do|buy|eat|drink|sleep).*(<|&gt;)/.*').match(line):
                # Opening tag containing interesting attributes.
                line = re.compile('^<li>\s*(<|&lt;)(see|do|buy|eat|drink|sleep)[^\s]* [^\s]*="').sub('<li>',line)
                line = re.compile('" [^\s]*="[^"]').sub('. ', line)
                line = re.compile('" [^\s]*="').sub('', line)
                line = re.compile('"\s*(>|&gt;)').sub('. ', line)
                # Closing tag.
                line = re.compile('</.*>').sub('', line)
                line = re.compile('&lt;/.*&gt;').sub('', line)

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

# First pass: Build map of redirects
redirects = {}
for line in open(databaseDump):
    if line.startswith('      <text xml:space="preserve">#REDIRECT'):
        # Get the wikilink of the REDIRECT
        target = line.partition('[[')[2].partition(']]')[0].partition('#')[0]
        # Substitute underscores with spaces
        target = re.compile('_').sub(' ', target)
        #print "Redirect from " + articleName + " to " + target
        # Add to dictionary
        redirects[articleName] = target
    if line.startswith("    <title>"):
        articleName = line.partition('>')[2].partition('<')[0]

# Second pass: Generate articles
flag=0;c=0
for line in open(databaseDump):
    if line.startswith("    <title>"):
        articleName = re.compile('    <title>').sub('', line)
        articleName = re.compile('</title>.*', re.DOTALL).sub('', articleName)
    if line.startswith("  </page>"):
        flag=0
        if not "REDIRECT" in page:
            wikicode = re.compile('.*preserve">', re.DOTALL).sub('', page)
            wikicode = re.compile('      <sha1>.*', re.DOTALL).sub('', wikicode)
            article = Article(wikicode, articleName);
            article.saveHTML();
    if line.startswith("  <page>"):
        flag=1;c=c+1
        page=""
    if flag and not line.startswith("  <page>"):
        page += line
