# pass meta

An extension for the pass [password store](https://www.passwordstore.org/) that allows retrieval of values for specific properties from the meta data stored in a password file.

[password store](https://www.passwordstore.org/) proposes a format to store meta data in the password file. The password is stored in the first line followed by data like the URL, username and other meta data in the following lines. A common password file would look like this:
```
Yw|ZSNH!}z"6{ym9pI
URL: *.amazon.com/*
Username: AmazonianChicken@example.com
AnswerToASecretQuestion: 42
```

A common use case is to copy the first line, the password, using `pass
show -c <password file>`.
The meta data usually cannot be copied but needs to be displayed as it
contains type and value.

## pass meta

`pass meta <password file> Username` searches the meta data (the whole
file except the first line) for a line starting with 'Username:', and
prints the corresponding value:

```
AmazonianChicken@example.com
```


Similarly, we can pass any property we like:

`pass meta <password file> AnswerToASecretQuestion`

```
42
```


If the property is not found, the command simply returns nothing.

## Case Insensitivity

By default, the `pass meta` command treats property names in a case
insensitive way. That means that `pass meta <password file>
AnswerToASecretQuestion` and `pass meta <password file>
answertoasecretquestion` will give the same result. If you need case
sensitive matching, pass the -C option:

`pass meta -C <password file> AnswerToASecretQuestion`

## Finding usernames

Passing the option -u will return any properties with the names
`user`, `username` or `login`. By default this is case-insensitive, so
it will also find `Username`, for example.

## Finding urls

Passing the option -U will return any properties with the name
`url`. By default this is case-insensitive, so it will also find
`URL`, for example.

## Finding all matches

By default, `pass meta` only prints the first matching property. If
you want to see all matches, pass `-a`. This will print all matches.

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
