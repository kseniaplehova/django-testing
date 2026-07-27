from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesListPage(TestCase):

    NOTES_LIST_URL = reverse("notes:list")

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор Заметок")
        for index in range(3):
            Note.objects.create(
                title=f"Заметка {index}",
                text=f"Текст заметки {index}.",
                slug=f"note-{index}",
                author=cls.author,
            )

    def test_notes_list_in_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertEqual(object_list.count(), 3)

    def test_notes_list_only_author_notes(self):
        another_user = User.objects.create(username="Другой Автор")
        Note.objects.create(
            title="Чужая заметка",
            text="Чужой текст",
            slug="foreign-note",
            author=another_user,
        )
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context["object_list"]
        for note in object_list:
            with self.subTest(note=note):
                self.assertEqual(note.author, self.author)


class TestAddEditPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор Заметки")
        cls.note = Note.objects.create(
            title="Тестовая заметка",
            text="Текст для теста.",
            slug="test-note",
            author=cls.author,
        )
        cls.add_url = reverse("notes:add")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))

    def test_add_page_contains_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)

    def test_edit_page_contains_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)
