# Command: md2hlp

### Convert from Markdown to Orix Help

## SYNOPSYS
md2hlp [-h] [--config CONFIG] [--file FILE] [--output OUTPUT] [--verbose] [--version]

## DESCRIPTION
Convert from Markdown to Orix Help

## OPTIONS
*  -h, --help
                show this help message and exit

*  --config CONFIG, -c CONFIG
                Configuration filename (default: md2hlp.cfg)

*  --file FILE, -f FILE
                Input filename (default: None)

*  --output OUTPUT, -o OUTPUT
                output filename (default: None)

*  --verbose, -v
                increase verbosity (default: 0)

*  --version, -V
                show program's version number and exit

## EXAMPLES
md2hlp -f README.md -o help/md2hlp.hlp

![](https://github.com/assinie/md2hlp/blob/master/img/md2hlp.png)


md2hlp -f examples/date.md -o help/date.hlp
![](https://github.com/assinie/md2hlp/blob/master/img/date.png)

---

## Arborescence
- examples: Fichiers d'exemples (pages man de Orix)
- help: Fichiers du répertoire examples après conversion
- img: screenshots
- src: Sources

