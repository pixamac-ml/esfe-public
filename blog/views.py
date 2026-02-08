from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Article, Comment
from .services import create_comment, approve_comment
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from .services import like_comment


def article_list(request):
    articles = Article.objects.filter(status='published')
    return render(request, 'blog/article_list.html', {
        'articles': articles
    })


def article_detail(request, slug):
    article = get_object_or_404(
        Article,
        slug=slug,
        status='published'
    )

    comments = article.comments.filter(
        status='approved',
        parent__isnull=True
    )

    if request.method == 'POST' and article.allow_comments:
        create_comment(
            article,
            request.POST,
            request.user if request.user.is_authenticated else None
        )
        return redirect('blog:article_detail', slug=slug)

    return render(request, 'blog/article_detail.html', {
        'article': article,
        'comments': comments
    })

@login_required
def article_create(request):
    form = ArticleForm(request.POST or None)

    if form.is_valid():
        article = form.save(commit=False)
        article.author = request.user
        article.save()
        return redirect('blog:article_list')

    return render(request, 'blog/article_form.html', {'form': form})


@login_required
def article_edit(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        is_deleted=False
    )

    form = ArticleForm(request.POST or None, instance=article)

    if form.is_valid():
        form.save()
        return redirect('blog:article_list')

    return render(request, 'blog/article_form.html', {'form': form})


@login_required
def article_delete(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.is_deleted = True
    article.save()
    return redirect('blog:article_list')


@login_required
def moderate_comments(request):
    comments = Comment.objects.filter(status='pending')
    return render(request, 'blog/moderate_comments.html', {
        'comments': comments
    })


@login_required
def approve_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    approve_comment(comment, request.user)
    return redirect('blog:moderate_comments')


def like_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    like_comment(comment, request)
    return redirect('blog:article_detail', slug=comment.article.slug)
