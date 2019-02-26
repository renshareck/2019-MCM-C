#! usr/bin/env python
# -*- coding:utf-8 -*-

import plotly
import plotly.figure_factory as ff
import pymysql

import numpy as np

class map():

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

        self.fips = []
        self.values = []


    def get_map(self):
        # ---------------------------
        print('Begin connect!')
        self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, charset=self.charset)
        self.cursor = self.conn.cursor()
        print('connect to ' + self.host)
        # ---------------------------

        for year_num in self.year_list:
            sql = 'select * from ' + str(year_num) + '_data'
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                if row[2]>10:
                    self.fips.append(row[0])
                    self.values.append(100 * row[1]/row[2])
                    print(year_num, row[0], row[1], row[2], 100*row[1]/row[2])

            endpts = list(np.mgrid[min(self.values):max(self.values):6j])

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

                show_hover=True,
                exponent_format=False,
            )

            plotly.offline.plot(fig, filename=str(year_num) + '_map.html')

        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print('disconnect to ' + self.host)



if __name__ == "__main__":
    test = map()
    test.get_map()