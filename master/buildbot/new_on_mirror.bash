#!/usr/bin/env bash

rsync_url="$1"
local_dir="$2"

comm -23 \
	<(rsync --list-only "$rsync_url" | rev | cut -d ' ' -f 1 | rev | grep 'xbps$' | sort) \
	<(ls "$local_dir" | grep 'xbps$' | sort)
