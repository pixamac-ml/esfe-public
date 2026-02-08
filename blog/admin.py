from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Comment, CommentLike


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'status',
        'published_at',
        'is_deleted',
        'created_at',
    )

    list_filter = (
        'status',
        'is_deleted',
        'created_at',
        'published_at',
    )

    search_fields = (
        'title',
        'excerpt',
        'content',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'created_at',
        'updated_at',
        'published_at',
    )

    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Publication', {
            'fields': ('status', 'allow_comments')
        }),
        ('Métadonnées', {
            'fields': ('author', 'published_at', 'created_at', 'updated_at')
        }),
        ('Suppression', {
            'fields': ('is_deleted',)
        }),
    )

    actions = [
        'publish_articles',
        'archive_articles',
        'soft_delete_articles'
    ]

    def publish_articles(self, request, queryset):
        queryset.update(status='published')

    publish_articles.short_description = "Publier les articles sélectionnés"

    def archive_articles(self, request, queryset):
        queryset.update(status='archived')

    archive_articles.short_description = "Archiver les articles sélectionnés"

    def soft_delete_articles(self, request, queryset):
        queryset.update(is_deleted=True)

    soft_delete_articles.short_description = "Supprimer (soft delete)"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'short_content',
        'article',
        'author_name',
        'status',
        'created_at',
        'approved_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'author_name',
        'content',
    )

    readonly_fields = (
        'created_at',
        'approved_at',
    )

    fieldsets = (
        ('Commentaire', {
            'fields': ('article', 'parent', 'content')
        }),
        ('Auteur', {
            'fields': ('author_name', 'author_email', 'author_user')
        }),
        ('Modération', {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
        ('Dates', {
            'fields': ('created_at',)
        }),
    )

    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        for comment in queryset:
            comment.status = 'approved'
            comment.approved_by = request.user
            comment.save()

    approve_comments.short_description = "Approuver les commentaires"

    def reject_comments(self, request, queryset):
        queryset.update(status='rejected')

    reject_comments.short_description = "Rejeter les commentaires"

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    short_content.short_description = "Contenu"



@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = (
        'comment',
        'user',
        'ip_address',
        'created_at',
    )

    readonly_fields = (
        'comment',
        'user',
        'ip_address',
        'created_at',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False




