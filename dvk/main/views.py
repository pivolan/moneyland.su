from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from google.appengine.api import images

from pprint import pprint

from dvk.main.util import render_to
from dvk.main.models import *

from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import users as googleUser

import timeit
import re
import random
import datetime
from datetime import timedelta
import os

PARTNER = "partner_"
CHILDREN = "children_"
# memcache keys for index page

class m:
	countUsers = 'countUsers'
	news3 = 'news'
	count1level = 'count1level'
	count2level = 'count2level'
	countNewbies = 'countNewbies'
	lastMember = 'lastMember'

	@staticmethod
	def keys():
		return dir(m)[2:]

	# start pages

def index(request, refurl=None):
	needData = m.keys()
	result = memcache.get_multi(needData)
	needData = [k for k in needData if k not in result]
	if len(needData) > 0:
		stat = Statistic.gql('ORDER BY added_on DESC LIMIT 1').get()
		toCache = {}
		for key in needData:
			if key == m.news3:
				news3 = News.gql('ORDER BY added_on DESC LIMIT 3')
				news = []
				for new in news3:
					news.append(new)
				result[m.news3] = news
				toCache[m.news3] = news
			elif key == m.countUsers:
				result[m.countUsers] = User.all().count()
			#				stat.countusers
			#				toCache[m.countUsers] = result[m.countUsers]
			elif key == m.count1level:
				#result[m.count1level] = stat.count1level
				User.gql('WHERE level=1').count()
			#toCache[m.count1level] = result[m.count1level]
			elif key == m.count2level:
				#result[m.count2level] = stat.count2level #
				User.gql('WHERE level=2').count()
			#toCache[m.count2level] = result[m.count2level]
			elif key == m.countNewbies:
				result[m.countNewbies] = User.gql(
					'WHERE date_joined >= DATETIME(:1,:2,:3)',
					datetime.date.today().year,
					datetime.date.today().month,
					datetime.date.today().day,
					).count()
			#				result[m.countNewbies] = stat.countNewbies
			#				toCache[m.countNewbies] = result[m.countNewbies]
			elif key == m.lastMember:
				user = User.gql('ORDER BY date_joined DESC LIMIT 1').get()
				#				if(stat):
				#					result[m.lastMember] = stat.lastMember#user.username
				#				else:
				#					result[m.lastMember] = ''
				result[m.lastMember] = user.username
				toCache[m.lastMember] = result[m.lastMember]
		if len(toCache) > 0:
			memcache.set_multi(toCache, time=60 * 60 * 5)

	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			login(request, form.cleaned_data)
			return HttpResponseRedirect('/user/')
	else:
		form = LoginForm()

	result['form'] = form
	response = render_to_response("index.html", result, context_instance=RequestContext(request))
	if refurl is not None and refurl.isdigit():
		member = User.get_by_id(int(refurl))
		if member:
			if member.level > 0:
				max_age = 30 * 24 * 60 * 60
				expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
				                                     "%a, %d-%b-%Y %H:%M:%S GMT")
				response.set_cookie('referal', member.key().id(), max_age=max_age, expires=expires)
	return response


@render_to('news.html')
def news(request, id):
	needData = ['news10', 'new_%s' % id]
	result = memcache.get_multi(['news10', 'new_%s' % id])
	needData = [k for k in needData if k not in result]

	toCache = {}
	newsFlag = True
	newFlag = True
	for key in needData:
		if key == 'news10':
			news10 = News.gql('ORDER BY added_on DESC LIMIT 10')
			news = []
			for new in news10:
				news.append(new)
			result[m.news3] = news
			toCache['news10'] = news
			newsFlag = False
		elif key == 'new_%s' % id:
			result['new'] = News.get_by_id(int(id))
			toCache['new_%s' % id] = result['new']
			newFlag = False
	if len(toCache) > 0:
		memcache.set_multi(toCache)
	if newFlag:
		result['new'] = result['new_%s' % id]
	if newsFlag:
		result[m.news3] = result['news10']
	return result


@login_required
def user(request, page):
	form = Messages_OrdersForm()
	if request.method == 'POST':
		form = Messages_OrdersForm(request.POST)
		if form.is_valid():
			order = form.save(commit=False)
			order.source = request.user
			order.put()
			return HttpResponseRedirect('/user/%s.html' % page)
	try:
		return render_to_response('/user/%s.html' % page, {'form': form}, context_instance=RequestContext(request))
	except:
		return HttpResponseRedirect('/user/status.html')


@login_required
@render_to('user/books1.html')
def user_books1(request):
	return {}


@login_required
@render_to('user/books2.html')
def user_books2(request):
	return {}


