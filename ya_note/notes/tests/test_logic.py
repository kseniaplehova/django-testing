from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = "Заголовок заметки"
    NOTE_TEXT = "Текст заметки"

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse("notes:add")
        cls.success_url = reverse("notes:success")
        cls.user = User.objects.create(username="Мимо Крокодил")
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            "title": cls.NOTE_TITLE,
            "text": cls.NOTE_TEXT,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_create_note_with_slug(self):
        form_data = {
            "title": "Заголовок",
            "text": "Текст",
            "slug": "my-custom-slug",
        }
        response = self.auth_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, "my-custom-slug")

    def test_unique_slug_validation(self):
        Note.objects.create(
            title="Первая заметка",
            text="Текст",
            slug="unique-slug",
            author=self.user,
        )
        form_data = {
            "title": "Вторая заметка",
            "text": "Текст",
            "slug": "unique-slug",
        }
        response = self.auth_client.post(self.add_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertIn("slug", form.errors)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_auto_generation(self):
        form_data = {
            "title": "Тестовая заметка",
            "text": "Текст",
        }
        response = self.auth_client.post(self.add_url, data=form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertIsNotNone(new_note.slug)
        self.assertNotEqual(new_note.slug, "")


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = "Заголовок заметки"
    NOTE_TEXT = "Текст заметки"
    NEW_NOTE_TITLE = "Обновлённый заголовок"
    NEW_NOTE_TEXT = "Обновлённый текст"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор заметки")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug="test-slug",
            author=cls.author,
        )
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))
        cls.success_url = reverse("notes:success")
        cls.form_data = {
            "title": cls.NEW_NOTE_TITLE,
            "text": cls.NEW_NOTE_TEXT,
            "slug": cls.note.slug,
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
