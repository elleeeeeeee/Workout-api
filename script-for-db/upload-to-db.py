import sqlite3

with open('exercise.txt', 'r') as f1:
    conn = sqlite3.connect('../conf/db.sqlite3')
    txt = f1.readlines()
    for e in txt:
        if e == "\n":
            txt.remove(e)

    d = {}
    uid = 1
    for i in range(0, 140, 7):
        name = txt[i]
        desc = txt[i + 1]
        instruction = txt[i + 2]
        muscles = txt[i + 3]
        duration = txt[i + 4]
        rest = txt[i + 5]
        exercise_type = txt[i + 6]
        d[uid] = {'name': name.strip(),
                 'desc': desc.split(":")[1].strip(),
                 'instruction': instruction.split(':')[1].strip(),
                 'muscles': muscles.split(':')[1].strip(),
                 'duration': duration.split(':')[1].strip(),
                 'rest': rest.split(':')[1].strip(),
                  'exercise_type': exercise_type.split(':')[1].strip()}
        uid += 1

    for v in d.values():
        name = v['name']
        desc = v['desc']
        instruction = v['instruction']
        muscles = v['muscles']
        exercise_type = v['exercise_type']
        conn.cursor().execute(
            """INSERT INTO 
            mainapp_exercises(name, description, instruction, target_muscles, rest_between_sets, exercise_type)
             VALUES (?, ?, ?, ?, ?, ?)""",
            (name, desc, instruction, muscles, rest, exercise_type))
        conn.commit()
