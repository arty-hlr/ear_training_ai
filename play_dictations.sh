#!/bin/bash

if [[ $# -lt 1 ]]
then
    echo 'Usage: ./play_dictations.sh <CHAPTER_NO>'
    exit
fi

CHAPTER=$1

PATH=$PATH:/Applications/MuseScore\ 4.app/Contents/MacOS

for musicxml in $(ls new_dictations/$CHAPTER.*.musicxml)
do
    echo "Processing $musicxml with musescore..."
    filename=$(echo $musicxml | cut -d '.' -f 1-2)
    mscore $musicxml -o $filename.mp3 2> /dev/null
    mscore $musicxml -o $filename.pdf 2> /dev/null
done
