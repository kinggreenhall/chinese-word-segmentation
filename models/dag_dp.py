import re
from math import log


class Tokenizer(object):
    def __init__(self):
        self.dict_path = "./datas/dict.txt"
        self.re_cn = re.compile("([\u4E00-\u9FD5a-zA-Z0-9+#&._%-]+)", re.U)
        self.re_eng = re.compile("[a-zA-Z0-9]", re.U)
        self.freq_dict, self.freq_total = self.get_freq_dict()

    def get_freq_dict(self):
        with open(self.dict_path, "r", encoding="utf-8") as f_dict:
            freq_dict = {}
            freq_total = 0
            for line in f_dict.readlines():
                word, freq = line.split(" ")[:2]
                freq = int(freq)
                freq_dict[word] = freq
                freq_total += freq
                for word_index in range(len(word)):
                    word_frag = word[:word_index + 1]
                    if word_frag not in freq_dict:
                        freq_dict[word_frag] = 0
        return freq_dict, freq_total

    def get_dag(self, sentence):
        dag = {}
        sen_len = len(sentence)
        for i in range(sen_len):
            temp_list = []
            j = i
            frag = sentence[i]
            while j < sen_len and frag in self.freq_dict:
                if self.freq_dict[frag]:
                    temp_list.append(j)
                j += 1
                frag = sentence[i:j + 1]
            if not temp_list:
                temp_list.append(i)
            dag[i] = temp_list
        return dag

    def dp(self, sentence):
        dag = self.get_dag(sentence)
        sen_len = len(sentence)
        route = {sen_len: (0, 0)}
        # 取 log 防止数值下溢
        log_total = log(self.freq_total)
        for sen_index in reversed(range(sen_len)):
            freq_list = []
            for word_index in dag[sen_index]:
                word_freq = self.freq_dict.get(sentence[sen_index:word_index + 1])
                # 解决 log(0) 无定义问题, 则取 log(1)=0
                freq_index = (log(word_freq or 1) - log_total + route.get(word_index + 1)[0], word_index)
                freq_list.append(freq_index)
            route[sen_index] = max(freq_list)
        return route

    def cut_util(self, sentence):
        word_index = 0
        word_buf = ""
        result = []
        route = self.dp(sentence)
        while word_index < len(sentence):
            word_index_end = route[word_index][1] + 1
            word = sentence[word_index:word_index_end]
            # 找出单词
            if self.re_eng.match(word) and len(word) == 1:
                word_buf += word
                word_index = word_index_end
            else:
                if word_buf:
                    result.append(word_buf)
                    word_buf = ""
                else:
                    result.append(word)
                    word_index = word_index_end
        if word_buf:
            result.append(word_buf)
        return result

    def cut(self, sentence):
        block_list = self.re_cn.split(sentence)
        cut_result_list = []
        for block in block_list:
            # 跳过空的 block
            if not block:
                continue
            if self.re_cn.match(block):
                cut_result_list.extend(self.cut_util(block))
            else:
                cut_result_list.append(block)
        return cut_result_list


t = Tokenizer()
cut = t.cut
