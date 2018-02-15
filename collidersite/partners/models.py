from django import forms
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from taggit.models import Tag, TaggedItemBase
from modelcluster.fields import ParentalManyToManyField

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, StreamFieldPanel
    )
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from django.shortcuts import redirect, render

from collidersite.base.blocks import BaseStreamBlock



@register_snippet
class Country(models.Model):
    """
    A Django model to store set of countries of origin.
    It uses the `@register_snippet` decorator to allow it to be accessible
    via the Snippets UI (e.g. /admin/snippets/partners/country/) In the PartnerPage
    model you'll see we use a ForeignKey to create the relationship between
    Country and PartnerPage. This allows a single relationship (e.g only one
    Country can be added) that is one-way (e.g. Country will have no way to
    access related PartnerPage objects).
    """

    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Countries of Origin"


class PartnerPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the BlogPage object and tags. There's a longer guide on using it at
    http://docs.wagtail.io/en/latest/reference/pages/model_recipes.html#tagging
    """
    content_object = ParentalKey('PartnerPage', related_name='tagged_partners', on_delete=models.CASCADE)



@register_snippet
class PartnerType(models.Model):
    """
    A Django model to define the Partner type
    It uses the `@register_snippet` decorator to allow it to be accessible
    via the Snippets UI. In the PartnerPage model you'll see we use a ForeignKey
    to create the relationship between PartnerType and PartnerPage. This allows a
    single relationship (e.g only one PartnerType can be added) that is one-way
    (e.g. PartnerType will have no way to access related PartnerPage objects)
    """

    title = models.CharField(max_length=255)

    panels = [
        FieldPanel('title'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Partner types"


class PartnerPage(Page):
    """
    Detail view for a specific partner
    """
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.'
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True
    )
    origin = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # We include related_name='+' to avoid name collisions on relationships.
    # e.g. there are two FooPage models in two different apps,
    # and they both have a FK to bread_type, they'll both try to create a
    # relationship called `foopage_objects` that will throw a valueError on
    # collision.
    partner_type = models.ForeignKey(
        'partners.PartnerType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tags = ClusterTaggableManager(through=PartnerPageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
        FieldPanel('origin'),
        FieldPanel('partner_type'),
        FieldPanel('tags'),
    ]

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = '/'+'/'.join(s.strip('/') for s in [
                self.get_parent().url,
                'tags',
                tag.slug
            ])
        return tags

    @property
    def get_people(self):
        people = self.people_covering.all()
        return people

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('tags'),
    ]

    parent_page_types = ['PartnersIndexPage']


class PartnersIndexPage(RoutablePageMixin, Page):
    """
    Index page for partners.

    This is more complex than other index pages on the bakery demo site as we've
    included pagination. We've separated the different aspects of the index page
    to be discrete functions to make it easier to follow
    """

    introduction = models.TextField(
        help_text='Text to describe the page',
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
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
    ]

    # Can only have PartnerPage children
    subpage_types = ['PartnerPage']

    # Returns a queryset of PartnerPage objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_partners(self, tag=None):
        partners = PartnerPage.objects.live().descendant_of(self)
        if tag:
            partners = partners.filter(tags=tag)
        return partners

    # Allows child objects (e.g. PartnerPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    # Pagination for the index page. We use the `django.core.paginator` as any
    # standard Django app would, but the difference here being we have it as a
    # method on the model rather than within a view function

    def paginate(self, request, *args):
        page = request.GET.get('page')
        paginator = Paginator(self.get_partners(), 6)
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
        context = super(PartnersIndexPage, self).get_context(request)

        # PartnerPage objects (get_partners) are passed through pagination
        partners = self.paginate(request, self.get_partners())

        context['partners'] = partners

        return context

    # This defines a Custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the PartnersIndexPage.
    # More information on RoutablePages is at
    # http://docs.wagtail.io/en/latest/reference/contrib/routablepage.html


    @route('^tags/$', name='tag_archive')
    @route('^tags/(\w+)/$', name='tag_archive')
    def tag_archive(self, request, tag=None):

        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no partners tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        partners = self.get_partners(tag=tag)
        context = {
            'tag': tag,
            'partners': partners
        }
        return render(request, 'partners/partners_index_page.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child PartnerPage objects for this PartnersPageIndex.
    # If a tag is used then it will filter the posts by tag.


    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for partner in self.get_partners():
            # Not tags.append() because we don't want a list of lists
            tags += partner.get_tags
        tags = sorted(set(tags))
        return tags