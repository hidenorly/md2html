# What's md2html.py?

It's a converter from markdown to html.
Remarkable points are considered to use the converted result as html mail and this has tiny template engine.
In short, this tool can convert link as Content-ID for html email and you can output html from the dynamic markdown with the template engine.

# How to use

## Preparation

```
$ pip install markdown
$ pip install py-gfm
```

Prepare preferred css file such as http://qiita.com/gamura@github/items/cda556061b6af247b9bc, https://github.com/sindresorhus/github-markdown-css, etc.

## Basic usage

```
$ md2html.py hoge.md -o hoge.html -s bootstrap-md.css -t "Hoge"
```

```
$ md2html.py hoge.md -o hoge.html -s bootstrap-md.css -t "Hoge" -m email
```


```
Usage: md2html.py [options]

Options:
  -h, --help            show this help message and exit
  -t TITLE, --title=TITLE
                        Specify title
  -c CHARSET, --charset=CHARSET
                        Specify charset
  -o OUTFILENAME, --output=OUTFILENAME
                        Specify output filename
  -s CSS, --css=CSS     Specify css filename
  -m MODE, --mode=MODE  Specify web or email
  -r REPLACERS, --replace=REPLACERS
                        Specify replace key=value,...
  -b, --bodyonly        --b if no header/footer
```

# Advanced usage (1)

With[mail.py](https://github.com/hidenorly/mailpy), 

```
$ md2html.py hoge.md -o hoge.html -s bootstrap-md.css -t "Hoge" -m email
$ cat hoge.html | mail.py -r bootstrap-md.css -s "hoge" -t html hoge@gmail.com
```

# Advanced usgae (2)

## Simple keyword replace

```
$ md2html.py hoge.md -o hoge.html -s bootstrap-md.css -t "Hoge" -m email -r HOGE1=hoge1 -r HOGE2=hoge2
```

Please note that the specified replace requests (```-r```) are applied for the inputed markdown and converted html.

## Template engine

```
# Quote from file

<%include="hoge.md"%>
```

You can include other file with <%include%>.

```
# Quote executed result

```
<%exec="ls -la"%>
```
```

You can embed shell execution result. But please take care of risk on the injection vulnerability.