from django.contrib import admin

# Register your models here.
from interview.models import Author, User, Interview, Faq


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc',)
    list_filter = ('name', 'desc',)
    search_fields = ('name', 'desc',)


class InterviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'desc', 'company',)
    list_filter = ('title', 'desc', 'company',)
    search_fields = ('name', 'desc', 'company',)


class FaqAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Interview, InterviewAdmin)
admin.site.register(Faq, FaqAdmin)
