from django import forms
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ClusterableModel

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, StreamFieldPanel
    )
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from collidersite.base.blocks import BaseStreamBlock
from collidersite.locations.models import LocationPage
from collidersite.partners.models import PartnerPage
from collidersite.industries.models import IndustryPage

class Skill(models.Model):
    name = models.CharField("Name of the skill", max_length=254, null=True)
    level = models.IntegerField("from 0 to 100", null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Skills'

@register_snippet
class Person(Page):
    """
    A Django model to store People objects.
    It uses the `@register_snippet` decorator to allow it to be accessible
    via the Snippets UI (e.g. /admin/snippets/base/people/)

    `People` uses the `ClusterableModel`, which allows the relationship with
    another model to be stored locally to the 'parent' model (e.g. a PageModel)
    until the parent is explicitly saved. This allows the editor to use the
    'Preview' button, to preview the content, without saving the relationships
    to the database.
    https://github.com/wagtail/django-modelcluster
    """
    PERSON_TYPE_CHOICES = (('D', 'Innovation Director'),('T', 'Innovation Team'), ('A', 'Innovation Advisor'))

    first_name = models.CharField("First name", max_length=254, blank=True)
    last_name = models.CharField("Last name", max_length=254, blank=True)
    job_title = models.CharField("Job title", max_length=254, blank=True)
    person_type = models.CharField("Person type", choices = PERSON_TYPE_CHOICES, max_length = 1)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro_subtitle = models.CharField("Intro subtitle", max_length=254, blank=True)
    intro_paragraph = models.CharField("Intro paragraph", max_length=1022, blank=True)
    main_paragraph = models.CharField("Main paragraph", max_length=1022, blank=True)
    skills = ParentalManyToManyField(Skill, blank=True, related_name='skills')
    linkedin_link = models.URLField("Linkedin link", max_length=254, blank=True)
    nationality = models.CharField("Nationality", max_length=254 , blank=True)
    location = models.ForeignKey(LocationPage, on_delete=models.SET_NULL, null=True, related_name='location')
    covered_markets = ParentalManyToManyField(LocationPage, blank=True, related_name='covered_markets')
    partners = ParentalManyToManyField(PartnerPage, blank=True, related_name='people_covering')
    industries = ParentalManyToManyField(IndustryPage, blank=True, related_name='people_industries')
    content_panels = [
        FieldPanel('title', classname="col6"),
        FieldPanel('first_name', classname="col6"),
        FieldPanel('last_name', classname="col6"),
        FieldPanel('job_title', classname="col6"),
        FieldPanel('person_type', classname="col6"),
        ImageChooserPanel('image'),
        FieldPanel('location', classname="col6"),
        MultiFieldPanel(
            [
                FieldPanel(
                    'covered_markets',
                    widget=forms.CheckboxSelectMultiple,
                ),
                FieldPanel(
                    'partners',
                    widget=forms.CheckboxSelectMultiple,
                ),
                FieldPanel(
                    'industries',
                    widget=forms.CheckboxSelectMultiple,
                ),
            ],
            heading="Additional Metadata",
            classname="collapsible collapsed"
        ),
        FieldPanel('intro_subtitle', classname="col6"),
        FieldPanel('intro_paragraph', classname="col6"),
        FieldPanel('main_paragraph', classname="col6"),
        FieldPanel('linkedin_link', classname="col6"),
        MultiFieldPanel(
            [
                FieldPanel('skills', classname="col6"),
            ]),

    ]

    search_fields = Page.search_fields + [
        index.SearchField('first_name'),
        index.SearchField('last_name'),
    ]

    @property
    def thumb_image(self):
        # Returns an empty string if there is no profile pic or the rendition
        # file can't be found.
        try:
            return self.image.get_rendition('fill-50x50').img_tag()
        except:
            return ''

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def get_partners(self):
        partners = self.partners.all()
        return partners

    @property
    def get_industries(self):
        industries = self.industries.all()
        return industries

    search_fields = Page.search_fields + [
        index.SearchField('first_name'),
        index.SearchField('last_name'),
        index.SearchField('job_title'),
    ]

    parent_page_types = ['PeopleIndexPage']


class PeopleIndexPage(Page):
    introduction_directors = models.TextField(
        help_text='Text to describe the directors',
        blank=True)
    introduction_advisors = models.TextField(
        help_text='Text to describe the advisors',
        blank=True)
    introduction_team = models.TextField(
        help_text='Text to describe the ic team',
        blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and '
        '3000px.'
    )

    content_panels = Page.content_panels + [
        FieldPanel('introduction_directors', classname="full"),
        FieldPanel('introduction_advisors', classname="full"),
        FieldPanel('introduction_team', classname="full"),
        ImageChooserPanel('image'),
    ]

    # Can only have Person children
    subpage_types = ['Person']

    # Returns a queryset of Person objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_people(self):
        return Person.objects.live().descendant_of(
            self).order_by('-first_published_at')

    # Allows child objects (e.g. Person objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    # Pagination for the index page. We use the `django.core.paginator` as any
    # standard Django app would, but the difference here being we have it as a
    # method on the model rather than within a view function
    def paginate(self, request, *args):
        page = request.GET.get('page')
        paginator = Paginator(self.get_people(), 12)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages

    # Returns the above to the get_context method that is used to populate the
    # template
    def get_context(self, request):
        context = super(PeopleIndexPage, self).get_context(request)
        people = self.get_people()
        context['people'] = people

        return context




 