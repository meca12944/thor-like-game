#!/bin/bash
# usage: grab_new.sh SINCE "dst1 dst2 ..."  - copy attachments newer than SINCE (oldest first) to dsts
A=/cursor/stores/store-795156a0-7465-4f60-aac0-5ea8cd38a231/grok-bot/agents/4fedc784-0420-4bf1-b51b-e98cbd24f667/attachments
mapfile -t F < <(find $A -name "*.jpg" -newermt "$1" -printf "%T@ %p\n" | sort -n | cut -d' ' -f2)
i=0; for d in $2; do cp "${F[$i]}" "$d"; echo "$d <- $(basename ${F[$i]})"; i=$((i+1)); done
echo "found ${#F[@]}"
