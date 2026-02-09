from django_components import component

@component.register("footer")
class Footer(component.Component):
    template_name = "layout/footer/footer.html"

    def get_context_data(
        self,
        institution_name: str,
        description: str,
        navigation: list,
        contact: dict,
        legal_links: list,
    ):
        return {
            "institution_name": institution_name,
            "description": description,
            "navigation": navigation,
            "contact": contact,
            "legal_links": legal_links,
        }
