from django_components import component

@component.register("footer")
class Footer(component.Component):
    template_name = "layout/footer/footer.html"
