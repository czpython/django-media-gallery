import ipdb

from django.utils import simplejson
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings


from sorl.thumbnail import delete

from celery.result import TaskSetResult

from uploadit.tasks import upload_images as image_uploader

from cms_media_gallery.models import Gallery
from cms_media_gallery.forms import GalleryForm

UPLOADIT_TEMP_FILES = settings.UPLOADIT_TEMP_FILES

def create_gallery(request):
    form = GalleryForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        messages.success(request, 'Your gallery has been succesfully created. Now add images to it :)')
        return HttpResponseRedirect(reverse('gallery-upload-images', args=[instance.pk]))
    return render_to_response('gallery/add.html', {'form': form}, context_instance=RequestContext(request))

def edit_gallery(request, slug):
    gallery = get_object_or_404(Gallery, pk=slug)
    form = GalleryForm(request.POST or None, instance=gallery)
    if form.is_valid():
        form.save()
        messages.success(request, 'Gallery has been edited succesfully.')
    return render_to_response('gallery/edit.html', {'form': form, 'gallery': gallery}, context_instance=RequestContext(request))

def upload_images(request, slug):
    gallery = get_object_or_404(Gallery, pk=slug)
    try:
        del request.session['uploadit-%s' % gallery.slug]
    except KeyError:
        pass
    taskset_id = request.session.get('uploadit-%s' % gallery.slug, False)
    if taskset_id:
        result = TaskSetResult(taskset_id)
        if request.POST:
            messages.warning(request, 'Please wait a few minutes until your previously submitted files have been uploaded.')
        else:
            messages.warning(request, "I'm are currently uploading some files, give it some time until you upload again.")
    elif request.POST:
        task = image_uploader(gallery, gallery.created_on, UPLOADIT_TEMP_FILES)
        request.session['uploadit-%s' % gallery.slug] = task.taskset_id
        messages.success(request, 'Your files have been submitted succesfully.')
    return render_to_response('gallery/upload_images.html', 
                                {'gallery': gallery},
                                context_instance=RequestContext(request))


def delete_image(request, slug, img):
    gallery = get_object_or_404(Gallery, pk=slug)
    data = {"success" : "1"}
    try:
        picture = gallery.pictures.get(pk=img)
    except Picture.DoesNotExist:
        data['success'] = "0"
    else:
        # Need to delete the thumbnail Key Value Store reference
        delete(picture.image)
        picture.delete()
    response = JSONResponse([data], {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response




class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
