from random import choice

from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions (not including those set to be published in the future)."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        question = self.get_object()
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this poll.")
            return HttpResponseRedirect(reverse('polls:index'))
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """Vote for a choice on a question (poll)."""
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        # Redirect to the index page if voting is not allowed
        return HttpResponseRedirect(reverse("polls:index"))

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )

    # Reference to the current user
    this_user = request.user

    # Get the user's vote
    try:
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # user has a vote for this question! Update his choice.
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was updated to '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        # does not have a vote yet
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        # automatically saved
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")



    # selected_choice.votes = F("votes") + 1
    # selected_choice.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
