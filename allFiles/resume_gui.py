import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton
from PyQt5.QtCore import pyqtSlot
from designs import salaryCalculate
import sys
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib as plt
from sklearn.model_selection import train_test_split
from sklearn import preprocessing




def change_soup_text(cur_soup):
    texts = cur_soup.find_all(text=True)
    for t in texts:
        new_text = t.replace("\xa0", " ")
        new_text = new_text.replace("\u2009", "")
        t.replace_with(new_text)


def linear_regression(data, pred_data):
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(data.drop(['salary', 'salary_class'], axis=1),data['salary'], test_size=0.2, shuffle=True)
    model = LinearRegression()
    model.fit(Xtrain, Ytrain)
    Ypred = model.predict(pred_data.drop(['salary', 'salary_class'], axis=1))
    return Ypred


class CalculateWindow(QMainWindow, salaryCalculate.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.calculateB.clicked.connect(self.Calculate)
        self.show()


    @pyqtSlot()
    def Calculate(self):
        url = self.lineEdit.text()
        try:
            list_skills = []
            response = urllib.request.urlopen(url)
            webContent = response.read()

            soup = BeautifulSoup(webContent, features="html.parser")
            change_soup_text(soup)
            skills_block = soup.find('div', {'data-qa': 'skills-table'})
            if skills_block:
                all_skills = skills_block.find_all('span',
                                               {'class': 'bloko-tag__section bloko-tag__section_text'})
                for skill in all_skills:
                    list_skills.append(skill.text)
            city = soup.find('span',{'data-qa':'resume-personal-address'}).text
            resume_block = soup.find('div',{'data-qa':'resume-block-experience'})
            exp = resume_block.find('span',{'class':'resume-block__title-text resume-block__title-text_sub'}).text
            list_exp = exp.split('  ')[1:]
            exp_time_format = []
            if len(list_exp) > 2:
                exp_time_format.append(list_exp[0])
                exp_time_format.append(list_exp[2][1:])
            elif list_exp[1][1] == 'м':
                exp_time_format.append('0')
                exp_time_format.append(list_exp[0])
            else:
                exp_time_format.append(list_exp[0])
                exp_time_format.append('0')
            if int(exp_time_format[0]) < 5:
                exp_class = '1'
            elif int(exp_time_format[0]) < 10:
                exp_class = '2'
            elif int(exp_time_format[0]) < 15:
                exp_class = '3'
            elif int(exp_time_format[0]) < 20:
                exp_class = '5'
            elif int(exp_time_format[0]) < 25:
                exp_class = '6'
            else:
                exp_class = '7'
            data = pd.read_csv('data_for_model.csv')
            data2=pd.DataFrame(data=None, columns=data.columns)
            current_info = {}
            current_list = []
            i_skills = 0
            city_f = 0
            for column in data.columns:
                if column in list_skills:
                    i_skills += 1
                    current_info[column] = 1
                    current_list.append(1)
                elif column == 'exp_' + exp_class:
                    current_info[column] = 1
                    current_list.append(1)
                elif column == 'city_' + city:
                    city_f = 1
                    current_info[column] = 1
                    current_list.append(1)
                else:
                    current_info[column] = 0
                    current_list.append(0)
            data.loc[len(data)] = current_info
            data.iloc[:, :len(data.columns) - 2] = preprocessing.scale(data.iloc[:, :len(data.columns) - 2])
            data.mean(axis=0).round(3)
            data.std(axis=0).round(3)
            data2.loc[0,:] = data.iloc[-1].values
            pred_salary = linear_regression(data[:-1], data2)
            self.lineEdit.clear()
            if city_f == 0:
                self.label.setText('Cant predict for city: ' + city + '\nOnly Москва, Санкт-Петербруг'
                                                                      ' and Нижний Новгород available')
            elif i_skills > 0 :
                self.label.setText(f'Predicted salary: {int(pred_salary)}')
            else:
                self.label.setText('Not enough skills to predict salary')
        except:
            self.label.setText('Cant get info from page')


def main():
    app = QApplication(sys.argv)
    window = CalculateWindow()
    app.exec_()

if __name__ == '__main__':
    main()
