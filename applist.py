# -*- coding: utf-8 -*-

import os

class UninstallEntry:
    def __init__(self, key):
        self._key = key
        self._d = {}

    def add(self, raw_line):
        # Line Format
        # (4space)(ENTRY-NAME)(4space)(TYPE-NAME)(4space)(VALUE)
        #
        # * VALUE は存在しない時がある.
        # * VALUE が 4space を含む可能性も考慮(split上限の設定)しなきゃ.
        ls = raw_line[4:].split(' '*4, 2)

        entryname = ls[0]
        typename = ls[1]
        value = ''
        if len(ls)>2:
            value = ls[2]

        self._d[entryname] = value

    NOT_FOUND_MARK = '<<NoData>>'

    @staticmethod
    def extract_identifiers(formatstr):
        st_none = 0
        st_start = 1

        status = st_none
        curname = ''
        ret = []

        for i in range(len(formatstr)):
            c = formatstr[i]

            if c=='%':

                if status==st_none:
                    status = st_start
                    curname = ''
                    continue

                if status==st_start:
                    status = st_none
                    ret.append(curname)
                    continue

                raise RuntimeError('invalid status at parsing `%`.')

            else:

                if status==st_none:
                    continue

                if status==st_start:
                    curname += c
                    continue

            raise RuntimeError('invalid if-branch.')

        return ret

    def formatstr(self, formatstr, identifiers):
        ret = formatstr
        for query in identifiers:
            replacee = '%{0}%'.format(query)
            value = self._d.get(query, UninstallEntry.NOT_FOUND_MARK)
            if query!=value:
                ret = ret.replace(replacee, value)
        return ret

    def keys(self):
        return self._d.keys()

class UninstallEntrySet:
    def __init__(self, targetkey):
        self._targetkey = targetkey
        self._entries = []

    def parse(self, rawstr):
        ls = rawstr.split('\r\n')

        current_entry = None

        for line in ls:
            if len(line)==0:
                continue

            if line.startswith('HKEY_'):
                # HKEY...Uninstall\{XXXX}
                #                  ~~~~~~ Extract here.
                key = line[len(self._targetkey)+1:]
                curent_entry = UninstallEntry(key)
                self._entries.append(curent_entry)
                continue

            if line.startswith(' '):
                curent_entry.add(line)
                continue

            # ここに来るケースもあるので明示的に無視.
            # 例:
            # - If you later install ... will be uninstalled automatically.
            # - For more information, visit ...
            continue

    def get_entries_by_list(self):
        return self._entries

def get_stdout(commandline):
    import subprocess
    return subprocess.check_output(commandline, shell=True)

def unittest():
    ret = UninstallEntry.extract_identifiers('InstallDate')
    assert(len(ret)==0)
    ret = UninstallEntry.extract_identifiers('InstallDate%%')
    assert(ret[0]=='' and len(ret[0])==0)
    ret = UninstallEntry.extract_identifiers('%InstallDate%')
    assert(ret[0]=='InstallDate')
    ret = UninstallEntry.extract_identifiers('%InstallDate%/%DisplayName%')
    assert(ret[0]=='InstallDate' and ret[1]=='DisplayName')
    ret = UninstallEntry.extract_identifiers('date:%InstallDate%, name:%DisplayName%')
    assert(ret[0]=='InstallDate' and ret[1]=='DisplayName')

def entry_name_report(entryset_list):
    keys = []
    for entry in entryset_list:
        keys.extend(entry.keys())

    countstore = {}
    for key in keys:
        if countstore.get(key, None)==None:
            countstore[key] = 1
        else:
            countstore[key] += 1

    pairs = sorted(countstore.items(), key=lambda x: x[1])
    #pairs.reverse()
    for pair in pairs:
        entryname, count = pair
        print('{:3d} {:}'.format(count, entryname))

    print('All entries: {:}'.format(len(entryset_list)))

def display_entrynames():
    s='''DisplayName
DisplayVersion
Publisher
VersionMinor
VersionMajor
Version
HelpLink
HelpTelephone
InstallDate
InstallLocation
InstallSource
URLInfoAbout
URLUpdateInfo
AuthorizedCDFPrefix
Comments
Contact
EstimatedSize
Language
ModifyPath
Readme
UninstallString
SettingsIdentifier
...

See: https://msdn.microsoft.com/ja-jp/library/windows/desktop/aa372105(v=vs.85).aspx'''
    print(s)

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(description='print application lists in appwiz.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f', '--format', default='%InstallDate% %DisplayName%',
        help='You can use %%EntryName%% as a variable. Raw output if not given.')
    parser.add_argument('--format-help1', default=False, action='store_true',
        help='Display valid entry names from MSDN.')
    parser.add_argument('--format-help2', default=False, action='store_true',
        help='Display valid entry names from occurrence frequency report.')

    parser.add_argument('--no-empty', default=False, action='store_true',
        help='Exclude data which has No-Data.')
    parser.add_argument('--no-kb', default=False, action='store_true',
        help='Exclude data which is about Windows Update(KBXXXXX).')

    parser.add_argument('-r', '--raw', default=False, action='store_true',
        help='If given, output the internal command\'s raw output.')


    parser.add_argument('--unittest', default=False, action='store_true',
        help='FOR DEBUG.')

    parsed_args = parser.parse_args()
    return parsed_args

args = parse_arguments()

TARGETKEY   = r'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall'
COMMANDLINE = 'reg query "{:}" /s'.format(TARGETKEY)

if args.unittest:
    unittest()
    exit(0)

if args.format_help1:
    display_entrynames()
    exit(0)

if args.raw:
    os.system(COMMANDLINE)
    exit(0)

raw_cmdline_output = get_stdout(COMMANDLINE)
# python 3 からは sys.stdout.encoding が utf-8 固定になっちゃってるので
# どうせ cmd.exe からしか使わないし cmd デフォの cp932 で固定しちゃう.
cmdline_output     = raw_cmdline_output.decode('cp932')

entries = UninstallEntrySet(TARGETKEY)
entries.parse(raw_cmdline_output.decode('cp932'))
ls = entries.get_entries_by_list()

if args.format_help2:
    entry_name_report(ls)
    exit(0)

identifiers = UninstallEntry.extract_identifiers(args.format)
for entry in ls:
    displaystr = entry.formatstr(args.format, identifiers)

    if args.no_empty and displaystr.find(UninstallEntry.NOT_FOUND_MARK)!=-1:
        continue

    if args.no_kb and displaystr.find('(KB')!=-1:
        continue

    print(displaystr)