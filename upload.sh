#!/bin/bash
ZIPNAME=OxygenGuide_2013-12-16-a.zip
echo "Uploading to Sourceforge"
su - nicolas-raoul
rsync -e ssh $ZIPNAME wvuploader,wikivoyage@frs.sourceforge.net:/home/frs/project/w/wi/wikivoyage/OxygenGuide/
