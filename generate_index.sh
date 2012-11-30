#!/bin/bash

# Generates index page 

output=index.html

echo "Generating $output".. 

echo "<html>
<head><title>OxygenGuide</title></head>
<body>
<ul>" > ${output}

for i in "Africa" "Antarctica" "Asia" "South Asia" "Southeast Asia" "Caribbean" \
"Central America" "Europe" "Middle East" "North America" "South America" \
"Other destinations" "Travel topics" "List of phrasebooks"
do
echo -n "Looking for $i ... "
c="<title>${i}</title>"
link=`grep -lir "$c" articles`
if test "$link"x != "x" 
then
echo  '<li><a href="'${link}'">'${i}'</a></li>' >> ${output}
echo OK
else
echo "Not found"
fi
done
echo '</ul>
<p>This content is based on work by all volunteers of <a href="http://wikivoyage.org">Wikivoyage</a> and <a href="http://wikitravel.org">Wikitravel</a>.
Text is available under <a href="http://creativecommons.org/licenses/by-sa/1.0/">Creative Commons Attribution-ShareAlike 1.0</a>.
Comments welcome on <a href="https://en.wikivoyage.org/wiki/User:Nicolas1981">my user page</a>.</p>
</body>
</html>' >> ${output}
