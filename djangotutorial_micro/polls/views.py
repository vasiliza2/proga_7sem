import random
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View, generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User

from .forms import NewUserForm

from .models import Choice, Question
from .forms import QuestionForm


SLOGANS = [
    "Проснись и пой!",
    "Доброе утро, страна",
    "Проснулись - улыбнулись"
]


class PollsBaseView(View):
    slogans = SLOGANS

    def get_slogan(self):
        return random.choice(self.slogans)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slogan'] = self.get_slogan()
        return context


class IndexView(PollsBaseView, generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(PollsBaseView, generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(PollsBaseView, generic.DetailView):
    model = Question
    template_name = "polls/results.html"


class VoteView(PollsBaseView, View):
    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        try:
            selected_choice = question.choice_set.get(pk=request.POST["choice"])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(
                request,
                "polls/detail.html",
                {
                    "slogan": self.get_slogan(),
                    "question": question,
                    "error_message": "You didn't select a choice.",
                },
            )
        else:
            selected_choice.votes += 1
            selected_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


class UserIsStaffMixin(UserPassesTestMixin):
    login_url = "polls:login"
    redirect_field_name = "next"
    raise_exception = False

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        # next_url = self.request.path
        # return redirect(self.login_url, f"{self.redirect_field_name}={next_url}")
        return redirect_to_login(self.request.get_full_path(), self.login_url, self.redirect_field_name)
        # return redirect('{}?{}={}'.format(reverse(self.login_url), self.redirect_field_name, next_url))


class PollNewView(PollsBaseView, UserIsStaffMixin, LoginRequiredMixin, View):
    
    def get(self, request):
        form = QuestionForm()
        return render(
            request,
            'polls/poll_new_edit.html',
            {
                'form': form,
                "slogan": self.get_slogan(),
            }
        )

    def post(self, request):
        form = QuestionForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.save()
            return redirect('polls:detail', pk=poll.pk)
        return render(
            request,
            'polls/poll_new_edit.html',
            {
                'form': form,
                "slogan": self.get_slogan(),
            }
        )

class PollEditView(PollsBaseView, UserIsStaffMixin, LoginRequiredMixin, View):
    
    def get(self, request, pk):
        poll = get_object_or_404(Question, pk=pk)
        form = QuestionForm(instance=poll)
        return render(
            request, 'polls/poll_new_edit.html', {
                "slogan": self.get_slogan(),
                'form': form
            }
        )

    def post(self, request, pk):
        poll = get_object_or_404(Question, pk=pk)
        form = QuestionForm(request.POST, instance=poll)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.pub_date = timezone.now()
            poll.save()
            return redirect('polls:detail', pk=poll.pk)
        return render(
            request, 'polls/poll_new_edit.html', {
                "slogan": self.get_slogan(),
                'form': form
            }
        )


class LoginView(PollsBaseView, View):
    logger = logging.getLogger(__name__)
    
    def get(self, request):
        form = AuthenticationForm()
        return render(request=request, template_name="polls/login.html", context={"login_form": form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                next_url = self.request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('polls:index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
        
        slogan = self.get_slogan()
        # logger.warning(f"Slogan {slogan}.")
        return render(
            request=request,
            template_name="polls/login.html",
            context={
                "slogan": slogan,
                "login_form": form
            }
        )


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have successfully logged out.")
        return redirect("polls:index")


class AccountRegisterView(View):
    form_class = NewUserForm
    template_name = "polls/register.html"

    def get(self, request):
        form = self.form_class()
        return render(request=request, template_name=self.template_name, context={"register_form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(request)
            messages.success(request, f"Registration successful. Please go to your '{user.email}' e-mail inbox messages to activate the account.")
            return redirect("polls:index")

        messages.error(request, "Unsuccessful registration. Invalid information.")
        return render(request=request, template_name=self.template_name, context={"register_form": form})


class AccountActivationView(View):
    def get(self, request, uidb64, token):
        # messages.error(request, f"uidb64 = {uidb64}, token = {token}")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            # messages.error(request, f"uid = {uid}")
            user = User.objects.get(pk=uid)
            # messages.error(request, f"user = {user}")
        except:
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'polls/account_activation_success.html')
        else:
            return render(request, 'polls/account_activation_failure.html')

def search_polls(request):
    return render(request, 'polls/search_polls.html')
# def login_request(request):
# 	if request.method == "POST":
# 		form = AuthenticationForm(request, data=request.POST)
# 		if form.is_valid():
# 			username = form.cleaned_data.get('username')
# 			password = form.cleaned_data.get('password')
# 			user = authenticate(username=username, password=password)
# 			if user is not None:
# 				login(request, user)
# 				messages.info(request, f"You are now logged in as {username}.")
# 				return redirect("polls:index")
# 			else:
# 				messages.error(request,"Invalid username or password.")
# 		else:
# 			messages.error(request,"Invalid username or password.")
# 	form = AuthenticationForm()
# 	return render(request=request, template_name="polls/login.html", context={"login_form": form})


# def logout_request(request):
# 	logout(request)
# 	messages.info(request, "You have successfully logged out.") 
# 	return redirect("polls:index")

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST["choice"])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(
#             request,
#             "polls/detail.html",
#             {
#                 "question": question,
#                 "error_message": "You didn't select a choice.",
#             },
#         )
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

