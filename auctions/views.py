from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import User, Category, Listing, Watchlist, Bid, Comment
from .forms import CreateListingForm

from decimal import *


def index(request):
    return render(request, "auctions/index.html", {
        "active_listings": Listing.objects.filter(is_active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return render(request, "auctions/login.html", {
        "message": "Logged out."
    })


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })


def category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        raise Http404("Category not found.")
    return render(request, "auctions/category.html", {
        "category": category,
        "active_listings": Listing.objects.filter(is_active=True, category=category)
    })


def listing(request, listing_id):
    if request.user.is_authenticated:
        try:
            listing = Listing.objects.get(id=listing_id)

            if listing.bids.all().first() == None:
                listing.current_bid = listing.starting_bid
            else: 
                listing.current_bid = listing.bids.all().last().bid_amount
            
            listing.save()
        except Listing.DoesNotExist:
            return HttpResponseBadRequest("Listing not found.")


        return render(request, "auctions/listing.html", {
            "listing": listing,
            "in_watchlist": Watchlist.objects.filter(user=request.user, listings=listing).exists(),
            "all_bids": listing.bids.all().order_by('-bid_time'),
            "highest_bid": get_highest_bid(listing_id),
            "all_comments": listing.comments.all().order_by('-comment_time'),
        })
    return HttpResponseRedirect(reverse('auctions:login'))


# @login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.current_bid = listing.starting_bid
            form.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        
    else:
        return render(request, "auctions/create_listing.html", {
            "form" : CreateListingForm()
        })


# @login_required
def add_to_watchlist(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        watchlist, just_created = Watchlist.objects.get_or_create(user=request.user)
        watchlist.listings.add(listing)

    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))


# @login_required
def remove_from_watchlist(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        watchlist = Watchlist.objects.get(user=request.user)
        watchlist.listings.remove(listing)

        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))


# @login_required
def watchlist(request):
    try:
        watchlist = Watchlist.objects.get(user=request.user)
        listings = watchlist.listings.all()
    except Watchlist.DoesNotExist:
        return HttpResponseBadRequest("Nothing here in watchlist.")
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


# @login_required
def place_bid(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        # get bid that is in request
        bid_placed = request.POST["bid"]
        # get all bids of the list
        all_bids = [bid.bid_amount for bid in listing.bids.all()]

        # IF the bid_placed is greater than any other bids, then bid successful
        # ELSE, return an error message
        if all_bids == [] or all(Decimal(bid_placed) > bid for bid in all_bids):
            listing.current_bid = bid_placed
            listing.save()
            Bid.objects.create(bidder=request.user, listing=listing, bid_amount=bid_placed)
        else:
            messages.error(request, "Your bid is too low. Bid higher.")
    
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))


def get_highest_bid(listing_id):
    try:
        listing = get_object_or_404(Listing, id=listing_id)
        highest_bid = Bid.objects.filter(listing=listing).order_by('-bid_amount').first()
        return highest_bid
    except Bid.DoesNotExist:
        return None
    

# @login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    listing.is_active = False
    listing.save()
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))


@login_required
def comment(request, listing_id):
    if request.method == "POST":
        # get list
        listing = get_object_or_404(Listing, id=listing_id)

        # get comment
        comment = request.POST["comment"]

        # add new comment to the list
        Comment.objects.create(commenter=request.user, listing=listing, comment=comment)

    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))