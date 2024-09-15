import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question, Vote


logger = logging.getLogger('polls')


class IndexView(generic.ListView):
    """View for displaying a list of the most recent questions."""

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions (not including those set to be published in the future)."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """View for displaying a specific question's details."""

    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        """Add the user's vote to the context if authenticated."""
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        if self.request.user.is_authenticated:
            try:
                vote = Vote.objects.get(user=self.request.user, choice__question=question)
                context['selected_choice'] = vote.choice.id
            except Vote.DoesNotExist:
                context['selected_choice'] = None

        return context

    def get(self, request, *args, **kwargs):
        """Redirect to the index page if the question is closed or does not exist."""
        question = get_object_or_404(Question, pk=self.kwargs['pk'])
        if not question.can_vote():
            return HttpResponseRedirect(reverse('polls:index'))

        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """View for displaying the results of a specific question."""

    model = Question
    template_name = "polls/results.html"


def signup(request):
    """Handle user signups and log the user in upon successful registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def vote(request, question_id):
    """Handle voting for a choice on a question."""
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        return HttpResponseRedirect(reverse("polls:index"))

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )

    this_user = request.user

    try:
        vote = Vote.objects.get(user=this_user, choice__question=question)
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was updated to '{selected_choice.choice_text}'")
        logger.info(f'User {this_user.username} updated their vote to "{selected_choice.choice_text}" '
                    f'for question "{question.question_text}".')
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")
        logger.info(f'User {this_user.username} voted for "{selected_choice.choice_text}" '
                    f'for question "{question.question_text}".')

    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
