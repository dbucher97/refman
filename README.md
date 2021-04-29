# RefMan

This is a lightweight Reference Manager for BibTeX. It's default use is
continuously watching a reference directory (recursively) and add or delete a
reference BibTeX entry from the `master.bib` database when a paper is added in
the directory. It uses `pdf2doi` to extract the `DOI` or `arXiv ID` from a
paper. When none is found, it will notify you to manually ad information into
the database. If just the `DOI` or `arXiv ID` was not found, add it into the
BibTeX database with the identifier `\doi` (`arxiv`) and leave the field
`todo`. Upon closing _refman_ will try to retrieve more info about the
reference. If this fails, it will automatically remove it again. If you just
want manual entries for references without a `DOI`, just remove `\todo` and
fill in the necessary fields like `\author`, `\year`, etc.

## Installation

To install _refman_. Use python setuptools and pip.

```
python3 setup.py sdist
pip3 install dist/refman-*.tar.gz
```

This module comes with `zsh` auto-completion, especially handy for opening
references. You have to add the autocompletion script to the `$fpath`.
In `.zshrc`:

```.zshrc
fpath=(/usr/local/opt/refman/zsh $fpath)
```

You might have to modify the path depending on your system.

Now you need to start the watching of your directory. First, create the config
file `~/.refman.conf` and specify the dir

```
dir = /path/to/your/lib/
```

Because I am on MacOs, _refman_ only comes with tooling for automatically
setting up the continuous observation in the background using `launchctl`.
Simply run `ref start` to start the watching (state preserves on reboot) and
`ref stop` to stop it.
On Linux, depending on your init system, you can easily do this manually
running the command `ref watch` on startup.

## Usage

Put a paper into the directory you have specified. You will observe a
`master.bib` in this directory with added BibTeX entry. The Program will also
notify you, whether the search for metatdata was successful.

The BibTeX entry will have an ID composed of the first author and the year. You
can also open PDFs by using this identifier by

```
ref open id
```

Also you can test the matadata retrieval for any PDF with

```
ref info /path/to/document.pdf
```
