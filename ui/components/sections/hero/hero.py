from django_components import component

@component.register("hero")
class Hero(component.Component):
    template_name = "sections/hero/hero.html"

    def get_context_data(
        self,
        title="",
        subtitle="",
        cta_label="",
        cta_href="#"
    ):
        return {
            "title": title,
            "subtitle": subtitle,
            "cta_label": cta_label,
            "cta_href": cta_href,
        }
