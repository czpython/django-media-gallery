import ipdb

from django.utils import simplejson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.cache import never_cache
from django.db import transaction

from endless_pagination.decorators import page_template

from sorl.thumbnail import delete

from celery.result import TaskSetResult

from uploadit.tasks import upload_images as image_uploader
from uploadit.models import UploadedFile

from cms_media_gallery.models import MediaGallery, Collection
from cms_media_gallery.forms import GalleryForm
from cms_media_gallery import signals

UPLOADIT_TEMP_FILES = settings.UPLOADIT_TEMP_FILES


@never_cache
@login_required
def dashboard(request):
    """
        Dislays all galleries that have images.
    """

    galleries = MediaGallery.objects.with_images()
    
    return render_to_response('media-gallery/dashboard.html', 
        {'galleries': galleries}, context_instance=RequestContext(request))


@login_required
def create_gallery(request):
    form = GalleryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        signals.media_gallery_created.send(sender=None, gallery=instance)
        messages.success(request, 'Your gallery has been succesfully created. Now add images to it :)')
        return HttpResponseRedirect(reverse('gallery-upload-images', args=[instance.pk]))
    return render_to_response('media-gallery/add.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def edit_gallery(request, slug):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    form = GalleryForm(request.POST or None, edit=True, instance=gallery)
    if form.is_valid():
        instance = form.save()
        messages.success(request, 'Gallery has been edited succesfully.')
    return render_to_response('media-gallery/edit.html', {'form': form, 'gallery': gallery}, context_instance=RequestContext(request))

@login_required
def upload_images(request, slug):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    taskset_id = request.session.get('uploadit-%s' % gallery.slug, False)
    if taskset_id:
        result = TaskSetResult.restore(taskset_id)
        if result.failed():
            del request.session['uploadit-%s' % gallery.slug]
            result.delete()
            messages.error(request, "Oops, We have encountered an error while uploading your file. Please try again later...")
        elif result.ready() and result.successful():
            # Remove the old task id and result
            del request.session['uploadit-%s' % gallery.slug]
            result.delete()
            if request.POST:
                task = image_uploader(gallery, gallery.created_on, UPLOADIT_TEMP_FILES)
                request.session['uploadit-%s' % gallery.slug] = task.taskset_id
                messages.success(request, 'Your files have been submitted succesfully.')
                return HttpResponseRedirect(reverse('gallery-edit', args=[gallery.pk]))
        else:
            messages.warning(request, "I'm are currently uploading some files, give it some time until you upload again.")
    elif request.POST:
        task = image_uploader(gallery, gallery.created_on, UPLOADIT_TEMP_FILES)
        request.session['uploadit-%s' % gallery.slug] = task.taskset_id
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
    for file_ in gallery.pictures.all():
        delete(file_.file)
    gallery.delete()
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')

@login_required
def delete_image(request, slug, img):
    gallery = get_object_or_404(MediaGallery, pk=slug)
    data = {"success" : "1"}
    try:
        file_ = gallery.pictures.get(pk=img)
    except UploadedFile.DoesNotExist:
        data['success'] = "0"
    else:
        # Need to delete the thumbnail Key Value Store reference
        delete(file_.file)
        file_.delete()
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')


@never_cache
@login_required
def publish_gallery(request, slug):
    """
        Publishes or unpublishes a gallery.
    """
    gallery = get_object_or_404(MediaGallery, slug=slug)
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
    gallery = get_object_or_404(collection.gallery_set.all(), slug=gallery)
    if gallery.published is False and not request.user.is_authenticated():
        raise Http404
    context = {
        'images': gallery.pictures.all(),
        'gallery': gallery,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render_to_response(template, context,
        context_instance=RequestContext(request))