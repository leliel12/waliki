# -*- coding: utf-8 -*-
import os.path
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from waliki import _markups, settings


class Page(models.Model):
    MARKUP_CHOICES = [(m.name, m.name) for m in _markups.get_all_markups()]
    title = models.CharField(verbose_name=_('Title'), max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    path = models.CharField(max_length=200, unique=True)
    markup = models.CharField(verbose_name=_('Markup'), max_length=20, choices=MARKUP_CHOICES, default=settings.WALIKI_DEFAULT_MARKUP)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.path

    def get_absolute_url(self):
        return reverse('waliki_detail', args=(self.slug,))

    def get_edit_url(self):
        return reverse('waliki_edit', args=(self.slug,))

    def save(self, *args, **kwargs):
        self.slug = self.slug.strip('/')
        if not self.path:
            self.path = self.slug + self._markup.file_extensions[0]
        super(Page, self).save(*args, **kwargs)

    @property
    def raw(self):
        filename = self.abspath
        if not os.path.exists(filename):
            return ""
        return open(filename, "r").read()

    @raw.setter
    def raw(self, value):
        filename = os.path.join(settings.WALIKI_DATA_DIR, self.path)
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass
        with open(filename, "w") as f:
            f.write(value)

    @property
    def abspath(self):
        return os.path.abspath(os.path.join(settings.WALIKI_DATA_DIR, self.path))

    @staticmethod
    def get_markup_instance(markup):
        markup_settings = settings.WALIKI_MARKUPS_SETTINGS.get(markup, None)
        markup_class = _markups.find_markup_class_by_name(markup)
        return markup_class(**markup_settings)

    @staticmethod
    def preview(markup, text):
        return Page.get_markup_instance(markup).get_document_body(text)

    @property
    def _markup(self):
        if not hasattr(self, '__markup_instance'):
            self.__markup_instance = Page.get_markup_instance(self.markup)
        return self.__markup_instance

    def _get_part(self, part):
        return getattr(self._markup, part)(self.raw)

    @property
    def body(self):
        return self._get_part('get_document_body')

    @property
    def stylesheet(self):
        return self._get_part('get_stylesheet')

    @property
    def javascript(self):
        return self._get_part('get_javascript')
