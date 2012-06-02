import ipdb

from django.utils import simplejson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.cache import never_cache
from django.db import transaction

from sorl.thumbnail import delete

from celery.result import TaskSetResult

from uploadit.tasks import upload_images as image_uploader
from uploadit.models import UploadedFile

from cms_media_gallery.models import CMSMediaGallery
from cms_media_gallery.forms import GalleryForm
from cms_media_gallery.utils import get_or_create_page, cms_recursive_publish

UPLOADIT_TEMP_FILES = settings.UPLOADIT_TEMP_FILES

try:
    CMS_MEDIA_GALLERY_PAGE = settings.CMS_MEDIA_GALLERY_PAGE
except AttributeError:
    raise ImproperlyConfigured("Please create a page for CMS_MEDIA_GALLERY and add its reverse_id to settings.CMS_MEDIA_GALLERY_PAGE")


@never_cache
def dashboard(request):
    """
        Dislays all galleries that have images.
    """

    galleries = CMSMediaGallery.objects.with_images()
    return render_to_response('cms_media_gallery/dashboard.html', 
        {'galleries': galleries}, context_instance=RequestContext(request))



def create_gallery(request):
    form = GalleryForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        parent = get_or_create_page(
            parent=dict(reverse_id=CMS_MEDIA_GALLERY_PAGE), 
            child=form.cleaned_data['parent'], 
            template='cms_media_gallery/set.html'
        )
        page = get_or_create_page(parent, instance.name, template='cms_media_gallery/gallery.html', )
        instance.cms_page = page
        instance.save()
        messages.success(request, 'Your gallery has been succesfully created. Now add images to it :)')
        return HttpResponseRedirect(reverse('gallery-upload-images', args=[instance.pk]))
    return render_to_response('cms_media_gallery/add.html', {'form': form}, context_instance=RequestContext(request))

def edit_gallery(request, slug):
    gallery = get_object_or_404(CMSMediaGallery, pk=slug)
    form = GalleryForm(request.POST or None, edit=True, instance=gallery, 
        initial=dict(parent=gallery.cms_page.parent, publish=gallery.cms_page.published))
    if form.is_valid():
        instance = form.save()
        # Yes I know, repeated code.... 
        # I need to do this so that if the user changes the "parent" field value,
        # its page gets created.
        parent = get_or_create_page(
            parent=dict(reverse_id=CMS_MEDIA_GALLERY_PAGE), 
            child=form.cleaned_data['parent'], 
            template='cms_media_gallery/gallery.html'
        )
        # And here i move the gallery to the newly created page.
        # Nothing happens ( as far as i know ) if i move it to the same location.
        instance.cms_page.move_page(target=parent)
        messages.success(request, 'Gallery has been edited succesfully.')
    return render_to_response('cms_media_gallery/edit.html', {'form': form, 'gallery': gallery}, context_instance=RequestContext(request))

def upload_images(request, slug):
    gallery = get_object_or_404(CMSMediaGallery, pk=slug)
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
        else:
            messages.warning(request, "I'm are currently uploading some files, give it some time until you upload again.")
    elif request.POST:
        task = image_uploader(gallery, gallery.created_on, UPLOADIT_TEMP_FILES)
        request.session['uploadit-%s' % gallery.slug] = task.taskset_id
        messages.success(request, 'Your files have been submitted succesfully.')
    return render_to_response('cms_media_gallery/upload_images.html', 
                                {'gallery': gallery},
                                context_instance=RequestContext(request))

@transaction.commit_on_success
def delete_gallery(request, slug):
    gallery = get_object_or_404(CMSMediaGallery, pk=slug)
    data = {"success" : "1"}
    for file_ in gallery.pictures.all():
        delete(file_.file)
    gallery.delete()
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')


def delete_image(request, slug, img):
    gallery = get_object_or_404(CMSMediaGallery, pk=slug)
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
def publish_gallery(request, slug):
    """
        Publishes a gallery and its parents.
        It also unpublishes the gallery, but not its parents.
        I use the never_cache decorator because if not then browser caches the response
        and never changes the page.
    """
    gallery = get_object_or_404(CMSMediaGallery, pk=slug)
    cms_page = gallery.cms_page
    publish = request.GET.get('publish', 'false')
    data = {'success' : "1"}

    if publish == "true":
        try:
            cms_recursive_publish(cms_page, request.user)
            # Ahhhhh >:c
        except Exception, e:
            data['success'] = "0"

    elif publish == "false":
        cms_page.published = False
        cms_page.save()
    else:
        # Seems like someone has modified the param so just return 0
        data['success'] = "0"
    response = simplejson.dumps(data)
    return HttpResponse(response, mimetype='application/json')
