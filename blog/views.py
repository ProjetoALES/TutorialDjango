from django.views.generic import ListView, DetailView
from .models import Post


class Index(ListView):
    template_name = 'blog/index.html'
    model = Post

    def get_queryset(self):
        return super().get_queryset()


class PostDetail(DetailView):
    template_name = 'blog/post.html'
    model = Post
    slug_field = 'id'
    slug_url_kwarg = 'id'
