import datetime
import json

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from django.views.generic import CreateView

from card.models import Audio, Card, Report
from users.forms import RegisterUserForm


# Create your views here.

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('home')


def user_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            name = request.headers.get("Name")
            if name == "Save":
                video =  (json.loads(request.body)).get("video")
                auto_transition =  (json.loads(request.body)).get("auto_transition")
                request.user.allow_auto_transition = auto_transition
                request.user.allow_video = video
                request.user.save()
        user_audio = Audio.objects.filter(user=request.user)
        count_audio = len(user_audio)
        cards_id = [card.id for card in Card.objects.filter(user=request.user)]
        count_report = 0
        audios_time = [audio.duration for audio in user_audio]
        voicing_time = datetime.timedelta()
        all_cards = len(Card.objects.all())
        percent = 0

        if all_cards != 0:

            percent = int(round(count_audio/all_cards*100,1))
            neccessary = int(440 - (440*(0.01*percent)))
        for time in audios_time:
            voicing_time += time
        voicing_time -= datetime.timedelta(microseconds=voicing_time.microseconds)
        for card_id in cards_id:
            count_report += len(Report.objects.filter(card=card_id))
        percent2 = int(440 - (440*(0.01*percent)))
        return render(request, "profile.html", {"count_audio": count_audio, "count_card": len(cards_id),
                                            "count_report": count_report,
                                            "voicing_time":voicing_time,
                                            "all_cards":all_cards,
                                            "percent":percent,
                                            "percent2": percent2})

    else:
        return render(request, "profile.html")


def successful(request):
    return render(request, "successful.html")
