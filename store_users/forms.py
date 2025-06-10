from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django import forms
from .models import StoreUser



class UserLoginForm(AuthenticationForm):
    '''форма для аутентификации юзера, валидации вводимых данных'''
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = StoreUser # модель, в которую будут поступать валидные данные из формы авторизации
        fields = ['username','password']
        labels = {'username':'ВВедите имя пользователя','password':'Введите пароль'}


class UserRegistrationForm(UserCreationForm):
    '''Форма для регистрации юзера + валидация вводимых данных'''
    #атрибуты при слиянии бэка с фронтом
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите имя'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите фамилию'}))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите имя пользователя'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите адрес эл. почты'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Подтвердите пароль'}))
    code_word = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Кодовое слово на случай утраты пароля'}))
    
    class Meta:
        model = StoreUser
        fields = ['username','first_name','last_name','email','password1','password2', 'code_word']

    def save(self, commit = True):
        new_user = super().save(commit=commit) 
        # new_user = super(UserCreationForm,self).save(commit=True)# сохранение нового юзера в бд
        return new_user
    
class UserProfileForm(UserChangeForm):
    '''Форма для отоббражения полей профиля пользователя с возможностью 
    CRUD операций + аватарку поставить'''
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите имя пользователя'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите имя'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите фамилию'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите адрес эл. почты'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class':'form-control mt-3',
        'placeholder' : 'Выберите изображение'}),required=False)
    class Meta:
        model = StoreUser
        fields = ['username','first_name','last_name','email','image']


class VerifyCodeWordForm(forms.Form):
    '''форма для верификации кодового слова при смене пароля'''
    username = forms.CharField(label='имя пользователя')
    code_word = forms.CharField(label='кодовое слово')
    email = forms.CharField(label='почта пользователя')

    def clean(self):
        cleaned_data =super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        code_word =  cleaned_data.get('code_word')
        try:
            current_user = StoreUser.objects.get(username=username, email=email)
        except StoreUser.DoesNotExist as err:
            raise forms.ValidationError(f'Пользователь с таким именем или почтой не найден')
        if current_user.code_word != code_word:
                raise forms.ValidationError('Неверное кодовое слово')
        return cleaned_data
    
class NewPasswordForm(forms.Form):
    '''форма для ввода нового пароля верифицированного пользователя'''
    password1 = forms.CharField(label='новый пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='подтверждение пароля', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError('пароли не совпадают')
        return cleaned_data

