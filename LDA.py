# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 21:25:38 2021

@author: amits
"""

import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
import os


def plot_top_words(model, feature_names, n_top_words, yr, title):
    row = len(model.components_)//5
    fig, axes = plt.subplots(5, row, figsize=(100, 50), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]

        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f'Topic {topic_idx +1}',
                     fontdict={'fontsize': 15})
        ax.invert_yaxis()
        ax.tick_params(axis='both', which='major', labelsize=10)
        for i in 'top right left'.split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=20)

    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    #plt.show()
    plt.savefig("LDA_PFIZ_vocab_output/output_best_models_"+yr+".png")



if __name__ == '__main__':
    n_features = 50000
    n_components = 5
    n_top_words = 50
    years = ['0'+x if len(x) == 1 else x for x in [str(i) for i in range(21)]]
    #years = ['08']
    for yr in years:
        print(yr)
        base = 'output/PFE/' + yr
        files = os.listdir(base)
        files = [os.path.join(base, f) for f in files]
        
        tf_vectorizer = CountVectorizer(input = 'filename', max_df=0.95, min_df=2,
                                            max_features=n_features,
                                            stop_words='english',
                                            lowercase=True,                   

                                            token_pattern='[a-zA-Z0-9]{3,}'
                                            )
        tf = tf_vectorizer.fit_transform(files)
        
        lda = LatentDirichletAllocation(n_components=n_components,\
                                        learning_method='online',\
                                        learning_offset=20,\
                                        random_state=1024,\
                                        n_jobs = -1)
        
        search_params = {'n_components': [5, 10, 15], \
                          'learning_decay': [0.7, 0.9],\
                          'max_iter': [75]}
        
        
        model = GridSearchCV(lda, param_grid=search_params)
        model.fit(tf)
        best_model = model.best_estimator_
        print("Log Likelihood: ", best_model.score(tf))
        print("Perplexity: ", best_model.perplexity(tf))
        print("parameters:", model.best_params_)
        
        tf_feature_names = tf_vectorizer.get_feature_names()
        plot_top_words(best_model, tf_feature_names, n_top_words, yr, 'Topics in LDA model')
    