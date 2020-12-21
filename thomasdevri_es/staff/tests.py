import os
import shutil
from io import StringIO
from pathlib import Path
from unittest.mock import mock_open
from tempfile import TemporaryDirectory


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client

class TestLoginView(TestCase):

    def setUp(self):
        self.username = 'thisisatestusernamethatislong'
        self.password = 'fdsahifhsaudfireua9eaighueaar3ww2w'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=True,
        )
        self.client = Client()

    def test_login_view_get_request(self):
        self.client.get(reverse('staff_login'))

    def test_staff_login_view_empty_post_request(self):
        self.client.post(reverse('staff_login'))

    def test_staff_login_view_authenticates_user(self):
        response = self.client.post(
            reverse('staff_login'),
            {
                'username': self.username,
                'password': self.password,
            }
        )
        self.assertRedirects(response, reverse('dashboard'))


class TestRenderMarkdown(TestCase):

    def setUp(self):
        self.testdir__obj = TemporaryDirectory()
        self.testdir = Path(self.testdir__obj.name)
        self.appdir = Path(self.testdir, 'staff')
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
            Path(i) for i in [
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

    def test_command_generates_expected_html_for_a_single_path(self):
        with self.settings(BASE_DIR=self.testdir):
            call_command('rendermarkdown')
        with open(Path(self.appdir, 'templates', 'a', 'a1.html'), 'r') as htmlf:
            generated_html = htmlf.read()
        # print(self.expected_html)
        # print(generated_html)
        self.assertEqual(self.expected_html, generated_html)

    def test_command_generates_all_expected_html(self):
        """
        Iterate over self.mock_markdown_paths and make sure that all
        of the  expected html is generated.
        """
        raise NotImplementedError


    def test_naming_conflict_causes_exception(self):
        """
        If a template is already in the templates folder with the target file
        name of the markdown currently being rendered, it should only
        be overwritten if it appears to be a previously generated markdown file.

        Otherwise, an exception will be raised to avoid overwriting genuine
        templates.
        """
        raise NotImplementedError
