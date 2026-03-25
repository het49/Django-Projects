from django.http import HttpResponse
# Create your views here.
from BeerBuddy.users.management.commands.tasks import create_random_user_accounts


def testforcronjob(request):
    print("let's start")
    create_random_user_accounts.delay(1)
    return HttpResponse("start")