PATTERN = "some"
REPL = "another"
DIR = ".\"
EXT = "xxx"


set fileSystem = createObject("scripting.fileSystemObject")
set folder = fileSystem.getFolder(DIR)
index = 0

for each file in folder.files
	segments = split(file.name, ".")
	extension = segments(uBound(segments))
    newName = replace(file.name, PATTERN, REPL)

    if (extension = EXT) then
    	newName = cStr(index) & "." & extension
    	index = index + 1
    end if
    

    if (newName <> file.name) then
        file.move(file.parentFolder & "\" & newName)
    end if
next