#!/bin/bash

regex_opts='i'
first_match_only='1'
property=''
clip=''


while getopts 'auUCc' opt; do
    case $opt in
        u)
            property='user|username|login'
        ;;
        U)
            property='url'
            ;;
        c)
            clip='y'
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

# This function returns a perl script
# It's an ugly way to include a nicely indented script here
get_perl_source() {
    cat <<EOF
my \$dummy=<>;   # throw away password line
while(<>){
    if(/^\s*?       # read any whitespace before the property name 
       ($1):         # property name and :
       \s*         # read any whitespace after :
       (.*)        # capture the rest of the line
       /x$regex_opts){
           print \$2;
           exit if $first_match_only;
    }
}
EOF
}

value=$($GPG -d "${GPG_OPTS[@]}" "$passfile" | perl -nl <(get_perl_source "$property" ) )
if [[ -n $clip ]]; then
    clip "$value"
else
    echo "$value"
fi
