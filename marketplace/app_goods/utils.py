class TitleMixin:
    def get_title(self, context):
        return getattr(self, "title", "Megano")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_title(context)
        return context

