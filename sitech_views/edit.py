from django.views.generic import (
    DeleteView as DjangoDeleteView, UpdateView as DjangoUpdateView,
    CreateView as DjangoCreateView, FormView as DjangoFormView, View
)
from django.views.generic.edit import BaseUpdateView
from django.http import HttpResponseRedirect


class FormView(DjangoFormView):
    """A view for displaying a form and rendering a template response."""


class CreateView(DjangoCreateView):
    """
    View for creating a new object, with a response rendered by a template.
    """


class UpdateView(DjangoUpdateView):
    """View for updating an object, with a response rendered by a template."""
    def get(self, request, *args, **kwargs):
        before_get_object = self.before_get_object()
        if before_get_object:
            return before_get_object
        self.object = self.get_object()
        after_get_object = self.after_get_object()
        if after_get_object:
            return after_get_object
        return super(BaseUpdateView).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        before_get_object = self.before_get_object()
        if before_get_object:
            return before_get_object
        self.object = self.get_object()
        after_get_object = self.after_get_object()
        if after_get_object:
            return after_get_object
        return super(BaseUpdateView).post(request, *args, **kwargs)

    def before_get_object(self):
        pass

    def after_get_object(self):
        pass


class DeleteView(DjangoDeleteView):
    """
    View for deleting an object retrieved with self.get_object(), with a
    response rendered by a template.
    """
    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        before_get_object = self.before_get_object()
        if before_get_object:
            return before_get_object
        self.object = self.get_object()
        after_get_object = self.after_get_object()
        if after_get_object:
            return after_get_object
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def before_get_object(self):
        pass

    def after_get_object(self):
        pass
