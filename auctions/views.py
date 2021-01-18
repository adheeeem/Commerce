from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import *


class CreateForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Subject',
        'class': 'form-control',
        'aria-label': 'Subject',
        'aria-describedby': 'basic-addon1'
    }))
    desc = forms.CharField(label='', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'aria-label': 'Description'
    }))
    price = forms.FloatField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Starting Bid',
        'class': 'form-control',
        'aria-label': 'Amount (to the nearest dollar)'
    }))
    image = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Paste image url',
        'class': 'form-control',
        'id': 'basic-url'
    }))
    category = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Category',
        'class': 'form-control',
        'id': 'cat'
    }))

class BidForm(forms.Form):
    bid = forms.FloatField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'bid-item',
        'placeholder': '0.00'
    }), required=False)

class CommentForm(forms.Form):
    comment = forms.CharField(label='', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'id': 'exampleFormControlTextarea1',
        'placeholder': 'Leave a comment here',
        'rows': '5'
    }), required=False)


def index(request):
    return render(request, "auctions/index.html", {
        "list": Listing.objects.all()

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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    cat = Categories.objects.all()
    test = True
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            user = request.user.username
            title = form.cleaned_data["title"]
            price = form.cleaned_data["price"]
            desc = form.cleaned_data["desc"]
            image_url = form.cleaned_data["image"]
            category = form.cleaned_data["category"]
            f = Listing(user=user, title=title, price=price, image_url=image_url, desc=desc, category=category.title())
            f.save()
            for dog in cat:
                if dog.title.lower() == category.lower(): test = False

            if test:
                ctgry = Categories(title=category.title())
                ctgry.save()

    return render(request, "auctions/create.html", {
        "form": CreateForm()
        
    })

def items(request, listing_id):
    watch = Watchlist.objects.all()
    u = request.user.username
    cnt = 0
    for w in watch:
        if w.user == u: cnt += 1
    if_click = False
    all_com = Comment.objects.all()
    listing = Listing.objects.get(id=listing_id)
    highest_bid = False
    winner = None
    highest_bid_id = -1
    for bids in Bid.objects.all():
        if bids.title == listing.title: 
            highest_bid = True
            highest_bid_id = bids.id
    if highest_bid:
        winner = Bid.objects.get(id=highest_bid_id)
    bid_made_this_guy = False
    username = None
    won_message = False
    message = False
    b = 1
    if (not listing.active) and winner.user == request.user.username: won_message = True
    if request.user.is_authenticated: username = request.user.username
    test = True
    on_off = False
    if request.user.username == listing.user: bid_made_this_guy = True 
    if request.method == "GET": 
        for watch in Watchlist.objects.all():
            if watch.title.title == listing.title and watch.visibility and watch.user == username:
                on_off = watch.visibility
        return render(request, "auctions/items.html", {
            "listing": listing,
            "on_off": on_off,
            "bids": BidForm(),
            "message": message,
            "bid_made_this_guy": bid_made_this_guy,
            "winner": winner,
            "won_message": won_message,
            "comment": CommentForm(),
            "comment_text": all_com,
            "cnt": cnt
        })
    if 'watchlist' in request.POST:
        listing = Listing.objects.get(id=listing_id)
        watch_id = -1
        user_id = -1 
        on_off = True
        for watch in Watchlist.objects.all():
            if watch.title.title == listing.title and watch.user == username: 
                on_off = False
                watch_id = watch.id
        if on_off:
            watch = Watchlist(user=username, title=listing, visibility=True)
            watch.save()
            watch_id = watch.id
        else:
            test = Watchlist.objects.get(id=watch_id)
            if test.visibility:
                test.visibility = False
                test.save()
            else:
                test.visibility = True
                test.save()

        return render(request, "auctions/items.html", {
            "listing": listing,
            "on_off": Watchlist.objects.get(id=watch_id).visibility,
            "bids": BidForm(),
            "message": message,
            "bid_made_this_guy": bid_made_this_guy,
            "winner": winner,
            "comment": CommentForm(),
            "comment_text": all_com
        })
    if 'bar' in request.POST:
        message = True
        for watch in Watchlist.objects.all():
            if watch.title.title == listing.title and watch.visibility and watch.user == username:
                on_off = watch.visibility
        form = BidForm(request.POST)
        if form.is_valid():
            b_id = -1
            response = True
            form.fields["bid"].required = True
            b = form.cleaned_data["bid"]
            if b == None: b = 0
            for bids in Bid.objects.all(): 
                if bids.title == listing.title: b_id = bids.id
            if b_id != -1:
                foo = Bid.objects.get(id=b_id)
                if b > foo.bid:
                    foo.bid = b
                    foo.user = request.user.username
                    foo.save()
                    response = False
            else:
                foo = Bid(user=request.user.username, title=listing.title, bid=listing.price)
                if b > foo.bid:
                    foo.bid = b
                    foo.user = request.user.username
                    foo.save()
                    response = False

            return render(request, "auctions/items.html", {
                "bids": BidForm(),
                "on_off": on_off,
                "listing": listing,
                "response": response,
                "message": message,
                "bid_made_this_guy": bid_made_this_guy,
                "winner": foo,
                "comment": CommentForm(),
                "comment_text": all_com
            })
    if 'close' in request.POST:
        if_click = True
        listing.active = False
        listing.save()
        return render(request, "auctions/items.html", {
            "bids": BidForm(),
            "on_off": on_off,
            "listing": listing,
            "message": message,
            "bid_made_this_guy": bid_made_this_guy,
            "winner": winner,
            "if_click": if_click,
            "won_message": won_message,
            "comment": CommentForm(),
            "comment_text": all_com
        })
    if 'com' in request.POST:
        test = True
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            for cm in Comment.objects.all():
                if request.user.username == cm.user and cm.comment == comment: test = False
            if test:
                c = Comment(theme=listing, comment=comment, user=request.user.username)
                c.save()
            return render(request, "auctions/items.html", {
                "listing": listing,
                "on_off": on_off,
                "bids": BidForm(),
                "message": message,
                "bid_made_this_guy": bid_made_this_guy,
                "winner": winner,
                "won_message": won_message,
                "comment": CommentForm(),
                "comment_text": all_com
            })

def watchlists(request):
    watch = Watchlist.objects.all()
    u = request.user.username
    return render(request, "auctions/watchlists.html", {
        "watch": watch,
        "u": u,

    })

def category(request):
    cats = Categories.objects.all()
    return render(request, "auctions/category.html", {
        "cats": cats
    })

def exact_category(request, ex_category):
    test = True
    listings = Listing.objects.all()
    for lists in listings:
        if lists.category == ex_category: test = False

    if test:
        return HttpResponse("<h1>Ooops, Not Found</h1>") 
    return render(request, "auctions/categories.html", {
        "listings": listings,
        "ex_category": ex_category
    })
