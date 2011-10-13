from google.appengine.ext import db
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.syndication.feeds import Feed
from google.appengine.api import images

#from appengine_admin.db_extensions import ManyToManyProperty 

from django import forms
from django.utils.translation import ugettext as _

class Messages(db.Model):
	added_on = db.DateTimeProperty(auto_now_add=True)
	source = db.ReferenceProperty(User, collection_name='Messages_out')
	destination = db.ReferenceProperty(User, collection_name='Messages_in')
	title = db.StringProperty(required=True)
	textmail = db.TextProperty(required=True)
	read = db.BooleanProperty(default=False)
	source_visible = db.BooleanProperty(default=True)
	destination_visible = db.BooleanProperty(default=True)


class PersonalPage(db.Model):
	domen = db.StringProperty(required=True)
	imenit = db.StringProperty(required=True)
	datel = db.StringProperty(required=True)
	roditel = db.StringProperty(required=True)
	datebirth = db.DateTimeProperty(required=True)
	country = db.StringProperty(required=True)
	city = db.StringProperty(required=True)
	region = db.StringProperty(required=False)
	photo = db.BlobProperty(required=True)
	user = db.ReferenceProperty(User, collection_name='Personal_page')


class PersonalPage_Form(forms.ModelForm):
	class Meta:
		model = PersonalPage
		exclude = ['user']


class Statistic(db.Model):
	countUsers = db.IntegerProperty()
	count1level = db.IntegerProperty()
	count2level = db.IntegerProperty()
	countNewbies = db.IntegerProperty()
	lastMember = db.TextProperty()
	added_on = db.DateTimeProperty(auto_now_add=True)


class MessagesForm(forms.ModelForm):
	destination = forms.CharField(widget=forms.TextInput(attrs={'class': 'sentmail'}))
	title = forms.CharField(widget=forms.TextInput(attrs={'class': 'sentmail'}))
	textmail = forms.CharField(widget=forms.Textarea(attrs={'class': 'sentmail'}))

	def clean_destination(self):
		destination = self.cleaned_data['destination']
		if User.gql("WHERE username='%s'" % destination).count() > 0:
			return destination
		else:
			raise forms.ValidationError(_('This Username is not exist'))

	class Meta:
		model = Messages
		exclude = ['added_on', 'source']


class Messages_Orders(db.Model):
	added_on = db.DateTimeProperty(auto_now_add=True)
	source = db.ReferenceProperty(User, collection_name='Orders_out')
	destination = db.ReferenceProperty(User, collection_name='Orders_in')
	paysystem = db.StringProperty(default='')
	protection = db.StringProperty(default='')
	activated = db.BooleanProperty(default=False)
	level = db.IntegerProperty(default=1)
	line = db.IntegerProperty(default=1)


class Messages_OrdersForm(forms.ModelForm):
	class Meta:
		model = Messages_Orders
		exclude = ['active', 'added_on', 'level']


class MembersForm(forms.ModelForm):
	class Meta:
		model = User
		exclude = ['level', 'user', 'date', 'email', ]


class AdminForm(forms.ModelForm):
	class Meta:
		model = User
		exclude = ['user_permissions', 'groups', 'parentList', 'childList']


class RestorePasswordForm(forms.ModelForm):
	username = forms.CharField()

	def clean_username(self):
		username = self.cleaned_data['username']
		users = User.gql("WHERE username='%s'" % username.lower())
		if users.count() == 0:
			raise forms.ValidationError(_('This Username is not exist'))

		return users


class RegisterForm(forms.ModelForm):
	username = forms.CharField()
	first_name = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'OFF'}), min_length=6)
	confirm = forms.CharField(widget=forms.PasswordInput, required=False)
	skype = forms.CharField(required=False)
	email = forms.EmailField()
	icq = forms.IntegerField()
	phone = forms.CharField()
	wme = forms.CharField(required=False)
	yandexmoney = forms.CharField(required=False)
	liqpay = forms.CharField(required=False)
	#parents = forms.CharField(required=False, widget = forms.HiddenInput)
	terms = forms.BooleanField(
		widget=forms.CheckboxInput(attrs={'id': 'checkbox'}),
		error_messages={'required': _('You had not agree with the terms of the contract')},
		)

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.gql("WHERE username='%s'" % username.lower()).count() > 0:
			raise forms.ValidationError(_('A user with that username already exists.'))
		return username.lower()

	def clean_parents(self):
		parent = self.cleaned_data['parents']
		parents = User.SetParent([parent])
		#raise forms.ValidationError('vasya parent.username = %s' % parents.username)
		if parents is None:
			raise forms.ValidationError(_('Sorry, but no free areas for you.'))
		return parents

	def clean(self):
		cd = self.cleaned_data
		password = cd.get('password')
		confirm = cd.get('confirm')
		wme = cd.get('wme')
		yandexmoney = cd.get('yandexmoney')
		liqpay = cd.get('liqpay')
		if password != confirm:
			self._errors['confirm'] = self.error_class([_("The two password fields didn't match.")])

		if not wme and not yandexmoney and not liqpay:
			self._errors['wme'] = self.error_class([_('You must specify at least one purse')])

		return cd

	class Meta:
		model = User
		exclude = ['level', 'user', 'parentList', 'childList']


class EditProfile(RegisterForm):
	password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'OFF'}), min_length=6, required=False)
	first_name = forms.CharField()

	def clean_username(self):
		return True

	class Meta:
		model = User
		exclude = ['username', 'parents', 'childList', 'parentList']


class LoginForm(forms.ModelForm):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		data = self.cleaned_data
		user = authenticate(username=data.get('username').lower(), password=data.get('password'))
		if user is not None:
			if user.is_active:
				return user
			else:
				raise forms.ValidationError(_('User is not active.'))
		else:
			raise forms.ValidationError(_('Please enter a correct username and password.'))


class News(db.Model):
	title = db.StringProperty()
	content = db.TextProperty()
	added_on = db.DateTimeProperty(auto_now_add=True)


class NewsForm(forms.ModelForm):
	title = forms.CharField(required=True)
	class Meta:
		model = News
		exclude = ['added_on']


class rss(Feed):
	tite = 'Moneyland'
	link = 'moneyland.su'
	description = 'News from Moneyland'

	def items(self):
		return News.all()

	def item_title(self, item):
		return item.title

	def item_description(self, item):
		return item.description
