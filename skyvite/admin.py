from django.contrib import admin
from .models import Session, SchoolClass, Section, Student


# ----------------------------
# Base admin with user filter
# ----------------------------
class UserFilteredAdmin(admin.ModelAdmin):
    """Limit objects to those created by the logged-in user (unless superuser)."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # only set created_by on create
            obj.created_by = request.user
        obj.save()


# ----------------------------
# Session
# ----------------------------
@admin.register(Session)
class SessionAdmin(UserFilteredAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name',)


# ----------------------------
# SchoolClass
# ----------------------------
@admin.register(SchoolClass)
class SchoolClassAdmin(UserFilteredAdmin):
    list_display = ('name', 'session', 'created_by')
    list_filter = ('session',)
    search_fields = ('name',)


# ----------------------------
# Section
# ----------------------------
# Section
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class', 'get_session', 'created_by')
    list_filter = ('school_class__session', 'school_class')
    search_fields = ('name',)

    def get_session(self, obj):
        return obj.school_class.session
    get_session.short_description = 'Session'



# ----------------------------
# Student
# ----------------------------
@admin.register(Student)
class StudentAdmin(UserFilteredAdmin):
    list_display = (
        'first_name',
        'surname',
        'gender',
        'student_class',
        'section',
        'get_session',  # custom column for display
        'created_by',
    )
    list_filter = (
        'student_class',
        'section',
        'state',
        'gender',
        'session',   # use the real FK field
    )
    search_fields = ('first_name', 'surname')

    def get_session(self, obj):
        return obj.session.name
    get_session.short_description = 'Session'
