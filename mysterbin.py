#!/usr/bin/env python
# python cli for mysterbin.com
#
# Copyright (C) 2012 Matthias Hecker (apoc.cc)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# should work with Python 2.6+ and (hopefully) 3.0+
#
from __future__ import print_function
VERSION = 'v0.0.2'

import re
import os
import sys
import json
import time
import getopt
import string
# to support python 2 and 3 (not that urllib has gotten
# any less crappy of an http library)
try:
    from urllib.request import urlopen
    from urllib.parse import quote_plus
except ImportError:
    from urllib import urlopen
    from urllib import quote_plus

Bold = '\x1B[1m'
Normal = '\x1B[0m'

FYTYPE = { # only used in the cli frontend as a convenient abstraction
    'video': 1,
    'audio': 2,
    'exe': 3,
    'iso': 4,
    'picture': 5,
    'archive': 6,
    'par2': 7,
    'ebook': 8,
    'other': 100
}
FSIZE = {
    '1m': 1,
    '1-10m': 2,
    '10-100m': 3,
    '100m-1g': 4,
    '1g-4g': 5,
    '4g': 6
}

class Request(object):

    url = 'http://www.mysterbin.com/api'
    key = 'dff54eb2539fb62bc9452b8d93fc2e6f'
    
    def __init__(self):
        self.group = None
        self._nresults = 25
        self.start = None
        self._match = None
        self.nocollapse = False
        self.nfo = False
        self.passwd = False
        self._complete = None
        self._fytype = None
        self._fsize = None
        self.min_size = None
        self.max_size = None
        self.max_age = None

    def search(self, query):
        self.query = query
        params = []
        hparams = {
            'q': self.query,
            'group': self.group,
            'nresults': self.nresults,
            'start': self.start,
            'match':self.match,
            'nocollapse': 'true' if self.nocollapse else 'false',
            'nfo': 'true' if self.nfo else 'false',
            'passwd': 'true' if self.passwd else 'false',
            'complete': self.complete,
            'key': Request.key,
            'fytype': self.fytype,
            'fsize': self.fsize,
            'minSize': self.min_size,
            'maxSize': self.max_size if self.max_size != -1 else 'max',
            'maxAge': self.max_age
        }
        for param in iter(hparams):
            if hparams[param]: 
                params.append('%s=%s' % (
                    quote_plus(str(param)), 
                    quote_plus(str(hparams[param]))))
        url = '%s?%s' % (Request.url, '&'.join(params))

        content = urlopen(url).read().decode('utf-8')

        return Result(json.loads(content))

    def set_nresults(self, nresults):
        if not nresults in (25, 50, 100):
            raise ValueError('Use nresults of 25, 50 or 100 only.')
        self._nresults = nresults

    def get_nresults(self):
        return self._nresults

    nresults = property(get_nresults, set_nresults)

    def set_match(self, match):
        if not match in ('best', 'normal', 'fuzzy', 'desperate'):
            raise ValueError('Specify match as best, normal, fuzzy or desperate only.')
        self._match = match

    def get_match(self):
        return self._match

    match = property(get_match, set_match)

    def set_complete(self, complete):
        if not complete in (0, 1, 2, 3):
            raise ValueError('Use a complete value between 0 and 3.')
        self._complete = complete

    def get_complete(self):
        return self._complete

    complete = property(get_complete, set_complete)

    def set_fytype(self, fytype):
        if not fytype in range(1, 9) or fytype == 100:
            raise ValueError('Valid fytype values are 1-8 and 100.')
        self._fytype = fytype

    def get_fytype(self):
        return self._fytype

    fytype = property(get_fytype, set_fytype)

    def set_fsize(self, fsize):
        if not fsize in range(1, 7):
            raise ValueError('Valid fsize values are 1-6.')
        self._fsize = fsize

    def get_fsize(self):
        return self._fsize

    fsize = property(get_fsize, set_fsize)

class Result(list):

    def __init__(self, result):
        self.start = int(result['hits_start'])
        self.total = int(result['hits_total'])
        for posting in result['hits']:
            self.append(Posting(posting))
        if result['hits_shown'] != len(self):
            raise Error('Hits expected: %d, received: %d.' % (result['hits_shown'], len(self)))

