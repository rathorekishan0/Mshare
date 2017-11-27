from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import Http404
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render,redirect,get_object_or_404,_get_queryset,HttpResponse
from django.contrib.auth import authenticate,login
from django.views.generic import View,CreateView,ListView,DetailView
from django.views import View
from .models import userprofile,music
from .forms import musicform,profileform,UserRegisterForm
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

User=get_user_model()
AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

@login_required
def indexpage(request):
    qs=userprofile.objects.get(user=request.user)
    if qs.first:
        print(request.user)
        print(request.user.id)
        print(qs.id)
        path=reverse_lazy('music:profilecreate',kwargs={'pk':qs.id})
        print(path)
        return redirect(path)
    else:
        return redirect('music:homefeed')

class myfav(LoginRequiredMixin,ListView):
    model = music
    template_name = 'music/favorites.html'
    def get_context_data(self,*args,**kwargs):
        context=super(myfav,self).get_context_data(*args,**kwargs)
        user=self.request.user
        songs=music.objects.all()
        li=[]
        for i in songs:
            if user in i.likes.all():
                li.append(i)
        context['songs']=li
        print(li)
        return context

class follower(LoginRequiredMixin,ListView):
    model = User
    template_name = 'music/follower.html'
    def get_context_data(self,*args,**kwargs):
        context=super(follower,self).get_context_data(*args,**kwargs)
        user=self.request.user
        qs=user.userprofile.followers.all()
        context['users']=qs
        return context

class welcome(LoginRequiredMixin,ListView):
    model = userprofile
    template_name = 'music/welcome.html'
    def get_context_data(self,*args,**kwargs):
        context=super(welcome,self).get_context_data(*args,**kwargs)
        user=self.request.user
        qs=userprofile.objects.filter(prefferedgenre=user.userprofile.prefferedgenre)
        context['person']=qs
        print(qs)
        return context

class following(LoginRequiredMixin,ListView):
    model = userprofile
    template_name = 'music/following.html'
    def get_context_data(self,*args,**kwargs):
        context=super(following,self).get_context_data(*args,**kwargs)
        user=self.request.user
        qs=user.is_following.all()
        context['users']=qs
        print(qs)
        return context


class searchview(View):
    def post(self,request,**kwargs):
        q=request.POST.get('q')
        print(q)
        qname = userprofile.objects.filter(name__contains=q).order_by('name')
        qsong = music.objects.filter(songname__contains=q).order_by('-likenum')
        qgenre = music.objects.filter(genre__contains=q).order_by('-likenum')
        return render(request,'music/search-list.html',{'qname':qname,'qsong':qsong,'qgenre':qgenre})

    # def post(self,request,**kwargs):
    #     q=request.GET.get['q']
    #     if q is None:
    #         redirect('music:homefeed')
    #     print(q)
    #     qname=userprofile.objects.filter(name__contains=q).order_by('name')[:5]
    #     qsong=music.objects.filter(songname__contains=q).order_by('-like')[:5]
    #     qgenre=music.objects.filter(genre__contains=q).order_by('-like')[:5]
    #     return render(request,'music/search-list.html',{'qname':qname,'qsong':qsong,'qgenre':qgenre,'error':error})


def activate_user_view(request, code=None, *args, **kwargs):
    if code:
        qs = userprofile.objects.filter(activation_key=code)
        if qs.exists() and qs.count() == 1:
            profile = qs.first()
            if not profile.activated:
                user_=profile.user
                user_.is_active=True
                user_.save()
                profile.activated=True
                profile.activation_key=None
                profile.save()
                path=reverse_lazy('music:login')
                return redirect(path)
    # invalid code
    return redirect('/music/login')