@login_required
@render_to('user/news.html')
def user_news(request):
	user = request.user
	newMessages = user.Messages_in.filter('added_on >', datetime.datetime.today() - timedelta(days=1)).count()
	unreadInMessages = user.Messages_in.filter('read =', False).count()
	unreadOutMessages = user.Messages_out.filter('read =', False).count()
	lines = [[], [], []]
	periods = [[], [], []]
	unreads = []
	withOrders = []
	lines[0] += user.children.filter('date_joined >', datetime.datetime.today() - timedelta(days=4))
	periods[0] += user.children.filter('last_login <', datetime.datetime.today() - timedelta(days=3)).filter(
		'last_login >=', datetime.datetime.today() - timedelta(days=7))
	periods[1] += user.children.filter('last_login <', datetime.datetime.today() - timedelta(days=7)).filter(
		'last_login >=', datetime.datetime.today() - timedelta(days=31))
	periods[2] += user.children.filter('last_login <', datetime.datetime.today() - timedelta(days=31))
	for ch in user.children:
		periods[0] += ch.children.filter('last_login <', datetime.datetime.today() - timedelta(days=3)).filter(
			'last_login >=', datetime.datetime.today() - timedelta(days=7))
		periods[1] += ch.children.filter('last_login <', datetime.datetime.today() - timedelta(days=7)).filter(
			'last_login >=', datetime.datetime.today() - timedelta(days=31))
		periods[2] += ch.children.filter('last_login <', datetime.datetime.today() - timedelta(days=31))
		if ch.Messages_in.filter('read =', False).filter('source =', user).count() > 0:
			unreads += [ch]
		if ch.Orders_in.filter('activated =', False).count() > 0:
			withOrders += [ch]

		lines[1] += ch.children.filter('date_joined >', datetime.datetime.today() - timedelta(days=4))
		for chch in ch.children:
			periods[0] += chch.children.filter('last_login <', datetime.datetime.today() - timedelta(days=3)).filter(
				'last_login >=', datetime.datetime.today() - timedelta(days=7))
			periods[1] += chch.children.filter('last_login <', datetime.datetime.today() - timedelta(days=7)).filter(
				'last_login >=', datetime.datetime.today() - timedelta(days=31))
			periods[2] += chch.children.filter('last_login <', datetime.datetime.today() - timedelta(days=31))
			if chch.Messages_in.filter('read =', False).filter('source =', user).count() > 0:
				unreads += [chch]
			if chch.Orders_in.filter('activated =', False).count() > 0:
				withOrders += [chch]
			lines[2] += chch.children.filter('date_joined >', datetime.datetime.today() - timedelta(days=4))
			for chchch in chch.children:
				if chchch.Messages_in.filter('read =', False).filter('source =', user).count() > 0:
					unreads += [chchch]
				if chchch.Orders_in.filter('activated =', False).count() > 0:
					withOrders += [chchch]

	return {
		'lines': lines,
		'periods': periods,
		'unreads': unreads,
		'withOrders': withOrders,
		'newMessages': newMessages,
		'unreadInMessages': unreadInMessages,
		'unreadOutMessages': unreadOutMessages,
		}


