from itertools import groupby
import requests, bs4
import re
import pandas as pd
import datetime
from datetime import datetime,timedelta

start_date = '2020.01.01'   #開始日期
end_date = '2022.02.13' #結束日期

start = datetime.strptime(str(start_date),"%Y.%m.%d")
end = datetime.strptime(str(end_date),"%Y.%m.%d")

new_start_date = start.strftime("%Y-%m-%d")
new_end_date = end.strftime("%Y-%m-%d")

idx = pd.date_range(f'{new_start_date}',f'{new_end_date}',)


csv_date = []
csv_local = []

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
                #找出本土的例子
                pattern = r'(\d+)例((COVID-19)?)本土'
                result = re.search(pattern, covid_text)
                real_date = str(covid_year[j].text + '-' + covid_date[j].text).replace(' - ','-')   #整理日期格式
                #print(real_date)

                if result != None:  #如果有本土案例
                    if ('新增' in covid_text) and ('例本土' in covid_text) and ('境外' in covid_text):
                        csv_date.append(real_date)
                        pattern1 = r'(\d+)例本土'
                        result1 = re.search(pattern1, covid_text)
                        local_num = str(result1.group().replace(r'例本土',''))
                        print(local_num)
                        csv_local.append(int(local_num))
                    elif ('新增' in covid_text) and ('例COVID-19本土' in covid_text) and ('境外' in covid_text):
                        csv_date.append(real_date)
                        pattern2 = r'(\d+)例COVID-19本土'
                        result2 = re.search(pattern2, covid_text)
                        local_num = str(result2.group().replace(r'例COVID-19本土',''))
                        print(local_num)
                        csv_local.append(int(local_num))
                    elif ('新增' in covid_text) and ('本土' in covid_text) and ('境外' not in covid_text):
                        csv_date.append(real_date)
                        pattern3 = r'(\d+)例'
                        result3 = re.search(pattern3, covid_text)
                        local_num = str(result3.group().replace(r'例',''))
                        print(local_num)
                        csv_local.append(int(local_num))
                else: 
                    continue
    else:
        break


# ##方法二
# for page in range(1,1500):
#     url = f'https://www.cdc.gov.tw/Bulletin/List/MmgtpeidAR5Ooai4-fgHzQ?page={page}&startTime={start_date}&endTime={end_date}'
#     htmlfile = requests.get(url)
#     objSoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

#     objTag = objSoup.select('.cbp-item')    #找到.cbp-item這個class
#     #print("objTag串列長度 = ", len(objTag))

#     if len(objTag) != 0:    #若selecet回傳的串列不為空則繼續循環(因為不知道會有多少分頁，所以與設了1500頁，如果回傳為空就代表沒有那頁，就結束循環)
#         for i in range(len(objTag)):
#             covid = objTag[i].find_all('p', {'class':'JQdotdotdot'})    #新聞標題（本日新增xx例本土，xx例境外）
#             covid_year = objTag[i].find_all('p',{'class':'icon-year'})  #新聞的年月（2022 - 1）
#             covid_date = objTag[i].find_all('p',{'class':'icon-date'})  #新聞的日（12）
#             for j in range(len(covid)):
#                 covid_text = str(covid[j].text) #將新聞標題文字轉為string
#                 if ('新增' in covid_text) and ('本土' in covid_text) and ('境外' in covid_text):
#                     pattern = r'(\d+)例本土'
#                     result = re.search(pattern, covid_text)
#                     real_date = str(covid_year[j].text + '-' + covid_date[j].text).replace(' - ','-')   #整理日期格式
#                     if result != None:  #如果格式為'(\d+)例本土'
#                         csv_date.append(real_date)
#                         local_num = str(result.group().replace(r'例本土',''))
#                         print(local_num)
#                         csv_local.append(int(local_num))
#                     else: 
#                         csv_date.append(real_date)
#                         pattern = r'(\d+)例COVID-19本土'
#                         result = re.search(pattern, covid_text)
#                         local_num = str(result.group().replace(r'例COVID-19本土',''))
#                         print(local_num)
#                         csv_local.append(int(local_num))

#                 elif ('新增' in covid_text) and ('本土' in covid_text) and ('境外' not in covid_text):
#                     pattern = r'(\d+)例'
#                     result = re.search(pattern, covid_text)
#                     real_date = str(covid_year[j].text + '-' + covid_date[j].text).replace(' - ','-')   #整理日期格式
#                     if result != None:  #如果有本土案例
#                         csv_date.append(real_date)
#                         csv_local.append(int(str(result.group().replace('例',''))))
#                     else: 
#                         continue
#                 else:
#                     continue
#     else:
#         break   #(因為不知道會有多少分頁，所以與設了1500頁，如果回傳為空就代表沒有那頁，就結束循環)


# print(len(csv_date))
# print(len(csv_local))
data = [csv_date, csv_local]
col = ['日期','本土確診人數']
df = pd.DataFrame(list(zip(*data)),columns=col)
df_new1 = df.groupby(['日期'], sort=False)['本土確診人數'].sum().reset_index()  #如果同一天有兩條新增本土案例的新聞，則相加
df_new2 = df_new1.set_index(pd.to_datetime(df_new1['日期']))
#print(df_new2)

df_new = df_new2.reindex(idx, fill_value=0)
df_final = df_new['本土確診人數']
#print(df_final)
df_final.to_csv(f'{new_start_date}_{new_end_date}本土確診人數.csv')