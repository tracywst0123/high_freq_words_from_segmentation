import pandas as pd
import os
import numpy as np
import pkuseg
import jieba
import json
import pickle

Ignores = ['-', '_', ' ', '有限公司', '(', ')', '（', '）', '1', '2', '3', '01', '02']


class Piece:
    def __init__(self, piece, piece_id=None, cut=False, cut_type='jieba', length_cut_n=2, cut_char='-'):
        self.piece = piece
        self.id = piece_id
        if cut:
            self.word_list = self.cut_segments(cut_type=cut_type, length_cut_n=length_cut_n, cut_char=cut_char)
        else:
            self.word_list = []

    def cut_segments(self, cut_type='jieba', length_cut_n=2, cut_char='-'):
        """

        :param cut_type:
        :param length_cut_n:
        :param cut_char:
        :return:
        """
        if cut_type is 'jieba':
            word_list = jieba.cut(self.piece, cut_all=False, HMM=True)
        elif cut_type is 'pk':
            seg = pkuseg.pkuseg()
            word_list = seg.cut(self.piece)
        elif cut_type is 'length':
            word_list = self.cut_segments_length(n=length_cut_n)
        elif cut_type is 'character':
            word_list = self.piece.split(cut_char)
        else:
            raise Exception('Wrong cut type: ' + cut_type)

        word_list = clean_list(word_list)
        return word_list

    def cut_segments_length(self, n=2):
        p = self.piece
        word_list = []
        while len(p) >= n:
            word_list.append(p[:(n - 1)])
            p = p[n:]
        return word_list


def clean_list(word_list):
    w_df = pd.Series(word_list).str.extract(r'([\u4e00-\u9fff]+)').dropna()
    return w_df[0].tolist()


class Word:
    def __init__(self, word_string):
        self.word = word_string
        self.frequency = 0
        self.pieces = []
        self.pieces_id = []

    def increment_piece(self, piece, p_id=None, data=pd.read_csv('original_data.csv')):
        self.frequency += 1
        self.pieces.append(piece)
        if p_id is None:
            p_id = data.index[data['account_name'] == piece].tolist()[0]
        self.pieces_id.append(p_id)


class WordDict:
    def __init__(self):
        self.dictionary = {}


def get_words_df_with_seg(filter_seg=None, cut_type='character', cut_char='-'):
    accounts = pd.read_csv('original_data.csv')
    if filter_seg:
        accounts = accounts[accounts['account_name'].str.contains(filter_seg)]
    word_dict = dict()
    for row in accounts.iterrows():
        # index = row[0]
        p = Piece(row[1][0], cut=True, cut_type=cut_type, cut_char=cut_char)
        segments = p.word_list
        # print(segments)
        for s in segments:
            if s in word_dict:
                word_dict[s] += 1
            else:
                word_dict[s] = 1
    word_freq = pd.DataFrame(list(word_dict.items()))
    word_freq.rename(columns={0: 'word', 1: 'count'}, inplace=True)
    return word_freq


if __name__ == '__main__':
    word_freq = get_words_df_with_seg()
    word_freq.to_csv('word_dictionary_pk.csv')

    # with open('word_dict1.json', 'wb') as fp:
    #     json.dump(word_dict, fp)


