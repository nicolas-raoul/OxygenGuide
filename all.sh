#!/bin/bash

# Download the latest dump from the Wikivoyage server and transform it to an HTML guide.

wget http://dumps.wikimedia.org/enwikivoyage/ -O /tmp/dump-dates.txt
LAST_DUMP_LINE=`grep Directory /tmp/dump-dates.txt | grep -v latest | tail -n 1`
LAST_DUMP_DATE=`echo $LAST_DUMP_LINE | sed -e "s/<\/a>.*//g" -e "s/.*>//g"`
echo "Last dump date: $LAST_DUMP_DATE"

# Check if already downloaded
if [ -f enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml ];
then
   echo "Already present. Exiting."
   exit
else
   echo "Not present yet. Generating."
fi

wget http://dumps.wikimedia.org/enwikivoyage/$LAST_DUMP_DATE/enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml.bz2

bunzip2 enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml.bz2

rm index.html
rm -rf articles
mkdir articles

./generate_html_guide.py enwikivoyage-$LAST_DUMP_DATE-pages-articles.xml

PRETTY_DATE=`echo $LAST_DUMP_DATE | sed 's/^\(.\{4\}\)/\1-/' | sed 's/^\(.\{7\}\)/\1-/'`
mkdir OxygenGuide_$PRETTY_DATE-a
mv index.html articles OxygenGuide_$PRETTY_DATE-a/
ZIPNAME="OxygenGuide_$PRETTY_DATE-a.zip"
zip -r $ZIPNAME OxygenGuide_$PRETTY_DATE-a/

echo "Done: $ZIPNAME"

#echo "Uploading to Google Code"
#GOOGLECODE_PASSWORD=`cat ~/src/googlecode-password.txt` # Can be found at https://code.google.com/hosting/settings
#./googlecode_upload.py --summary "OxygenGuide" --project oxygenguide --user nicolas.raoul --password $GOOGLECODE_PASSWORD OxygenGuide_$PRETTY_DATE-a.zip

echo "Uploading to Sourceforge"
rsync -e ssh $ZIPNAME wvuploader,wikivoyage@frs.sourceforge.net:/home/frs/project/w/wi/wikivoyage/OxygenGuide/
