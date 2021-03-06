import ipdb

from django.utils import simplejson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.cache import never_cache
from django.db import transaction

from endless_pagination.decorators import page_template

from sorl.thumbnail import delete

from pwd_this.utils import create_pwd

from media_gallery import signals
from media_gallery.models import MediaGallery, Collection
from media_gallery.forms import GalleryForm


@never_cache
@login_required
def dashboard(request):
    """
        Dislays all galleries that have images.
    """

    galleries = MediaGallery.objects.all()
    
    return render_to_response('media-gallery/dashboard.html', 
        {'galleries': galleries}, context_instance=RequestContext(request))


@login_required
def create_gallery(request):
    form = GalleryForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        signals.media_gallery_created.send(sender=None, gallery=instance)
        messages.success(request, 'Your gallery has been succesfully created. Now add images to it :)')
        return HttpResponseRedirect(reverse('gallery-upload-images', args=[instance.pk]))
    return render_to_response('media-gallery/add.html', {'form': form}, context_instance=RequestContext(request))

@never_cache
@login_required
def edit_gallery(request, slug):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    gallery_url = gallery.get_absolute_url()
    password = getattr(gallery.password, 'password', '')
    form = GalleryForm(request.POST or None, edit=True, instance=gallery, initial={'password': password})
    if form.is_valid():
        instance = form.save(commit=False)
        pwd = instance.password
        # Makes sure to only update the password if its required and
        # sets it to "Active".
        if instance.lock and pwd is not None:
            pwd.password = form.cleaned_data['password']
            pwd.active = True
            pwd.save()
        # Check if lock is true and if there's not a password associated with this gallery.
        # if so then create it.
        elif instance.lock and not pwd:
            new = create_pwd(path=gallery_url, password=form.cleaned_data['password'])
            instance.password = new
        # Mark the password object associated with this gallery as "Inactive".
        elif not instance.lock and pwd:
            pwd.active = False
            pwd.save()
        instance.save()
        messages.success(request, 'Gallery has been edited succesfully.')
    return render_to_response('media-gallery/edit.html', 
        {'form': form, 'gallery': gallery}, 
        context_instance=RequestContext(request))

@login_required
def upload_images(request, slug):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    if request.method == "POST":
        messages.success(request, 'Your files have been submitted succesfully.')
        return HttpResponseRedirect(reverse('gallery-edit', args=[gallery.pk]))
    return render_to_response('media-gallery/upload_images.html', 
                                {'gallery': gallery},
                                context_instance=RequestContext(request))

@transaction.commit_on_success
@login_required
def delete_gallery(request, slug):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    data = {"success" : "1"}
    gallery.delete()
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')

@login_required
def delete_image(request, slug, img):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    data = {"success" : "1"}
    try:
        file_ = gallery.images.get(pk=img)
        file_.delete()
    except gallery.images.model.DoesNotExist:
        data['success'] = "0"
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')


@never_cache
@login_required
def publish_gallery(request, slug):
    """
        Publishes or unpublishes a gallery.
    """
    gallery = get_object_or_404(MediaGallery, pk=slug)
    publish = request.GET.get('publish', 'false')
    data = {'success' : "1"}

    if publish == "true":
        try:
            gallery.published = True
            gallery.save()
            # Ahhhhh >:c
        except Exception, e:
            data['success'] = "0"

    elif publish == "false":
        gallery.published = False
        gallery.save()
    else:
        # Seems like someone has modified the param so just return 0
        data['success'] = "0"
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')


@page_template("media-gallery/loaded-galleries.html")
def view_galleries(request, collection, template="media-gallery/collection.html",
    extra_context=None):
    collection = get_object_or_404(Collection, slug=collection)
    context = {
        'galleries': collection.gallery_set.all(),
    }
    if extra_context is not None:
        context.update(extra_context)
    return render_to_response(template, context,
        context_instance=RequestContext(request))


@page_template("media-gallery/loaded-images.html")
def view_gallery(request, collection, gallery, template="media-gallery/gallery.html",
    extra_context=None):
    collection = get_object_or_404(Collection, slug=collection)
    gallery = get_object_or_404(collection.gallery_set.all(), pk=gallery)
    if gallery.published is False and not request.user.is_authenticated():
        raise Http404
    # Client required me to add extra sorting...
    # might as well.
    images = gallery.images.get_custom_sorted()
    context = {
        'images': images,
        'gallery': gallery,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render_to_response(template, context,
        context_instance=RequestContext(request))
