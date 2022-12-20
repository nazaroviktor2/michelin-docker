import datetime
import json
import logging
import os
import tempfile

from zipfile import ZipFile
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from card.scripts.add_accent import plus_to_accent
from card.forms import AddCardForm
from card.models import Card, Audio, Video, Report
from card.permissions import IsEditorOrStaffAndAuth, IsOwnerOrStaff
from card.scripts.bold_func import stars_to_highlight
from card.scripts.from_csv import from_csv
from card.scripts.reading_speed import reading_speed
from card.serializers import CardSerializer, AudioSerializer
from michelinDictator.settings import MEDIA_ROOT, SEPARATOR_CSV, CARD_ON_PAGE

# Create your views here.

my_logger = logging.getLogger("michelin")
class CardViewSet(ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsEditorOrStaffAndAuth]
    filterset_fields = ['id', "user", "name"]

    class Meta:
        ordering = ['id']
    def perform_create(self, serializer):
        serializer.validated_data["user"] = self.request.user
        serializer.save()


class AudioViewSet(ModelViewSet):
    queryset = Audio.objects.all()
    serializer_class = AudioSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsOwnerOrStaff]

    filterset_fields = ['id', "user", "card"]

    class Meta:
        ordering = ['id']
    def perform_create(self, serializer):
        serializer.validated_data["user"] = self.request.user
        serializer.save()


def not_found_page(request,exception):
    return render(request,"not_found.html",status=404)

def home_page(request):
    cards = Card.objects.all().order_by('id')
    page_num = request.GET.get('page', 1)
    paginator = Paginator(cards, CARD_ON_PAGE)

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, deliver the last page
        page_obj = paginator.page(paginator.num_pages)
    nums = "a" * page_obj.paginator.num_pages
    return render(request, "index.html", {"cards": page_obj, "nums":nums})


def card_page(request):
    card_id = request.GET.get("id")
    status = request.GET.get("status")
    if status == "next":
        ids = Card.objects.filter(id__gt=card_id).values_list('id')
        if len(ids)!= 0:
            card_id = ids[0][0]
            return redirect(reverse('card') + '?id={0}'.format(card_id))
        else:
            ids = Card.objects.filter(id__lt=card_id).values_list('id').order_by('id')
            if len(ids) != 0:
                card_id = ids[0][0]
                return redirect(reverse('card') + '?id={0}'.format(card_id))
    elif status == "last":
        ids = Card.objects.filter(id__lt=card_id).values_list('id').order_by('-id')
        if len(ids) != 0:
            card_id = ids[0][0]
            return redirect(reverse('card')+ '?id={0}'.format(card_id))
        else:
            # если таких карт нет
            ids = Card.objects.filter(id__gt=card_id).values_list('id')
            if len(ids) != 0:
                card_id = ids.last()[0]
                return redirect(reverse('card') + '?id={0}'.format(card_id))

    card = get_object_or_404(Card, id=card_id)

    if  card == Card.objects.none():
        return redirect("not_found")
    if request.user.is_authenticated:
        audio = Audio.objects.filter(card=Card.objects.get(id=card_id), user=request.user)
        video = Video.objects.filter(card=Card.objects.get(id=card_id), user=request.user)
        if request.method == "POST":
            now = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            name = request.headers.get("Name")
            if name == "audio":
                duration = request.headers.get("Audio-Time")
                if audio.exists():
                    audio.delete()

                overwrites = request.headers.get("Overwrites")
                audio_file = ContentFile(request.body, name="{0}_audio.wav".format(now))
                audio = Audio.objects.create(file_path=audio_file, card=Card.objects.get(id=card_id), user=request.user,
                                                 duration=duration)
                audio.save()
                my_logger.info("user with id:{0} added audio for card with id:{1} number of overwrites:{2} file_path: {3}".format(
                    request.user.id, card_id,overwrites, audio.file_path.path ))
            elif name == "Video":
                if video.exists():
                    video.delete()
                overwrites = request.headers.get("Overwrites")
                video_file = ContentFile(request.body, name="{0}_video.mp4".format(now))
                video = Video.objects.create(file_path = video_file,card=Card.objects.get(id=card_id), user=request.user)
                video.save()
                my_logger.info(
                        "user with id:{0} added video for card with id:{1} number of overwrites:{2} file_path: {3}".format(
                            request.user.id, card_id, overwrites, video.file_path.path))
            elif name == "Report":
                text = (json.loads(request.body)).get("text")
                report = Report.objects.create(text = text,card=Card.objects.get(id=card_id), user=request.user)
                report.save()
                my_logger.info(
                    "user with id: {0} complained about the card with id: {1} report id: {2}".format(request.user.id, card_id,
                                                                                              report.id))



        return render(request, "card.html", {"card": card,
                                             "audios": Audio.objects.filter(card=Card.objects.get(id=card_id),
                                                                            user=request.user),
                                             "videos": Video.objects.filter(card=Card.objects.get(id=card_id),
                                                                            user=request.user)
                                             })
    else:
        return render(request, "card.html", {"card": card,
                                             "audios": None,
                                             "videos": None,
                                             })


