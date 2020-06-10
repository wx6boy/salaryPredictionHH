import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re


def add2db(id_list, city, exp, salary, list_of_skills):
    with open("resume_base_hh.txt", "a", encoding='utf-8') as p:
        for i in range(len(id_list)):
            p.write(id_list[i] + '/' + city + '/' + exp[i] + '/' + str(salary[i]) + '/')
            for j in range(len(list_of_skills[i])):
                p.write(list_of_skills[i][j] + ';;')
            p.write('\n')
        p.close()


def make_skills_file(skills_list):
    with open("skills.txt", "w", encoding='utf-8') as p:
        for new_skill in skills_list:
            p.write(new_skill[0] + ';;' + str(new_skill[1]) + '\n')
        p.close()


def change_soup_text(cur_soup):
    texts = cur_soup.find_all(text=True)
    for t in texts:
        new_text = t.replace("\xa0", " ")
        new_text = new_text.replace("\u2009", "")
        t.replace_with(new_text)


cities_list = {1: 'Москва', 2: 'Санкт Петербург', 66: 'Нижний Новгород'}

frequency_of_skills = {}
for j in cities_list:
    city = cities_list[j]
    for i in range(220, -1, -1):
        try:
            url = 'https://nn.hh.ru/search/resume?area=' + str(j) + '&exp_period=all_' \
                  'time&logic=normal&pos=full_text&from=employer_index_header&text=&specialization=1&page=' + str(i)

            response = urllib.request.urlopen(url)
            webContent = response.read()

            soup = BeautifulSoup(webContent, features="html.parser")
            change_soup_text(soup)

            resume_block = soup.find('div', {'data-qa': 'resume-serp__results-search'})
            resumes_list = resume_block.find_all('div', {'data-qa': 'resume-serp__resume'})
            resume_id = []
            salaries = []
            skills = []
            exp_time = []
            for resume in resumes_list:
                list_skills = []
                current_salary = resume.find('div', {'class': 'resume-search-item__compensation'}).text

                if current_salary.find('руб.') != -1:
                    numbers = re.findall('(\d+)', current_salary)[0]
                    if int(numbers) < 1000:
                        numbers = numbers + '000'

                    new_url = "https://nn.hh.ru" + resume.find('a', {'class': 'resume-search-item__name'}).get('href')
                    resume_response = urllib.request.urlopen(new_url)
                    resume_content = resume_response.read()
                    new_soup = BeautifulSoup(resume_content, features="html.parser")
                    change_soup_text(new_soup)
                    skills_block = new_soup.find('div', {'data-qa': 'skills-table'})
                    if skills_block:
                        all_skills = skills_block.find_all('span',
                                                           {'class': 'bloko-tag__section bloko-tag__section_text'})
                        for skill in all_skills:
                            list_skills.append(skill.text)
                    resume_id.append(resume.get('data-resume-id'))
                    exp_time_format = []
                    current_exp = resume.find('div', {'data-qa': 'resume-serp__resume-excpirience-sum'}).text
                    list_exp = current_exp.strip().split(' ')
                    if len(list_exp) > 4:
                        exp_time_format.append(list_exp[0])
                        exp_time_format.append(list_exp[6])
                    elif list_exp[3][0] == 'м':
                        exp_time_format.append('0')
                        exp_time_format.append(list_exp[0])
                    else:
                        exp_time_format.append(list_exp[0])
                        exp_time_format.append('0')
                    myString = '-'.join(exp_time_format)
                    exp_time.append(myString)
                    salaries.append(numbers)
                    skills.append(list_skills)
                    for skill in list_skills:
                        if skill:
                            count = frequency_of_skills.get(skill, 0)
                            frequency_of_skills[skill] = count + 1

            add2db(resume_id, city, exp_time, salaries, skills)
        except Exception:
            continue

frequency_of_skills = sorted(frequency_of_skills.items(), key=lambda kv: kv[1], reverse=True)
make_skills_file(frequency_of_skills)
