from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.db.models import Q

from .forms import CommentForm, PostForm, GroupForm, ProfileForm
from .models import Follow, Group, Post, User, Profile, Likes


DEFAULT_PAGE_SIZE = 10


def search(request):
    query = request.GET.get('q')
    object_list = Post.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query) | Q(author__username__icontains=query) | Q (group__title__icontains=query)
        )
    return render(request,'search_results.html',
            {'object_list': object_list, 'query': query})
    


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, DEFAULT_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, DEFAULT_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group, 'posts': posts, 'page': page,
        'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username) 
    posts = user.posts.all()
    paginator = Paginator(posts, DEFAULT_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=user).exists()
    return render(request, 'profile.html', {'author': user, 'page': page,
                  'paginator': paginator, 'following': following})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm()
    comments = post.comments.all()
    likes = post.likes.all()
    return render(request, 'post.html', {
        'author': post.author, 'post': post, 'form': form,
        'comments': comments, 'likes':likes})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    if request.user != author:
        return redirect('post', username=request.user.username,
                        post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post',
                            username=request.user.username,
                            post_id=post_id)
    return render(request, 'new.html',
                  {'form': form, 'author': author, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    group_list = Group.objects.all()
    paginator = Paginator(post_list, DEFAULT_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html',
                  {'paginator': paginator, 'page': page, 'groups': group_list})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def new_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            return redirect('all_groups')
        return render(request, 'new_group.html', {'form': form})
    form = GroupForm()
    return render(request, 'new_group.html', {'form': form})

@login_required
def group_edit(request, username, slug):
    creator = get_object_or_404(User, username=username)
    group = get_object_or_404(Group, creator=creator, slug=slug)
    if request.user != creator:
        return redirect('all_groups')
    form = GroupForm(request.POST or None, files=request.FILES or None,
                    instance=group)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('all_groups')
    return render(request, 'new_group.html',
                  {'form': form, 'creator': creator, 'group': group})


def all_groups(request):
    group_list = Group.objects.all()
    paginator = Paginator(group_list, DEFAULT_PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'all_groups.html', {
        'page': page, 'paginator': paginator, 'groups': group_list})


@login_required
def profile_settings(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    form = ProfileForm(request.POST or None, files=request.FILES or None, instance=profile)
    if not form.is_valid():
        return render(request, 'profile_settings.html', {'form': form})
    form.save()
    return redirect('profile', username=request.user.username)


@login_required
def post_delete(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    if request.user != author:
        return redirect('post', username=request.user.username,
                        post_id=post_id)
   
    else:
        post.delete()
        return redirect('profile',username=request.user.username,)


@login_required
def group_delete(request, username, slug):
    creator = get_object_or_404(User, username=username)
    group = get_object_or_404(Group, creator=creator, slug=slug)
    if request.user != creator:
        return redirect('all_groups')
    else:
        group.delete()
        return redirect('all_groups')


@login_required
def user_delete(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('profile',username=request.user.username,)
    else:
        user.delete()
        return redirect('index')


def author_groups(request, username):
    creator = get_object_or_404(User, username=username)
    groups = Group.objects.filter(creator__username=username)
    return render(request, 'author_groups.html', {'creator': creator , 'groups': groups})


@login_required
def likes(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.likes.filter(user=request.user.id).exists():
        Likes.objects.get(user=request.user, post=post).delete()
    else:
        Likes.objects.get_or_create(user=request.user, post=post)
    prewious_url = request.META.get('HTTP_REFERER')
    return redirect(prewious_url)

def all_authors(request):
    author_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(author_list, 20)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'all_authors.html', {
        'page': page, 'paginator': paginator, 'author_list': author_list})


def following(request, username):
    author = get_object_or_404(User, username=username) 
    followers = author.follower.all()
    return render(request, 'following.html',{
        'author': author, 'followers': followers,
    })

def followers(request, username):
    author = get_object_or_404(User, username=username) 
    followers = author.following.all()
    return render(request, 'followers.html',{
        'author': author, 'followers': followers,
    })
