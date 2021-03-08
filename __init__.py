from app import app, db, User, Role, Examen, User_Examen, Branch, Semester, Class, Salle, Module
############ Create ##############
with app.app_context():
    db.create_all()
    m1 = Module(name="mecanique de point", label="Mecanique de point")
    m2 = Module(name="technologie web 1", label="Technologie web 1")
    sa1 = Salle(name="c1", label="C1", capacity=30)
    sa2 = Salle(name="a6", label="A6", capacity=20)
    sa3 = Salle(name="amphi1", label="Amphi", capacity=100)
    b1 = Branch(name="g-gnfo", label="G-Info")
    b2 = Branch(name="g-indus", label="G-Indus")
    s1 = Semester(name="s5", label="S5")
    s2 = Semester(name="s6", label="S6")
    s3 = Semester(name="s7", label="S7")

    c1 = Class(name="G-Info-S7", capacity=0)
    c2 = Class(name="G-Info-S5", capacity=3)
    c3 = Class(name="G-Indus-S7", capacity=0)
    r1 = Role(name="Admin")
    r2 = Role(name="SubAdmin")
    r3 = Role(name="Professor")
    r4 = Role(name="Student")
    u1 = User(name="Admin", email="hamza.elharsi@uit.ac.ma")
    u3 = User(name="Saad", email="saad.errazgouni99@gmail.com",
              apogee="17005228", class_id=1)
    u4 = User(name="Aymane", email="aymane.elammar@gmail.com",
              apogee="17007831", class_id=1)
    u2 = User(name="Yahya", email="hamzaelharsi123@gmail.com",
              apogee="17007212", class_id=1)
    c2.students.append(u2)
    c2.students.append(u3)
    u1.roles.append(r1)
    u3.roles.append(r4)
    u4.roles.append(r4)
    u2.roles.append(r4)
    db.session.add_all([r1, r2, r3, r4, m1, m2, sa1, sa2, sa3, b1, b2, s1, s2, s3, c1, c2, c3,
                        u1, u2, u3, u4])
    db.session.commit()
    ########### Testing ###################
    semesters = db.session.query(Semester).all()
    for name in semesters:
        print(name.name)
