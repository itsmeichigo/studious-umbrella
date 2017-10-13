#!/usr/bin/env python3.6
import coverage
COV = coverage.coverage(branch=True, include='app/*')
COV.start()

import unittest
from tests import suite
unittest.TextTestRunner(verbosity=2).run(suite)

COV.stop()
COV.report()
