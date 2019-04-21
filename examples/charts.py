import matplotlib.pyplot as plt
from librus_tricks import aio, SynergiaClient, filters
from examples.hello_librus import ask_for_credentials

session = SynergiaClient(aio(**ask_for_credentials()), cache_location='../librus_tricks/cache.sqlite')

def count_avg(*grades):
    """

    :type grades: librus_tricks.classes.SynergiaGrade
    :rtype: float
    """
    s_grades = 0
    total_weight = 0
    for grade in grades:
        for n in range(grade.category.weight):
            s_grades += grade.real_value
        total_weight += grade.category.weight
    return s_grades / total_weight


if __name__ == '__main__':
    target_subject = 'Matematyka'
    math_grades = [gr for gr in filters.filter_grades(session.get_grades()) if gr.subject.name == target_subject and gr.real_value is not None]
    arvgs = []
    for grade_index in range(math_grades.__len__()):
        arvgs.append(count_avg(*math_grades[:grade_index+1]))

    plt.plot(
        [grade.date for grade in math_grades],
        arvgs
    )
    plt.scatter(
        [grade.date for grade in math_grades],
        [grade.real_value for grade in math_grades],
        color='orange',
        s=10
    )
    # plt.xticks([grade.date for grade in math_grades])
    plt.xlabel('ilość ocen')
    plt.ylabel('średnia')
    plt.title(f'{target_subject} ({str(arvgs[-1])})')
    plt.grid(True)
    plt.show()
