from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


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
    print "called:", request.GET, request.POST
    if request.method == "POST":
        print "POST:", request.POST
    context = {"player": None}
    return HttpResponse("<p>Testing, testing.</p>", content_type="text/plain")
