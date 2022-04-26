#2020： 例本土、例境外
#2021：例COVID-19本土、例COVID-19境外
#2022：例本土、例境外
#已知例外：新增75例COVID-19本土病例，均為本土個案
#國內新增1例自印度境外移入COVID-19個案

from itertools import groupby
import requests, bs4
import re
import pandas as pd
import datetime
from datetime import datetime,timedelta

def get_total_case(start_date,end_date):
    start = datetime.strptime(str(start_date),"%Y.%m.%d")
    end = datetime.strptime(str(end_date),"%Y.%m.%d")

    new_start_date = start.strftime("%Y-%m-%d")
    new_end_date = end.strftime("%Y-%m-%d")

    idx = pd.date_range(f'{new_start_date}',f'{new_end_date}',)


    csv_date = []
    csv_local = []
    csv_total = []

    
    #例外
    patterna = r'((\d+),(\d+))|(\d+)例[\u4e00-\u9fa5]+'

    ##方法一
    for page in range(1,1500):
        url = f'https://www.cdc.gov.tw/Bulletin/List/MmgtpeidAR5Ooai4-fgHzQ?page={page}&startTime={start_date}&endTime={end_date}'
        htmlfile = requests.get(url)
        objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

        objTag = objSoup.select('.cbp-item')    #找到.cbp-item這個class
        #print("objTag串列長度 = ", len(objTag))

        if len(objTag) != 0:    #若selecet回傳的串列不為空則繼續循環(因為不知道會有多少分頁，所以預設了1500頁，如果回傳為空就代表沒有那頁，就結束循環)
            for i in range(len(objTag)):
                covid = objTag[i].find_all('p', {'class':'JQdotdotdot'})    #新聞標題（本日新增xx例本土，xx例境外）
                covid_year = objTag[i].find_all('p',{'class':'icon-year'})  #新聞的年月（2022 - 1）
                covid_date = objTag[i].find_all('p',{'class':'icon-date'})  #新聞的日（12）

                for j in range(len(covid)):
                    covid_text = str(covid[j].text) #將新聞標題文字轉為string
                    pattern = r'新增((\S+)?)'
                    result = re.search(pattern, covid_text)
                    real_date = str(covid_year[j].text + '-' + covid_date[j].text).replace(' - ','-')   #整理日期格式
                    print(real_date)

                    if result != None:  #如果有案例
                        # 超例外情況(本土)
                        # if ('均為' in covid_text) and ('本土' in covid_text):
                        #     csv_date.append(real_date)
                        #     resulta = re.search(patterna, covid_text)
                        #     local_num = str(resulta.group().replace(r'例','')).replace(',','')
                        #     print(local_num)
                        #     total = local_num
                        #     print(total)
                        #     csv_total.append(int(total))
                        # # 超例外情況(境外)
                        # elif ('均為' in covid_text) and ('境外' in covid_text):
                        #     csv_date.append(real_date)
                        #     resulta = re.search(patterna, covid_text)
                        #     outside_num = str(resulta.group().replace(r'例','')).replace(',','')
                        #     print(outside_num)
                        #     total = outside_num
                        #     print(total)
                        #     csv_total.append(int(total))
                        # 如果兩個都有
                        if ('本土' in covid_text) and ('境外' in covid_text):
                            csv_date.append(real_date)
                            #本土pattern
                            pattern1 = r'(((\d+),(\d+))|(\d+))例((COVID-19)?)本土'
                            #境外pattern
                            pattern2 = r'(((\d+),(\d+))|(\d+))例((COVID-19)?)境外'
                            result1 = re.search(pattern1, covid_text)
                            result2 = re.search(pattern2, covid_text)
                            local_num = int(str(result1.group()).replace('COVID-19','').replace('本土','').replace('例','').replace(',',''))
                            outside_num = int(str(result2.group()).replace('COVID-19','').replace('境外','').replace('例','').replace(',',''))
                            print(local_num)
                            print(outside_num)
                            total = local_num + outside_num
                            print(total)
                            csv_total.append(total)
                        # 只有本土
                        elif ('本土'in covid_text) and ('境外' not in covid_text):
                            csv_date.append(real_date)
                            patterna = r'((\d+),(\d+))|(\d+)例'
                            result3 = re.search(patterna, covid_text)
                            local_num = int(str(result3.group()).replace('COVID-19','').replace('本土','').replace('例','').replace(',',''))
                            print(local_num)
                            total = local_num
                            print(total)
                            csv_total.append(total)
                        # 只有境外
                        elif ('本土' not in covid_text) and ('境外' in covid_text):
                            csv_date.append(real_date)
                            patterna = r'((\d+),(\d+))|(\d+)例'
                            result4 = re.search(patterna, covid_text)
                            outside_num = int(str(result4.group()).replace('COVID-19','').replace('境外','').replace('例','').replace(',',''))
                            print(outside_num)
                            total = outside_num
                            print(total)
                            csv_total.append(total)
                    else: 
                        continue
        else:
            break

    # print(len(csv_date))
    # print(len(csv_local))
    data = [csv_date, csv_total]
    col = ['日期','當日總確診人數']
    df = pd.DataFrame(list(zip(*data)),columns=col)
    df_new1 = df.groupby(['日期'], sort=False)['當日總確診人數'].sum().reset_index()  #如果同一天有兩條新增本土案例的新聞，則相加
    df_new2 = df_new1.set_index(pd.to_datetime(df_new1['日期']))
    #print(df_new2)

    df_new = df_new2.reindex(idx, fill_value=0)
    df_final = df_new['當日總確診人數']
    #print(df_final)
    df_final.to_csv(f'{new_start_date}_{new_end_date}當日總確診人數.csv')

start_date = '2020.10.30'   #開始日期
end_date = '2020.10.31' #結束日期
get_total_case(start_date,end_date)
