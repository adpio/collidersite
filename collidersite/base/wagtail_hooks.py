from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)

from collidersite.breads.models import Country, BreadIngredient, BreadType
from collidersite.partners.models import Country, PartnerPageTag, PartnerType
from collidersite.people.models import Person
from collidersite.base.models import FooterText
from collidersite.locations.models import LocationPage
from collidersite.industries.models import IndustryPage

'''
N.B. To see what icons are available for use in Wagtail menus and StreamField block types,
enable the styleguide in settings:

INSTALLED_APPS = (
   ...
   'wagtail.contrib.wagtailstyleguide',
   ...
)

or see http://kave.github.io/general/2015/12/06/wagtail-streamfield-icons.html

This demo project includes the full font-awesome set via CDN in base.html, so the entire
font-awesome icon set is available to you. Options are at http://fontawesome.io/icons/.
'''


class BreadIngredientAdmin(ModelAdmin):
    # These stub classes allow us to put various models into the custom "Wagtail Bakery" menu item
    # rather than under the default Snippets section.
    model = BreadIngredient


class BreadTypeAdmin(ModelAdmin):
    model = BreadType


class BreadCountryAdmin(ModelAdmin):
    model = Country


class BreadModelAdminGroup(ModelAdminGroup):
    menu_label = 'Bread Categories'
    menu_icon = 'fa-suitcase'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (BreadIngredientAdmin, BreadTypeAdmin, BreadCountryAdmin)


class PartnerPageTagAdmin(ModelAdmin):
    # These stub classes allow us to put various models into the custom "Wagtail Bakery" menu item
    # rather than under the default Snippets section.
    model = PartnerPageTag


class PartnerTypeAdmin(ModelAdmin):
    model = PartnerType


class PartnerCountryAdmin(ModelAdmin):
    model = Country

class LocationPageAdmin(ModelAdmin):
    model = LocationPage

class PersonAdmin(ModelAdmin):
    model = Person

class IndustryPageAdmin(ModelAdmin):
    model = IndustryPage

#Groups

class PartnerModelAdminGroup(ModelAdminGroup):
    menu_label = 'Partners'
    menu_icon = 'fa-building'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (PartnerPageTagAdmin, PartnerTypeAdmin, PartnerCountryAdmin)


class PeopleModelAdminGroup(ModelAdminGroup):
    menu_label = 'People'
    menu_icon = 'fa-users'
    menu_order = 300
    items = (PersonAdmin,)


class LocationModelAdminGroup(ModelAdminGroup):
    menu_label = 'Locations'
    menu_icon = 'fa-map'
    menu_order = 300
    items = (LocationPageAdmin,)


class IndustryModelAdminGroup(ModelAdminGroup):
    menu_label = 'Industries'
    menu_icon = 'fa-industry'
    menu_order = 300
    items = (IndustryPageAdmin,)


class FooterTextAdmin(ModelAdmin):
    model = FooterText


class BakeryModelAdminGroup(ModelAdminGroup):
    menu_label = 'Bakery Misc'
    menu_icon = 'fa-cutlery'  # change as required
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (FooterTextAdmin,)


# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(BreadModelAdminGroup)
modeladmin_register(BakeryModelAdminGroup)
modeladmin_register(PartnerModelAdminGroup)
modeladmin_register(PeopleModelAdminGroup)
modeladmin_register(LocationModelAdminGroup)
modeladmin_register(IndustryModelAdminGroup)