@login_required
@render_to('user/status.html')
def user_status(request):
	user = request.user
	price1 = [5, 50, 500, 500]
	price3 = [10, 100, 1000, 1000]
	if request.method == "POST":
		if request.POST['orderid'].isdigit():
			order = Messages_Orders.get_by_id(int(request.POST['orderid']))
			if order:
				if order.destination.level > user.level:
					order.paysystem = request.POST['paysystem']
					order.protection = request.POST['protection']
					order.save()
					msg = render_to_string("mail/order.html", {'order': order, 'body': True})
					title = render_to_string("mail/order.html", {'title': True})

					mail.send_mail(sender="no-reply@moneyland.su",
					               to="%s <%s>" % (user.first_name, user.email),
					               subject=title,
					               body=msg
					)

				return HttpResponseRedirect('/user/')

		parent = User.get_by_id(int(request.POST['destination']))
		if parent:
			if parent.level > user.level:
				order = Messages_Orders(
					destination=parent,
					level=user.level + 1,
					source=user,
					paysystem=request.POST['paysystem'],
					protection=request.POST['protection'],
					line=int(request.POST['line']),
					)
				msg = render_to_string("mail/order.html", {'order': order, 'body': True})
				title = render_to_string("mail/order.html", {'title': True})
				mail.send_mail(sender="no-reply@moneyland.su",
				               to="%s <%s>" % (user.first_name, user.email),
				               subject=title,
				               body=msg
				)
				order.save()
			return HttpResponseRedirect('/user/')

	parent = request.user.parents
	orders = []
	parents = []
	orderscount = [
		user.Orders_in.filter('level =', 1).filter('activated =', False).count(),
		user.Orders_in.filter('level =', 2).filter('activated =', False).count(),
		user.Orders_in.filter('level =', 3).filter('activated =', False).count(),
		]
	activeorderscount = [
		user.Orders_in.filter('level =', 1).filter('activated =', True).count(),
		user.Orders_in.filter('level =', 2).filter('activated =', True).count(),
		user.Orders_in.filter('level =', 3).filter('activated =', True).count(),
		]
	if parent:
		orders += [user.Orders_out.filter('destination =', parent).filter('level =', user.level + 1).get()]
		parents = [
				{
				'username': parent.username,
				'first_name': parent.first_name,
				'email': parent.email,
				'id': parent.key().id(),
				'icq': parent.icq,
				'phone': parent.phone,
				'skype': parent.skype,
				'level': parent.level,
				'wme': parent.wme,
				'yandexmoney': parent.yandexmoney,
				'liqpay': parent.liqpay,
				'price': price1[user.level],
				'order': orders[0],
				}]

		if parent.parents:
			orders += [user.Orders_out.filter('destination =', parent.parents).filter('level =', user.level + 1).get()]
			parents.append({
				'username': parent.parents.username,
				'first_name': parent.parents.first_name,
				'email': parent.parents.email,
				'id': parent.parents.key().id(),
				'icq': parent.parents.icq,
				'phone': parent.parents.phone,
				'skype': parent.parents.skype,
				'level': parent.parents.level,
				'yandexmoney': parent.parents.yandexmoney,
				'liqpay': parent.parents.liqpay,
				'wme': parent.parents.wme,
				'price': price1[user.level],
				'order': orders[1],
				})
			if parent.parents.parents:
				orders += [user.Orders_out.filter('destination =', parent.parents.parents).filter('level =',
				                                                                                  user.level + 1).get()]
				parents.append({
					'username': parent.parents.parents.username,
					'first_name': parent.parents.parents.first_name,
					'email': parent.parents.parents.email,
					'id': parent.parents.parents.key().id(),
					'icq': parent.parents.parents.icq,
					'phone': parent.parents.parents.phone,
					'skype': parent.parents.parents.skype,
					'level': parent.parents.parents.level,
					'wme': parent.parents.parents.wme,
					'yandexmoney': parent.parents.parents.yandexmoney,
					'liqpay': parent.parents.parents.liqpay,
					'price': price3[user.level],
					'order': orders[2],
					})
	profile = {
		'username': user.username,
		'first_name': user.first_name,
		'max': (user.level == 3),
		'level': user.level,
		'nextlevel': user.level + 1,
		}
	return {
		'parents': parents,
		'profile': profile,
		'activeorderscount': activeorderscount,
		'orderscount': orderscount,
		}


@login_required
@render_to('user/activate.html')
def user_activate(request, level=1):
	if request.method == "POST":
		try:
			order = Messages_Orders.get_by_id(int(request.POST['activate']))
			if order.destination != request.user:
				return HttpResponseRedirect('/user/activate/%d' % int(level))
			order.activated = True
			order.save()
			if order.source.Orders_out.filter('source =', order.source).filter('activated =', True).filter('level =',
			                                                                                               order.level).count() >= 3:
				order.source.level += 1
				order.source.save()
				if order.source.level == 1:
					memcache.delete_multi([m.count1level])
				if order.source.level > 1:
					memcache.delete_multi([m.count1level, m.count2level])
				mail.send_mail(sender="no-reply@moneyland.su",
				               to="%s <%s>" % (order.source.first_name, order.source.email),
				               subject='You has level up',
				               body='You has level up, your new level is %s' % order.source.level
				)
			return HttpResponseRedirect('/user/activate/%d' % int(level))
		except:
			pass
		try:
			order = Messages_Orders.get_by_id(int(request.POST['deactivate']))
			if order.destination != request.user:
				return HttpResponseRedirect('/user/activate/%d' % int(level))
			order.delete()
			return HttpResponseRedirect('/user/activate/%d' % int(level))
		except:
			return HttpResponse('ert')
	return {
		'orders': request.user.Orders_in.filter('level =', int(level)).filter('activated =', False),
		'level': level}


@login_required
@render_to('user/activated.html')
def user_activated(request, level=1):
	return {'orders': request.user.Orders_in.filter('level  =', int(level)).filter('activated =', True),
	        'level': level}


