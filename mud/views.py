from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from mud.models import Player, PlayerMessage


########################################################################
def home(request):
    return render(request, "mud/index.html")


########################################################################
@login_required
def game(request):
    context = {"player": None}
    return render(request, "mud/game.html", context)


########################################################################
@login_required
def game_ajax(request):
    if request.method == "POST":
        player_id = int(request.POST["player_id"])
        player = Player.objects.filter(user=request.user, id=player_id).first()
        query_set = PlayerMessage.object.filter(player=player)
        messages = [m.text for m in query_set.order_by("created")]
        query_set.delete()
        output = {"hit_points": player.hit_points,
                  "max_hit_points": player.max_hit_points,
                  "messages": messages}
        print "text:", request.POST.get("text")
        return JsonResponse({"success": True, "foo": "bar"})
    else:
        return HttpResponse("<p>Testing, testing.</p>", content_type="text/plain")