class Posting(object):

    nzb_url = 'http://www.mysterbin.com/nzb?c='

    def __init__(self, posting):
        self.rar_extract = posting['RARextract']
        self.rar_passwd = posting['RARpasswd']
        self.extensions = posting['extensions']
        if posting['groupid']: self.groupid = int(posting['groupid'])
        self.groups = posting['groups']
        self.has_nfo = posting['hasNFO']
        self.has_rars = posting['hasRARs']
        self.id = int(posting['id'])
        self.mimes = posting['mimes']
        self.parts_found = int(posting['parts_found'])
        self.parts_total = int(posting['parts_total'])
        self.posted_date = int(posting['postedDate'])
        self.poster = posting['poster']
        self.size = int(posting['size'])
        self.subject = posting['subject']

    def get_subject_bold(self):
        if re.search("\".*\"", self.subject):
            subject = re.sub("^([^\"]+)\"", "\g<1>\""+Bold, self.subject)
            return re.sub("\"([^\"]+)$", Normal+"\"\g<1>", subject)
        else:
            return self.subject
        
    subject_bold = property(get_subject_bold)

    def get_retention(self):
        return time.localtime((time.time() - int(self.posted_date))).tm_mday 

    retention = property(get_retention)

    def get_readable_size(self):
        size = self.size
        for postfix in ["B", "KiB", "MiB", "GiB", "TiB"]:
            if size < 1024.0:
                return "%3.1f %s" % (size, postfix)
            size /= 1024.0

    readable_size = property(get_readable_size)

    def get_complete_percent(self):
        return self.parts_found / (self.parts_total / 100.0)

    complete_percent = property(get_complete_percent)

    def downloadNZB(self, directory, filename=None):
        # default filename to the filename responded by the 
        # content disposition header
        response = urlopen(Posting.nzb_url + str(self.id))

        directory = os.path.expanduser(directory)

        if not filename:
            try:
                for header in response.info().headers:
                    match = re.search('attachment; filename="([^\"]+)"', header)
                    if match:
                        filename = match.group(1)
            except:
                filename = response.info().get_filename()

        filename = filename.replace(' ', '.')

        path = os.path.join(directory, filename)

        if os.path.exists(path):
            # filename = os.path.basename(path) 
            filename = re.sub('\.nzb$', '%d.nzb' % self.id, filename)
            path = os.path.join(directory, filename)

        print('Download NZB to: ' + path)
        with open(path, 'w') as f:
            f.write(response.read().decode('utf-8'))




