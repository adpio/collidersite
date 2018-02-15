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



class IndustryPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the BlogPage object and tags. There's a longer guide on using it at
    http://docs.wagtail.io/en/latest/reference/pages/model_recipes.html#tagging
    """
    content_object = ParentalKey('IndustryPage', related_name='tagged_industries', on_delete=models.CASCADE)



class IndustryPage(Page):
    """
    Detail view for a specific industry
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

    tags = ClusterTaggableManager(through=IndustryPageTag, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
        StreamFieldPanel('body'),
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
        people = self.people_industries.all()
        return people

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('tags'),
    ]

    parent_page_types = ['IndustriesIndexPage']

class IndustriesIndexPage(RoutablePageMixin, Page):

    """
    Index page for industries.

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

    # Returns a queryset of IndustryPage objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_industries(self, tag=None):
        industries = IndustryPage.objects.live().descendant_of(self)
        if tag:
            industries = industries.filter(tags=tag)
        return industries

    # Allows child objects (e.g. IndustryPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request):
        context = super(IndustriesIndexPage, self).get_context(request)

        # IndustryPage objects (get_industries) are passed through pagination
        industries = self.get_industries()
        context['industries'] = industries
        return context

    # This defines a Custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the industriesIndexPage.
    # More information on RoutablePages is at
    # http://docs.wagtail.io/en/latest/reference/contrib/routablepage.html


    @route('^tags/$', name='tag_archive')
    @route('^tags/(\w+)/$', name='tag_archive')
    def tag_archive(self, request, tag=None):

        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no industries tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        industries = self.get_industries(tag=tag)
        context = {
            'tag': tag,
            'industries': industries
        }
        return render(request, 'industries/industries_index_page.html', context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child IndustryPage objects for this industriesPageIndex.
    # If a tag is used then it will filter the posts by tag.


    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for industry in self.get_industries():
            # Not tags.append() because we don't want a list of lists
            tags += industry.get_tags
        tags = sorted(set(tags))
        return tags