'''
Called by the debugger in Visual Studio Code
'''

import sys
import re
from flask.cli import main

# remove the file extension if its 'exe' or 'pyw'
sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
sys.exit(main())
