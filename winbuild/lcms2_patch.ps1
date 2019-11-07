
Get-ChildItem .\Projects\VC2015\ *.vcxproj -recurse |
    Foreach-Object {
        $c = ($_ | Get-Content)
        $c = $c -replace 'MultiThreaded<','MultiThreadedDLL<'
        $c = $c -replace '<WindowsTargetPlatformVersion>8.1</WindowsTargetPlatformVersion>','<WindowsTargetPlatformVersion>10</WindowsTargetPlatformVersion>'
        $c = $c -replace '<PlatformToolset>v140</PlatformToolset>','<PlatformToolset>v142</PlatformToolset>'
        [IO.File]::WriteAllText($_.FullName, ($c -join "`r`n"))
    }