class registerview(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('music:activation')
    def dispatch(self,*args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect('/music/login')
        return super(registerview,self).dispatch(*args,**kwargs)


# @login_required
class profilefollowtoggle(LoginRequiredMixin,View):

    def post(self,request,**kwargs):
        username_to_toggle=request.POST.get('username')
        print(username_to_toggle)
        profile_,is_following=userprofile.objects.toggle_follow(request.user,username_to_toggle)
        return redirect('music:profiledetail',profile_.slug)

class liketoggle(LoginRequiredMixin,View):
    def post(self,request,**kwargs):
        songtolike=request.POST.get('songid')
        song=music.objects.get(id=songtolike)
        user = request.user
        like_by = False
        if user in song.likes.all():
            song.likes.remove(user)

        else:
            song.likes.add(user)
            liked_by = True
        return redirect('music:songplay',pk=songtolike)


# class indexlistview(LoginRequiredMixin,generic.ListView):
#     template_name = 'music/index.html'
#     context_object_name = 'allalbum'
#     def get_queryset(self):
#         return music.objects.filter(user=self.request.user)

class homeview(LoginRequiredMixin,View):

    def get(self,request,*args,**kwargs):
        if not request.user.is_authenticated():
            return render(request, 'registration/login1.html', {})
        user=request.user
        liked_by=False
        is_following_user_id=[x.user.id for x in user.is_following.all()]
        recartist=[]
        for x in userprofile.objects.filter(prefferedgenre=user.userprofile.prefferedgenre):
            print(x)
            if not(x in user.is_following.all()):
                    recartist.append(x)
        print(recartist)
        qs=music.objects.filter(artist__id__in=is_following_user_id,public=True).order_by('-timestamp')#[:]
        trend = music.objects.all().order_by('-likenum')[:5]

        return render(request,'music/homefeed.html',{'feed':qs,'trendlist':trend,'user':user,'rec':recartist})

class profiledetail(LoginRequiredMixin,DetailView):
    model = User
    template_name = 'music/profiledetail.html'
    def get_object(self,*args,**kwargs):
        slug=self.kwargs.get('slug')
        if slug==None:
            raise Http404
        else:
            qs=userprofile.objects.get(slug=slug)
            return qs.user
            # return get_object_or_404(User, user__iexact=username, is_active=True)
    # def get_queryset(self):
    #     return User.userprofile.objects.get(user=self.request.user)
    def get_context_data(self,*args,**kwargs):
        context=super(profiledetail,self).get_context_data(**kwargs)
        user=context['user']
        is_following=False
        if user.userprofile in self.request.user.is_following.all():
            is_following=True
        context['is_following']=is_following
        context['user_songlist']=user.music_set.all().order_by('-timestamp')[4:]
        qs=user.music_set.all().order_by('-timestamp')[:4]
        qslike=user.liked_by.all()[:4]
        context['qlike']=user.liked_by.all()[4:]
        context['qfollowers']=user.userprofile.followers.all()[4:]
        context['followerfirst']=user.userprofile.followers.all()[:4]
        context['likefour']=qslike
        qfirst=user.is_following.all()[:4]
        print(qfirst)
        qfollowing=user.is_following.all()[4:]
        context['qfirst']=qfirst
        context['qfollowing']=qfollowing
        context['firstfour']=qs
        # li=[]
        # for i in range(4):
        #     li.append()
        return context


class createmusic(LoginRequiredMixin,CreateView):
    template_name = 'music/createmusic.html'
    # context_object_name = 'allalbum'
    form_class =musicform
    success_url = reverse_lazy('music:indexpage')
    def form_valid(self, form):
        instance=form.save(commit=False)
        instance.artist=self.request.user
        # instance.songphoto = self.request.FILES['songphoto']
        # file_type = instance.songphoto.url.split('.')[-1]
        # file_type = file_type.lower()
        # if file_type not in IMAGE_FILE_TYPES:
        #     context = {
        #         'music': music,
        #         'form': form,
        #         'error_message': 'Image file must be PNG, JPG, or JPEG',
        #     }
        #     return render(self.request, 'music/createmusic.html', context)
        # instance.save()
        return super(createmusic,self).form_valid(form)
    # def get_form_kwargs(self):
    #     kwargs=super(createmusic,self).get_form_kwargs()
    #     kwargs['user']=self.request.user
    #     return kwargs
    def get_queryset(self):
        return music.objects.filter(user=self.request.user)


class profilecreate(LoginRequiredMixin,UpdateView):
    model=userprofile
    template_name = 'music/profilecreate.html'
    form_class = profileform
    success_url = reverse_lazy('music:welcome')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        print(self.object)
        print(self.object.first)
        self.object.first=False
        print(self.object.first)
        return super(profilecreate, self).form_valid(form)


class songplay(LoginRequiredMixin,DetailView):
    model = music
    template_name='music/songplay.html'
    def get_context_data(self,*args,**kwargs):
        context=super(songplay,self).get_context_data(*args,**kwargs)
        print(context)
        # s=context['object']
        # qs=music.objects.filter(genre__exact=s.genre)
        qs=music.objects.all()
        context['songs']=qs
        # paginator = Paginator(qs, 4)  # Show 25 contacts per page
        #
        # page = self.request.GET.get('page')
        # try:
        #     q = paginator.page(page)
        # except PageNotAnInteger:
        #     # If page is not an integer, deliver first page.
        #     q = paginator.page(1)
        # except EmptyPage:
        #     # If page is out of range (e.g. 9999), deliver last page of results.
        #     q = paginator.page(paginator.num_pages)
        # context['q']=q
        return context






# class albumupdate(UpdateView):
#     model = album
#     fields = ['artist','albumtitle','genre','albumlogo']
#
# class albumdelete(DeleteView):
#     model = music
#     success_url = reverse_lazy('music: index')

# class UserFormView(View):
#     form_class=UserForm
#     template_name='music/registerform.html'
#     def get(self,request):
#         form=self.form_class(None)
#         return render(request,self.template_name,{'form':form})
#     def post(self,request):
#         form=self.form_class(request.POST)
#         if form.is_valid():
#             username=form.cleaned_data['username']
#             password=form.cleaned_data['password']
#             user.set_password(password)
#             user.save()
#             user=authenticate(username=username,password=password)
#             if user is not None:
#                 if user.is_active:
#                     login(request,user)
#                     return redirect('music:profile')
#         return render(request,self.template_name,{'form':form})

# def SpecificSong(request, songName):
#     song = music.objects.get(songname = songName)
#     context = {'song':song}
#     return render_to_response('musicadd.html',context, context_instance=RequestContext(request))

