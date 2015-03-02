#!/bin/sh

for file in static/less/*.less
do
	echo "Processing $file"
	filename=$(basename "$file")
    filename=${filename%.*}
    lessc $file > static/css/$filename.css
done