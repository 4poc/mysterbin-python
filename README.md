mysterbin-python
================

This is a command line interface (and possibly library) for the usenet search [mysterbin.com](http://mysterbin.com/) written in python. It uses their [API](http://www.mysterbin.com/aboutapi.html) and I would like to thank the Mysterbin Team for providing me with an API Key!

Here is an example usage:

```
% ./mysterbin.py -h

Mysterbin v0.0.2 - NZB Search and Download

Syntax: ./mysterbin.py [OPTION] <QUERY>

API Search Options:

  <QUERY>                    the text query, you may include ranges
                             like {01-25}

  -g, --group <group>        exact name of a group to search into
  -n, --nresults <25/50/100> number of results per call
  -s, --start <offset>       offset in the result list
  -m, --match <best/normal/fuzzy/desperate>
                             matching mode
      --nocollapse           don't hide too many consecutive results 
                             from the same poster
  -t, --type                 type: archive, audio, ebook, exe, iso, other, par2, picture, video
      --size                 size: 1-10m, 10-100m, 100m-1g, 1g-4g, 1m, 4g
      --min-size <size>      minimum size in mb
      --max-size <size>      maximum size in mb (or 'max')
  -r, --max-age              the maximum retention time in days (default: None)
  -f, --nfo                  get only results with a NFO file
  -p, --passwd               skip results with passwords
  -c, --complete <0/1/2/3>   set a restriction on the completeness
                             higher values are more restrictive

Local Options:

  -l, --limit <limit>        (local) limits the results
  -a, --auto                 (local) automatically download all found
                             postings
  -o, --output <path>        specify output directory for nzb files
                             (default: /home/apoc/projects/python/mysterbin-python)
      --file <file>          use this as a base for filenames (if 
                             necessary append id)
      --qfile                use search query for filename (if 
                             necessary append id)             

  -h, --help                 show this help
  
Environment:

  MYSTERBIN_PATH             set to change default output directory
  MYSTERBIN_RETENTION        set to the default maximum age


% ./mysterbin.py -o ~/nzb -t iso -r 90 -p Ubuntu 12.04
Found 9 (9 total) postings found for: Ubuntu 12.04

[ 1] (01/40) "Ubuntu_12.04.par2" - 823,95 MB - yEnc (1/1)
     17d | 806.9 MiB | 97.42% | 28 rar - 10 par2 | lord4163

[ 2] ubuntu-12.04-dvd 64 bit -enjoy- [02/42] - "ubuntu-12.04-dvd-amd64.iso.001" yEnc (01/82)
     20d | 1.6 GiB | 100.00% | 1 nzb - 1 iso - 1 par2 | alien

[ 3] Ubuntu-12-04-NL-Instal-64bitl[03/18] - "ubuntu-12.04-desktop-amd64-nl.part1.rar" yEnc (001/403)
     20d | 669.3 MiB | 100.00% | 7 rar | CPman

[ 4] Ubuntu-12-04-NL-Install[03/18] - "ubuntu-12.04-desktop-i386-nl.part1.rar" yEnc (001/403)
     20d | 668.0 MiB | 100.00% | 7 rar | CPman

[ 5] "ubuntu-12.04-desktop-i386.par2" yEnc (1/1)
     21d | 943.2 MiB | 100.00% | 1 sfv - 15 rar - 10 par2 | Dless

[ 6] ubuntu-12.04-desktop-amd64.iso - toverdoos - "ubuntu-12.04-desktop-amd64.par2" yEnc (1/1)
     22d | 800.7 MiB | 100.00% | 28 rar - 8 par2 | Toverdoos

[ 7] ubuntu-12.04-desktop-amd64.iso - toverdoos 2 - "ubuntu-12.04-desktop-amd64.par2" yEnc (1/1)
     22d | 800.8 MiB | 100.00% | 28 rar - 8 par2 | toverdoos 2

[ 8] ubuntu-12.04-desktop-i386.iso - toverdoos 2 - "ubuntu-12.04-desktop-i386.par2" yEnc (1/1)
     22d | 804.3 MiB | 100.00% | 29 rar - 8 par2 | toverdoos 2

[ 9] (Ubuntu 12.04 LTS NegativeB) [03/62] - "Ubuntu12.04.par2" yEnc (1/1)
     26d | 799.2 MiB | 100.00% | 49 rar - 11 par2 | Yenc-PP-A&A

Download[q=quit,a=all]: 7
Your selection: [7]
Download id: 74263764
Download NZB to: /home/apoc/nzb/ubuntu-12.04-desktop-amd64.nzb
```
