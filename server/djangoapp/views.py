from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html', {})

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        psw = request.POST["psw"]
        user = authenticate(username=username, password=psw)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/index.html', context)
    return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
    return render(request, 'djangoapp/registration.html', context)
            

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://andrewtimmer-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        context["dealerships"] = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://andrewtimmer-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?id=" + str(dealer_id)
        # Get dealers from the URL
        context["dealer_reviews"] = get_dealer_reviews_from_cf(url,dealer_id)
        # Concat all dealer's short name
        #reviews = ' '.join([report.review + " " + report.sentiment for report in dealer_reviews])
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}

            url = "https://andrewtimmer-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
            
            dealerships = get_dealers_from_cf(url, dealer_id=dealer_id)
            context["dealerships"] = dealerships

            for dealer in dealerships:
                context["dealer_name"] = dealer
            context["dealer_id"] = dealer_id

            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == "POST":
            review = {}
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = request.POST["dealer_id"]
            review["review"] = request.POST["content"]
            review["name"] = request.user.get_username()
            review["purchase_date"] = request.POST["purchasedate"].strftime("%Y")
            review["purchase"] = False

            for k in request.POST:
                if key == "purchasecheck":
                    review["purchase"] = True
            
            parts = request.POST["car"].split("-")
            review["car_make"] = parts[0]
            review["car_model"] = parts[1]
            review["car_year"] = parts[2]

            json_payload = {"review": review}
            url = "https://andrewtimmer-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"

            post_response = post_request(url, json_payload, dealerId=dealer_id)

            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

