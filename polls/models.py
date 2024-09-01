import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin


# class Question(models.Model):
#     """
#     Represents a poll question.
#
#     Attributes:
#         question_text (str): The text of the question.
#         pub_date (datetime): The date and time the question was published.
#     """
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField("date published")
#
#     def __str__(self):
#         return self.question_text
#
#     @admin.display(
#         boolean=True,
#         ordering="pub_date",
#         description="Published recently?",
#     )
#     def was_published_recently(self):
#         """
#         Checks if the question was published within the last day.
#
#         Returns:
#             bool: True if the question was published within the last day,
#                   False otherwise.
#         """
#         now = timezone.now()
#         return now - datetime.timedelta(days=1) <= self.pub_date <= now


from django.db import models
from django.utils import timezone
from datetime import timedelta

class Question(models.Model):
    """
    Represents a poll question.

    Attributes:
        question_text (str): The text of the question.
        pub_date (datetime): The date and time the question was published.
        end_date (datetime, optional): The date and time when voting ends.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField("date ending", null=True, blank=True)

    def __str__(self):
        return self.question_text

    def is_published(self):
        """
        Returns True if the current local date-time is on or after the question’s publication date.
        """
        now = timezone.localtime()  # Get the current local date-time
        return now >= self.pub_date

    def can_vote(self):
        """
        Returns True if the current local date-time is between pub_date and end_date.
        If end_date is null, then voting is allowed anytime after pub_date.
        """
        now = timezone.localtime()  # Get the current local date-time
        if self.end_date:
            return self.pub_date <= now <= self.end_date
        return now >= self.pub_date

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        """
        Checks if the question was published within the last day.

        Returns:
            bool: True if the question was published within the last day,
                  False otherwise.
        """
        now = timezone.now()
        return now - timedelta(days=1) <= self.pub_date <= now



class Choice(models.Model):
    """
    Represents a choice for a poll question.

    Attributes:
        question (Question): The question this choice is related to.
        choice_text (str): The text of the choice.
        votes (int): The number of votes this choice has received.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text