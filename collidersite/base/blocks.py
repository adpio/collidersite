from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailcore.blocks import (
    CharBlock, ChoiceBlock, RichTextBlock, StreamBlock, StructBlock, TextBlock, ListBlock, IntegerBlock,
)

from wagtailstreamforms.blocks import WagtailFormBlock
from collidersite.people.models import Person

class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """
    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = 'image'
        template = "blocks/image_block.html"


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headers
    """
    heading_text = CharBlock(classname="title", required=True)
    size = ChoiceBlock(choices=[
        ('', 'Select a header size'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4')
    ], blank=True, required=False)

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"


class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author
    """
    text = TextBlock()
    attribute_name = CharBlock(
        blank=True, required=False, label='e.g. Mary Berry')

    class Meta:
        icon = "fa-quote-left"
        template = "blocks/blockquote.html"


#Particles tempplate starts here
pe_icon_help_text = 'icon name from pe-icon-7 set, refer     http://themes-pixeden.com/font-demos/7-stroke/'
ion_icon_help_text = 'icon name from ionicons set, refer     https://ionicframework.com/docs/ionicons/'

class CounterBlock(StructBlock):
    finish = IntegerBlock(help_text='finish counting at')
    text = CharBlock(help_text='what is it counting to')
    icon = CharBlock(help_text=ion_icon_help_text)


class CounterPanel(StructBlock):
    title = CharBlock()
    subtitle = CharBlock()
    counters = ListBlock(CounterBlock)

    class Meta:
        icon = "title"
        template = "blocks/counter_panel.html"

class ProcessBlock(StructBlock):
    number = IntegerBlock(help_text='number of process')
    title = CharBlock(help_text='title for the block')
    subtitle = CharBlock()
    icon = CharBlock(help_text=pe_icon_help_text)


class ProcessPanel(StructBlock):
    title = CharBlock(help_text='title for the panel')
    processes = ListBlock(ProcessBlock)

    class Meta:
        icon = "fa-quote-left"
        template = "blocks/process.html"


class Service(StructBlock):
    icon = CharBlock(help_text=pe_icon_help_text)
    title = CharBlock()
    subtitle = CharBlock()
    popup_text = RichTextBlock()

class ServicePanel(StructBlock):
    services = ListBlock(Service)
    title = CharBlock(help_text='title for the block')

    class Meta:
        icon = "fa-quote-left"
        template = "blocks/services_panel.html"

class TeamBlock(StructBlock):
    title = CharBlock(help_text='Title for the team block')
    description = CharBlock(help_text='Team description')
    @property
    def get_team():
        team_members = Person.objects.live().filter(person_type='T')

    class Meta:
        icon = "fa-quote-left"
        template = "blocks/team_block.html"



# StreamBlocks
class BaseStreamBlock(StreamBlock):
    """
    Define the custom blocks that `StreamField` will utilize
    """
    heading_block = HeadingBlock()
    paragraph_block = RichTextBlock(
        icon="fa-paragraph",
        template="blocks/paragraph_block.html"
    )
    image_block = ImageBlock()
    block_quote = BlockQuote()
    embed_block = EmbedBlock(
        help_text='Insert an embed URL e.g https://www.youtube.com/embed/SGJFWirQ3ks',
        icon="fa-s15",
        template="blocks/embed_block.html")
    counter_panel = CounterPanel()
    process_panel = ProcessPanel()
    services_panel = ServicePanel()
    streamform = WagtailFormBlock()
    