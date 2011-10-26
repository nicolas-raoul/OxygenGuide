## OxygenGuide - Offline travel guide
##
## Generate HTML files for articles from http://wikitravel.org
## Input: XML file generated with "Web Content Extractor"
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
#wikicodeFilePath = 'unittests.xml'
wikicodeFilePath='articles.xml'
outputDirectory = 'articles'
minimization = False

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
        hashvalue = '%d' % abs(hash(articleName))
        directory = hashvalue[:2]
        file = hashvalue[2:]
        if not os.path.isdir('%s/%s' % (outputDirectory, directory)):
            os.mkdir('%s/%s' % (outputDirectory, directory))
        return directory + '/' + file + '.html'

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
                    restOfLine = split[2]
                    # Process this portion
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
                    target = self.neutralize(target)
                    # Create link only if the article exists.
                    if target in articlesNames:
                        line += '<a href="../%s">%s</a>' % (self.hashName(target), label)
                    else:
                        # Don't create a link, because it would be a broken link.
                        line += label

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

# This handler receives the whole XML data and builds an index of articles names,
# that will be used to know whether a link would be a red link or not.
class ArticlesNamesHandler(ContentHandler):
    def __init__ (self):
        self.isArticleNameElement=False
        self.articleName=''
   
    def startElement(self, name, attrs):
        if name=='article_name':     
            self.isArticleNameElement = True

    def characters (self, characters):
        if self.isArticleNameElement:
            self.articleName += characters

    def endElement(self, name):
        if name=='article_name':
            articleName = self.articleName[8:] # Remove "Editing " prefix
            articlesNames.append(articleName)
            self.articleName = ''
            self.isArticleNameElement = False

# This handler receives the whole XML data and builds Article objects.
# The scrape XML file must have this format:
# Items
#   Item
#     article_name Page title displayed by Wikipedia when editing wikicode, for instance "Editing Paris"
#     wikicode
class WikitravelScrapeHandler(ContentHandler):
    def __init__ (self):
        self.isArticleNameElement = False
        self.isWikicodeElement = False
        self.articleName = ''
        self.wikicode = ''
   
    def startElement(self, name, attrs):
        if name=='article_name':     
            self.isArticleNameElement = True
        elif name=='wikicode':
            self.isWikicodeElement = True

    def characters (self, characters):
        if self.isArticleNameElement:
            self.articleName += characters
        if self.isWikicodeElement:
            self.wikicode += characters

    def endElement(self, name):
        if name=='article_name':
            self.isArticleNameElement = False
        if name=='wikicode':
            self.isWikicodeElement = False
        if name=='Item':
            articleName = self.articleName[8:]
            article = Article(self.wikicode, articleName);
            article.saveHTML();
            self.articleName = ''
            self.wikicode = ''

# Main
print 'Transforming from '+wikicodeFilePath+' ...'
parser = make_parser()

# Builds the list of articles names (for red link prevention).
parser.setContentHandler(ArticlesNamesHandler())
parser.parse(open(wikicodeFilePath))

# Process the wikicode and write guide
parser.setContentHandler(WikitravelScrapeHandler())
parser.parse(open(wikicodeFilePath))
print 'Done.'
