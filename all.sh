#!/bin/bash

# Download the latest dump from the Wikivoyage server and transform it to an HTML guide.

wget http://dumps.wikimedia.org/enwikivoyage/ -O /tmp/dump-dates.txt
LAST_DUMP_LINE=`grep Directory /tmp/dump-dates.txt | grep -v latest | tail -n 1`
LAST_DUMP_DATE=`echo $LAST_DUMP_LINE | sed -e "s/<\/a>.*//g" -e "s/.*>//g"`
echo "Last dump date: $LAST_DUMP_DATE"

# TODO check if already downloaded

wget http://dumps.wikimedia.org/enwikivoyage/$LAST_DUMP_DATE/enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml.bz2

bunzip2 enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml.bz2

rm index.html
rm -rf articles/*

./generate_html_guide.py enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml
