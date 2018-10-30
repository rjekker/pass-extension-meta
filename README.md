# pass meta

An extension for the pass [password store](https://www.passwordstore.org/) that allows retrieval of values for specific properties from the meta data stored in a password file.

[password store](https://www.passwordstore.org/) proposes a format to
store meta data in the password file.  The password is stored in the
first line followed by data like the URL, username and other meta data
in the following lines.

A password file might look like this (this is a slightly silly
example, but it will allow us to explain the functionality of this
extension):

```
Yw|ZSNH!}z"6{ym9pI
URL: *.amazon.com/*
Username: AmazonianChicken@example.co
url: https://amazon.com/someotherurl
notes: Buy milk
```

A common use case is to copy the first line, the password, using `pass
show -c <password file>`. The meta data usually cannot be copied but
needs to be displayed as it contains type and value.

## pass meta

`pass meta <password file> Username` searches the meta data (the whole
file except the first line) for a line starting with 'Username:', and
prints the corresponding value:

```
AmazonianChicken@example.com
```


Similarly, we can pass any property we like:

`pass meta <password file> notes`

```
Buy milk
```

If the property is not found, the command returns nothing.

But if you don't specify a property to search for, a list of all the
property names is given:

`pass meta <password file>`

``` 
URL
Username
url
notes
```

## Copy to clipboard

Instead of showing the value, you can also have it copied to the
clipboard by specifying the `-c` option:

`pass meta -c <password file> notes` will copy the value of the
"notes" property to the clipboard.

## Finding usernames

Passing the option -u will return any properties with the names
`user`, `username` or `login`. By default this is case-insensitive, so
it will also find `Username`, for example.

`pass meta -cu <password file>` will find the (first) username and
copy it to the clipboard.

## Finding urls

Passing the option -U will return any properties with the name `url`
or `http`. By default this is case-insensitive, so it will also find
`URL`, for example.

`pass meta -cU <password file>` will find the first URL and copy it to
the clipboard.

## Finding all matches

By default, `pass meta` only prints the first matching property. If
you want to see all matches, pass `-a`. This will print all
matches. For example, to print all url fields:

`pass meta -aU <password file>`

```
*.amazon.com/*
https://amazon.com/someotherurl
```

## Complex searches

The search term you pass is used by the script as a (part of a) Perl
regular expression. This means that you can do quite powerful things,
like searching for multiple words:

`pass meta -a <password file> 'user|notes'`

```
AmazonianChicken@example.com
Buy milk
```

Or to match any properties with names not starting with the letter u:

`pass meta -a <password file> '^[^u]'`

```
Buy milk
```

Note that in the example above we have to pass the `-a` option,
because the normal behaviour would be to return only the first
matching line, and we wouldn't see the notes. 

Some more technical notes: before the search term is used as a regular
expression, any whitespace is removed from the start of the line. The
regular expression will only match the content of the line up to the
first colon (`:`). 

## Case Insensitivity

By default, the `pass meta` command treats property names in a case
insensitive way. That means that `pass meta <password file>
AnswerToASecretQuestion` and `pass meta <password file>
answertoasecretquestion` will give the same result. If you need case
sensitive matching, pass the -C option:

`pass meta -C <password file> url`

```
https://amazon.com/someotherurl
```


## Installation

- Enable password-store extensions by setting ``PASSWORD_STORE_ENABLE_EXTENSIONS=true``
- ``make install``
- alternatively add `meta.bash` to your extension folder (by default at `~/.password-store/.extensions`)

## Completion

This extensions comes with the extension bash completion support added
with password-store version 1.7.3

When installed, bash completion is already installed. Alternatively
source `completion/pass-meta.bash.completion`

fish and zsh completion are not available, feel free to contribute.

## Contribution

Contributions are always welcome.
