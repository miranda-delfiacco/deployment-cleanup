#!/bin/bash

debug=""
bucket="mdelf-releases"

usage () {
    echo $(basename $0) "NUMBER_OF_DAYS [debug]"
    echo "e.g. " $(basename $0) "30 debug"
    echo ""
    echo "This script will delete deployment folders in S3 that are older than \$NUMBER_OF_DAYS days"
}

if [[ $# -lt 1 ]] ; then
  usage
  exit 0
fi

# Ensure user supplied an integer for $NUMBER_OF_DAYS
[[ $1 == ?(-)+([0-9]) ]] || { echo "Invalid NUMBER_OF_DAYS provided" ; exit 1 ;}

# Get timestamp to pass to awscli
ts=$(date +%Y-%m-%d -d "$1 days ago")

# Add debug option that only logs objects that would be removed in normal mode
if [[ $2 == "debug" ]] ; then
  echo "Running in debug mode, no objects will be deleted..."
  echo "Listing objects created on or before $ts ..."
  set -x
  debug="--dryrun"
else
  echo "Removing objects created on or before $ts ..."
fi

# Retrieve list of objects older than $ts, return top-level key / deployment folder to delete
objects_to_delete=$(aws s3api list-objects-v2 --bucket $bucket --query 'Contents[?LastModified<=`'"$ts"'`].Key' | jq -r '.[]' | cut -d'/' -f1 | uniq)

for i in $(echo $objects_to_delete) ; do
  aws s3 rm --recursive s3://${bucket}/${i} $debug
done
