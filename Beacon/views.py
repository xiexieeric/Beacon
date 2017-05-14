from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
# importing loading from django template
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
import logging

from math import sin, cos, sqrt, atan2, radians
from django.core.mail import send_mail, BadHeaderError
from .models import *

logger = logging.getLogger(__name__)
def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())

@csrf_exempt
def signin(request):
    uname = request.POST.get('uname')
    pwd = request.POST.get('pwd')

    user = authenticate(username=uname, password=pwd)
    if user is not None:
        # A backend authenticated the credentials
        login(request, user)
        return HttpResponseRedirect('/home')
    else:
        template = loader.get_template('index.html')
        return HttpResponse(template.render({'error_message': 'Wrong Credentials', }, request))
@csrf_exempt
def register(request):
    template = loader.get_template('register.html')
    return HttpResponse(template.render())

@csrf_exempt
def signup(request):
    email = str(request.POST.get('email'))
    name = request.POST.get('name')
    gender = request.POST.get('gender')
    tel = request.POST.get('tel')
    pwd = request.POST.get('pwd')
    username = email.split('@')[0]
    try:
        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=pwd)
        wrapper = UserWrapper.objects.create(user=user, name=name, gender=gender, tel=tel)
        send_mail("Welcome!",
                  "Thank you for joining us here at Beacon! " + '\n' +
                  "We hope that you have a safe night out!" + '\n' +
                  "Please feel free to email this email with any questions or concerns, our staff is always eager to help! :)",
                  'lokahi.group9.test@gmail.com', [user.email], fail_silently=False, )
    except:
        # If failed, a field was missing so reload page with error warning
        template = loader.get_template('register.html')
        return HttpResponse(template.render({'error_message': 'Fill in all fields!', }, request))
    template = loader.get_template('register.html')
    return HttpResponse(template.render())


@csrf_exempt
@login_required
def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

@csrf_exempt
@login_required
def pair(request):
    minutes = int(request.POST.get('min'))
    delta = datetime.timedelta(minutes=minutes)
    now = datetime.datetime.now()
    leaving = now+delta
    lat = float(request.POST.get('lat'))
    lon = float(request.POST.get('lon'))
    loc2 = (lat, lon)
    user = request.user
    listing = Listing(poster=request.user, lat=lat, lon=lon, leavingTime=leaving)
    listing.save()
    otherListings = Listing.objects.filter(leavingTime__gte=now).exclude(poster=request.user)
    dist = []
    for listing in otherListings:
        loc1 = (float(listing.lat), float(listing.lon))
        d = distance(loc1, loc2)
        if(d < 1000):
            dist.append((listing, d))
            user.listing_set.add(listing)
    if len(dist)==0:
        template = loader.get_template('thank-you.html')
        return HttpResponse(template.render())
    else:
        dist.sort(key=lambda x: x[1])
        return match(request, dist[0])
    # except:
    #     template = loader.get_template('home.html')
    #     return HttpResponse(template.render({'error_message': 'Select a time', }, request))


def match(request, tup):
    template = loader.get_template('match.html')
    listing = tup[0]
    dist = int(tup[1])
    user = listing.poster
    wrapper = UserWrapper.objects.get(user=user)
    context = {
        'name' : wrapper.name,
        'gender' : wrapper.gender,
        'dist' : dist,
        'tel' : wrapper.tel,
        'id' : listing.id
    }
    return HttpResponse(template.render(context))

@login_required
def match_accept(request, pk):
    listing = Listing.objects.get(id=pk)
    user = request.user
    w1 = UserWrapper.objects.get(user=user)
    wrapper = UserWrapper.objects.get(user=listing.poster)
    listing.delete()
    send_mail("Hey",
              "We found a Beacon for you!" + '\n' +
              w1.name+ '\n' +
              w1.tel +'\n',
              'lokahi.group9.test@gmail.com', [wrapper.user.email], fail_silently=False, )
    context = {
        'name': wrapper.name,
        'gender': wrapper.gender,
        'tel': wrapper.tel,
    }
    template = loader.get_template('accept.html')
    return HttpResponse(template.render(context))


def dec_match(request, listing):
    template = loader.get_template('match.html')
    user = listing.poster
    wrapper = UserWrapper.objects.get(user=user)
    context = {
        'name' : wrapper.name,
        'gender' : wrapper.gender,
        'tel' : wrapper.tel,
        'id' : listing.id,
        'dist' : 0,
    }
    return HttpResponse(template.render(context))

def match_decline(request, pk):
    user = request.user
    listing = Listing.objects.get(id=pk)
    user2 = listing.poster
    s = user.listing_set.exclude(poster=user2).all()
    if len(s) != 0:
        return dec_match(request, s[0])
    else:
        template = loader.get_template('thank-you.html')
        return HttpResponse(template.render())

def distance(loc1, loc2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(loc1[0])
    lon1 = radians(loc1[1])
    lat2 = radians(loc2[0])
    lon2 = radians(loc2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c / 1000