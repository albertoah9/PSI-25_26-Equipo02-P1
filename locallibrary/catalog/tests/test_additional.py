import datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from catalog.models import Author, Book, BookInstance, Genre, Language

User = get_user_model()


class BookModelAdditionalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Language.objects.create(name="English")
        cls.author = Author.objects.create(first_name="A", last_name="B")

        cls.g1 = Genre.objects.create(name="G1")
        cls.g2 = Genre.objects.create(name="G2")
        cls.g3 = Genre.objects.create(name="G3")
        cls.g4 = Genre.objects.create(name="G4")

        cls.book = Book.objects.create(
            title="Book Title",
            summary="Summary",
            isbn="1234567890123",
            author=cls.author,
            language=cls.lang,
        )
        cls.book.genre.set([cls.g1, cls.g2, cls.g3, cls.g4])

    def test_display_genre_returns_first_three(self):
        self.assertEqual(self.book.display_genre(), "G1, G2, G3")


class BookInstanceModelAdditionalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lang = Language.objects.create(name="English")
        cls.author = Author.objects.create(first_name="A", last_name="B")
        cls.book = Book.objects.create(
            title="Book Title",
            summary="Summary",
            isbn="1234567890123",
            author=cls.author,
            language=cls.lang,
        )
        cls.user = User.objects.create_user(username="u1", password="pass")

    def test_is_overdue_true(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        bi = BookInstance.objects.create(
            book=self.book,
            imprint="Imprint",
            due_back=yesterday,
            borrower=self.user,
            status="o",
        )
        self.assertTrue(bi.is_overdue)

    def test_is_overdue_false_future(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        bi = BookInstance.objects.create(
            book=self.book,
            imprint="Imprint",
            due_back=tomorrow,
            borrower=self.user,
            status="o",
        )
        self.assertFalse(bi.is_overdue)

    def test_is_overdue_false_none(self):
        bi = BookInstance.objects.create(
            book=self.book,
            imprint="Imprint",
            due_back=None,
            borrower=self.user,
            status="o",
        )
        self.assertFalse(bi.is_overdue)

class AuthorDeleteAdditionalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="deleter", password="pass")
        perm = Permission.objects.get(codename="delete_author")
        cls.user.user_permissions.add(perm)
        cls.user.save()

        cls.author = Author.objects.create(first_name="A", last_name="B")

    def setUp(self):
        self.client.login(username="deleter", password="pass")

    def test_author_delete_success_redirects(self):
        url = reverse("author-delete", kwargs={"pk": self.author.pk})
        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("authors"))

    def test_author_delete_exception_redirects_back(self):
        url = reverse("author-delete", kwargs={"pk": self.author.pk})

        with patch("catalog.views.Author.delete", side_effect=Exception("fail")):
            resp = self.client.post(url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], url)


class BookDeleteAdditionalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="bookdeleter", password="pass")
        perm = Permission.objects.get(codename="delete_book")
        cls.user.user_permissions.add(perm)
        cls.user.save()

        lang = Language.objects.create(name="English")
        author = Author.objects.create(first_name="A", last_name="B")
        genre = Genre.objects.create(name="Fantasy")

        cls.book = Book.objects.create(
            title="T",
            summary="S",
            isbn="1234567890123",
            author=author,
            language=lang,
        )
        cls.book.genre.add(genre)

    def setUp(self):
        self.client.login(username="bookdeleter", password="pass")

    def test_book_delete_exception_redirects_to_author_delete_path(self):
        url = reverse("book-delete", kwargs={"pk": self.book.pk})

        with patch("catalog.views.Book.delete", side_effect=Exception("fail")):
            resp = self.client.post(url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp["Location"],
            reverse("author-delete", kwargs={"pk": self.book.pk})
        )
