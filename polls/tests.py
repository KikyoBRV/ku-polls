import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Choice
from mysite import settings


class QuestionModelTests(TestCase):
    """Test suite for the Question model."""

    def test_is_published_with_future_question(self):
        """is_published() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """is_published() returns True for questions whose pub_date is the current date and time."""
        time = timezone.now()
        default_question = Question(pub_date=time)
        self.assertIs(default_question.is_published(), True)

    def test_is_published_with_past_question(self):
        """is_published() returns True for questions whose pub_date is in the past."""
        time = timezone.now() - datetime.timedelta(days=30)
        past_question = Question(pub_date=time)
        self.assertIs(past_question.is_published(), True)

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions whose pub_date is within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_can_vote_with_no_end_date(self):
        """Voting is allowed if the end_date is None (null) and the current date is after the pub_date."""
        pub_date = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_date, end_date=None)
        self.assertTrue(question.can_vote())

    def test_can_vote_with_end_date_in_future(self):
        """Voting is allowed if the end_date is in the future and the current date is after the pub_date."""
        pub_date = timezone.now() - datetime.timedelta(days=1)
        end_date = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=pub_date, end_date=end_date)
        self.assertTrue(question.can_vote())

    def test_cannot_vote_before_pub_date(self):
        """Voting is not allowed if the current date is before the pub_date."""
        pub_date = timezone.now() + datetime.timedelta(days=1)
        question = Question(pub_date=pub_date, end_date=None)
        self.assertFalse(question.can_vote())

    def test_cannot_vote_after_end_date(self):
        """Voting is not allowed if the current date is after the end_date."""
        pub_date = timezone.now() - datetime.timedelta(days=10)
        end_date = timezone.now() - datetime.timedelta(days=1)
        question = Question(pub_date=pub_date, end_date=end_date)
        self.assertFalse(question.can_vote())


def create_question(question_text, days):
    """Create a question with the given `question_text` and published the given number of `days` offset to now."""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """Test suite for the index view of the polls app."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertListEqual(list(response.context["latest_question_list"]), [])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertListEqual(list(response.context["latest_question_list"]), [question])

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertListEqual(list(response.context["latest_question_list"]), [])

    def test_future_question_and_past_question(self):
        """Even if both past and future questions exist, only past questions are displayed."""
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertListEqual(list(response.context["latest_question_list"]), [question])

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertListEqual(list(response.context["latest_question_list"]), [question2, question1])


class QuestionDetailViewTests(TestCase):
    """Test suite for the detail view of the polls app."""

    def test_future_question(self):
        """The detail view of a question with a pub_date in the future redirects to the index page."""
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Check for redirect status code
        self.assertRedirects(response, reverse('polls:index'))  # Check redirection

    def test_past_question(self):
        """The detail view of a question with a pub_date in the past displays the question's text."""
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class UserAuthTest(TestCase):
    """Test suite for user authentication in the polls app."""

    def setUp(self):
        """Set up test data for authentication tests."""
        # Create a test user
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # Create a poll question and choices
        q = Question.objects.create(question_text="First Poll Question", pub_date=timezone.now())
        for n in range(1, 4):
            Choice.objects.create(choice_text=f"Choice {n}", question=q)
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url."""
        logout_url = reverse("logout")
        # Authenticate the user
        self.client.login(username=self.username, password=self.password)
        # Visit the logout page
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)
        # Can login using a POST request
        form_data = {"username": self.username, "password": self.password}
        response = self.client.post(login_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        self.assertEqual(response.status_code, 302)  # Redirect to login for unauthenticated user

    def test_authenticated_user_can_vote(self):
        """An authenticated user can submit a vote."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        form_data = {"choice": f"{choice.id}"}
        # Authenticate the user
        self.client.login(username=self.username, password=self.password)
        # Submit a vote
        response = self.client.post(vote_url, form_data)
        # Should redirect to the results page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:results', args=[self.question.id]))

    def test_login_required_for_vote(self):
        """Redirect to login page when trying to vote without authentication."""
        vote_url = reverse('polls:vote', args=[self.question.id])
        response = self.client.get(vote_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={vote_url}")
