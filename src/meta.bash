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
            property='url|http'
            ;;
        c)
            clip='y'
            ;;
        C)
            regex_opts=''
            ;;
        a)
            first_match_only='0'
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

[[ -f $passfile ]] || die "Error: $path is not in the password store."

# This function returns a perl script
# It's an ugly way to include a nicely indented script here
get_perl_source() {
    cat <<EOF
my \$dummy=<>; # skip password
my \$needle="$1"; # thing to search for

sub  trim { my \$s = shift; \$s =~ s/^\s+|\s+\$//g; return \$s };

while(<>){
    if(/^\s*         # read any whitespace before the property name 
       (.+?):        # property name and :
       \s*           # read any whitespace after :
       (.*)          # capture the rest of the line
       /x){
           my \$prop_name = \$1;
           my \$prop_val = \$2;
           if(\$needle){
               # we are searching a specific prop
               if(\$prop_name =~ /(\$needle)/$regex_opts){
                   # this one matches; print the value
                   print \$prop_val;
                   exit if $first_match_only;
               }
           } else {
               # not searching; just printing all metadata props
               print trim(\$prop_name);
           }
    }
}
EOF
}

value=$($GPG -d "${GPG_OPTS[@]}" "$passfile" | perl -l <(get_perl_source "$property" ) )
if [[ -n $clip ]]; then
    clip "$value"
else
    echo "$value"
fi
