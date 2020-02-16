import pandas as pd
import requests
import re
import json
import bs4
import datetime,time

# grab authors who public ETF related information
# related platform: so.eastmoney.com, xueqiu.com
# so.eastmoney.com: caifuhao, guba
# xueqiu.com: article & tweet, activity

class grab_etf():
    def __init__(self,local_data_path,etf_code,user_id):
        self.get_session()
        self.local_data_path = local_data_path
        self.etf_code=etf_code
        self.user_id=user_id

    def get_session(self):
        cookies='EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; qgqp_b_id=d99e223c857b909c1f15465170c75e9b; EMFUND9=01-08 11:21:08@#$%u56FD%u6CF0%u4E2D%u8BC1%u5168%u6307%u8BC1%u5238%u516C%u53F8ETF@%23%24512880; st_si=16905610209912; Hm_lvt_e834f0bcb11ce14253b9eba75492b597=1579225820,1579229885,1579244237,1580890821; emshistory=%5B%22%E5%86%9B%E5%B7%A5%E9%BE%99%E5%A4%B4etf%22%2C%22%E5%8D%8E%E5%A4%8F%205Getf%22%2C%22%E5%8D%8E%E5%A4%8F5Getf%22%2C%225Getf%22%2C%22%E5%88%9B%E8%93%9D%E7%AD%B9ETF%22%2C%22%E5%88%9B%E8%93%9D%E7%AD%B9ETF%20159966%22%2C%22%E5%8D%8E%E5%A4%8F%20%E5%88%9B%E8%93%9D%E7%AD%B9%22%2C%22%E5%8D%8E%E5%A4%8F%205GETF%22%2C%225GETF%22%2C%22%E5%86%9B%E5%B7%A5ETF%22%2C%22%E7%A7%91%E6%8A%80%E9%BE%99%E5%A4%B4ETF%22%2C%22%E5%9B%BD%E6%B3%B0%E5%86%9B%E5%B7%A5ETF%22%2C%22%E5%9B%BD%E6%B3%B0%E5%86%9B%E5%B7%A5%22%2C%22%E5%88%9B%E8%93%9D%E7%AD%B9%22%2C%225GETF%20515050%22%2C%22%E5%8D%8E%E5%AE%9D%20%E7%A7%91%E6%8A%80%E9%BE%99%E5%A4%B4ETF%22%2C%22%E5%8D%8E%E5%AE%9D%20%E7%A7%91%E6%8A%80%E9%BE%99%E5%A4%B4%22%2C%22%E5%8D%8E%E5%A4%8F5G%20ETF%22%2C%22%E5%8D%8E%E5%A4%8F5G%20ETF%20515050%22%2C%22%E5%9B%BD%E6%B3%B0%E5%86%9B%E5%B7%A5ETF%20512660%22%5D; st_asi=delete; Hm_lpvt_e834f0bcb11ce14253b9eba75492b597=1580891133; st_pvi=66137721156776; st_sp=2019-11-24%2023%3A02%3A05; st_inirUrl=https%3A%2F%2Fwww.google.com%2F; st_sn=26; st_psi=20200205162533196-118000300908-1881009697'
        headers={
        'Cookie':cookies,
        'Host':'api.so.eastmoney.com',
        'Referer':'http://so.eastmoney.com/CArticle/s?keyword=%E5%8D%8E%E5%A4%8F5GETF&pageindex=4&searchrange=8192&sortfiled=32',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }
        s=requests.Session()
        s.headers=headers
        self.session=s

    def get_article_info(self,url):
        id=re.search('http://caifuhao\.eastmoney\.com/news/(.*)',str(url)).group(1)
        arti_url='http://gubawebapi.eastmoney.com/v3/package/getdata/common?url=read/Custom/Web/GetArticleBriefInfo.aspx?id%3D{}%26type%3D20%26deviceid%3D0.3410789631307125%26version%3D100%26product%3DGuba%26plat%3DWeb'.format(id)
        a=self.session.get(arti_url)
        a = re.search('{.*}', a.text).group()
        dic=json.loads(a)['re'][0]
        dic={"post_click_count":dic["post_click_count"],"post_comment_count":dic["post_comment_count"],"post_forward_count":dic["post_forward_count"],"post_like_count":dic["post_like_count"]}
        return dic

    # caifuhao

    def get_caifuhao(self,etf_code):
        url='http://api.so.eastmoney.com/bussiness/Web/GetSearchList?type=8224&pageindex=1&pagesize=10&keyword={}&name=caifuhaowenzhang&cb=jQuery112405252183175621794_1581304455595&_=1581304455601'.format(etf_code)
        r = self.session.get(url)
        r = re.search('{.*}', r.text).group()
        r = re.sub('<em>', '', r)
        maxPage=json.loads(r)['TotalPage']
        info = pd.DataFrame(json.loads(r)['Data'])
        info = info[['NickName', 'ShowTime', 'Title', 'Content','ArticleUrl']]
        info[['Title', 'Content']] = info[['Title', 'Content']].applymap(lambda x: re.sub('(<em>|</em>)', '', x))

        # article related info: "post_click_count","post_comment_count","post_forward_count","post_like_count"
        info['article_info'] = info['ArticleUrl'].to_frame().applymap(self.get_article_info)
        info = info[info['ShowTime'] > '2019-07-01 00:00:00']
        result = info

        for page in range(2,maxPage):
            new_url='http://api.so.eastmoney.com/bussiness/Web/GetSearchList?type=8224&pageindex={}&pagesize=10&keyword={}&name=caifuhaowenzhang&cb=jQuery112405252183175621794_1581304455595&_=1581304455601'.format(page,etf_code)
            url= new_url.format(page)
            r=self.session.get(url)
            r=re.search('{.*}',r.text).group()
            r=re.sub('<em>','',r)
            info=pd.DataFrame(json.loads(r)['Data'])
            info=info[['NickName','ShowTime','Title','Content','ArticleUrl']]
            info[['Title','Content']]=info[['Title','Content']].applymap(lambda x:re.sub('(<em>|</em>)','',x))

            # article related info
            info['article_info'] = info['ArticleUrl'].to_frame().applymap(self.get_article_info)
            if True in (info['ShowTime'] < '2019-07-01 00:00:00').values:
                break
            result=pd.concat([result,info])
            print("{} {}".format(etf_code,page))

        # count the # of occurrence of a specific author
        result['count']=1
        grouped=result.groupby('NickName')
        count=grouped['count'].sum().to_frame()
        result=result.merge(count,on="NickName",suffixes=["_drop",""])
        result.drop(['count_drop'],axis=1,inplace=True)

        result=result[['ShowTime','NickName','count','Title','Content','article_info']]

        out_path=local_data_path+"财富号（含阅读数）"
        result.to_excel(out_path+'/{}.xlsx'.format(etf_code))

    # xueqiu activity

    def get_time(self,x):
        x = x // 1000
        dateArray = datetime.datetime.fromtimestamp(x)
        time = dateArray.strftime("%Y/%m/%d %H:%M:%S")
        return time

    def clean_str(self,x):
        return re.sub("[^，、！。（）0-9\u4e00-\u9fa5]", "", x)

    def grab_xueqiu_activity(self,etf_code,user_id):
        # get maxPage
        url = "https://xueqiu.com/v4/statuses/user_timeline.json?page=1&user_id={}".format(user_id)
        r=self.session.get(url)
        r=r.json()
        maxPage=r['maxPage']
        info=pd.DataFrame(r['statuses'])
        info['time'] = info['created_at'].apply(self.get_time)
        info = info[['time', 'title', 'retweet_count', 'reply_count', 'like_count','offer','description']]
        info = info[info['time'] > '2019/07/01 00:00:00']
        result=info

        for page in range(2,maxPage):
            url = "https://xueqiu.com/v4/statuses/user_timeline.json?page={}&user_id=1403930284".format(page)
            r=self.session.get(url)
            r=r.json()
            info = pd.DataFrame(r['statuses'])
            info['time'] = info['created_at'].apply(self.get_time)
            info = info[['time', 'title', 'retweet_count', 'reply_count', 'like_count', 'offer', 'description']]
            if True in (info['time'] < '2019-07-01 00:00:00').values:
                break
            if page%15==0:
                time.sleep(10)
            print(page)
            result=pd.concat([result,info])

        result[['title','description']]=result[['title','description']].applymap(self.clean_str)
        result=result[['time', 'title', 'retweet_count', 'reply_count', 'like_count', 'offer', 'description']]

        out_path=local_data_path+'/雪球活动'
        result.to_excel(out_path+'/{}.xlsx'.format(etf_code))

    # xueqiu article and tweet

    def grab_xueqiu_article(self,etf_code):
        url = "https://xueqiu.com/statuses/search.json?sort=time&source=all&q={}&count=10&page=1".format(etf_code)
        r = self.session.get(url)
        r = r.json()
        maxPage = r['maxPage']
        info = pd.DataFrame(r['list'])
        info['name'] = info['user'].apply(lambda x: x['screen_name'])
        info['followers_count'] = info['user'].apply(lambda x: x['followers_count'])
        info['friends_count'] = info['user'].apply(lambda x: x['friends_count'])
        info['tweet_number'] = info['user'].apply(lambda x: x['status_count'])
        info['time'] = info['created_at'].apply(self.get_time)
        info = info[info['time'] > '2019/07/01 00:00:00']
        result = info

        for page in range(2, maxPage):
            url = "https://xueqiu.com/statuses/search.json?sort=time&source=all&q={}&count=10&page={}".format(etf_code,page)
            r = self.session.get(url)
            r = r.json()
            info = pd.DataFrame(r['list'])
            info['name'] = info['user'].apply(lambda x: x['screen_name'])
            info['followers_count'] = info['user'].apply(lambda x: x['followers_count'])
            info['friends_count'] = info['user'].apply(lambda x: x['friends_count'])
            info['tweet_number'] = info['user'].apply(lambda x: x['status_count'])
            info['time'] = info['created_at'].apply(self.get_time)
            if True in (info['time'] < '2019-07-01 00:00:00').values:
                break
            if page % 15 == 0:
                time.sleep(10)
            print(page)
            result = pd.concat([result, info], sort=True)

        grouped = result.groupby('name')
        result['count'] = 1
        count = grouped['count'].sum().to_frame()
        result = result.merge(count, on="name", suffixes=["_drop", ""])
        result.drop(['count_drop'], axis=1, inplace=True)

        result[['title', 'text']] = result[['title', 'text']].applymap(self.clean_str)

        result = result[
            ['time', 'name', 'count', 'followers_count', 'friends_count', 'tweet_number', 'user_id', 'title', 'text',
             'retweet_count', 'reply_count']]

        out_path = '/Users/priscilla/Desktop/python/Fuguo/ETF/ETF统计/华夏创蓝筹'
        result.to_excel(out_path + '/雪球_tweet.xlsx')

    # grab guba (so.eastmoney.com)

    def getHTMLText(self,url):
        try:
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            return ""

    def find_author(self,x):
        html = self.getHTMLText(x)
        soup = bs4.BeautifulSoup(html, "html.parser")
        source = soup.find("div", attrs={'class': 'data'})
        return json.loads(source['data-json'])["user_nickname"]


    def grab_guba(self,etf_code):

        first_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?type=701&pageindex=1&pagesize=10&keyword={}&name=normal&cb=jQuery112409045809333848216_1581821153878&_=1581821153884'.format(etf_code)
        r = self.session.get(first_url)
        r = re.search('{.*}', r.text).group()
        info = pd.DataFrame(json.loads(r)['Data'])
        info = info[['CreateTime', 'Title', 'Content', 'Url']]
        info = info[info['CreateTime'] > '2019-07-01 00:00:00']
        info['author'] = info['Url'].to_frame().applymap(self.find_author)
        info[['Title', 'Content']] = info[['Title', 'Content']].applymap(lambda x: re.sub('(<em>|</em>)', '*', x))
        result = info

        maxPage = json.loads(r)['TotalPage']

        for page in range(2, maxPage):
            url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?type=701&pageindex={}&pagesize=10&keyword={}&name=normal&cb=jQuery112409045809333848216_1581821153878&_=1581821153884'.format(page,etf_code)
            r = self.session.get(url)
            r = re.search('{.*}', r.text).group()
            info = pd.DataFrame(json.loads(r)['Data'])
            info = info[['CreateTime', 'Title', 'Content', 'Url']]
            if True in (info['time'] < '2019-07-01 00:00:00').values:
                break
            info['author'] = info['Url'].to_frame().applymap(self.find_author)
            info[['Title', 'Content']] = info[['Title', 'Content']].applymap(lambda x: re.sub('(<em>|</em>)', '*', x))
            result = pd.concat([result, info])
            if page % 5 == 0:
                time.sleep(10)
            print('guba {} {}'.format(etf_code, page))

        result['count'] = 1
        grouped = result.groupby('author')
        count = grouped['count'].sum().to_frame()
        result = result.merge(count, on="author", suffixes=["_drop", ""], how="left")
        result.drop(['count_drop'], axis=1, inplace=True)
        result = result[['CreateTime', "author", 'count', 'Title', 'Content', 'Url']]
        result = result.sort_values(by=['CreateTime'], ascending=False)

        out_path=local_data_path+'/雪球文章和发帖'
        result.to_excel(out_path + '{}.xlsx'.format(etf_code), index=None)


local_data_path="/Users/priscilla/Desktop/python/Fuguo/ETF/ETF统计_new/"
# 国泰证券，国泰军工，华宝科技龙头，华夏5G，华夏创蓝筹，富国军工龙头，富国科技50
keyword=[512660,515000,515050,159966,512710,515750] #512880,\
user_id=0
for code in keyword:
    etf=grab_etf(local_data_path,code,user_id)
    etf.grab_guba()