from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render
from mud.models import Player, PlayerMessage
import logging

logger = logging.getLogger(__name__)


########################################################################
def home(request):
    return render(request, "mud/index.html")


########################################################################
@login_required
def player_login(request):
    context = {"players": Player.objects.filter(user=request.user)}
    return render(request, "mud/player_login.html", context)


########################################################################
@login_required
def game(request, player_id):
    context = {"player_id": player_id}
    player = Player.objects.get(id=player_id)
    player.get_handler_module().enter(player)
    return render(request, "mud/game.html", context)


########################################################################
@login_required
def get_messages(request):
    logger.debug("get_messages called")
    if request.method != "POST":
        return HttpResponseForbidden()
    print "GET:", request.POST
    player_id = int(request.POST["player_id"])
    player = Player.objects.filter(user=request.user, id=player_id).first()
    print "player:", player
    query_set = PlayerMessage.objects.filter(player=player)
    messages = [m.text for m in query_set.order_by("created")]
    query_set.delete()
    output = {"hit_points": player.hit_points,
              "max_hit_points": player.max_hit_points,
              "messages": messages}
    return JsonResponse(output)


########################################################################
@login_required
def submit_command(request):
    logger.info("submit_command called")
    if request.method != "POST":
        return HttpResponseForbidden()
    player_id = int(request.POST["player_id"])
    text = request.POST["text"]
    player = Player.objects.filter(user=request.user, id=player_id).first()
    player.handle(text)
    return JsonResponse({"received": True})
