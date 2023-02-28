from io import StringIO
from contextlib import redirect_stdout
from django.test import TestCase
from django.core.management import call_command


class TestLoadSample(TestCase):
    def test_command_output(self):
        out = StringIO()
        command = "load_sample"
        with out, redirect_stdout(out):
            call_command(command, stdout=out)
            expected = (
                "Created menu item for Clothing\n"
                "Created menu item for Men's\n"
                "Created menu item for Women's\n"
                "Created menu item for Suits\n"
                "Created menu item for Slacks\n"
                "Created menu item for Jackets\n"
                "Created menu item for Dresses\n"
                "Created menu item for Skirts\n"
                "Created menu item for Blouses\n"
                "Created menu item for Evening Gowns\n"
                "Created menu item for Sun Dresses\n"
            )
            self.assertIn(expected, out.getvalue())
