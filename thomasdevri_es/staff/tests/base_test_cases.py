from tempfile import TemporaryDirectory
from pathlib import Path
import os


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client


class BaseMarkdownFilesystemTest(TestCase):
    """
    Generate a temporary directory full of markdown files with an expected
    html result for testing workflows involving markdown files in the
    filesystem.
    """

    def setUp(self):
        super().setUp()
        self.testdir__obj = TemporaryDirectory()
        self.testdir = Path(self.testdir__obj.name)
        self.appdir = Path(self.testdir, 'staff')
        self.markdown_root = Path(self.appdir, 'markdown')
        os.mkdir(self.appdir)
        self.mock_markdown = (
            "# Hello World!\n\n> This is a test of the markdown build process."
            "\n\n- Hierarchal\n    - List\n    - Goes\n        - Here\n\n"
            "## Hopefully\n\n### It\n\n`works!`\n\n```\nprint('hello world!')\n```\n"
        )
        self.expected_html = (
            '{% comment AUTOMATICALLY GENERATED by "manage.py rendermarkdown" %}\n'
            '{% comment Do not edit this file. Edit it\'s markdown source at '
            f'{Path(self.appdir, "markdown", "a", "a1.md")} %}}\n'
            '{% comment Because this is now a template, you can use it simply '
            'with {% include \\\'this\\\' %} %}\n<div class="staff__markdown">\n'
            '<h1>Hello World!</h1>\n<blockquote>\n'
            '<p>This is a test of the markdown build process.</p>\n'
            '</blockquote>\n<ul>\n<li>Hierarchal<ul>\n<li>List</li>\n'
            '<li>Goes<ul>\n<li>Here</li>\n</ul>\n</li>\n</ul>\n</li>\n</ul>'
            '\n<h2>Hopefully</h2>\n<h3>It</h3>\n<p><code>works!</code></p>\n'
            '<p><code>print(\'hello world!\')</code></p>\n</div>'
        )
        self.mock_markdown_paths = [
            Path(self.markdown_root, i) for i in [
                'root.md',
                'a/a1.md',
                'a/a2.md',
                'a/a3.md',
                'b/b/b1.md',
                'b/b/b2.md',
                'b/b/b3.md',
                'c/c/c/c1.md',
                'c/c/c/c2.md',
                'c/c/c/c3.md',
            ]
        ]
        for fl in self.mock_markdown_paths:
            dir_ = Path(self.appdir, 'markdown', fl.parent)
            if not os.path.exists(dir_):
                os.makedirs(dir_)
            with open(Path(self.appdir, 'markdown', fl), 'w') as fl:
                fl.write(self.mock_markdown)

    def tearDown(self):
        self.testdir__obj.cleanup()


class BaseTestWithStaffUser(TestCase):

    def setUp(self):
        super().setUp()
        self.username = 'thisisatestusernamethatislong'
        self.password = 'fdsahifhsaudfireua9eaighueaar3ww2w'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=True,
        )
        self.client = Client()
        self.client.post(
            reverse('staff_login'),
            {
                'username': self.username,
                'password': self.password,
            }
        )
