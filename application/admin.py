from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AdminPasswordChangeForm
from django.contrib.admin.actions import delete_selected as django_delete_selected
from django.contrib.admin.widgets import FilteredSelectMultiple 
from . import models


class PermisionFieldFilter(admin.RelatedFieldListFilter):

    # def queryset(self, request, queryset):
    #     import pdb; pdb.set_trace()
    #     return super(PermisionFieldFilter, self).queryset(request, queryset)


    def field_choices(self, field, request, model_admin):
        origin_choices = field.get_choices(include_blank=False)
        res_choices = []
        # import pdb; pdb.set_trace()
        for key, value in origin_choices:
            if value.startswith('application | demo user |'):
                res_choices.append((key, value))
        return res_choices

class DemoUserCreationForm(forms.ModelForm):

    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    # user_group = forms.CharField(label='Group', widget=forms.TextInput)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.DemoUser
        fields = ('username', )
        default_permissons = ()

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(DemoUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.view_password = self.cleaned_data["password1"]
        user.save()
        c_groups = self.cleaned_data['groups'].all()
        for c_group in c_groups:
            c_group.save()
            # if commit:
            #     user.save()
            #     # If committing, save the instance and the m2m data immediately.
            c_group.user_set.add(user)
            user.groups.add(c_group)
            user.user_permissions.add(c_group.permissions.get())
            c_group.save()
        user.save()
        #     self._save_m2m()
        # else:
        #     # If not committing, add a method to the form to allow deferred
        #     # saving of m2m data.
        #     self.save_m2m = self._save_m2m
        return user

    # def _save_m2m(self, commit=True):
    #     user = super().save(commit=False)
    #     group = self.cleaned_data['groups'].get()
    #     import pdb; pdb.set_trace()
    #     group.user_set.add(user)
    #     import pdb; pdb.set_trace()
    #     if commit:
    #         group.save()
    #         user.save()
    #     return user

    
class DemoUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    # password = ReadOnlyPasswordHashField()
    password = ReadOnlyPasswordHashField(label=("Password", ),
        help_text=("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>.",))

    class Meta:
        model = models.DemoUser
        fields = ('username', 'view_password', 'password', 'is_active', 'is_admin')
        default_permissons = ()

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["view_password"])
        user.view_password = self.cleaned_data["view_password"]
        if commit:
            user.save()
        return user

class DemoUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = DemoUserChangeForm
    add_form = DemoUserCreationForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'view_password', 'create_time', 'update_time', 'expire_day', 'is_admin', 'is_active', 'last_login', 'user_group', 'user_perm')
    list_filter = ('username', 'is_active', 'expire_day', 'groups', ('user_permissions', PermisionFieldFilter))
    fieldsets = (
        (None, {'fields': ('view_password', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_admin',)}),
        ('Groups', {'fields': ('groups',)})
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'groups')}
        ),
    )
    search_fields = ('username', )
    ordering = ('id',)
    filter_horizontal = ('groups', 'user_permissions',)

    class Meta:
        default_permissons = ()

    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     return super(DemoUserAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

    def user_group(self, obj):
        # import pdb; pdb.set_trace()
        return ','.join([group.name for group in obj.groups.all()])

    def user_perm(self, obj):
        return ','.join([permission.name for permission in obj.user_permissions.all()])

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # if db_field.name == 'permissions':
        #     qs = kwargs.get('queryset', db_field.remote_field.model.objects)
        #     # Avoid a major performance hit resolving permission names which
        #     # triggers a content_type load:
        #     # kwargs['queryset'] = qs.select_related('content_type')
        #     kwargs['queryset'] = qs.filter(codename__contains='view')
            # kwargs['queryset'] = qs.get_by_natural_key(codename='view_hello', app_label='application', model='Task')
        # import pdb; pdb.set_trace()
        result = super(DemoUserAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)
        return result



class GroupAdminForm(forms.ModelForm):

    class Meta:
        model = Group
        exclude = ()
        default_permissons = ()

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
         queryset=models.DemoUser.objects.all(), 
         required=False,
         # Use the pretty 'filter_horizontal widget'.
         widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance

class DemoUserGroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)
    list_display = ('name', 'all_users', 'group_perm')
    # filter_horizontal = ('user_set', 'permissions')

    class Meta:
        default_permissons = ()

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            qs = kwargs.get('queryset', db_field.remote_field.model.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            # kwargs['queryset'] = qs.select_related('content_type')
            kwargs['queryset'] = qs.filter(codename__contains='view')
            # kwargs['queryset'] = qs.get_by_natural_key(codename='view_hello', app_label='application', model='Task')
        result = super(DemoUserGroupAdmin, self).formfield_for_manytomany(
            db_field, request=request, **kwargs)
        return result


    def all_users(self, obj):
        return ','.join([user.username for user in obj.user_set.all()])

    def group_perm(self, obj):
        return ','.join([perm.name for perm in obj.permissions.all()])
# Now register the new UserAdmin...
admin.site.register(models.DemoUser, DemoUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, DemoUserGroupAdmin)
admin.site.register(models.UploadFileMetaData)