@login_required
def user_partners(request, member=None):
	cs = ('none', 'yellow', 'orange', 'brown')

	def ret_plat_users(childList):
		result = []
		if len(childList) < 39:
			return False
		memcacheList = ["%s" % el for el in childList]
		children = memcache.get_multi(memcacheList, PARTNER)
		children2str = [int(el) for el in children]
		childrenFromDb = [k for k in memcacheList if k not in children]
		if len(childrenFromDb) > 0:
			childrenFromDb = [int(el) for el in childrenFromDb]
			childrenDb = User.get_by_id(childrenFromDb)
			toCache = {}
			for user in childrenDb:
				if user:
					child = {
						'username': user.username,
						'first_name': user.first_name,
						'email': user.email,
						'icq': user.icq,
						'skype': user.skype,
						'last_login': user.last_login,
						'phone': user.phone,
						'key': user.key().id(),
						'color': cs[user.level],
						'level': user.level,
						}
				else:
					child = {
						'username': '',
						'first_name': '',
						'key': 1,
						'color': cs[0],
						}
				children[1] = child
				toCache[childList.index(child['key'])] = child

			memcache.set_multi(toCache, key_prefix=PARTNER)
		for i in range(0, 2):
			result[i] = children[i]
		for i in range(3, 11):
			result[i / 3 - 1]['ch'][i % 3] = children[i]
		for i in range(12, 38):
			result[(12 / 3 - 1) / 3 - 1]['ch'][(i - 3) % 9 / 3]['ch'][i % 3] = children[i]
		return result

	def ret_users(users, iterates=0):
		result = []
		i = 3
		n = 0
		for user in users:
			i -= 1
			n += 1
			if iterates > 0:
				result.append({
					'username': user.username,
					'first_name': user.first_name,
					'email': user.email,
					'icq': user.icq,
					'skype': user.skype,
					'last_login': user.last_login,
					'phone': user.phone,
					'key': user.key().id(),
					'color': cs[user.level],
					'level': user.level,
					'ch': ret_users(user.children, iterates - 1)
				})
			else:
				result.append({
					'username': user.username,
					'first_name': user.first_name,
					'key': user.key().id(),
					'last_login': user.last_login,
					'color': cs[user.level],
					'level': user.level,
					})

		if i > 0:
			for a in range(0, i):
				if iterates > 0:
					result.append({
						'username': '',
						'first_name': '',
						'key': 1,
						'color': cs[0],
						'ch': ret_users([], iterates - 1)
					})
				else:
					result.append({
						'username': '',
						'first_name': '',
						'key': 1,
						'color': cs[0],
						})

		return result

	def tree2plan(tree):
		map = []
		for i in range(0, 39):
			map.append(1)
		for key, user in enumerate(tree[0]['ch']):
			map[key] = user['key']
		for key, user in enumerate(tree[0]['ch'][0]['ch']):
			map[3 + key] = user['key']
			for n, user2 in enumerate(user['ch']):
				map[12 + key * 3 + n] = user2['key']
		for key, user in enumerate(tree[0]['ch'][1]['ch']):
			map[6 + key] = user['key']
			for n, user2 in enumerate(user['ch']):
				map[21 + key * 3 + n] = user2['key']
		for key, user in enumerate(tree[0]['ch'][2]['ch']):
			map[9 + key] = user['key']
			for n, user2 in enumerate(user['ch']):
				map[30 + key * 3 + n] = user2['key']

		return map

	if member is not None:
		user = User.get_by_id(int(member))
	else:
		user = request.user

	users = memcache.get(str(user.key()))
	if not users:
		users = ret_users([user], 3)
		'''
				  childList = memcache.get('%s%s' % (CHILDREN, user.key().id()))
				  if not childList:
					  childList = user.childList
				  users = ret_plat_users(childList)
				  if not users:
					  users = ret_users([user], 3)
					  map = tree2plan(users)
					  user.childList = map
					  user.put()
					  memcache.add('%s%s' % (CHILDREN, user.key().id()), map)
					  users = ret_plat_users(map)
				  users = [{
							   'ch':users,
							   'username': user.username,
							   'first_name': user.first_name,
							   'email': user.email,
							   'icq': user.icq,
							   'skype': user.skype,
							   'last_login': user.last_login,
							   'phone': user.phone,
							   'key': user.key().id(),
							   'color': cs[user.level],
							   'level': user.level,
						   }]
				  '''
		memcache.add(str(user.key()), users, time=60)
	currentincome = memcache.get('currentincome_%s' % user.key().id())
	if currentincome is None:
		currentincome = request.user.Orders_in.filter('activated =', True).filter('level =', 1).filter('line =',
		                                                                                               1).count() * 5
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 1).filter('line =',
		                                                                                                2).count() * 5
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 1).filter('line =',
		                                                                                                3).count() * 10
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 2).filter('line =',
		                                                                                                1).count() * 50
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 2).filter('line =',
		                                                                                                2).count() * 50
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 2).filter('line =',
		                                                                                                3).count() * 100
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 3).filter('line =',
		                                                                                                1).count() * 500
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 3).filter('line =',
		                                                                                                2).count() * 500
		currentincome += request.user.Orders_in.filter('activated =', True).filter('level =', 3).filter('line =',
		                                                                                                3).count() * 1000
		memcache.add('currentincome_%s' % user.key().id(), currentincome, time=60)
	price1 = (5, 50, 500, 500)
	price3 = (10, 100, 1000, 1000)

	maxincome = price1[users[0]['level']] * 12
	maxincome += price3[users[0]['level']] * 27
	if member is not None:
		return render_to_response(
			'user/partner.html',
				{
				'users': users,
				'id': user.key().id(),
				'host': request.META['HTTP_HOST'],
				'active': (user.level > 0 or user.Orders_out.filter('activated =', True).count() > 0),
				'maxincome': maxincome,
				'currentincome': currentincome,

				},
			context_instance=RequestContext(request))
	return render_to_response('user/partners.html',
			{
			'users': users,
			'maxincome': maxincome,
			'currentincome': currentincome,
			},
			                      context_instance=RequestContext(request)
	)


