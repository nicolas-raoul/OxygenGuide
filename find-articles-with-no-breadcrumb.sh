#!/bin/bash
find ../oxygenpump/wikicode -type f \! -exec grep -qi -e "IsPartOf\|IsIn\|REDIRECT\|itinerary}}\|{{phrasebookguide}}\|disamb\|topic}}" {} \; -print \
| grep -v "wikicode/.*%2F" \
| sed -e "s/.*wikicode\//* http:\/\/wikitravel.org\/en\//g" -e "s/.wikicode//g" -e "s/%2F/\//g"
