# all the imports
from __future__ import with_statement
from flask import Flask, request, redirect, url_for, render_template
from collections import Counter, defaultdict, OrderedDict
import json

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


iq = ""
database = ''

@app.route('/')
def show_result():
    # new_chars = []
    # iq = request.args[
    #     'iq'] if 'iq' in request.args else ''
    # print iq
    # if iq == "":
    #     new_chars = []
    # else:
    #     # print linggle_dict[iq+' something']
    #     # new_chars = linggle_dict[iq+' something']

    #     for key in linggle_dict:
    #         if iq in key:
    #             print linggle_dict[key]
    #             new_chars += [linggle_dict[key]]

    # return render_template('show_result.html', output=new_chars, inputquery=iq)
    database = request.args['database'] if 'database' in request.args else ''
    pattern_result = []
    pattern = request.args['iq'] if 'iq' in request.args else ''
    if database == '0': #linggle 
        if pattern =="":
            pattern_result = ""
        else:
            for p in linggle_dict:
                if pattern in p:
                    #print '======================='
                    pattern_result += [(p,linggle_dict[p])]
                    #print pattern_result
                # else:
                #     pattern_result = ""
        return render_template('show_result.html', output=pattern_result, inputquery=pattern)

    elif database == '1': #Writeahead
        if pattern =="":
            pattern_result = ""
        else:
            for p in writeAhead_dictionary:
                if pattern in p:
                    #print '======================='
                    pattern_result += [(p,writeAhead_dictionary[p])]
                    #print pattern_result
                # else:
                #     pattern_result = ""
        return render_template('show_result_w.html', output=pattern_result, inputquery=pattern)
    else:
        return render_template('show_result.html', output=pattern_result, inputquery=pattern)


@app.route('/search', methods=['POST'])
def search_entry():
    iq = request.form['Inputword']
    database = request.form['inlineRadioOptions']

    print database
    return redirect(url_for('show_result', iq=iq, database=database))

if __name__ == '__main__':

    linggle_dict = defaultdict(lambda: None)
    linggle_data_prefix = '../linggle/linggle_sen_result/reducer-0'

    for i in range(8):
        with open(linggle_data_prefix + str(i)) as linggle:
            for line in linggle.readlines():
                list_line = line.strip().split('\t')
                if linggle_dict[list_line[1]] == None or linggle_dict[list_line[1]] == 'N/A':
                    linggle_dict[list_line[1]] = list_line[2]

    print 'linggle_dict has built!'

    writeAhead_dictionary = defaultdict(lambda: 0) 
    writeahead_data_prefix = '../writeahead/writeahead_result/reducer-0'
    #read json file
    for i in range(8):
        with open(writeahead_data_prefix + str(i)) as json_file:
            json_data = json.load(json_file)
            for pattern_layer, pattern_set in json_data.iteritems():
                choose = 0
                for each_pattern in pattern_set:
                    if choose == 0 :
                        choose = 1
                        continue
                    #print each_pattern[0]

                    sec_choose = 0
                    for sentence in each_pattern[2]:
                        #print sentence[0]
                        writeAhead_dictionary[each_pattern[0]] = sentence[0]
    print 'WriteAHead_dict has built!'

    app.run()