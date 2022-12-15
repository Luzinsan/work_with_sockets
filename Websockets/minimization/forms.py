from django import forms


class UserForm(forms.Form):
    name = forms.CharField(label='Введите Ваше имя: ', max_length=20, min_length=2)
    age = forms.IntegerField(label='Введите Ваш возраст: ', min_value=5, max_value=150)
    email = forms.EmailField(label='Логин: ')
    password = forms.CharField(label='Пароль: ', widget=forms.PasswordInput)


class TaskForm(forms.Form):
    method = forms.ChoiceField(choices=((1, "Метод Ньютона"), (2, "Метод Золотого сечения"), (3, "Метод Секущих"),
                                        (4, "Метод Стивенсона"), (5, "Метод Больцано")))
    function = forms.CharField()