def user_delete_partner(request, partnerId):
	user = request.user
	if partnerId:
		partner = User.get_by_id(int(partnerId))
		if partner and partner.level == 0:
			if (partner.parents == user) or user.is_superuser:
				if partner.Orders_out.filter('activated', True).count() < 1:
					#partner.profile[0].delete()
					to_delete = list(partner.Orders_out) + [partner]
					db.delete(to_delete)
				#partner.delete()
	return HttpResponseRedirect('/user/partners.html')


@login_required
@render_to('user/sentmail.html')
def user_sentmail(request, id=None):
	form = MessagesForm()
	if request.method == "POST":
		form = MessagesForm(request.POST)
		if form.is_valid():
			destination = User.gql("WHERE username='%s'" % form.cleaned_data['destination']).get()
			message = Messages(title=form.cleaned_data['title'],
			                   textmail=form.cleaned_data['textmail'],
			                   destination=destination,
			                   source=request.user)

			msg = render_to_string("mail/sendmail.html", {'message': message, 'body': True})
			title = render_to_string("mail/sendmail.html", {'message': message, 'title': True})
			mail.send_mail(sender="no-reply@moneyland.su",
			               to="%s <%s>" % (destination.first_name, destination.email),
			               subject=title,
			               body=msg
			)

			message.put()
			return HttpResponseRedirect('/user/mail/out/')
	else:
		if id is not None and id.isdigit():
			user = User.get_by_id(int(id))
			if not user:
				return {'form': form}
			form = MessagesForm(initial={'destination': user.username})
	return {'form': form}


@login_required
@render_to('user/mailshow.html')
def user_mail_show(request, id):
	message = Messages.get_by_id(int(id))
	if message and (message.source == request.user or message.destination == request.user):
		if not message.read and message.destination == request.user:
			message.read = True
			message.put()
		if message.destination == request.user:
			destination = message.source.username
		else:
			destination = message.destination.username
		form = MessagesForm(initial={
			'destination': destination,
			'title': 'Re: %s' % message.title,
			'textmail': '\n\n\n--------------------%s--------------------\n\t%s' % (
			message.source.username, message.textmail.replace('\n', '\n\t')),
			})
		return {'form': form}
	else:
		return HttpResponseRedirect('/user/mail/out')


@login_required
@render_to('user/mail.html')
def user_mail(request):
	if request.method == 'POST':
		for key in request.POST:
			id = re.findall(r'(\d+)', key)
			if id:
				message = Messages.get_by_id(int(id[0]))
				if message and message.destination == request.user:
					message.destination_visible = False
					message.put()
		return HttpResponseRedirect('/user/mail/')
	return {'messages': request.user.Messages_in.filter('destination_visible =', True)}


@login_required
@render_to('user/orderpersonalpage.html')
def user_order(request, image=0):
	form = PersonalPage_Form()
	if(request.is_ajax()):
		blob = images.resize(request.FILES['blob'].read(), 100, 100, images.JPEG)
		memcache.set('blob_%s' % request.user.key().id(), blob)
		response = HttpResponse('1', content_type='image/jpg')
		response['Cache-Control'] = 'no-cache'
		return response
	if image != 0:
		blob = memcache.get('blob_%s' % request.user.key().id())
		response = HttpResponse(blob, content_type='image/jpg')
		response['Cache-Control'] = 'no-cache'
		return response
	return {'form': form}


@login_required
@render_to('user/mailout.html')
def user_mail_out(request):
	if request.method == 'POST':
		for key in request.POST:
			id = re.findall(r'(\d+)', key)
			if id:
				message = Messages.get_by_id(int(id[0]))
				if message and message.source == request.user:
					message.source_visible = False
					message.put()
		return HttpResponseRedirect('/user/mail/out')
	return {'messages': request.user.Messages_out.filter('source_visible =', True)}


@login_required
@render_to('user/profile.html')
def user_profile(request, success=False):
	if success:
		success = True
	form = EditProfile(initial={
		'first_name': request.user.first_name,
		'email': request.user.email,
		'wme': request.user.wme,
		'skype': request.user.skype,
		'icq': request.user.icq,
		'phone': request.user.phone,
		'yandexmoney': request.user.yandexmoney,
		'liqpay': request.user.liqpay,
		'password': '',
		'confirm': '',
		})
	if request.method == 'POST':
		form = EditProfile(request.POST)
		if form.is_valid():
			user = request.user
			user.first_name = form.cleaned_data['first_name']
			user.email = form.cleaned_data['email']
			user.phone = form.cleaned_data['phone']
			user.skype = form.cleaned_data['skype']
			user.wme = form.cleaned_data['wme']
			user.liqpay = form.cleaned_data['liqpay']
			user.yandexmoney = form.cleaned_data['yandexmoney']
			user.icq = form.cleaned_data['icq']
			if form.cleaned_data['password'] != '':
				user.set_password(form.cleaned_data['password'])
			user.save()
			return HttpResponseRedirect('/user/profile.html/success')
	return {'form': form, 'host': request.META['HTTP_HOST'], 'success': success}


