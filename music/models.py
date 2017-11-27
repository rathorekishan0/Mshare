from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save,pre_save,m2m_changed
from django.dispatch import receiver
from django.core.urlresolvers import reverse
# from django.conf import settings
# from .utils import unique_slug_generator
from django.core.mail import send_mail
from .utils import code_generator
from music.utils import unique_slug_generator,code_generator
from django.core.validators import FileExtensionValidator


# User=settings.AUTH_USER_MODEL

class userprofilemanager(models.Manager):
    def toggle_follow(self,request_user,username_to_toggle):
        profile=userprofile.objects.get(user__username__iexact=username_to_toggle)
        user=request_user
        is_following=False
        if user in profile.followers.all():
            profile.followers.remove(user)

        else:
            profile.followers.add(user)
            is_following=True
        return profile,is_following

class userprofile(models.Model):
    user=models.OneToOneField(User)
    activation_key=models.CharField(max_length=250,null=True,blank=True)
    name=models.CharField(max_length=100)
    userphoto=models.ImageField(upload_to='static/music/userimages',validators=[FileExtensionValidator(['jpeg','png','bmp','jpg'],"file exteion not valid")],null=True)
    # username=models.CharField(max_length=50)
    # emailid=models.CharField(max_length=100)
    description=models.CharField(max_length=200)
    first=models.BooleanField(default=True)
    prefferedgenre=models.CharField(max_length=20)
    slug = models.SlugField(null=True,blank=True)
    timestamp = models.DateTimeField(null=True,blank=True)
    followers=models.ManyToManyField(User,related_name='is_following',blank=True)
    # followingd=models.ManyToManyField(User,related_name='following',blank=True)
    activated=models.BooleanField(default=False)
    objects=userprofilemanager()
    def __str__(self):
        return self.user.username
    def get_absolute_url(self):
        return reverse('detail-page',kwargs={'slug':self.slug})
    def send_activation_email(self):
        if not self.activated:
            self.activation_key=code_generator()
            self.save()
            path_=reverse('music:activate',kwargs={'code':self.activation_key})
            path_='http://127.0.0.1:8000'+path_
            subject = 'Mshare email activation'
            from_email = settings.DEFAULT_FROM_EMAIL
            message = f'activate your account here: {path_}'
            recipient_list = [self.user.email]
            html_message = f'<h1>activate your account here: {path_}</h1>'
            sent_mail=send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)
            return sent_mail

def post_save_user_reciever(sender,instance,created,*args,**kwargs):
    if created:
        profile, is_created=userprofile.objects.get_or_create(user=instance)

post_save.connect(post_save_user_reciever,sender=User)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         userprofile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()

class music(models.Model):
    artist=models.ForeignKey(User,on_delete=models.CASCADE)
    songname=models.CharField(max_length=50)
    description=models.CharField(max_length=200)
    genre=models.CharField(max_length=30)
    songphoto=models.FileField(upload_to="static/music/songimages",validators=[FileExtensionValidator(['jpeg','png','bmp','jpg'],"file exteion not valid")])
    songupload=models.FileField(upload_to="static/music/songs", validators=[FileExtensionValidator(['mp3','aac'],"file extension not valid")])
    likes=models.ManyToManyField(User,related_name='liked_by',blank=True)
    likenum=models.IntegerField(default=0)
    timestamp=models.DateField(auto_now_add=True)
    public=models.BooleanField(default=True)
    favourites=models.ManyToManyField(User,related_name='favourite_by',blank=True)
    def __str__(self):
        return self.artist.userprofile.name+'-'+ self.songname
    class Meta:
        ordering=['timestamp']


@property
def title(self):
    return self.name
def rl_pre_save_reciever(sender,instance,*args,**kwargs):
    print('saving..')
    print(instance.timestamp)
    if not instance.slug:
        if instance.first is False:
            instance.slug=unique_slug_generator(instance)

def rl_post_save_reciever(sender, instance, created , *args, **kwargs):
    print('saved')
    print(instance.timestamp)
    if not instance.slug and instance.first is False:
        instance.slug=unique_slug_generator(instance)
        instance.save()

@receiver(m2m_changed, sender=music.likes.through)
def addlike(sender,instance,action,**kwargs):
    print(instance)
    print('in model')
    if action=="post_add":
        i=instance.likenum
        print(i)
        instance.likenum=i+1
        instance.save()
        print(instance.likenum)
    if action=='post_remove':
        i =instance.likenum
        print(i)
        instance.likenum=i-1
        instance.save()
        print(instance.likenum)


pre_save.connect(rl_pre_save_reciever,sender=userprofile)
post_save.connect(rl_post_save_reciever,sender=userprofile)
