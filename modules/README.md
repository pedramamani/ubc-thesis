## `Dataset`
A dataset is a folder with this structure:
* One or more data files numbered in order of capture starting with `0.extension`
* A required `info.txt` file that follows the format specified below
* An optional `notes.txt` containing additional notes on the data

Example dataset directory:
```
0.xls
1.xls
...
15.xls
info.txt
notes.txt
```

The `info.txt` file contains a table with information for each data file.
It is parsed during `Dataset` initialization and must follow this format:
* Empty lines or comment lines starting with `#` are ignored
* The first valid line is the header and specifies column names, types, and whether they are optional
* The header line is followed with one valid line per data file

Example `info.txt` file:

```
# bad tag means notch did not attenuate uniformly
# fpDistance is in mm

- number(int) fiberConfig fpDistance(int) tag
0 2 0 -
1 2 5 -
...
15 1(1)1 5 bad
```

