from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm, ProfileForm
from .models import Group, Post, User, Follow, Profile_Author, Preference


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
                )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        {'path': request.path},
        status=500
                )


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, 'paginator': paginator}
        )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group, 'page': page, 'paginator': paginator, 'posts':posts
        })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None,)
        if form.is_valid():
            post_get = form.save(commit=False)
            post_get.author = request.user
            post_get.save()
            return redirect('index')
    form = PostForm()
    return render(request, 'new.html', {'form': form})


@login_required
def groups(request):
    all_groups = Group.objects.all()
    paginator = Paginator(all_groups, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group_all.html',
        {'groups': all_groups, 'page': page, 'paginator': paginator}
        )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile_author = Profile_Author.objects.filter(author__username=username).first()
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=user, user=request.user)
    return render(
        request,
        'profile.html',
        {
            'author': user,
            'page': page,
            'paginator': paginator,
            'following': following,
            'profile': profile_author
        }
        )


def post_view(request, username, post_id):
    profile_author = Profile_Author.objects.filter(author__username=username).first()
    post = get_object_or_404(
        Post,
        author__username=username,
        pk=post_id
        )
    items = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(request, 'post.html', {
        'author': post.author,
        'post': post,
        'items': items,
        'form': form,
        'profile': profile_author
        })


def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        pk=post_id,
        author__username=username
        )
    if request.user != post.author:
        return redirect('post', post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    else:
        edit = True
        return render(request, 'new.html', {'form': form, 'post': post, 'edit': edit})


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment_get = form.save(commit=False)
        comment_get.author = request.user
        comment_get.post_id = post.pk
        comment_get.save()
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    items = post.comments.all()
    return render(request, 'post.html', {'form':form, 'items': items, 'post': post})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    follow = False
    if post_list is not None:
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        follow = True
    return render(
        request,
        "follow.html",
        {"page": page, 'paginator': paginator, 'follow': follow}
        )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author.username != request.user.username:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author.username != request.user.username:
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('profile', username=username)

@login_required
def post_delete(request, post_id, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        post = get_object_or_404(Post, id=post_id)
        post.delete()
    return redirect('profile', username=username)

@login_required
def profile_edit(request, username):
    profile_1 = Profile_Author.objects.filter(author__username=username).first()
    form = ProfileForm(
        request.POST or None,
        files=request.FILES or None,
        instance=profile_1
    )
    if form.is_valid():
        new_profile = form.save(commit=False)
        new_profile.author = request.user
        new_profile.save()
        return redirect('profile', username=username)
    return render(request, 'profile_edit.html', {'form': form})

def following_view(request, username):
    author = get_object_or_404(User, username=username)
    followings = Follow.objects.filter(author=author)
    paginator = Paginator(followings, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'following_view.html',
        {
            'author': author,
            'paginator': paginator,
            'page': page
        }
        )

def follower_view(request, username):
    author = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(user=author)
    paginator = Paginator(followers, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'followers_view.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator
        }
        )

@login_required
def rating_plus(request, post_id, username):
    post = get_object_or_404(Post, pk=post_id)
    Preference.objects.get_or_create(user=request.user, post=post)
    post.rating = post.like.all().count()
    post.save()
    return redirect('post', username=username, post_id=post_id)

@login_required
def rating_minus(request, post_id, username):
    post = get_object_or_404(Post, id=post_id)
    preference = Preference.objects.filter(user=request.user, post=post)
    preference.delete()
    post.rating = post.like.all().count()
    post.save()
    return redirect('post', username=username, post_id=post_id)
