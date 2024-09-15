import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question, Vote


logger = logging.getLogger('polls')

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    logger.info(f'User {user.username} logged in from IP {get_client_ip(request)}.')

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    logger.info(f'User {user.username} logged out from IP {get_client_ip(request)}.')

@receiver(user_login_failed)
def user_logged_in_fail_handler(sender, request, **kwargs):
    logger.warning(f' Failed login from IP {get_client_ip(request)}.')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        # Get the user's vote for this question if it exists
        if self.request.user.is_authenticated:
            try:
                vote = Vote.objects.get(user=self.request.user, choice__question=question)
                context['selected_choice'] = vote.choice.id
            except Vote.DoesNotExist:
                context['selected_choice'] = None

        return context

    def get(self, request, *args, **kwargs):
        # Check if the question exists and if it's a future question
        try:
            question = get_object_or_404(Question, pk=self.kwargs['pk'])
            if question.pub_date > timezone.now():
                # Redirect to the index page if the question is from the future
                return HttpResponseRedirect(reverse('polls:index'))
        except Http404:
            # Redirect to the index page if the question does not exist
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
        logger.info(f'User {this_user.username} updated their vote to "{selected_choice.choice_text}" for question "{question.question_text}".')
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        messages.success(request, f"You voted for '{selected_choice.choice_text}'")
        logger.info(f'User {this_user.username} voted for "{selected_choice.choice_text}" for question "{question.question_text}".')

    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
