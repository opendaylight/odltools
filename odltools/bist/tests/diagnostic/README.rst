Intro
=====

Default diagnostics for ODL BIST should be created in this folder.

The DOCSTRINGS are important as they will provide a nicer output that will be
easier to understand, they should therefore be always added to the class and
tests. They should be a one line summary of what is being checked.


Example
=======

::

    import unittest

    from odltools.bist.diagnostics import Diagnostic


    class DiagnosticTest(Diagnostic):
        """DIAGNOSTICS"""

            def test_succeed(self):
                """A succeeding test"""
                pass

            @unittest.expectedFailure
            def test_fail(self):
                """A failing test"""

                self.fail('I was forced to fail')