def add_card(request):

    if request.method == "POST":
        form = AddCardForm(request.POST)
        card = form.save(commit=False)
        card.user = request.user
        text = request.POST.get("text")
        instruction = request.POST.get("instruction")
        time_speed = request.POST.get("time_speed")
        error = request.POST.get("error")
        hours, minute, second = map(int,error.split(":"))
        time_min, time_max = reading_speed(text,
                                           average_error=datetime.timedelta(hours=hours,minutes=minute,seconds=second),
                                           average_speed=int(time_speed))
        if request.POST.get("accent"):
            text = plus_to_accent(text)
            instruction = plus_to_accent(instruction)

        if request.POST.get("highlight"):
            text = stars_to_highlight(text)
            instruction = stars_to_highlight(instruction)

        card.text = text
        card.instruction = instruction
        card.duration_min = time_min
        card.duration_max = time_max

        if form.is_valid():
            card.save()
            my_logger.info(
                "user with id: {0} create a card with id: {1}".format(request.user, card.id))

            return render(request, "successful.html", {"text": "Карта для озвучивания создана"})
    return render(request, "add_card.html")

def add_card_file(request):
    if  request.method == "POST":

        file = request.FILES.get("file")
        if str(file).endswith(".json"):
            pass
        elif str(file).endswith(".csv"):

            accent = request.POST.get("accent")
            error = request.POST.get("error")
            hours, minute, second = map(int, error.split(":"))
            time_speed = request.POST.get("time_speed")
            cards_file = from_csv(file, SEPARATOR_CSV)
            for card_file in cards_file:
                if  len(card_file) ==3 :
                     name, text, instruction = card_file

                elif len(card_file) ==2 :
                        name, text = card_file
                        instruction = ""
                else:
                    my_logger.info(
                        "user with id: {0} unsuccessfully tried to create a card".format(request.user))
                    continue
                
               
                if accent:
                    text = plus_to_accent(text)
                    name = plus_to_accent(name)
                    instruction = plus_to_accent(instruction)

                form = AddCardForm({"name":name,"text":text,"instruction":instruction})
                card = form.save(commit=False)
                time_min, time_max = reading_speed(text,
                                                   average_error=datetime.timedelta(hours=hours, minutes=minute,
                                                                                    seconds=second),
                                                   average_speed=int(time_speed))

                card.duration_min = time_min
                card.duration_max = time_max
                card.user = request.user
                if form.is_valid():
                    card.save()
                    my_logger.info(
                        "user with id: {0} create a card with id: {1}".format(request.user, card.id))
                else:
                    my_logger.info(
                        "user with id: {0} unsuccessfully tried to create a card".format(request.user))

        
        return render(request, "successful.html", {"text": "Карты для озвучивания созданы"})
    return render(request, "add_card_from_file.html")

def my_cards(request):
    if  request.method == "POST":
        name = request.headers.get("Name")
        if name == "Delete":
            id = int(request.body)

            card = Card.objects.get(id=id)
            card.delete()
            return redirect("my_cards")
    else:
        user = request.user
        cards = Card.objects.filter(user=user).order_by('id')
        page_num = request.GET.get('page', 1)
        paginator = Paginator(cards, CARD_ON_PAGE)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
        nums = "a" * page_obj.paginator.num_pages

        return render(request, "my_cards.html", {"cards": page_obj, "nums":nums})


def my_audios(request):
    user = request.user
    card_id = [audio.card.id for audio in Audio.objects.filter(user=user).order_by('id')]

    res = []
    for id in card_id:
        res.append(Card.objects.get(id=id))
    page_num = request.GET.get('page', 1)
    paginator = Paginator(res, CARD_ON_PAGE)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, deliver the last page
        page_obj = paginator.page(paginator.num_pages)

    # return render(request, "index.html", {"cards": page_obj})
    nums = "a" * page_obj.paginator.num_pages
    return render(request, "my_audios.html", {"cards": page_obj, "nums":nums})


def user_card(request):
    id = (request.GET.get("id"))

    if request.method == "POST":
        name = request.POST.get("name")
        if name == "delete":
            card = Card.objects.get(id=id)
            card.delete()
            return redirect("my_cards")
        elif name == "download":
           pass

        elif name == "doit":
            audios_id = request.POST.getlist("audio")
            card_adm = request.POST.get("card_adm")
            if card_adm == "delete":
   
                for audio_id in audios_id:
                    Audio.objects.filter(id=audio_id).delete()

            elif card_adm == "download":
                if len(audios_id) != 0:

                    file_name = "{0}_audio_{1}-{2}.zip".format(id,audios_id[0],audios_id[-1])

                    tmpdir = tempfile.mkdtemp()
                    zip_fn = os.path.join(tmpdir, file_name)
                    zip_file = ZipFile(zip_fn, 'w')


                    for audio_id in audios_id:
                        audio = Audio.objects.get(id=audio_id)
                        path = MEDIA_ROOT + "/" + str(audio.file_path)
                      
                        zip_file.write(path, "{0}.wav".format(audio.id))

                    zip_file.close()
                    return FileResponse((open(zip_fn, "rb")))



    return render(request, "user_card.html", {"card": Card.objects.get(id=id),
                                              "audios": Audio.objects.filter(card=Card.objects.get(id=id))})
