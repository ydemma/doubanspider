import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class doubanspider(object):
    def __init__(self):
        self.server='https://book.douban.com'
        self.target='https://book.douban.com/tag/?view=type&icn=index-sorttags-all'
        self.tags=[]
        self.urls=[]
        self.tagdict={}
        self.colname=[u'网址',u'书名',u'作者',u'出版社',u'副标题',u'原作名',u'译者',u'出版年',u'页数',u'定价',u'ISBN',u'评分',u'评价人数']
        self.bookinfo_list=[self.colname]
    def get_download_url(self):
        r=requests.get(url=self.target)
        html=BeautifulSoup(r.text,"html.parser")
        tables=html.find_all('table',class_='tagCol')
        #debug code
        #file=open("./2.txt","a",encoding="UTF-8")
        #file.write(str(tables))
        for eacht in tables[:]:            
            a=BeautifulSoup(str(eacht),"html.parser").find_all('a')
            for each in a[:]:
                self.tags.append(each.string)
                self.urls.append(self.server+each.get('href'))
           #debug code
        #file=open("./3.txt","a",encoding="UTF-8")
        #file.write(str(self.tags))
        self.tagdict=dict(zip(self.tags,self.urls))
        #file=open("./4.txt","a",encoding="UTF-8")
        #file.write(str(tagdict))
    def getbooks(self,tagname):
        ##here should have a loop to get nextpage
        tagtarget=self.tagdict[tagname]
        r=requests.get(tagtarget)
        html=BeautifulSoup(r.text,"html.parser")  

        pageinator=html.find_all('div',class_='paginator')
        #print(str(pageinator[0].contents[0]))
        pagenummax=1        
        for each in pageinator[0].find_all('a'):
            try:
                a_num=int(each.string)                
            except ValueError:
                print('excepiton log')
            else:
                if a_num>pagenummax:
                    pagenummax=a_num
        #print(str(pagenum))
        pagenum=1
        listnum=0
        while (pagenum<2):#use 2 for test, here should use pagenummax
            items=html.find_all('li',class_='subject-item')
            for eachi in items[:]:
                book_url=BeautifulSoup(str(eachi),"html.parser").find_all('a',class_='nbg')
                booklink=book_url[0].get('href')
                self.getbookinfo(str(booklink))
            if pagenum<pagenummax:
                pagenum=pagenum+1
                listnum=listnum+20
                nextpage=tagtarget+'?start='+str(listnum)+'&type=T'
                r=requests.get(nextpage)
                html=BeautifulSoup(r.text,"html.parser")

        #last step is to write in the excel
        infoDataFrame=pd.DataFrame(self.bookinfo_list)
        filename='./book_'+tagname+'.xls'
        infoDataFrame.to_excel(filename,index=False)

    def getbookinfo(self,bookurl):
        r=requests.get(bookurl)
        html=BeautifulSoup(r.text,"html.parser")
        #file=open("./4.txt","a",encoding="UTF-8")
        #file.write(str(r.text))
        infos=[]
        infos.append(bookurl)
        titleh1=html.find_all('h1')
        titlespan=titleh1[0].find_all('span')
        title=titlespan[0].string
        infos.append(title)

        colindex=2
        infodiv=html.find_all('div',id='info')
        #use regular expression to extract infos
        for each in re.findall(r"<span(.+?)<br",str(infodiv[0]),re.S):
            #print(str(each)+'\n\n')
            #dr=re.compile(r'<[^>]+>',re.S)
            #dd=dr.sub('',str(each))
            #file.write('~~~~the begin~~~~'+str(each)+'~~~~the end~~~~~'+'\n\n')
            #spanhtml='<span'+str(each)
            #infoitem=BeautifulSoup(spanhtml,"html.parser").find_all('span',class_='pl')
            #tagname=str(infoitem[0].contents[0])
            #tagcontent=
            #print('~~~~the begin~~~~'+'\n\n')
            info_all=''
            infoname=''
            infocontent=''
            for infoitem in re.findall(r">(.+?)<",str(each)+'<',re.S):
                info_all=info_all+infoitem
            infonc=info_all.split(':')
            infoname=infonc[0].strip()
            infocontent=infonc[1].replace('\n','').strip()#replace(' ','')
            #print('~~~infoname:'+infoname)
            #print('~~~infocontent:'+infocontent+'\n\n')
            if self.colname[colindex] in infoname:
                infos.append(infocontent.strip())
                colindex=colindex+1
            else:
                i=colindex+1
                while (i<11):
                    if self.colname[i] in infoname:
                        j=colindex
                        while (j<i):
                            infos.append('N/A')
                            j=j+1
                        colindex=i+1
                        infos.append(infocontent)
                    i=i+1
        rating_num=html.find_all('strong',class_='rating_num')
        infos.append(rating_num[0].contents[0])
        rating_pnum=html.find_all('a',class_='rating_people')
        infos.append(rating_pnum[0].contents[0].contents[0])
        #print('~~~~~~~rating_people:'+str(rating_pnum[0].contents[0].contents[0]))
        #print(str(self.colname)+'\n\n')
        #print(str(infos))
        self.bookinfo_list.append(infos)
        #print(str(self.bookinfo_list))
    def getbooks_test(self,tagname):
        ##here should have a loop to get nextpage
        r=requests.get(self.tagdict[tagname])
        html=BeautifulSoup(r.text,"html.parser")
        items=html.find_all('li',class_='subject-item')
        for eachi in items[:]:
            book_url=BeautifulSoup(str(eachi),"html.parser").find_all('a',class_='nbg')
            booklink=book_url[0].get('href')
            print(str(booklink)+'\n\n')




if __name__=='__main__':
    dbspider=doubanspider()
    dbspider.get_download_url()
    dbspider.getbooks(u'编程')
    #dbspider.getbookinfo('https://book.douban.com/subject/26829016/')
