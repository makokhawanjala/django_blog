from django.core.paginator import EmptyPage,PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Post, Comment
from django.http import Http404
from .forms import CommentForm
from django.views.generic import ListView

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        return Post.published.all()

def post_list(request):
    post_list = Post.published.all()

    # pagination with 3 posts per page
    paginator = Paginator(post_list, 3)  # Show 3 posts per page.
    page_number = request.GET.get('page', 1)
    #posts= paginator.get_page(page_number)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts}) 

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for new comment
    form = CommentForm()
     
    return render(request, 'blog/post/detail.html', {'post': post,'comments': comments, 'form': form})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted.
    form = CommentForm(data=request.POST)
    #print(f"Form data: {form}")
    if form.is_valid():
        # Create a Comment object but don't save to database yet
        comment = form.save(commit=False)
        # Assign the current post to the comment
        comment.post = post
        #print(f"Comment before saving: {comment}")
        # Save the comment to the database
        comment.save()
    else:
        form = CommentForm()
    
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})