from http import HTTPStatus

from pytils.translit import slugify

from .common import CommonTestCase
from ..models import Note

NOTE_DATA = {
    "title": "Новая заметка",
    "text": "Текст новой заметки",
    "slug": "new-slug",
}
UPDATE_DATA = {
    "title": "Обновлённая заметка",
    "text": "Обновлённый текст",
    "slug": "updated-slug",
}


class TestNoteCreation(CommonTestCase):
    def test_anonymous_user_cant_create_note(self):
        initial_count = Note.objects.count()
        response = self.client.post(self.add_url, data=NOTE_DATA)
        expected_redirect = f"{self.login_url}?next={self.add_url}"
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_can_create_note(self):
        initial_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data=NOTE_DATA)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        new_note = Note.objects.get(slug=NOTE_DATA["slug"])
        self.assertEqual(new_note.title, NOTE_DATA["title"])
        self.assertEqual(new_note.text, NOTE_DATA["text"])
        self.assertEqual(new_note.author, self.author)

    def test_slug_auto_generation(self):
        Note.objects.all().delete()
        data = {"title": "Тестовая заметка", "text": "Текст"}
        response = self.author_client.post(self.add_url, data=data)
        self.assertRedirects(response, self.success_url)
        new_note = Note.objects.get()
        expected_slug = slugify(data["title"])
        self.assertEqual(new_note.slug, expected_slug)

    def test_unique_slug_validation(self):
        Note.objects.all().delete()
        existing_slug = "existing-slug"
        Note.objects.create(
            title="Существующая",
            text="Текст",
            slug=existing_slug,
            author=self.author,
        )
        data = {"title": "Новая", "text": "Текст", "slug": existing_slug}
        response = self.author_client.post(self.add_url, data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertIn("slug", form.errors)
        self.assertTrue(form.errors["slug"])
        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(CommonTestCase):
    def assert_note_unchanged(self, note, original_note):
        self.assertEqual(note.title, original_note.title)
        self.assertEqual(note.text, original_note.text)
        self.assertEqual(note.slug, original_note.slug)
        self.assertEqual(note.author, original_note.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=UPDATE_DATA)
        self.assertRedirects(response, self.success_url)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, UPDATE_DATA["title"])
        self.assertEqual(updated_note.text, UPDATE_DATA["text"])
        self.assertEqual(updated_note.slug, UPDATE_DATA["slug"])
        self.assertEqual(updated_note.author, self.note.author)

    def test_user_cant_edit_foreign_note(self):
        response = self.reader_client.post(self.edit_url, data=UPDATE_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        stored_note = Note.objects.get(pk=self.note.pk)
        self.assert_note_unchanged(stored_note, self.note)

    def test_author_can_delete_note(self):
        initial_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), initial_count - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cant_delete_foreign_note(self):
        initial_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_count)
        stored_note = Note.objects.get(pk=self.note.pk)
        self.assert_note_unchanged(stored_note, self.note)
