#-*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: set bg=dark noet ts=4 sw=4 fdm=indent :

import datetime
import csv
try:
    import cPikcle as pickle
except:
    import pickle
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn import cross_validation


def fetch_userinfo(filename):
    name_encode_dict = {}
    try:
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            # prepare data
            column_names = []
            position_code_dict = {}
            gender_code_dict = {}
            
            for row_idx, row in enumerate(reader):
                if not row_idx:
                    [ column_names.append(column_name) for column_name in row ]
                    continue

                for row_column_idx, row_column in enumerate(row):
                    if column_names[row_column_idx] == 'Sex':
                        if row_column not in gender_code_dict:
                            gender_code_dict[row_column] = len(gender_code_dict) + 1
                    elif column_names[row_column_idx] == 'Group':
                        if not row_column:
                            position_column_idx = column_names.index('Position')
                            position_name = row[position_column_idx]
                        else:
                            position_name = row_column

                        if position_name not in position_code_dict:
                            position_code_dict[position_name] = len(position_code_dict) + 1

        with open(filename, 'rb') as csvfile:
            # encode data
            reader1 = csv.reader(csvfile, delimiter=',')
            for row_idx, row in enumerate(reader1):
                if not row_idx:
                    [ column_names.append(column_name) for column_name in row ]
                    continue

                #print row
                name = row[column_names.index('Name')].decode('UTF-8')
                group = row[column_names.index('Group')]
                position_name = row[column_names.index('Position')] if not group else group
                position = position_code_dict[position_name]

                gender_name = row[column_names.index('Sex')]
                gender = gender_code_dict[gender_name]

                desc_name = row[column_names.index('Description')]
                desc = 1 if not desc_name else 2

                on_board_date = row[column_names.index('OnBoard')]

                name_encode_dict.setdefault(name, [position, gender, on_board_date, desc])

            #print name_encode_dict
            #print len(name_encode_dict)
            userinfo_file = 'output/username.dat'
            with open(userinfo_file, 'w') as userinfo_writer:
                pickle.dump(name_encode_dict, userinfo_writer)

    except Exception as e:
        print e
    finally:
        return name_encode_dict

def load_records(record_name):
    records_dict = {}
    try:
        with open(record_name, 'r') as fp_r:
            records_dict = pickle.load(fp_r)
    except Exception as e:
        print e
    finally:
        return records_dict

def transfer_onboard_date(onboard_date, detailed_time):
    onboard_dt = datetime.datetime.strptime(str(onboard_date), '%Y-%m-%d')
    detailed_dt = datetime.datetime.strptime(str(detailed_time), '%Y%m')

    if onboard_dt >= detailed_dt:
        return 0

    delta = detailed_dt - onboard_dt
    if delta < datetime.timedelta(days=150):
        return 1
    elif delta < datetime.timedelta(days=365):
        return 2
    elif delta < datetime.timedelta(days=730):
        return 3
    else:
        return 4

def merge(name_encode_dict, records_dict):
    detailed_times = [201504, 201508]
    winners = [[u'田霄',u'曲锐',u'谢丹丹',u'李必忠',u'李正旭',u'胡浩然',u'王晓露'],
        [u'张斯晗',u'杜聪',u'褚桐',u'陈伟',u'张攀',u'何雪',u'姚斯宇',u'周庭'],
        [u'李必忠',u'王晓露',u'张立',u'胡浩然',u'李正旭',u'丁崇',u'张斯晗',u'刘浩天',u'李治雄']]

    record_x = []
    record_y = []
    for idx, detailed_time in enumerate(detailed_times):
        for name, (position, gender, on_board_date, desc) in name_encode_dict.iteritems():
            encoded_onboard = transfer_onboard_date(on_board_date, detailed_time)
            #print on_board_date, detailed_time, encoded_onboard
            if encoded_onboard <= 0:
                continue

            key = '.'.join([name, str(detailed_time)])
            if key not in records_dict:
                X = [position, gender, encoded_onboard, desc, 0, 0, 0]
                Y = 1 if name in winners[idx+1] else 0
            else:
                (detailed_time, comment_num, comment_avg_word, this_winner, next_winner) = records_dict[key]
                encoded_comment_word = comment_avg_word / 50 + 1
                X = [position, gender, encoded_onboard, desc, comment_num, encoded_comment_word, this_winner]
                Y = next_winner

            record_x.append(X)
            record_y.append(Y)

    record_all = [ record_x, record_y ]

    for idx, x in enumerate(record_x):
        y = record_y[idx]
        print x, y

    with open('output/train.dat', 'w') as fp_w:
        pickle.dump(record_all, fp_w)

    return record_all

def train(record_all):
    (record_x, record_y) = record_all
    #clf = DecisionTreeRegressor()
    clf = DecisionTreeClassifier(min_samples_split=5)
    try:
        print record_x
        print record_y
        clf.fit(record_x,record_y)
        scores = cross_validation.cross_val_score(clf, record_x, record_y)
        print scores
    except Exception as e:
        print e

    return clf

def predict(name_encode_dict, records_dict, clf):
    detailed_time = 201512
    try:
        print 'predict result: '
        for name, (position, gender, on_board_date, desc) in name_encode_dict.iteritems():
            encoded_onboard = transfer_onboard_date(on_board_date, detailed_time)
            print on_board_date, detailed_time, encoded_onboard
            if encoded_onboard <= 0:
                continue

            key = '.'.join([name, str(detailed_time)])
            if key not in records_dict:
                X = [position, gender, encoded_onboard, desc, 0, 0, 0]
            else:
                (detailed_time, comment_num, comment_avg_word, this_winner, next_winner) = records_dict[key]
                encoded_comment_word = comment_avg_word / 50 + 1
                X = [position, gender, encoded_onboard, desc, comment_num, encoded_comment_word, this_winner]

            y = clf.predict_proba(X)
            print name, y

    except Exception as e:
         print e


if __name__ == '__main__':
    # get names
    filename = 'data/userinfo.csv'
    name_encode_dict = fetch_userinfo(filename)

    # load records
    record_name = 'output/record_with_date'
    records_dict = load_records(record_name)

    # generate train data
    record_all = merge(name_encode_dict, records_dict)

    # train
    clf = train(record_all)

    # predict
    test_record_name = 'output/test_with_date'
    test_records_dict = load_records(test_record_name)
    predict(name_encode_dict, records_dict, clf)
