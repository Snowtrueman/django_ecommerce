class ProfilePagesMixin:
    def get_subcategory(self, context):
        return getattr(self, "account_title", "")

    def get_active_status(self, context):
        active = getattr(self, "active", "")
        return "menu-item_ACTIVE" if active else ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["account_title"] = self.get_subcategory(context)
        context[f"{self.__class__.__name__.lower()}_active"] = self.get_active_status(context)
        return context
