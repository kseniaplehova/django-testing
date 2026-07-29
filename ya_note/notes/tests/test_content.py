from .common import CommonTestCase
from ..forms import NoteForm


class TestNotesListPage(CommonTestCase):
    def test_notes_list_in_context(self):
        response = self.author_client.get(self.list_url)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertEqual(object_list.count(), 1)
        note = object_list[0]
        self.assertEqual(note, self.note)

    def test_notes_list_only_author_notes(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context["object_list"]
        for note in object_list:
            with self.subTest(note=note):
                self.assertEqual(note.author, self.author)

    def test_author_note_not_in_reader_list(self):
        response = self.reader_client.get(self.list_url)
        object_list = response.context["object_list"]
        self.assertNotIn(self.note, object_list)


class TestAddEditPage(CommonTestCase):
    def test_add_edit_pages_contain_form(self):
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context.get("form"), NoteForm)
