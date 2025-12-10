setlocal EnableDelayedExpansion
for %%f in (winbuild\build\license\*) do (
  set x=%%~nf
  rem Skip FriBiDi license, it is not included in the wheel.
  set fribidi=!x:~0,7!
  if NOT !fribidi!==fribidi (
    rem Skip imagequant license, it is not included in the wheel.
    set libimagequant=!x:~0,13!
    if NOT !libimagequant!==libimagequant (
      echo. >> LICENSE
      echo ===== %%~nf ===== >> LICENSE
      echo. >> LICENSE
      type %%f >> LICENSE
    )
  )
)
call winbuild\\build\\build_env.cmd
%pythonLocation%\python.exe -m cibuildwheel . --output-dir wheelhouse
