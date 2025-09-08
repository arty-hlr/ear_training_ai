#!/bin/bash

PATH=$PATH:/Applications/AnthemScore.app/Contents/MacOS/

for mp3 in $(ls dictations/*.mp3)
do
    filename=$(echo $mp3 | cut -d '.' -f 1-2)
    echo -en "$mp3\r"
    AnthemScore $mp3 -a -x $filename.musicxml 2> /dev/null
done
