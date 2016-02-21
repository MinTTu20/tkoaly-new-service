from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse

from django_markup import markup

PAGE, DIRECT_LINK, PAGE_SEPARATOR = range(3)
FLATPAGE_TYPE_CHOICES = (
    (PAGE, _("Page")),
    (DIRECT_LINK, _("Direct Link")),
    (PAGE_SEPARATOR, _("Page with menu separator"))
)

MARKUP_CHOICES = markup.formatter.choices()


class Flatpage(models.Model):
    menu_category = models.IntegerField(
        choices=settings.FLATPAGES_MENU_CATEGORIES,
        default=settings.FLATPAGES_DEFAULT_MENU_CATEGORY,
        verbose_name=_("Menu category")
    )
    menu_index = models.IntegerField(
        default=0,
        help_text=_("Menus are sorted ascending by this value. The first menu item in a category is the category link itself. <strong>Note:</strong> The first menu item in the top level category should be the front page."),
        verbose_name=_("Menu index")
    )
    flatpage_type = models.IntegerField(
        choices=FLATPAGE_TYPE_CHOICES,
        default=PAGE,
        verbose_name=_("Flatpage type")
    )
    published = models.BooleanField(
        default=False,
        help_text=_("Published pages show up on the menu. Unpublished pages can be reached over direct link."),
        verbose_name=_("Published")
    )

    def __unicode__(self):
        return self.localflatpage_set.first().title

    class Meta:
        verbose_name = _("Flatpage")
        verbose_name_plural = _("Flatpages")

class LocalFlatpage(models.Model):
    flatpage = models.ForeignKey(Flatpage)
    language = models.CharField(
        max_length=5,
        choices=settings.LANGUAGES,
        verbose_name=_("Language")
    )
    url = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        verbose_name=_("URL"),
        help_text=_("The page is accessible on this path. Even external links have one.")
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    menu_title = models.CharField(
        max_length=40,
        blank=True,
        verbose_name=_("Menu Title"),
        help_text=_("Shorter title that fits in menu elements")
    )
    content = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Body text for pages, URL for direct links")
    )
    content_markup = models.CharField(
        verbose_name=_("Content markup"),
        max_length=20,
        choices=MARKUP_CHOICES,
        default=MARKUP_CHOICES[0][0]
    )

    def has_separator(self):
        return self.flatpage.flatpage_type == PAGE_SEPARATOR

    def __unicode__(self):
        return self.title

    def get_other_lang(self, language):
        return self.flatpage.localflatpage_set.get(language=language)

    def get_absolute_url(self):
        if self.flatpage.flatpage_type == DIRECT_LINK:
            return self.content
        else:
            return reverse('flatpage', kwargs={"url": self.url})


    class Meta:
        verbose_name = _("Local Flatpage")
        verbose_name_plural = _("Local Flatpages")
        unique_together = (('flatpage', 'language'), ('url', 'language'))
        ordering = ('language', 'flatpage__menu_index', 'title')


class Sponsor(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )
    url = models.URLField(verbose_name=_("URL"))
    logo = models.ImageField(upload_to="sponsors/")
    titletext = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Title text")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    class Meta:
        verbose_name = _("Sponsor")
        verbose_name_plural = _("Sponsors")
        ordering = ('name',)