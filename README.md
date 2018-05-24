# applist
A light-weight installed application viewer on Windows.

## Demo

### No options
Display `InstallDate` and `DisplayName`.

```
$ python applist.py
<<NoData>> 7-Zip 9.20
<<NoData>> <<NoData>>
<<NoData>> Adobe AIR
...
<<NoData>> IIS Express Application Compatibility Database for x86
20131126 Microsoft Help Viewer 2.0
20140729 Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022
```

### Formatting
Use `-f` option.

```
$ python applist.py -f "%DisplayName% %DisplayVersion%"
7-Zip 9.20 <<NoData>>
<<NoData>> <<NoData>>
Adobe AIR 14.0.0.110
...
IIS Express Application Compatibility Database for x86 <<NoData>>
Microsoft Help Viewer 2.0 2.0.50727
Microsoft Visual C++ 2008 Redistributable - x86 9.0.21022 9.0.21022
```

About valid entry names, see `--format-help1`, `--format-help2` or [Uninstall Registry Key | MSDN](https://msdn.microsoft.com/ja-jp/library/windows/desktop/aa372105.aspx).

### Filtering
Exclude `<<NoData>>` entries and KB entries.

```
$ python applist.py | wc -l
336

$ python applist.py --no-empty --no-kb | wc -l
165
```

## Requirement
- Windows 7+
- Python 3.6+

## Installation
- Install [Python 3.6](https://www.python.org/) on your Windows.
- `git clone https://github.com/stakiran/applist` command or [Download ZIP](https://github.com/stakiran/applist/archive/master.zip) link.

## Technical notes

### Wrapper of reg query
AAMOF `applist.py` is the wrapper of `reg query "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Uninstall" /s` command.

## License
[MIT License](LICENSE)

## Author
[stakiran](https://github.com/stakiran)
