#!/usr/bin/env bash

set -ex

function decompress_traceroute() {
  bunzip2 in/traceroute-2026-06-20T0000.bz2
}

function preview_traceroute() {
  head -n 100 in/traceroute-2026-06-20T0000.ndjson
}

function take_google_sample() {
  count=$1
  cat in/traceroute-2026-06-20T0000.ndjson | grep google.com | head -n $count > out/google_com_sample_$count.ndjson
}

function count_google_records() {
  cat in/traceroute-2026-06-20T0000.ndjson | grep -c google.com 
}

function count_facebook_records() {
  cat in/traceroute-2026-06-20T0000.ndjson | grep -c facebook.com
}

mkdir -p out

# preview_traceroute
take_google_sample 100
