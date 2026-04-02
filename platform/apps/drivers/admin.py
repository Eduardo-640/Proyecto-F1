from django.contrib import admin, messages
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from apps.races.models import RaceResult
from .models import Driver, DriverStanding, DriverPointTransaction


class DriverCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Confirmar contraseña", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = Driver
        fields = "__all__"
        exclude = ["password"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        driver = super().save(commit=False)
        p1 = self.cleaned_data.get("password1")
        if p1:
            driver.set_password(p1)
        if commit:
            driver.save()
        return driver


class DriverStandingInline(admin.TabularInline):
    model = DriverStanding
    extra = 0
    fields = [
        "season",
        "total_points",
        "races_entered",
        "wins",
        "podiums",
        "pole_positions",
        "fastest_laps",
        "dnf_count",
    ]
    readonly_fields = []


class DriverPointTransactionInline(admin.TabularInline):
    model = DriverPointTransaction
    extra = 0
    fields = ["season", "amount", "description", "race", "created_at"]
    readonly_fields = ["season", "amount", "description", "race", "created_at"]


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    form = DriverCreationForm
    list_display = [
        "name",
        "team",
        "steam_id",
        "password_status",
        "active",
        "created_at",
    ]
    list_filter = ["active", "team"]
    search_fields = ["name", "steam_id", "team__name"]
    readonly_fields = ["password_status"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "last_name",
                    "number",
                    "country",
                    "birth_date",
                    "team",
                    "steam_id",
                    "active",
                ),
            },
        ),
        (
            "Contraseña",
            {
                "fields": ("password_status", "password1", "password2"),
                "description": "Deja en blanco para no cambiar la contraseña.",
            },
        ),
    )

    inlines = [DriverStandingInline, DriverPointTransactionInline]

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:driver_id>/reset-password/",
                self.admin_site.admin_view(self.reset_password_view),
                name="drivers_driver_reset_password",
            ),
        ]
        return custom + urls

    def reset_password_view(self, request, driver_id):
        driver = get_object_or_404(Driver, pk=driver_id)
        if request.method == "POST":
            form = SetPasswordForm(driver, request.POST)
            if form.is_valid():
                new_password = form.cleaned_data["new_password1"]
                driver.set_password(new_password)
                driver.save(update_fields=["password"])
                messages.success(
                    request, f"Contraseña de {driver} restablecida correctamente."
                )
                return redirect(
                    reverse("admin:drivers_driver_change", args=[driver_id])
                )
        else:
            form = SetPasswordForm(driver)

        context = {
            **self.admin_site.each_context(request),
            "title": f"Restablecer contraseña: {driver}",
            "form": form,
            "driver": driver,
            "opts": self.model._meta,
        }
        return render(request, "admin/drivers/reset_password.html", context)

    def password_status(self, obj):
        if obj.pk:
            reset_url = reverse("admin:drivers_driver_reset_password", args=[obj.pk])
            link = format_html(
                ' &nbsp;<a href="{}">Restablecer contraseña</a>', reset_url
            )
        else:
            link = ""
        if obj.has_usable_password():
            return format_html('<span style="color:green">✔ Establecida</span>{}', link)
        return format_html('<span style="color:gray">✘ Sin contraseña</span>{}', link)

    password_status.short_description = "Estado contraseña"


@admin.register(DriverStanding)
class DriverStandingAdmin(admin.ModelAdmin):
    list_display = [
        "driver",
        "season",
        "total_points",
        "points_breakdown",
        "races_entered",
        "wins",
        "podiums",
        "pole_positions",
        "fastest_laps",
        "dnf_count",
    ]
    list_filter = ["season"]
    search_fields = ["driver__name", "season__name"]

    def points_breakdown(self, obj):
        # Show per-race contribution for this standing's season
        qs = (
            RaceResult.objects.filter(driver=obj.driver, race__season=obj.season)
            .select_related("race", "race__circuit")
            .order_by("race__round_number", "race__status")
        )
        if not qs.exists():
            return "-"
        parts = []
        for rr in qs:
            pts = rr.points_awarded or 0
            status = rr.race.status or ""
            parts.append(
                f"R{rr.race.round_number} {rr.race.circuit.name} ({status}): {pts}"
            )
        return format_html("<br/>".join(parts))

    points_breakdown.short_description = "Points breakdown"
