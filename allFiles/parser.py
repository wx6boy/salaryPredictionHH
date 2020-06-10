with open("data_resume.csv", "w", encoding='utf-8') as f:
    f.write('city,exp,salary')
    skills = []
    with open("skills.txt", "r", encoding='utf-8') as p:
        i = 0
        for line in p:
            lst = line.strip().split(';;')
            if int(lst[1]) > 100:
                skills.append(lst[0])
            else:
                break
        p.close()
    for skill in skills:
        f.write(',' + skill)
    f.write('\n')
    with open("resume_base_hh.txt", "r", encoding='utf-8') as o:
        o_file = o.read().strip().split('\n')
        for line in o_file:
            lst = line.strip().split('/')
            lst[2] = lst[2].split('-')[0]
            if int(lst[2]) < 5:
                lst[2] = '1'
            elif int(lst[2]) < 10:
                lst[2] = '2'
            elif int(lst[2]) < 15:
                lst[2] = '3'
            elif int(lst[2]) < 20:
                lst[2] = '5'
            elif int(lst[2]) < 25:
                lst[2] = '6'
            else:
                lst[2] = '7'
            f.write(lst[1] + ',' + lst[2] + ',' + lst[3])
            lst_skills = lst[4].split(';;')
            for skill in skills:
                if skill in lst_skills:
                    f.write(',1')
                else:
                    f.write(',0')
            f.write('\n')
