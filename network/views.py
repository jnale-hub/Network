from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, resolve_url
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from markdown2 import Markdown


import json

from .models import *

markdowner = Markdown()

def index(request):
    allPosts = Post.objects.all().order_by("-date")

    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts_page": posts_page,
    })

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    allPosts = Post.objects.filter(author=profile).order_by("-date")

    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "profile": profile,
        "posts_page": posts_page,
    })

def following(request):
    followed_users = request.user.following.all()
    followingPosts = list(Post.objects.filter(author__in=followed_users).order_by("-date"))
    
    paginator = Paginator(followingPosts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_page": posts_page,
    })

@login_required
def follow(request, username):
    profile = get_object_or_404(User, username=username)
    if request.method == "POST" and request.user != profile:
        if profile not in request.user.following.all():
            request.user.following.add(profile)
        else:
            request.user.following.remove(profile)
        return HttpResponseRedirect(resolve_url("profile", profile))

@login_required
def new_post(request):
    if request.method == "POST":
        content = markdowner.convert(request.POST['content'])
        post = Post(content=content, author=request.user)
        post.save()
        return HttpResponseRedirect(reverse(index))

@login_required
@csrf_exempt
def post(request, post_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    data = json.loads(request.body)

    if "toggle_like" in data:
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

    if "content" in data:
        if request.user != post.author:
            return JsonResponse({"error": "Unauthorized edit."}, status=401)
        else:
            post.content = data["content"]

    post.save()
    return JsonResponse({"num_likes": post.likes.count()}, status=201)

def search_results(request):
    query = request.GET.get('q')
    posts = Post.objects.filter(Q(author__username__icontains=query) | Q(content__icontains=query) | Q(author__first_name__icontains=query) | Q(author__last_name__icontains=query))

    allPosts = Post.objects.all().order_by("-date")

    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts_page": posts_page,
        'query': query,
        'posts': posts,
    })

def edit_profile(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        picture = request.POST["profile_pic"]
        username = request.POST["username"]
        email = request.POST["email"]

        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if username:
            request.user.username = username
        if picture:
            request.user.picture = picture
        if email:
            request.user.email = email

        request.user.save()
        return HttpResponseRedirect(resolve_url("profile", username=request.user.username))

    return render(request, "network/edit.html")
    
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        profile_pic = request.POST["profile_pic"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            if profile_pic:
                user.picture = profile_pic
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
