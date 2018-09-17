import numpy as np
import pickle
class Hmm(object):
    def __init__(self,load=False):
        self.states=['B','M','E','S']
        self.model_path='r_hmm_data.pkl'
        self.A_dic={}
        self.B_dic={}
        self.Pi_dic={}
        self.Count_dit={}
        self.line_num=0
        if load:
            self.load_parameters()
        # self.char_set=set()
    #记录词频 ,使得可以继续训练参数
    def load_parameters(self):
        with open(self.model_path,'rb') as f:
            # pickle.dump(self.A_dic,f)
            self.A_dic=pickle.load(f)
            self.B_dic=pickle.load(f)
            self.Pi_dic=pickle.load(f)
            self.Count_dit=pickle.load(f)
            self.line_num=pickle.load(f)
            # pickle.dump(self.B_dic,f)
            # pickle.dump(self.Pi_dic,f)
            # pickle.dump(self.Count_dit,f)
            # pickle.dump(self.line_num,f)
            # pickle.dump(self.char_set,f)

    def save_parameters(self):
        with open(self.model_path,'wb') as f:
            pickle.dump(self.A_dic, f)
            pickle.dump(self.B_dic, f)
            pickle.dump(self.Pi_dic, f)
            pickle.dump(self.Count_dit, f)
            pickle.dump(self.line_num, f)

    def initparameters(self,trained=False):
        if trained:
            self.load_parameters()
        else :
            for state in self.states:
                self.A_dic[state]={s:0.0 for s in self.states}
                self.B_dic[state]={}
                self.Pi_dic[state]=0.0
                self.Count_dit[state]=0.0

    def makeLabel(self,text):
        length=len(text)
        if length==1:
            return ['S']
        else:
            return ['B']+['M']*(length-2)+['E']

    #从语料中获取词频
    def corpus_read(self,file_path,trained=False):
        self.initparameters(trained)
        chars_set=set()
        with open(file_path,'r') as f:
            for line in f:
                if not line:
                    continue
                #get chars
                chars=[word for word in line.strip() if word!=' ']
                self.line_num+=1
                #upgrade charset
                chars_set.update(chars)
                #get word
                words=line.split()
                word_state=[]
                #get word label
                for word in words:
                    word_state.extend(self.makeLabel(word))
                for index,status in enumerate(word_state):
                    self.Count_dit[status]+=1
                    if index==0:
                        self.Pi_dic[status]+=1
                    #统计A_dic,B_dic
                    else :
                        self.A_dic[word_state[index-1]][status]+=1
                        self.B_dic[status][chars[index]]=\
                            self.B_dic[status].get(chars[index],0)+1
    #词频转化为概率
    def wfre2pro(self):
        Pi_pro_dic={state:freq/self.line_num for state,freq in self.Pi_dic.items()}
        A_pro_dic={states:{state:freq/self.Count_dit[state]
                           for state,freq in freqs.items()}
                   for states,freqs in self.A_dic.items()}
        B_pro_dic={state:{char:freq/self.Count_dit[state]
                           for char,freq in charsfreqs.items()}
                   for state,charsfreqs in self.B_dic.items()}
        return Pi_pro_dic,A_pro_dic,B_pro_dic
    def viterbi(self,text):
        Pi_pro_dic,A_pro_dic,B_pro_dic=self.wfre2pro()
        print(Pi_pro_dic,'\n',A_pro_dic,'\n',B_pro_dic)
        path_v=[{}]
        path_max={}
        for state in self.states:
            path_v[0][state]=Pi_pro_dic[state]*B_pro_dic[state].get(text[0],0)
            path_max[state]=[state]

        for t in range(1,len(text)):
            path_v.append({})
            new_path={}
            for state in self.states:
                (temp_pro,temp_state)=max([(path_v[t-1][y0]*A_pro_dic[y0][state]*B_pro_dic[state].get(text[t],0),y0)
                                           for y0 in self.states])
                path_v[t][state]=temp_pro
                new_path[state]=path_max[temp_state]+[state]
            path_max=new_path
        best_path_pro,last_state=max([(path_v[len(text)-1][y0],y0) for y0 in self.states])
        return path_max[last_state]

    def cut(self,text,best_path):
        begin,end=0,0
        cut_string=[]
        for index,char in enumerate(text):
            signal=best_path[index]
            if signal=='B':
                begin=index
            elif signal=='E':
                cut_string.append(text[begin:index+1])
                end=index+1
            elif signal=='S':
                cut_string.append(char)
                end=index+1
        if end<len(text):
            cut_string.append(text[end:])
        return cut_string

    def use_cut(self,text):
        best_path=self.viterbi(text)
        return self.cut(text,best_path)

if __name__ == '__main__':
    testHmm=Hmm(load=True)
    # testHmm.corpus_read('trainCorpus.txt_utf8')
    text='喜欢你，么么哒!'
    print(testHmm.use_cut(text))


