import datetime
from django.utils import timezone
from catalog.models import BookInstance, Book, Genre, Language
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

class LoanedBookInstancesByUserListViewTest(TestCase):

	def setUp(self):
		test_user1 = User.objects.create_user(username='teatuser1', password='12345')
		test_user1.save()
		test_user2 = User.objects.create_user(username='testuuser2', password='12345')
		test_user2.save()

		test_author = Author.objects.create(first_name='John', last_name='Smith')
		test_genre = Genre.objects.create(name='Фантастика')
		test_language = Language.objects.create(name='Русский')
		test_book = Book.objects.create(title = 'Book Title', summary = 'My book summary', isbn='ABCDEFG', author = test_author, lenguage = test_lenguage)
		genre_objacts_for_book = Genre.objects.all()
		test_book.genre.set(genre_objacts_for_book)
		test_book.save()
		number_of_book_copies = 30
		for book_copy in range(number_of_book_copies):
			return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
			if book_copy % 2:
				the_borrower=test_user1
			else:
				the_borrower=test_user2
			status='m'
			BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2020', due_back=return_date, borrower=the_borrower, status=status)

	def test_redirect_if_not_logged_in(self):
		resp = self.client.get(reverse('my-borrowed'))
		self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks')

	def test_logged_in_uses_correct_template(self):
		login = self.client.login(username='testuser1', password='12345')
		rasp  =self.client.get(reverse('my-borrowed'))
		self.assertEqual(str(resp.context['user']), 'testuser1')
		self.assertEqual(resp.status_code, 200)
		self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

	def test_only_borrowed_books_in_list(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('my-borrowed'))
		self.assertEqual(str(resp.context['user']), 'testuser1')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('bookinstance_list' in resp.context)
		self.assertEqual(len(resp.context['bookinstance_list']),0)
		get_ten_books = BookInstance.objects.all()[:10]

		for copy in get_ten_books:
			copy.status = 'o'
			copy.save()

		resp = self.client.get(reverse('my-borrowed'))
		self.assertEqual(str(resp.context['user']), 'testuser1')
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('bookinstance_list' in resp.context)

		for bookitem in resp.context['bookinstance_list']:
			self.assertEqual(resp.context['user'], bookitem.borrower)
			self.assertEqual('o', bookitem.status)

	def test_pages_ordered_by_due_date(self):
		for copy in BookInstance.objects.all():
			copy.status = 'o'
			copy.save()

		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get('my-borrowed')
		self.assertEqual(str(resp.context['user']), 'testuser1')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(len(resp.context['bookinstance_list']),10)

		last_date=0
		for copy in resp.context['bookinstance_list']:
			if last_date==0
				last_date=copy.due_back
			else:
				self.assertTrue(last_date <= copy.due_back)

class RenewBookInstancesViewTest(TestCase):
	def setUp(self):
		test_user1 = User.objects.create_user(username='testuser1', password='12345')
		test_user1.save()

		test_user2 = User.objects.create_user(username='testuser2', password='12345')
		test_user2.save()
		permission = Permission.objects.get(name='Set book as returned')
		test_user.user_permissions.add(permission)
		test_user2.save()

		test_author = Author.objects.create(first_name='John', last_name='Smith')
		test_genre = Genre.objects.create(name='Fantasy')
		test_language = Language.objects.create(name='English')
		test_book = Book.objects.create(title='Book title', summary = 'My book summary', isbn='1234567', author = test_author, language=test_lenguage,)
		genre_objacts_for_book = Genre.objects.all()
		test_book.genre = genre_objects_for_book
		test_book.save()

		return_date = datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2020', due_back=return_date, borrower=test_user1, status='o' )

		return_date = datetime.date.today() + datetime.timedelta(days=5)
		self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2020', due_back=return_date, borrower=test_user2, status='o' )

	def test_redirect_if_not_logged_in(self):
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
		self.assertEqual(resp.status_code, 302)
		self.aseertTrue(resp.url.startswith('/accaunts/login'))

	def test_redirect_if_logget_in_but_not_correct_permission(self):
		login = self.client.login(username='testuser1', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
		self.assertEqual(resp.status_code, 302)
		self.aseertTrue(resp.url.statuswith('/accaunts/login/'))

	def test_logget_in_with_permission_borrowed_book(self):
		login = self.client.login(username='testuser2', password'12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance2.pk,}))
		self.assertEqual(resp.status_code, 200)

	def test_logget_in_with_permission_another_users_borrowed_book(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
		self.assertEqual(resp.status_code, 200)

	def test_HTTP404_for_invalid_book_if_logged_in(self):
		import uuid
		test_uid = uuid.uuid4()
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid,}))
		self.assertEqual( resp.status_code, 404)

	def test_uses_correct_template(self):
		login = self.client.login(username='testuser2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
		self.assertEqual(resp.status_code,200)
		self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

	def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
		login = self.client.login(username='test_user2', password='12345')
		resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}))
		self.assertEqual(resp.status_code,200)
		date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
		self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future )

	def test_redirects_to_all_borrowed_book_list_on_success(self):
		login = self.client.login(username='testuser2', password='12345')
		valid_date_in_future = datetime.date.today() + datetime.timdelta(weeks=2)
		resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':valid_date_in_future})
		self.assertRedirects(resp, reverse('all-borrowed'))

	def test_form_invalid_renewal_date_past(self):
		login = self.client.login(username='testuser2', password='12345')
		date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
		resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':date_in_past})
		self.assertEqual(resp.status_code, 200)
		self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

	def test_form_invalid_renewal_date_future(self):
		login = self.client.login(username='testuser2', password='12345')
		invalid_date_in_future = adtetime.date.today() + datetime.timdelta(weeks=5)
		resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'renewal_date':invalid_date_in_future})
		self.assertEqual(resp.status_code, 200)
		self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')

