from __future__ import print_function

# minimal test runner

import glob, os, os.path, sys, tempfile, re

try:
    root = os.path.dirname(__file__)
except NameError:
    root = os.path.dirname(sys.argv[0])

if not os.path.isfile("PIL/Image.py"):
    print("***", "please run this script from the PIL development directory as")
    print("***", "$ python Tests/run.py")
    sys.exit(1)

print("-"*68)

python_options = []
tester_options = []

if "--installed" not in sys.argv:
    os.environ["PYTHONPATH"] = "."

if "--coverage" in sys.argv:
    tester_options.append("--coverage")

if "--log" in sys.argv:
    tester_options.append("--log")

files = glob.glob(os.path.join(root, "test_*.py"))
files.sort()

success = failure = 0
include = [x for x in sys.argv[1:] if x[:2] != "--"]
skipped = []

python_options = " ".join(python_options)
tester_options = " ".join(tester_options)

ignore_re = re.compile('^ignore: (.*)$', re.MULTILINE)

for file in files:
    test, ext = os.path.splitext(os.path.basename(file))
    if include and test not in include:
        continue
    print("running", test, "...")
    # 2>&1 works on unix and on modern windowses.  we might care about
    # very old Python versions, but not ancient microsoft products :-)
    out = os.popen("%s %s -u %s %s 2>&1" % (
            sys.executable, python_options, file, tester_options
            ))
    result = out.read()

    # Extract any ignore patterns
    ignore_pats = ignore_re.findall(result)
    result = ignore_re.sub('', result)

    try:
        def fix_re(p):
            if not p.startswith('^'):
                p = '^' + p
            if not p.endswith('$'):
                p = p + '$'
            return p
        
        ignore_res = [re.compile(fix_re(p), re.MULTILINE) for p in ignore_pats]
    except:
        print('(bad ignore patterns %r)' % ignore_pats)
        ignore_res = []

    for r in ignore_res:
        result = r.sub('', result)

    result = result.strip()
    
    if result == "ok":
        result = None
    elif result == "skip":
        print("---", "skipped") # FIXME: driver should include a reason
        skipped.append(test)
        continue
    elif not result:
        result = "(no output)"
    status = out.close()
    if status or result:
        if status:
            print("=== error", status)
        if result:
            if result[-3:] == "\nok":
                # if there's an ok at the end, it's not really ok
                result = result[:-3]
            print(result)
        failure = failure + 1
    else:
        success = success + 1

print("-"*68)

temp_root = os.path.join(tempfile.gettempdir(), 'pillow-tests')
tempfiles = glob.glob(os.path.join(temp_root, "temp_*"))
if tempfiles:
    print("===", "remaining temporary files")
    for file in tempfiles:
        print(file)
    print("-"*68)

def tests(n):
    if n == 1:
        return "1 test"
    else:
        return "%d tests" % n

if skipped:
    print("---", tests(len(skipped)), "skipped.")
    print(skipped)
if failure:
    print("***", tests(failure), "of", (success + failure), "failed.")
    sys.exit(1)
else:
    print(tests(success), "passed.")
