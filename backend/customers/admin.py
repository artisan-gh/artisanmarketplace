
from django import forms
from django.contrib import admin, messages
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from .models import Customer


class LinkUserForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    phone = forms.CharField(max_length=20, help_text="Phone number of the CLIENT user to link.")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "organization",
                    "has_account", "created_at", "is_deleted", "created_by")
    list_filter = ("is_deleted", "organization", "created_at", "created_by")
    search_fields = ("name", "phone", "email", "address", "notes", "tags",
                     "user__username", "user__email")
    raw_id_fields = ("user", "organization")
    readonly_fields = ("id", "user", "created_at", "updated_at",
                       "created_by", "updated_by", "deleted_at")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("name", "phone", "email", "address")}),
        (_("Location"), {"fields": ("gps_lat", "gps_lng"), "classes": ("collapse",)}),
        (_("Organization"), {"fields": ("organization",)}),
        (_("App account"), {"fields": ("user",),
                            "description": "Linked when client logs in via OTP."}),
        (_("Metadata"), {"fields": ("notes", "tags")}),
        (_("Audit"), {"fields": ("id", "created_at", "updated_at",
                                 "created_by", "updated_by",
                                 "is_deleted", "deleted_at"),
                      "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj: return self.readonly_fields + ("created_by", "updated_by")
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(boolean=True, description="App account")
    def has_account(self, obj): return obj.user_id is not None

    @admin.action(description="Soft-delete selected customers", permissions=["delete"])
    def soft_delete_selected(self, request, qs):
        n = qs.update(is_deleted=True, deleted_at=timezone.now())
        self.message_user(request, f"{n} customer(s) soft-deleted.")

    @admin.action(description="Restore selected customers", permissions=["delete"])
    def restore_selected(self, request, qs):
        n = qs.update(is_deleted=False, deleted_at=None)
        self.message_user(request, f"{n} customer(s) restored.")

    @admin.action(description="Export selected customers as CSV", permissions=["view"])
    def export_csv(self, request, qs):
        import csv
        from django.http import HttpResponse
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="customers.csv"'
        w = csv.writer(resp)
        w.writerow(["ID", "Name", "Phone", "Email", "Address",
                    "Organization", "Has App Account", "Created At", "Is Deleted"])
        for c in qs.select_related("organization", "user"):
            w.writerow([c.id, c.name, c.phone, c.email, c.address,
                        c.organization.name if c.organization else "",
                        "Yes" if c.user_id else "No", c.created_at,
                        "Yes" if c.is_deleted else "No"])
        return resp

    @admin.action(description="Link to app account by phone", permissions=["change"])
    def link_to_user(self, request, qs):
        form = None
        if "apply" in request.POST:
            form = LinkUserForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data["phone"].strip().replace(" ", "").replace("-", "")
                user = User.objects.filter(phone=phone, user_type="CLIENT").first()
                if not user:
                    self.message_user(request, f"No CLIENT user with phone {phone}.",
                                      level=messages.ERROR)
                else:
                    linked = skipped = already = 0
                    for c in qs:
                        if c.user_id == user.id: already += 1; continue
                        if c.user_id and c.user_id != user.id: skipped += 1; continue
                        c.user = user; c.updated_by = request.user
                        c.save(update_fields=["user", "updated_by", "updated_at"])
                        linked += 1
                    parts = []
                    if linked: parts.append(f"{linked} linked")
                    if already: parts.append(f"{already} already linked")
                    if skipped: parts.append(f"{skipped} skipped")
                    self.message_user(request, f"Linked to {user}: {', '.join(parts) or 'no changes'}.",
                                      level=messages.SUCCESS if linked else messages.WARNING)
        if form is None:
            form = LinkUserForm(initial={"_selected_action": request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        return render(request, "admin/customers/link_user_form.html",
                      {"items": qs, "form": form,
                       "title": "Link selected customers to app account",
                       "opts": self.model._meta})

    actions = [soft_delete_selected, restore_selected, export_csv, link_to_user]
