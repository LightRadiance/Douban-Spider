import jieba
import pandas as pd
import matplotlib.pyplot as plt 
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans

class Parser :
    def __init__(self) :
        self.stopwords = []
        file_path = ['stopwords/baidu_stopwords.txt', 
                     'stopwords/cn_stopwords.txt', 
                     'stopwords/hit_stopwords.txt', 
                     'stopwords/scu_stopwords.txt',
                     'stopwords/typical_stopwords.txt']
        for path in file_path :
            with open(file=path) as f :
               for line in  f.readlines() :
                   self.stopwords.append(line.strip('\n'))
        
        pass
    
    ## 词云分析函数
    def parse_hot_words(self, texts, title) :
        sentence = ''
        for text in texts :
            ## 去除特殊符号
            text = text.replace('<spanstyle=""font-weight:bold;"">', '').replace('</span>', '')
    
            sentence += text
        words_str = ' '.join(jieba.cut(sentence))
        wordcloud = WordCloud(font_path='fonts/Hiragino Sans GB W3.ttf', width=2500, height=1500, max_words=20, stopwords=self.stopwords)
        wordcloud.generate(words_str)
        
        # 显示词云图
        plt.imshow(wordcloud)
        plt.axis('off')
        plt.show()
        
        ## 保存词云图
        # wordcloud.to_file('result/'+title+'.jpg')
        
    def statistic(self, data, classes) :
        statistic_res = {}
        statistic_df = []
        
        for feature_name, categories in classes.items() :
            ## 建立统计表
            statistic_res[feature_name] = {}
            for category in categories :
                statistic_res[feature_name][category] = []

            for film_name, features in data.items() :
                for feature in features :
                    if feature in categories :
                        statistic_res[feature_name][feature].append(film_name)
        
        ## 转化为Pandas数据格式分析
        for feature_name, categories  in statistic_res.items() :
            series = pd.Series(dict(map(lambda x : (x, len(categories[x])), categories.keys())))
            series = series.dropna()
            series = series.sort_values()
            statistic_df.append(series)
            
            # # 统计图绘制及保存
            # plt.figure(figsize=[15,9])  
            # series.plot(kind='barh')
            # plt.savefig('result/'+feature_name+'.jpg', dpi=300)
            
        return statistic_df
        
    def k_means_algorithm(self,  documents, k_num=8) :
        res = {}
        for index,texts in enumerate(documents) :
            sentence = ''
            for text in texts :
                text = text.replace('<spanstyle=""font-weight:bold;"">', '').replace('</span>', '').replace('&quot;', '')
                sentence += text
            documents[index] = sentence
        documents = [" ".join(jieba.cut(text)) for text in documents]   

        ## 计算TFIDF 
        vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
        X = vectorizer.fit_transform(documents)
        kmeans = KMeans(n_clusters=k_num, n_init=10, init='k-means++', random_state=None)
        Y = kmeans.fit_predict(X=X)
        
        return list(map(lambda x: str(x), Y))

        

if __name__ == '__main__' :
    parser = Parser()

    ## 读取待分析数据
    top250_df = pd.read_csv('data/top250.csv', names=['film_url', 'film_name', 'film_date', 'film_area', 'film_type'], dtype=object)    
    films_df = pd.read_csv('data/films.csv', names=['film_name', 'intro', 'actors_url', 'comment_url1', 'comment_url2'], dtype=object)
    comments_df = pd.read_csv('data/comments.csv', names=['film_name', 'comment1', 'comment2'], dtype=object)
    actors_df = pd.read_csv('data/actors.csv', dtype=object)
    
    ## 文本信息预处理
    intersted_films = ['阿甘正传']
    texts = []                
    for index,row in films_df.iterrows() :
        if row['film_name'] in intersted_films :
            texts.append(row['intro'])
   
    for index,row in comments_df.iterrows() :
        if row['film_name'] in intersted_films :
            texts.append(row['comment1'])
            texts.append(row['comment2'])
    ## 热词分析
    # parser.parse_hot_words(texts=texts, title=intersted_films[0])
    
    # 电影信息预处理
    dates = []
    areas = []
    types = []
    data = {}
    for index,row in top250_df.iterrows() :
        features = set()
        if str(row['film_date']) not in dates : 
            dates.append(str(row['film_date']))
        features.add(str(row['film_date']))

        for area in row['film_area'].split() :
            if area not in areas :
                areas.append(area)
            features.add(area)
            
        for type in row['film_type'].split() :
            if type not in types :
                types.append(type)
            features.add(type)
        data[row['film_name']] = features
    classes = {'Date':dates, 'Area':areas, 'Type':types}
    ## 统计
    # parser.statistic(data=data, classes= classes)
    
    ## 文本信息预处理
    documents = []
    for index, row in top250_df.iterrows() :
        texts = [] 
        texts.append(films_df.loc[index, 'intro'])
        texts.append(comments_df.loc[index, 'comment1'])
        texts.append(comments_df.loc[index, 'comment2'])
        documents.append(texts)
    for i in range(1, 11) :
        k_num = 8
        # # 聚类分析
        # class_res = parser.k_means_algorithm(documents=documents, k_num=k_num)
        
        # ## 保存结果
        # class_res_dict = {} 
        # for j in range(0, k_num) :
        #     class_res_dict['label'+str(j)] = []
            
        # for row,label in zip(top250_df.iterrows(),class_res) :
        #     class_res_dict['label'+label].append(row[1]['film_name'])
        # class_res_series = pd.Series(class_res_dict)
        # class_res_series.to_csv(path_or_buf='result/classfication_result'+str(i)+'.csv', encoding='utf-8',header=False, mode='w')
        