def main():
    request = Request()

    # some defaults for the local options
    limit = None
    auto = False
    output = os.getcwd()
    filename = None
    qfile = False
    max_age = None

    if 'MYSTERBIN_PATH' in os.environ:
        output = os.environ['MYSTERBIN_PATH']

    if 'MYSTERBIN_RETENTION' in os.environ:
        max_age = os.environ['MYSTERBIN_RETENTION']
    request.max_age = max_age

    def usage():
        print('''Mysterbin %s - NZB Search and Download

Syntax: %s [OPTION] <QUERY>

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
  -t, --type                 type: %s
      --size                 size: %s
      --min-size <size>      minimum size in mb
      --max-size <size>      maximum size in mb (or 'max')
  -r, --max-age              the maximum retention time in days (default: %s)
  -f, --nfo                  get only results with a NFO file
  -p, --passwd               skip results with passwords
  -c, --complete <0/1/2/3>   set a restriction on the completeness
                             higher values are more restrictive

Local Options:

  -l, --limit <limit>        (local) limits the results
  -a, --auto                 (local) automatically download all found
                             postings
  -o, --output <path>        specify output directory for nzb files
                             (default: %s)
      --file <file>          use this as a base for filenames (if 
                             necessary append id)
      --qfile                use search query for filename (if 
                             necessary append id)             

  -h, --help                 show this help
  
Environment:

  MYSTERBIN_PATH             set to change default output directory
  MYSTERBIN_RETENTION        set to the default maximum age''' % (VERSION, 
      sys.argv[0], ', '.join(sorted(FYTYPE.keys())), 
      ', '.join(sorted(FSIZE.keys())), max_age, output))

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'q:g:n:s:m:fpc:l:ao:ht:r:', ['query=', 
            'group=', 'nresults=', 'start=', 'match=', 'nocollapse',
            'nfo', 'passwd', 'complete=', 'limit=', 'auto', 
            'output=', 'file=', 'qfile', 'help', 'type=', 'size=', 'min-size=', 'max-size=', 'max-age='])

        for opt, arg in opts:
            if opt in ('-g', '--group'):
                request.qroup = arg

            elif opt in ('-n', '--nresults'):
                request.nresults = int(arg)

            elif opt in ('-s', '--start'):
                request.start = arg

            elif opt in ('-m', '--match'):
                request.match = arg

            elif opt in ('--nocollapse'):
                request.nocollapse = True

            elif opt in ('-f', '--nfo'):
                request.nfo = True

            elif opt in ('-p', '--passwd'):
                request.passwd = True

            elif opt in ('-c', '--complete'):
                request.complete = int(arg)

            elif opt in ('-l', '--limit'):
                limit = int(arg)

            elif opt in ('-a', '--auto'):
                auto = True

            elif opt in ('-o', '--output'):
                if os.path.exists(arg):
                    output = arg
                else:
                    raise ValueError('output directory not found')

            elif opt in ('--file'):
                filename = arg

            elif opt in ('--qfile'):
                qfile = True

            elif opt in ('-t', '--type'):
                if arg in FYTYPE:
                    request.fytype = FYTYPE[arg]
                else:
                    raise ValueError('unknown type')

            elif opt in ('--size'):
                if arg in FSIZE:
                    request.fsize = FSIZE[arg]
                else:
                    raise ValueError('unknown size')

            elif opt in ('--min-size'):
                if arg.isdigit():
                    request.min_size = int(arg)
                else:
                    raise ValueError('invalid minimum size')

            elif opt in ('--max-size'):
                if arg.isdigit():
                    request.max_size = int(arg)
                elif arg == 'max':
                    request.max_size = -1
                else:
                    raise ValueError('invalid maximum size')

            elif opt in ('-r', '--max-age'):
                request.max_age = int(arg)

            elif opt in ('-h', '--help'):
                usage()
                sys.exit()

            else:
                raise ValueError('unhandled option')

        if len(args) <= 1:
            raise getopt.GetoptError('You need to specify a search query.')

        queries = []
        query = ' '.join(args)
        m = re.search('(\{(\d+)\-(\d+)\})', query)
        if m:
            num_range = m.group(1)
            num_start = int(m.group(2))
            num_stop = int(m.group(3))
            for num in range(num_start, num_stop+1):
                queries.append(query.replace(num_range, ('%0'+str(len(str(num_stop)))+'d') % num))
        else:
            queries.append(query)

    except getopt.GetoptError as err:
        print(str(err))
        print()
        usage()
        sys.exit(2)

    except ValueError as err:
        print('Error in parsing parameter types: %s' % str(err))
        sys.exit(2)


    all_results = []
    for query in queries:
        results = request.search(query)

        print('Found %d (%d total) postings found for: %s' % (
            len(results), results.total, query))
        print()

        all_results += results

    for i in range(0, limit if (limit and limit < len(all_results)) else len(all_results)):
        posting = all_results[i]
        print('[%2d] %s' % (i+1, posting.get_subject_bold()))
        meta = (
            '%dd' % posting.retention,
            posting.readable_size, 
            '%.2f%%' % posting.complete_percent,
            posting.extensions, 
            posting.poster)
        print('     %s' % (' | '.join(meta)))
        print()

    selected = list(range(0, len(all_results)))
    if not auto and len(all_results) > 0:
        sys.stdout.write('Download[q=quit,a=all]: ')
        sys.stdout.flush()
        sel = sys.stdin.readline().strip()
        if sel == 'q':
            sys.exit()

        elif sel == 'a':
            selected = list(range(0, len(all_results)))

        else:
            # Valid syntax for selection:
            # 1, 2, 3
            # 1 2 3 4
            # 1-4
            # 1-2, 4-3 8-9
            # 1 - 3, 5 - 13
            sel = re.sub(' ?- ?', '-', sel)
            sel = re.split('[ ,]', sel)
            selected = []
            for s in sel:
                s = s.strip()
                if '-' in s:
                    rparts = s.split('-')
                    selected += list(range(int(rparts[0]), int(rparts[1])+1))
                elif s.isdigit():
                    selected += [ int(s) ]
                elif s != '':
                    print('WARNING: ignored your selection: %s' % s)
            print('Your selection: ' + str(selected))

    for selection in selected:
        posting = all_results[selection-1]
        print('Download id: '+str(posting.id))
        # TODO: fix that qfile here filename = posting.
        posting.downloadNZB(output, filename)




if __name__ == '__main__':
    main()

