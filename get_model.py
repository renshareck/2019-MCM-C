#! usr/bin/env python
# -*- coding:utf-8 -*-

import json
import pymysql
import plotly
import plotly.figure_factory as ff
import numpy as np


import sys
sys.setrecursionlimit(1000000)


class model():
    def __init__(self):
        print('Init all!')

        self.year_list = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
        self.state_list = ['VA', 'OH', 'WV', 'PA', 'KY']
        self.state_fips = ['51', '39', '54', '42', '21']
        self.state_name_list = ['Virginia', 'Ohio', 'West Virginia', 'Pennsylvania', 'Kentucky']

        self.host = 'localhost'
        self.user = 'root'
        self.passwd = 'Shareck'
        self.database = 'data'
        self.charset = 'utf8'

        self.json_file = 'list.json'

        self.select_fips = '21'
        self.data_dict={}
        for year_num in self.year_list:
            self.data_dict[str(year_num)] = {}
        self.data_dict['2018'] = {}
        self.data_dict['2019'] = {}
        self.data_dict['2020'] = {}

        self.gamma = 0
        self.gamma_list = {}
        self.k_list = {}

    def linefit(self, x, y):
        N = float(len(x))
        sx, sy, sxx, syy, sxy = 0, 0, 0, 0, 0
        for i in range(0, int(N)):
            sx += x[i]
            sy += y[i]
            sxx += x[i] * x[i]
            syy += y[i] * y[i]
            sxy += x[i] * y[i]
        #print(N, sxy, sxx)
        a = (sy * sx / N - sxy) / (sx * sx / N - sxx)
        b = (sy - a * sx) / N
        return a, b

    def get_json(self):
        f = open(self.json_file, 'r')
        self.network_map = json.load(f)
        #print(self.network_map)
        f.close()


    def generate_dict(self):
        # ---------------------------
        print('Begin connect!')
        self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, charset=self.charset)
        self.cursor = self.conn.cursor()
        print('connect to ' + self.host)
        # ---------------------------
        for year_num in self.year_list:
            sql = 'select * from ' + str(year_num) + '_data'
            #print(sql)
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                self.data_dict[str(year_num)][str(row[0])] = 100 * row[1]//row[2]

        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print('disconnect to ' + self.host)

        #print(self.data_dict)

    def generate_list(self):
        pass

    def real_data(self, year_num, fips):
        #print(year_num)
        #print(fips)
        if fips in self.data_dict[str(year_num)]:
            return self.data_dict[str(year_num)][fips]
        else:
            i_sum = 0
            i = 0
            if fips in self.network_map:
                #return self.real_data(year_num, "21229")
                for n_fips in self.network_map[fips]:
                    print("-", n_fips)
                    print("-", i)
                    if n_fips not in self.data_dict[str(year_num)]:
                        continue
                    i = i + 1
                    i_sum = i_sum + self.real_data(year_num, n_fips)
            return i_sum/i

    def set_param(self, gamma):
        self.gamma = gamma

    #def get_next(self, S, I, K, Sum):
    #    s = S - K + self.gamma*Sum
    #    i = I + K - self.gamma*Sum
    #    return s,i

    def get_next(self, I, K, I_sum):
        I_next = I - K + self.gamma*I_sum
        return I_next

    def I_sum(self, year_num, fips):
        i_sum = self.real_data(year_num, fips)
        i = 1
        if fips in self.network_map:
            #return self.real_data(year_num, "21229")
            for n_fips in self.network_map[fips]:
                print("--", n_fips)
                i = i + 1
                i_sum = i_sum + self.real_data(year_num, n_fips)
        return i_sum/i

    def I_next(self, year_num, k, fips):
        print(year_num, k, fips)
        return self.get_next(self.real_data(year_num, fips), k, self.I_sum(year_num, fips))

    def Caculate_gamma(self):
        for fips in self.data_dict['2010']:
            if fips[0:2]!="21":
                continue
            y_detal_list = []
            x_sum_list = []
            for year_num in self.year_list:
                if(year_num==2010 or year_num==2017):
                    pass
                else:
                    y_detal_list.append(self.real_data(year_num, fips)-self.real_data(year_num-1, fips))
                    x_sum_list.append(self.I_sum(year_num, fips))

            #print(self.real_data(2010, fips), self.real_data(2011, fips), self.real_data(2012, fips), self.real_data(2013, fips), self.real_data(2014, fips), self.real_data(2015, fips), self.real_data(2016, fips), self.real_data(2017, fips))
            print(x_sum_list)
            print(y_detal_list)
            gamma, K = self.linefit(x_sum_list, y_detal_list)
            #print(fips, gamma, K)
            self.gamma_list[fips] = gamma
            self.k_list[fips] = K
            #self.data_dict['2018'][fips] = self.I_next(2017, K, fips)

    def draw_map(self):
            tmp = 0
            i = 0
            for n_fips in self.gamma_list:
                tmp = tmp + self.gamma_list[n_fips]
                i = i + 1
            self.gamma = tmp/i

            for n_fips in self.gamma_list:
                self.data_dict['2018'][n_fips] = self.I_next(2017, self.k_list[n_fips], n_fips)

            self.fips = []
            self.values = []
            for n_fips in self.data_dict["2018"]:
                self.fips.append(n_fips)
                self.values.append(self.data_dict["2018"][n_fips])


            endpts = list(np.mgrid[min(self.values):max(self.values):6j])
            colorscale = ["#FF0000",
                          "#FF8C69",
                          "#FFD700",
                          "#FFFF00",
                          "#ADFF2F",
                          "#7FFF00",
                          "#00FF00",
                          "#7FFFAA"]

            sub_colorscale = ["#0000FF",
                              "#00CACA",
                              "#ADFF2F",
                              "#FFFF00",
                              "#FFD700",
                              "#FF8C69",
                              "#FF0000",
                              "#A52A2A"]

            fig = ff.create_choropleth(
                fips=self.fips, values=self.values, scope=self.state_name_list, show_state_data=True,
                colorscale=sub_colorscale, binning_endpoints=endpts, round_legend_values=True,
                plot_bgcolor='rgb(229,229,229)',
                paper_bgcolor='rgb(229,229,229)',
                legend_title='Percent; Count of Opioid-Reports',
                state_outline={'color': 'rgb(0,0,0)', 'width': 1},
                county_outline={'color': 'rgb(105,105,105)', 'width': 0.5},
                #state_outline={'color': 'rgb(105,105,105)', 'width': 0.5},
                #county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
                show_hover=True,
                exponent_format=False,
            )

            plotly.offline.plot(fig, filename='2018_map.html')

if __name__ == "__main__":
    test = model()
    test.get_json()
    test.generate_dict()
    test.Caculate_gamma()
    test.draw_map()