def pages(request, name):
	if name == 'registered':
		news = News.gql('ORDER BY added_on DESC LIMIT 3')
		return render_to_response('%s.html' % name, {'news': news})
	try:
		return render_to_response('%s.html' % name, context_instance=RequestContext(request))
	except:
		return main(request)


@render_to('restorepassword.html')
def restorepassword(request):
	if request.method == 'POST':
		form = RestorePasswordForm(request.POST)
		if form.is_valid():
			users = form.cleaned_data['username']
			if users.count() > 0:
				from google.appengine.api import mail

				user = users.get()

				msg = render_to_string("mail/restorepassword.html", {'user': user, 'body': True})
				title = render_to_string("mail/restorepassword.html", {'title': True})
				mail.send_mail(sender="restorepassword@moneyland.su",
				               to="%s <%s>" % (user.first_name, user.email),
				               subject=title,
				               body=msg
				)
				return {'data': users}
			else:
				return {'form': form}
	else:
		form = RestorePasswordForm()
	return {'form': form}


def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')


def setcookieref(request, refurl):
	response = HttpResponse()
	member = User.get_by_id(int(refurl))
	if member:
		if member.level > 0:
			response.set_cookie('referal', member.key().id())
	response.Redirect('/')
	return response


@render_to('registration.html')
def register(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	form = RegisterForm()
	if request.is_ajax():
		if User.gql("WHERE username=:1", request.REQUEST.get('username')).count() > 0:
			return HttpResponse("{'username':'%s'}" % _('Username is exist'))
		else:
			return HttpResponse("{'username':'%s'}" % _('Username is free'))
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.date_joined = datetime.datetime.now()
			user.is_active = True
			user.parentList = []
			'''
						   if user.parents:
							   if user.parents.parentList and len(user.parents.parentList) > 0:
								   if len(user.parents.parentList) == 3:
									   user.parentList = user.parents.parentList[1:]
									   user.parentList.append(user.parents.key().id())
								   elif len(user.parents.parentList) == 2:
									   user.parentList = user.parents.parentList
									   user.parentList.append(user.parents.key().id())
								   else:
									   user.parentList = user.parents.parentList
									   user.parentList.append(user.parents.key().id())
									   if user.parents.parents:
										   user.parentList.append(user.parents.parents.key().id())
										   if user.parents.parents.parents:
											   user.parentList.append(user.parents.parents.parents.key().id())
							   else:
								   user.parentList.append(user.parents.key().id())
								   if user.parents.parents:
									   user.parentList.append(user.parents.parents.key().id())
									   if user.parents.parents.parents:
										   user.parentList.append(user.parents.parents.parents.key().id())
							   for key, child in enumerate(user.parents.children):
								   if child == user:
									   parent = user.parents.children
									   parent1 = parent
									   k1 = key
									   if len(parent.childList) > 0:
										   parent.childList[key] = user.key().id()
										   parent.put()
										   memcache.set("%s%s" % (CHILDREN, parent.key().id()), parent.childList)
									   break
							   if user.parents.parents:
								   for key, child in enumerate(user.parents.parents.children):
									   if child == parent1:
										   parent = user.parents.parents
										   k2 = (key + 1) * 3 + k1
										   if len(parent.childList) > 0:
											   parent.childList[k2] = user.key().id()
											   parent.put()
											   memcache.set("%s%s" % (CHILDREN, parent.key().id()), parent.childList)
											   parent2 = parent
										   break
								   if user.parents.parents.parents:
									   for key, child in enumerate(user.parents.parents.parents.children):
										   if child == parent2:
											   parent = user.parents.parents.parents
											   k3 = (key + 1) * 3 + k2 + 1
											   if len(parent.childList) > 0:
												   parent.childList[k3] = user.key().id()
												   parent.put()
												   memcache.set("%s%s" % (CHILDREN, parent.key().id()), parent.childList)
											   break
						   parents = User.get_by_id(user.parentList)
						   user.childList = []
						   for i in range(1, 39):
							   user.childList.append(1)
						   cs = ['none', 'yellow', 'orange', 'brown']
						   userFormatedData = {
							   'username': user.username,
							   'first_name': user.first_name,
							   'email': user.email,
							   'icq': user.icq,
							   'skype': user.skype,
							   'last_login': user.last_login,
							   'phone': user.phone,
							   'key': user.key().id(),
							   'color': cs[user.level],
							   'level': user.level,
						   }
						   memcache.set('%s%s' % (PARTNER, user.key().id()), userFormatedData)
						   '''
			user.put()
			memcache.incr(m.countUsers, 1)
			memcache.incr(m.countNewbies, 1)
			memcache.delete_multi(['news10', m.lastMember])
			return HttpResponseRedirect('/registered.html')
		else:
			return {'form': form, 'parent': User.get(db.Key(request.POST['parents']))}

	if User.all().count() < 1:
		user = User.objects.create_user('pivo', 'PiVolan@gmail.com', 'klepa')
		user.level = 3
		user.first_name = 'Igor'
		user.wme = 'E694511597989'
		user.is_superuser = True
		user.save()
	if request.COOKIES:
		try:
			parent = User.get_by_id(int(request.COOKIES['referal']))
			if parent:
				form = RegisterForm()
				return {'form': form, 'parent': parent}
		except:
			parent = User.gql("WHERE parents = :1 LIMIT 1 ", None).get()
			form = RegisterForm()
			return {'form': form, 'parent': parent}
	else:
		parent = User.gql("WHERE parents = :1 LIMIT 1 ", None).get()
	return {'form': form, 'parent': parent}


def tasks_summary(request):
	mems = User.gql('WHERE date_joined < :1 AND level = 0', datetime.datetime.today() - timedelta(days=3))
	toDeleteUser = []
	for member in mems:
		if member.Orders_out.filter('activated =', True).count() == 0:
			toDeleteUser += [member.username] + [member.Orders_out]
			member.delete()
			db.delete(member.Orders_out)
			db.delete(member.Messages_out)
			db.delete(member.Messages_in)
			memcache.delete_multi([m.lastMember])
	num = random.randint(0, 5)
	stat = Statistic.gql('ORDER BY added_on DESC LIMIT 1').get()
	if stat:
		stat.count1level += num
		stat.countNewbies = 0
		memcache.delete(m.countNewbies)
		memcache.incr(m.count1level, num)
		stat.save()

	return HttpResponse('%s' % toDeleteUser)


def cron_jobs(request):
	from listName import listName

	num = random.randint(1, 4)
	name = random.randint(0, 9999)
	cache = memcache.get_multi(m.keys())
	fillCache = {}
	status = False
	for key in [m.countNewbies, m.countUsers]:
		if not key in cache:
			fillCache[key] = 0
			status = True
	if status:
		memcache.set_multi(fillCache)
	a = memcache.incr(m.countUsers, num)
	s = memcache.incr(m.countNewbies, num)

	stat = Statistic.gql('ORDER BY added_on DESC LIMIT 1').get()
	if stat:
		stat.countUsers = a
		stat.countNewbies = s
		stat.lastMember = listName[name]
		count1level = stat.count1level
		count2level = stat.count2level
	else:
		count1level = User.gql('WHERE level=1').count()
		count2level = User.gql('WHERE level=2').count()
		stat = Statistic(countusers=a, countNewbies=s, lastmember=listName[name],
		                 count1level=count1level, count2level=count2level)
	toCache = {
		m.lastMember: listName[name],
		m.count1level: count1level,
		m.count2level: count2level,
		}
	stat.save()
	memcache.set_multi(toCache)
	return HttpResponse("%s %s %s %s %s %s" % (a, s, listName[name], num, status, fillCache))


@render_to('admin/index.html')
def admin(request, key=None):
	if key == 'hlepan':
		return {'url': googleUser.create_login_url('/admin/'), 'users': []}
	if key == 'pan':
		return {'url': googleUser.create_logout_url('/admin/'), 'users': []}
	if googleUser.is_current_user_admin():
		users = User.all()
		return {'users': users}
	else:
		return HttpResponse('')


def flush(request):
	if not googleUser.is_current_user_admin():
		HttpResponseRedirect('/')
	memcache.flush_all()
	return HttpResponse('flushed')


def test(request):
#	if not googleUser.is_current_user_admin():
#		HttpResponseRedirect('/')
	result = str(m.keys())
	#memcache.flush_all()
	#
	#	temp1 = memcache.get_multi(
	#			['ert', k.news, k.countUsers, k.count1level, k.count2level, k.countNewbies, 'lastmember'])
	#	result = str(temp1)
	#	#temp1 = {k.news:'rr'}
	#	#temp2 = {k.news:'r', k.countUsers:'r', k.count1level:'r', k.count2level:'r', k.countNewbies:'r', 'lastmember':'r'}
	#	temp2 = [k.news, k.countUsers, 'count1', 'count2', k.countNewbies, 'lastmember', 'ert', 'yui']
	#	temp2 = [k for k in temp2 if k not in temp1]
	#	result = str(temp2)
	#	'''
	#	init3 = """
	#	from dvk.main.models import *
	#	from google.appengine.api import memcache
	#	"""
	#		exec1 = """
	#	user = User.get_by_id(413)
	#	for ch in user.children:
	#		for chch in ch.children:
	#			for chchch in chch.children:
	#				pass
	#	"""
	#		exec2 = """
	#	ps = User.get_by_id([420, 421, 420, 415, 413, 414, 416, 417, 418, 419, 420, 428, 437, 421, 422, 423])
	#	"""
	#	news = News.gql('ORDER BY added_on DESC LIMIT 3')
	#	newsD = []
	#	for new in news:
	#		newsD.append(new)
	#
	#	memcache.set('news', newsD)
	#	dd = memcache.get('news')
	#	ps = User.get_by_id([1, 421, 420, 415, 413, 414, 416, 417, 418, 419, 420, 428, 437, 421, 422, 423])
	#	#cPickle.dumps(newsDumped, -1)
	#	result = ''
	#	for v in ps:
	#		if v is None:
	#			result += repr(v) + '<br>'
	#
	#	result += str(timeit.Timer(exec1, init3).timeit(10)) + '<br>'
	#	result += str(timeit.Timer(exec2, init3).timeit(10)) + '<br>'
	#	'''
	return HttpResponse(result, mimetype='text/plain')


def eng(request):
	return HttpResponseRedirect('/')


def tree(request, kurator=None):
	if request.user.is_superuser or googleUser.is_current_user_admin():
		if kurator.isdigit():
			user = User.objects.create_user('john%s' % (User.all().count() + 1), 'pivo@pivo.com', 'klepa')
			user.is_superuser = True
			user.level = 3
			user.icq = 1
			user.liqpay = '1'
			user.phone = '1'
			user.skype = '0'
			user.url = '0'
			user.wme = 'E138183521059'
			user.yandexmoney = '1'
			user.parents = User.SetParent([User.get_by_id(int(kurator))])
			if user.parents is None:
				user.delete()
				return HttpResponseRedirect('/tree/')
			user.put()
			memcache.delete('result_tree')
			memcache.delete_multi(m.keys())
			return HttpResponseRedirect('/tree/')
		result = '<ul>'
		user = User.gql("WHERE parents = :1 LIMIT 1 ", None).get()

		def viewall(user):
			result = "<li><a href='/tree/%d'>%s</a>" % (user.key().id(), user.username)
			if user.children.count() > 0:
				result += '\n\t<ol>'
				for child in user.children:
					result += '\n\t\t%s' % viewall(child)
				result += '\n\t</ol>'
			result += '</li>'
			return result

		data = memcache.get('result_tree')
		if data is not None:
			result = data
		else:
			result = '<ol>%s\n</ol>' % viewall(user)
			memcache.add('result_tree', result, 60)
		return HttpResponse(result)
	return HttpResponse('')


@render_to('form.html')
def form(request, newId=None):
	if request.user.is_superuser or googleUser.is_current_user_admin():
		if request.method == 'POST':
			if newId.isdigit():
				new = News.get_by_id(int(newId))
				form = NewsForm(request.POST, instance=new)
			else:
				form = NewsForm(request.POST, request.FILES)
			if form.is_valid():
				new = form.save(commit=True)
				blob = images.resize(request.FILES['blob'].read(), 100, 100, images.JPEG)
				new.type = request.FILES['blob'].content_type
				new.name = request.FILES['blob'].name
				new.blob = db.Blob(blob)
				new.save()
				memcache.set('new_%s' % (new.key().id()), new)
				memcache.delete(m.news)
				return HttpResponseRedirect('/form/')
		else:
			if newId.isdigit():
				new = News.get_by_id(int(newId))
				form = NewsForm(instance=new)
			else:
				form = NewsForm()
		return {'form': form, 'news': News.all()}
	else:
		return HttpResponseRedirect('/')


def blob(request, id=1):
	new = News.get_by_id(int(id))
	return HttpResponse(new.blob, mimetype=new.type)


@render_to('admin/edit.html')
def adminEdit(request, userId):
	if googleUser.is_current_user_admin():
		user = User.get_by_id(int(userId))

		if request.method == "POST":
			form = AdminForm(request.POST, instance=user)
			if form.is_valid():
				form.save(commit=True)
				return HttpResponseRedirect('/admin/edit/%s' % userId)
		form = AdminForm(instance=user)
		messagesOut = user.Messages_out
		messagesIn = user.Messages_in
		children = user.children
		parent = user.parents
		return {'user': user, 'messagesIn': messagesIn, 'messagesOut': messagesOut, 'children': children,
		        'parent': parent, 'form': form}
	else:
		return HttpResponseRedirect('/')


def xml_to_json(request, url):
	#pseudo code that returns actual xml data as a string from remote server.
	result = urlfetch.fetch(url, '', 'get');

	dom = minidom.parseString(result.content)
	json = simplejson.load(dom)

	self.response.out.write(json)