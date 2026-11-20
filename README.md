# Django testing — YaNews and YaNote

Automated test suites for two Django projects: **ya_news** (news with comments), tested with `pytest`, and **ya_note** (personal notes), tested with Django `TestCase` (unittest).

Educational project — Yandex Practicum, Python Developer course.

## What is covered

**ya_news** — 14 test functions in `news/pytest_tests/` (more cases through parametrization), with shared fixtures in `conftest.py`:
- content: number of news items on the home page, news and comment ordering, comment form shown only to authenticated users;
- logic: anonymous users cannot comment, authors can create, edit and delete their comments, other users cannot change foreign comments, forbidden words are rejected;
- routes: page availability and redirects for anonymous users.

**ya_note** — 14 test methods in `notes/tests/` built on a shared `CommonTestCase`:
- content: notes appear in the list only for their author, add / edit pages contain a form;
- logic: creating, editing and deleting notes with permission checks, automatic slug generation (`pytils`) and slug uniqueness validation;
- routes: page availability and redirects for anonymous users.

## Tech stack

Python, Django 5.1.1, pytest, pytest-django, pytest-lazy-fixture, pytest-subtests, pytils, flake8 (see `requirements.txt`).

## Getting started

```bash
git clone https://github.com/kseniaplehova/django-testing.git
cd django-testing
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash); on Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## Tests

```bash
cd ya_news && pytest        # pytest suite for YaNews
cd ../ya_note && pytest     # unittest-style suite for YaNote, run by pytest
# alternatively: cd ya_note && python manage.py test
```

`run_tests.sh` runs flake8, the structure check and both suites in sequence.

## Author

Ksenia Plehova — [GitHub](https://github.com/kseniaplehova)
