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

## Settings
# Path to the input file:
##wikicodeFilePath = 'unittests.xml'
#wikicodeFilePath='articles.xml'
wikicodeDirectory = '../oxygenpump/wikicode'
outputDirectory = 'articles'
minimization = False
hashnames = False

# List of articles names. Useful to prevent red links.
articlesNames = []

# Create the directory where HTML files will be written.
if not os.path.isdir(outputDirectory):
    os.mkdir(outputDirectory)

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
        articleName = self.neutralize(self.articleName)
        print articleName
        outputFile = open('%s/%s' % (outputDirectory,self.hashName(self.articleName)), 'w')
        outputFile.write('<html><head><title>%s</title></head><body>' % self.articleName)
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

            # Template (ignored).
            if re.compile('^\{\{').match(line):
                continue
            if re.compile('^\|').match(line):
                continue
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
                    print "portion=" + portion
                    restOfLine = split[2]
                    # Process this portion
                    split = portion.partition('[[')
                    text = split[0]
                    wikilink = split[2]
                    print "wikilink=" + wikilink
                    line = line+text
                    # Parse the inside of the wikilink
                    target = wikilink
                    label = wikilink
                    if '|' in wikilink:
                        split = wikilink.partition("|")
                        target = split[0]
                        label = split[2]
                    target = self.neutralize(target)
                    # Create link only if the article exists.
                    if os.path.isfile(wikicodeDirectory + "/" + target + ".wikicode"):
                        level = '../' if hashnames else ''
                        line += '<a href="' + level + '%s">%s</a>' % (self.hashName(target), label)
                    else:
                        # Don't create a link, because it would be a broken link.
                        line += '<font color="red">' + label + '</font>'

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

            # Bold.
            # TODO Does not work: line=re.compile("'''(.*)'''").sub('<b>{\1}</b>', line)

            if minimization:
                line = re.compile('\s+').sub(' ', line)
            outputFile.write(line)
            if not minimization:
                outputFile.write('\n')
        outputFile.write('</body></html>')

    def neutralize(self, articleName):
        return articleName.replace('/','_')
# End of Article class

for infile in os.listdir(wikicodeDirectory):
    articleName = infile[:-9]
    wikicode = open(wikicodeDirectory + "/" + infile).read()
    article = Article(wikicode, articleName);
    article.saveHTML();

