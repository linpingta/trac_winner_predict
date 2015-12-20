#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import requests
from bs4 import BeautifulSoup
try:
    import cPickle as pickle
except:
    import pickle


def get_trac_info(url, session, cookies):
    response = session.get(url, cookies=cookies)
    if response.status_code == 200:
        return response.text
    else:
        return ''

session = requests.Session()
cookies = {'trac_form_token':'ba016fd61468c88055e2baa9', 'trac_auth':'2d3ba41767bb3717adcd8b102e10848a', 'trac_session':'596b052bc4220abdb206bd83'}

## read detail data
# all_url = 'http://trac.domob-inc.cn/domob/wiki/stars'
detailed_urls = ['http://trac.domob-inc.cn/domob/wiki/stars/2014q3', 'http://trac.domob-inc.cn/domob/wiki/stars/2015q1', 'http://trac.domob-inc.cn/domob/wiki/stars/2015q2']
detailed_times = [201504, 201508, 201512]
winners = [[u'田霄',u'曲锐',u'谢丹丹',u'李必忠',u'李正旭',u'胡浩然',u'王晓露'],
	[u'张斯晗',u'杜聪',u'褚桐',u'陈伟',u'张攀',u'何雪',u'姚斯宇',u'周庭'],
	[u'李必忠',u'王晓露',u'张立',u'胡浩然',u'李正旭',u'丁崇',u'张斯晗',u'刘浩天',u'李治雄']]

def generate_record(detailed_urls, detailed_times, winners):
	''' generate record based on input'''
	records_dict = {}
	record_num = 0
	for idx, detailed_url in enumerate(detailed_urls):

		#response_text = get_trac_info(detailed_url, session, cookies)
		#if response_text:
		#	with open('origin_trac_'+str(idx), 'w') as fp_w:
		#		pickle.dump(response_text, fp_w)

		soup = None
		with open('data/origin_trac_'+str(idx), 'r') as fp_r:
			text = pickle.load(fp_r)
			soup = BeautifulSoup(text, 'lxml')

		if idx ==  2:
			continue

		this_winners = winners[idx]
		predict_winners = winners[idx+1] if idx < len(detailed_urls) - 1 else -1
		detailed_time = detailed_times[idx]
		if soup:
			trac_content = soup.find('div', {'class':'trac-content'})
			# data_1
			if idx == 1:
				element = trac_content.ul
			# data_0
			if not idx:
				element = trac_content.ul.li

			while True:
				if not element:
					break
				# extract element
				#print element

				# data_1
				if idx == 1:
					name = element.li.contents[0].replace('\n', '')
					comment_num = len(element.li.ul.find_all('li'))
					comments = element.li.ul.find_all('li')
				# data_0
				if not idx:
					name = element.contents[0].replace('\n', '')
					comment_num = len(element.ul.find_all('li'))
					comments = element.ul.find_all('li')

				if comments:
					comment_avg_word = 0
					for comment in comments:
						if comment.string:
							comment_avg_word = comment_avg_word + len(comment.string)
					comment_avg_word = comment_avg_word / len(comments)
				else:
					comment_num = 0
					comment_avg_word = 0

				if name in this_winners:
					this_name_winner = 1
				else:
					this_name_winner = 0
				if name in predict_winners:
					predict_name_winner = 1
				else:
					predict_name_winner = 0
				print record_num, name, detailed_time, comment_num, comment_avg_word, this_name_winner, predict_name_winner
				if predict_name_winner:
					for x in range(10):
						records_dict.setdefault('.'.join([name, str(detailed_time)]),[detailed_time, comment_num, comment_avg_word, this_name_winner, predict_name_winner])
						#records_dict.setdefault('.'.join([name, str(detailed_time)]),[detailed_time, comment_num, comment_avg_word, predict_name_winner])
				else:
					records_dict.setdefault('.'.join([name, str(detailed_time)]),[detailed_time, comment_num, comment_avg_word, this_name_winner, predict_name_winner])
					#records_dict.setdefault('.'.join([name, str(detailed_time)]),[detailed_time, comment_num, comment_avg_word, predict_name_winner])
				element = element.nextSibling
				record_num = record_num + 1
				#print element
				#break

		break

	with open('output/record_with_date', 'w') as fp_w:
		pickle.dump(records_dict, fp_w)

def generate_test(detailed_urls, detailed_times, winners):
	records_dict = {}
	detailed_time = detailed_times[len(detailed_times) - 1]

	name_info_dict = {
		u'李必忠': [8, 67, 1],
		u'王晓露': [4, 95, 1],
		u'张立': [3, 53, 1],
		u'丁崇': [3, 70, 1],
		u'李正旭': [3, 30, 1],
		u'侯雨': [3, 40, 0],
		u'彭功逵': [2, 60, 0],
		u'刘浩天': [2, 90, 1],
		u'秦飞': [2, 45, 0],
		u'胡浩然': [2, 85, 1],
		u'姚斯宇': [2, 45, 0],
		u'张斯晗': [2, 90, 1],
		u'陈智铭': [2, 53, 0],
		u'陈振': [2, 47, 0],
		u'黄乐乐': [2, 95, 0],
		u'田霄': [2, 38, 0],
		u'陈俊瑶': [2, 95, 0],
		u'陈伟': [2, 80, 0],
		u'罗同龙': [2, 37, 0],
		u'张成志': [2, 52, 0],
		u'范佳宁': [2, 40, 0],
		u'邹先奇': [2, 32, 0],
		u'张娟娟': [2, 35, 0],
		u'梁方杰': [2, 44, 0],
		u'程宇航': [2, 47, 0],
		u'孔飞': [2, 47, 0],
		u'郑建波': [2, 25, 0],
		u'李治雄': [3, 50, 1]
	}

	predict_name_winner = -1
	for name, (comment_num, comment_avg_word, this_name_winner) in name_info_dict.iteritems():
		records_dict.setdefault('.'.join([name, str(detailed_time)]),[detailed_time, comment_num, comment_avg_word, this_name_winner, predict_name_winner])

	print records_dict

	with open('output/test_with_date', 'w') as fp_w:
		pickle.dump(records_dict, fp_w)

generate_record(detailed_urls, detailed_times, winners)
generate_test(detailed_urls, detailed_times, winners)
