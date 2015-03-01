from django.contrib.auth.decorators import login_required
from django.shortcuts import render


########################################################################
def home(request):
    return render(request, "mud/index.html")

########################################################################
@login_required
def game(request):
    context = {"player": None}
    return render(request, "mud/game.html", context)
