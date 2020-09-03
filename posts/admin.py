from django.contrib import admin

from .models import Group, Post, Comment, Profile_Author


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'text', 'author', 'created')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('author', 'text')

admin.site.register(Profile_Author, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
