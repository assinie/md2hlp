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
                Configuration filename (default: md2hlp.cfg in current working diretcory)

*  --file FILE, -f FILE
                Input filename (default: stdin)

*  --output OUTPUT, -o OUTPUT
                output filename (default: stdout)

*  --verbose, -v
                increase verbosity (default: 0)

*  --version, -V
                show program's version number and exit

## ENVIRONMENT
**MD2HLP_PATH**
              If MD2HLP_PATH is set, md2hlp uses it as the path to search for configuration file. It is overridden
              by the -c invocation option.

## NOTES
Search order for the configuration file is:
1. -c invocation option
2. **md2hlp.cfg** in current working directory
2. **m2hlp.cfg** in MD2HLP_PATH directory

## EXAMPLES
md2hlp -f README.md -o help/md2hlp.hlp

![](/img/md2hlp.png)


md2hlp -f examples/date.md -o help/date.hlp

![](/img/date.png)

---

## Arborescence
- examples: Fichiers d'exemples (pages man de Orix)
- help: Fichiers du répertoire examples après conversion
- img: screenshots
- src: Sources

