import json

from django.contrib.gis.forms import BaseGeometryWidget
from django.contrib.gis.geos import Point
from django.core.exceptions import ImproperlyConfigured

from mapwidgets.settings import mw_settings


class GoogleMapWidget(BaseGeometryWidget):
    template_name = "mapwidgets/google-map-widget.html"

    class Media:
        css = {
            "all": (
                "mapwidgets/css/map_widgets.css",
                )
        }

        js = (
            "https://maps.googleapis.com/maps/api/js?libraries=places&key=%s" % mw_settings.GOOGLE_MAP_API_KEY,
            "mapwidgets/js/jquery_class.min.js",
            "mapwidgets/js/django_mw_base.js",
            "mapwidgets/js/django_mw_google_map.js",
        )

    @staticmethod
    def map_options():
        return json.dumps(mw_settings.map_conf)

    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = dict()

        field_value = {}
        if isinstance(value,  Point):
            field_value["lng"] = value.x
            field_value["lat"] = value.y

        if value and isinstance(value, basestring):
            coordinates = self.deserialize(value)
            field_value["lng"] = coordinates.x
            field_value["lat"] = coordinates.y

        extra_attrs = {
            "options": self.map_options(),
            "field_value": json.dumps(field_value)
        }

        attrs.update(extra_attrs)
        return super(GoogleMapWidget, self).render(name, value, attrs)


class InlineMapWidgetMixin(object):
    inline_add_row_jquery_selector = None

    def get_js_widget_data(self, name, element_id):
        if not self.inline_add_row_jquery_selector:
            raise ImproperlyConfigured(
                "The '%s' does not specify "
                "a 'inline_add_row_jquery_selector'." % self.__class__.__name__)

        map_elem_selector = "#%s-mw-wrap" % name
        map_elem_id = "%s-map-elem" % name
        google_auto_input_id = "%s-mw-google-address-input" % name
        location_input_id = "#%s" % element_id
        js_widget_params = {
            "inline_add_row_jquery_selector": self.inline_add_row_jquery_selector,
            "wrapElemSelector": map_elem_selector,
            "mapElemID": map_elem_id,
            "googleAutoInputID": google_auto_input_id,
            "locationInputID": location_input_id
        }
        return js_widget_params


class GoogleInlineMapWidget(InlineMapWidgetMixin, GoogleMapWidget):
    inline_add_row_jquery_selector = None
    template_name = "mapwidgets/google-inline-map-widget.html"

    class Media:
        css = {
            "all": (
                "mapwidgets/css/map_widgets.css",
            )
        }

        js = (
            "https://maps.googleapis.com/maps/api/js?libraries=places&key=%s" % mw_settings.GOOGLE_MAP_API_KEY,
            "mapwidgets/js/jquery_class.min.js",
            "mapwidgets/js/django_mw_base.js",
            "mapwidgets/js/django-mw-generater.js",
            "mapwidgets/js/django_mw_google_map.js",
        )

    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = dict()

        element_id = attrs.get("id")
        is_formset_empty_from_template = "__prefix__" in element_id
        widget_data = self.get_js_widget_data(name, element_id)
        attrs.update({
            "js_widget_data": json.dumps(widget_data),
            "is_formset_empty_from_template": is_formset_empty_from_template
        })
        return super(GoogleInlineMapWidget, self).render(name, value, attrs)


class DjangoAdminInlineGoogleMapWidget(GoogleInlineMapWidget):
    inline_add_row_jquery_selector = ".inline-group .add-row a"

