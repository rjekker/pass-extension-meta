#!/bin/bash

match_opts='-iE'
first_match_opts='-m1'
property=''

while getopts 'auUC' opt; do
    case $opt in
        u)
            property='user|username|login'
        ;;
        U)
            property='url'
        ;;
        C)
            match_opts='-E'
            ;;
        a)
            first_match_opts=''
            ;;
        \?)
            exit 1
            ;;
    esac
done

shift $(($OPTIND - 1))
path=$1

[[ -z $path ]] && die

check_sneaky_paths "$path"
passfile="$PREFIX/$path.gpg"
property=${property:-$2}

[[ -z $property ]] && die "Please specify a property to search for"
[[ -f $passfile ]] || die "Error: $path is not in the password store."

$GPG -d "${GPG_OPTS[@]}" "$passfile" | tail -n +2 | grep $first_match_opts $match_opts "^${property}:" | cut -d' ' -f 2-
