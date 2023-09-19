# Configuration file

## Sections

### [DEFAULT]
The only mandatory section is **DEFAULT** which list all defaults

### [Headingx]
**Heading1** to **Heading6** list renderer for text below the specified heading up to the next heading section.

The number in the section's name correspond to the heading level:
+ `# Heading1`
+ `## Heading2`
+ `### Heading3`
+ ...

### Others
Other sections correspond to specific heading title.

Example:
+ **[NOTES]** section list specific options used to render all text between a heading section with title **NOTES** regardless of its level (`# NOTES`, `### NOTES`, ...) and the next heading.

## Options
### For Head Title
These options are used to render head title
+ **Head**: Displayed before heading titles
+ **Align**: Head title alignment (Default: left margin)
  - **^**: Center
  - **>**: Right margin

### For Paragraph
These options are used to render paragraph
+ **Break on hyphens**: if *True*, wrapping will occur preferably on whitespaces and right after hyphens in compound words. If *False*, only whitespaces will be considered for line breaks.
+ **Paragraph**: Unused
+ **Initial Indent**: Initial indentation for a paragraph (ie: first line indentation)
+ **Subsequent Indent**: Subsequent indentation for a paragraph (ie: from second line up to the last line of the paragraph)
+ **Quote block**: Displayed in front of each line of a quote bloc (` ```code bloc``` `)
+ **List**: Display in front of the begining of a list line
+ **Cite**: Displayed in front of each line of of cite bloc (`> Cite bloc`)

### For Emphasis styles
These options are used to render emphasis.
The prefix and postfix strings are separated by a comma.
If the option is set to `None`, the text will not be rendered.

Example: `Bold = ^T,\_^P` will render `**text**` as `<0x14>text<space><0x10>`

+ **Quote**: Prefix and postfix used for inline quote: ``inline quote``
+ **Link**: Prefix and Postfix used to display the text in brackets of a link: `[text in bracket](http://...)`
+ **Image**: Prefix and Postfix used to display the text in brackets of a image link: `![text in bracket](http://...)`
+ **bold**: Prefix and postfix for bold style: `** text **`
+ **italic**: Prefix and postfix for italic style: `* text *`
+ **strike through**: Prefix and postfix for strikethrough style: `~~ text ~~`
+ **underline**: Prefix and postfix for inderline style: `__ text __` (not Markdown syntax)

## Special characters in the *.md* file or the configuration file
+ If a character from the list \\`*_{}[]()#+-.!~^ is preceded by  a **\\**, this character is escaped (only whithin the *.md* file).
+ **_** will be rendered as a space (only within the configuration file).
+ **^** before an **uppercase** alphabetical character means **CONTROL CODE**.
  + `^A` means `CONTROL+A` and will be rendered as byte 0x01 (ie: red ink).
  + `^S` means `CONTROL+S` and will be renderer as byte 0x13 (ie: yellow paper).

+ **^v** means inverse video up to the next **^v**.
  + If the current paper is black and current ink is white, then **^vtext^v** will display **text** black on white.
  + If the current paper is black and current ink is blue, then **^vtext^v** will display **text** yellow on white.
  + If the current paper is red and current ink is green, then **^vtext^v** will display **text** purple on cyan.

| Color | Inverse |
| ----- | ------- |
| Black | White |
| Red   | Cyan |
| Green | Purple |
| Yellow | Blue |
| Blue   | Yellow |
| Purple | Green |
| Cyan   | Red |
| White  | Black |


